# Migration Plan — v3 Features into Improved v2

**Date:** 2026-03-19
**Input context:** `context.md`
**Goal:** Bring the three v3 improvements (3-agent BAML pipeline, Hybrid/Rules toggle, PII Privacy Mode toggle) into the improved v2 without breaking existing closed gaps.

---

## 1. Planning Principles

1. **Regression-safe delivery**
   - The existing 40-test regression suite is the acceptance gate. No tests may regress.

2. **Contract-first**
   - BAML output types must be mapped to the existing Stage-2 contract before UI work begins.

3. **Additive, not destructive**
   - Every change is an addition or targeted replacement. No existing routes, CORS config, or 3-screen frontend structure is removed.

4. **Scoring-weighted execution**
   - 3-agent BAML (Hybrid 35% + Pluggable 25%) is executed first; UI toggles (XAI 20% + Security 20%) follow.

---

## 2. Target End State

At completion, the improved v2 must demonstrate:

- 3-agent BAML recommendation pipeline producing structured reasoning per agent.
- `/api/recommend` accepting `force_rule_based: bool` and returning `recommendation_source`, `review_required`, and `security_metadata`.
- A live Hybrid AI / Rules mode toggle in the Screen 1 dashboard header.
- A live PII Privacy Mode toggle in the Screen 1 dashboard that switches between rehydrated and masked displays using `security_metadata.rehydration_map`.
- Reasoning trace displayed in Privacy Mode shows the masked (token-bearing) version of the AI output.
- Existing 40-test regression suite: still passing.
- All three screens operational.

---

## 3. Migration Items

| ID | Feature | POC Scoring Impact | Priority |
|----|---------|-------------------|----------|
| MIG-1 | BAML: 3-agent pipeline | Hybrid 35% + Pluggable 25% | P0 |
| MIG-2 | Workflow: RuleEvaluator + 3-agent chain + fallback | Hybrid 35% | P0 |
| MIG-3 | Orchestrator: force_rule_based + security_metadata | Hybrid 35% + Security 20% | P1 |
| MIG-4 | contracts.py: force_rule_based in request + security_metadata in response | Hybrid 35% | P1 |
| MIG-5 | Frontend: Hybrid AI/Rules toggle | XAI 20% | P2 |
| MIG-6 | Frontend: PII Privacy Mode toggle | Security 20% + XAI 20% | P2 |
| MIG-7 | Synthesis: enrichment.baml + scripts | Demo quality | P3 |

---

## 4. Execution Sequence

### Step 0 — Pre-Migration Baseline

- Run `uv run pytest scripts/tests -v` and confirm 40 passed.
- Capture baseline in `implementation/_lastest_test_results.md`.
- Confirm API starts cleanly on port 8010.

### Step 1 — BAML: 3-Agent Pipeline (MIG-1)

**File:** `POC/v2/baml_src/clinical/recommendation_output.baml`

Remove `GenerateRecommendation()` and `RecommendationOutput` BAML class. Add:

**New types:**
- `ClinicalRiskProfile`: `primary_risks[]`, `severity_assessment`, `biomarker_interpretation`, `clinical_summary_bullets[]`, `suggested_tier` (Tier), `supporting_signal_ids[]`, `missing_signal_ids[]`
- `RecommendationPlan`: `ai_recommended_tier` (Tier), `tier_deviation_justification` (string?), `selected_add_ons[]` (AddOnItem), `policy_reasoning` (string)
- `FinalRecommendation`: `plan` (RecommendationPlan), `communication_script` (CommunicationScript)

**New functions:**
```
function AnalyzeClinicalRisks(clinical_signals: string, biomarker_trends: string,
                               hard_constraints: string, program_ruleset: string) -> ClinicalRiskProfile
  client NavaveijClient
  prompt #"
    Role: Senior Physician and Clinical Analyst
    Task: Analyze the provided clinical signals, biomarker trends, and hard constraints.
    Return a structured ClinicalRiskProfile identifying primary risk categories,
    severity assessment, biomarker interpretation, clinical summary bullets,
    a suggested tier, and signal IDs supporting or missing from the analysis.
  "#

function MatchProgramRules(risk_profile: ClinicalRiskProfile,
                           program_ruleset: string) -> RecommendationPlan
  client NavaveijClient
  prompt #"
    Role: Navavej Program Policy Specialist
    Task: Given the clinical risk profile and program ruleset, select the appropriate
    package tier and add-on items. Justify any deviation from the rule preliminary tier.
    Return a RecommendationPlan with selected add-ons and policy reasoning.
  "#

function ComposeRecommendation(risk_profile: ClinicalRiskProfile,
                               plan: RecommendationPlan) -> FinalRecommendation
  client NavaveijClient
  prompt #"
    Role: Clinical Communicator
    Task: Compose a patient-facing communication script and finalize the recommendation.
    Combine the risk profile and recommendation plan into a FinalRecommendation.
    The communication_script must have all four sections: health_summary,
    recommendation_rationale, addon_highlights, next_steps.
    Use professional medical English. No greetings. No raw snake_case identifiers.
  "#
```

Keep unchanged: `ValidateRecommendation()`, `Tier`, `PriorityLevel`, `AddOnItem`, `CommunicationScript`.

After editing: `uv run baml-cli generate`

Gate: BAML generates without errors. Import check passes.

### Step 2 — Workflow: RuleEvaluator + 3-Agent Chain + Fallback (MIG-2)

**File:** `POC/v2/backend/src/services/workflows/clinical.py`

1. Check if `backend/src/services/rules.py` exists in v2. If not, copy from v3.
2. Add `force_rule_based: bool = False` to `execute()`.
3. Import `RuleEvaluator` and always run it to capture `rule_preliminary_tier`.
4. In Phase 4, replace single `b.GenerateRecommendation()` with:

```python
rule_tier = rule_evaluator.evaluate(...)

if force_rule_based:
    ai_output = _build_rule_based_output(rule_tier, ...)
    ai_output["recommendation_source"] = "RuleBased"
    ai_output["review_required"] = True
else:
    try:
        risk_profile = b.AnalyzeClinicalRisks(...)
        plan = b.MatchProgramRules(risk_profile, ...)
        final = b.ComposeRecommendation(risk_profile, plan)
        ai_output = _map_final_to_ai_output(final, rule_tier)
        ai_output["recommendation_source"] = "AI"
        ai_output["review_required"] = False
    except Exception:
        ai_output = _build_rule_based_output(rule_tier, ...)
        ai_output["recommendation_source"] = "RuleBased"
        ai_output["review_required"] = True
```

5. `_map_final_to_ai_output(final, rule_tier)` must produce keys compatible with `_normalize_stage2()` in contracts.py:

| Dict key | Source |
|---|---|
| `ai_recommended_tier` | `final.plan.ai_recommended_tier` |
| `tier_deviation_justification` | `final.plan.tier_deviation_justification` |
| `add_ons` | `final.plan.selected_add_ons` (serialized) |
| `reasoning_trace` | `"\n".join(risk_profile.clinical_summary_bullets) + "\n" + plan.policy_reasoning` |
| `supporting_signals` | `risk_profile.supporting_signal_ids` |
| `missing_signals` | `risk_profile.missing_signal_ids` |
| `communication_script` | `final.communication_script` (serialized) |
| `rule_preliminary_tier` | `rule_tier` |

Gate: `uv run pytest scripts/tests -v` → no regressions.

### Step 3 — Orchestrator: force_rule_based + security_metadata (MIG-3)

**File:** `POC/v2/backend/src/services/orchestrator.py`

1. Add `force_rule_based: bool = False` to `generate_recommendation()`. Pass to `workflow.execute()`.
2. Before rehydration, snapshot the masked output:
   ```python
   masked_ai_output = context.ai_output.copy()
   rehydrated_output = rehydrator.rehydrate(context.ai_output)
   ```
3. Include in result:
   ```python
   result["security_metadata"] = {
       "rehydration_map": context.rehydration_map,
       "masked_ai_output": masked_ai_output,
       "is_poc_demo": True
   }
   ```

Gate: Orchestrator returns `security_metadata` for both AI and rule-based paths.

### Step 4 — contracts.py: Wire force_rule_based + security_metadata (MIG-4)

**File:** `POC/v2/backend/src/api/routes/contracts.py`

1. Add `force_rule_based: bool = False` to `RecommendRequest` Pydantic model.
2. Pass to `orchestrator.generate_recommendation()`.
3. Ensure `security_metadata` from orchestrator result is included in the response body (not stripped by `_normalize_stage2`).
4. Surface `recommendation_source` and `review_required` in response.

Gate: `POST /api/recommend` with `force_rule_based: true` returns `recommendation_source: "RuleBased"`. With `false`, returns `"AI"`. Both include `security_metadata`.

### Step 5 — Frontend: Hybrid AI/Rules Toggle (MIG-5)

**File:** `POC/v2/frontend/src/app/page.tsx`
- Add state: `const [isRuleBasedForced, setIsRuleBasedForced] = useState(false)`
- Add toggle button in header utility bar (amber when ON, white when OFF)
- Pass `isRuleBasedForced` as prop to `<RecommendationPanel>`

**File:** `POC/v2/frontend/src/services/api.ts`
- Update `getRecommendation(patientToken, forceRuleBased = false)` to include `force_rule_based` in POST body

**File:** `POC/v2/frontend/src/components/dashboard/RecommendationPanel.tsx`
- Accept `isRuleBasedForced` prop; include in the `useEffect` dependency array to re-fetch on toggle

Gate: Toggling the button triggers a new recommendation fetch; response `recommendation_source` reflects the mode.

### Step 6 — Frontend: PII Privacy Mode Toggle (MIG-6)

**File:** `POC/v2/frontend/src/app/page.tsx`
- Add state: `const [privacyMode, setPrivacyMode] = useState(false)`
- Add `getDisplayValue(originalValue, fallbackToken)` helper that reverses the `rehydration_map`
- Replace hard-coded patient PII fields (name, ID, MRN, phone, email) with `getDisplayValue(field, "tok_*")`
- Add Privacy Mode toggle button (Lock/Unlock icon, red/green color)
- Pass `privacyMode` prop to `<RecommendationPanel>`

**File:** `POC/v2/frontend/src/components/dashboard/RecommendationPanel.tsx`
- Accept `privacyMode: boolean` prop
- In reasoning trace section: switch between `data.reasoning_trace` (physician view) and `data.security_metadata?.masked_ai_output?.reasoning_trace` (AI masked view)

Gate: Toggling Privacy Mode switches patient name/ID display and reasoning trace between real values and UUID tokens.

### Step 7 — Synthesis: enrichment.baml + scripts (MIG-7)

1. Copy `POC/v3/baml_src/synthesis/enrichment.baml` → `POC/v2/baml_src/synthesis/enrichment.baml`
2. Copy `POC/v3/scripts/enrich_*.py` (4 files) → `POC/v2/scripts/`
3. Run `uv run baml-cli generate`

Gate: BAML generates without errors. Enrichment scripts are importable.

---

## 5. Migration-to-Task Mapping

| MIG | Task | Depends On | Exit Evidence |
|---|---|---|---|
| MIG-1 | BAML 3-agent pipeline | Baseline | BAML generates; import passes |
| MIG-2 | Workflow update | MIG-1 | 40 tests still passing |
| MIG-3 | Orchestrator update | MIG-2 | security_metadata in response |
| MIG-4 | contracts.py update | MIG-3 | force_rule_based smoke test |
| MIG-5 | Frontend Hybrid toggle | MIG-4 | Re-fetch on toggle; source field reflects mode |
| MIG-6 | Frontend Privacy toggle | MIG-4 | PII display switches on toggle |
| MIG-7 | Synthesis enrichment | Independent | BAML generates; scripts run |

---

## 6. Deliverable Artifacts

During execution, maintain:

- `implementation/_discovery.md` — Findings and decisions during implementation.
- `implementation/_lastest_test_results.md` — Raw test outputs per step.
- `implementation/_development_summary.md` — Interpreted status, closed items, open risks.

Per-feature folders (recommended for traceability):
- `implementation/MIG-1-baml-3-agent/`
- `implementation/MIG-2-workflow-update/`
- `implementation/MIG-3-orchestrator/`
- `implementation/MIG-4-contracts-api/`
- `implementation/MIG-5-frontend-hybrid-toggle/`
- `implementation/MIG-6-frontend-privacy-toggle/`
- `implementation/MIG-7-synthesis/`

---

## 7. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| BAML output type mismatch with `_normalize_stage2` | Map `FinalRecommendation` → ai_output dict explicitly before passing to contracts.py; verify all V1–V10 validation rules are satisfied |
| `rehydration_map` not populated in rule-based fallback path | Ensure workflow always builds and returns rehydration_map even when `force_rule_based=True` (map may be empty) |
| BAML regeneration forgotten after schema edits | Run `uv run baml-cli generate` at the end of every MIG-1 or MIG-7 edit |
| Test regressions from workflow refactor | Run full `uv run pytest scripts/tests -v` after each step before proceeding |
| RuleEvaluator not present in v2 | Check first; copy from v3 if missing |

---

## 8. Definition of Done

The migration is complete when:

- All 7 MIG items are implemented with exit evidence.
- Full regression suite passes: `uv run pytest scripts/tests -v` → ≥ 40 passed.
- End-to-end demo works: Screen 1 shows AI recommendation, toggle switches to rule-based, Privacy Mode toggle shows masked tokens.
- `implementation/_development_summary.md` is up to date.

---

## 9. Migration Status (as of 2026-03-19)

| MIG | Status | Test Evidence |
|---|---|---|
| MIG-1 | Not started | — |
| MIG-2 | Not started | — |
| MIG-3 | Not started | — |
| MIG-4 | Not started | — |
| MIG-5 | Not started | — |
| MIG-6 | Not started | — |
| MIG-7 | Not started | — |
