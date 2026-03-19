# Rules Gap Discovery — POC v2 vs Rule Synthesis Framework

**Date:** 2026-03-19
**Scope:** Compare POC v2 implementation against the Rule Synthesis Framework and AI Team
Onboarding document (§4 Key Technical Decisions, §7 Output Schema, §8 Tier Logic, §9 Security)

---

## 1. Executive Summary

The POC v2 codebase correctly implements the high-level hybrid architecture: MCP tool calls,
BAML-driven inference, PII masking, audit logging, and graceful degradation markers.

However, several precise rules specified in the framework are either missing, semantically
incorrect, or architecturally inverted. These are not presentation gaps — they affect the
mathematical correctness of the confidence score, the determinism of safety enforcement, the
completeness of the AI's output contract, and the integrity of the audit trail.

Eight closure items are needed, two of which (GAP-R1 and GAP-R2) have direct impact on
evaluation scoring in the Hybrid/MCP (35%) and Security/Audit (20%) criteria.

---

## 2. Sources Used for This Discovery

- `doc_outputs/onboarding/ai-team-onboarding.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/samples/rule-synthesis-framework.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/data/clinical-guidelines-reference.md`
- `POC/v2/backend/src/api/routes/contracts.py`
- `POC/v2/backend/src/services/safety.py`
- `POC/v2/backend/src/services/audit.py`
- `POC/v2/backend/src/mcp_server/tools/program_ruleset.py`
- `POC/v2/baml_src/clinical/recommendation_output.baml`
- `POC/v3/assets/synthesis/rulesets/sample_ruleset_tier_config.json`

---

## 3. POC Strengths — What Correctly Applies the Framework

1. **Tier rule JSON structure is framework-compliant**
   - `sample_ruleset_tier_config.json` correctly implements all four rules
     (PREMIUM_SEVERE_SINGLE, PREMIUM_MULTI_SIGNAL, ADVANCED_METABOLIC_OR_CVD, STANDARD_DEFAULT)
     in priority order with the correct `match_logic` types.
   - `admin_configurable` fields are correctly scoped.

2. **Add-on item catalog has the right count and structure**
   - 33 add-on items with gender/age constraints, trigger signals, priority defaults,
     and safety contraindication signals match the derivation ledger.

3. **PII masking architecture is correct**
   - UUID v4 token mapping, request-scoped in-memory map, rehydration post-AI.

4. **Audit hash chaining is implemented**
   - SHA-256 hash chain with append-only JSONL and dual JSON storage.

5. **Confidence score formula exists**
   - Three-component weighted formula (signal_coverage, data_completeness, rule_agreement)
     with tier thresholds (High ≥ 0.75, Medium ≥ 0.50, Low < 0.50) is present.

---

## 4. Gap Register

### GAP-R1 — Confidence Calibrator Formula Deviations

**Severity:** High
**Criterion affected:** Hybrid/MCP (35%)

Three deviations from the framework formula:

1. `rule_agreement` penalises AI deviation with `0.7` instead of the framework's `0.0`.
   This inflates confidence by up to 0.14 when the AI disagrees with the rule tier.

2. `signal_coverage` uses `signals_fired / applicable_signals` (active signals / all relevant
   signals). The framework defines it as `signals_with_data / total_expected_signals` —
   data availability, not risk density.

3. `data_completeness` uses `signals_fired / (signals_fired + missing_signals)`.
   The framework defines it as `required_fields_present / total_required_fields` —
   schema field presence, not signal count ratio.

**Fix:** `contracts.py` — correct all three sub-formula calculations.

---

### GAP-R2 — Safety Rule Validator Architecture Inverted

**Severity:** High
**Criterion affected:** Hybrid/MCP (35%), Security/Audit (20%)

Two architectural deviations from Decision 6 of the AI Team Onboarding:

1. **Demographic filtering runs PRE-AI** in `get_program_ruleset` via
   `filter_add_ons_by_demographics()`. The framework explicitly requires the AI to see the
   full unfiltered candidate list; invalid items must be removed silently POST-AI.

2. **Post-AI safety check is LLM-based** (`ValidateRecommendation` BAML critic).
   The framework specifies a deterministic rule evaluation engine — not an LLM judge —
   that silently removes items and logs conflict events to the audit log.

**Fix:** Remove pre-AI filtering from `program_ruleset.py`; implement deterministic
post-AI `SafetyRuleValidator` in `safety.py` that checks gender, age, and safety flags
against each recommended item, silently removes violations, and appends conflict events
to the audit log.

---

### GAP-R3 — BAML Output Schema Incomplete (AddOnItem + CommunicationScript)

**Severity:** High
**Criterion affected:** All four criteria (schema drives all downstream validation)

`AddOnItem` in `recommendation_output.baml` is missing four Stage 1 fields required by the
framework: `label`, `product_code`, `price_thb`, `category`. Two field names are also wrong:
`item_code` should be `item_id`; `priority_level` should be `priority`.

`CommunicationScript` has one extra field (`clinical_conclusion` — not in framework) and two
renamed fields (`recommendation_explanation` should be `recommendation_rationale`;
`add_on_highlights` should be `addon_highlights`).

Without `item_id`, validation rule V2 cannot run. Without `price_thb`, rule V10 cannot run.

**Fix:** Update `recommendation_output.baml` — rename fields, add missing fields,
remove `clinical_conclusion`, update the prompt instructions accordingly.

---

### GAP-R4 — Validation Rules V2, V7, V9, V10 Not Enforced

**Severity:** Medium
**Criterion affected:** Hybrid/MCP (35%)

The framework specifies 10 BAML validation rules (V1–V10). Rules V1, V3, V4, V5, V6 are
implicitly enforced by BAML types. The remaining four are not implemented:

| Rule | Missing Check |
|------|--------------|
| V2 | item_id in add_ons[] must exist in get_program_ruleset response |
| V7 | supporting_signals[] must reference valid signal IDs from get_clinical_signals |
| V9 | add_ons[] must not be empty when clinical triggers are present |
| V10 | price_thb on each add-on must match ruleset value or be null |

**Fix:** Add a post-BAML Python validator in `contracts.py` (or a new `validator.py`)
that checks V2, V7, V9, V10 against the MCP context. Validation failure triggers graceful
degradation.

---

### GAP-R5 — Stage 2 Completeness: `patient_high_alert` and `metadata` Fields Missing

**Severity:** Medium
**Criterion affected:** UX / XAI (20%), Security/Audit (20%)

Two Stage 2 objects are absent from `_normalize_stage2()` in `contracts.py`:

1. `patient_high_alert` with `critical_signals[]` and `missing_data_alerts[]` — required
   for the alert banner on Screen 1.

2. `metadata.template_version` (e.g., `"v1.0"`) and `metadata.latency_ms` — both required
   by the framework's audit and XAI contracts.

**Fix:** Derive `patient_high_alert` from clinical signals in `_normalize_stage2()`;
add `template_version` constant and capture `latency_ms` from the BAML call timing
in `clinical.py`.

---

### GAP-R6 — Graceful Degradation Conflates Low Confidence with AI Failure

**Severity:** Medium
**Criterion affected:** Hybrid/MCP (35%)

The framework defines graceful degradation as: triggered when the AI model is unavailable,
BAML validation fails after retry, or the Phase 2 iteration cap is hit — and it builds a
rule-only recommendation directly from `get_program_ruleset` output.

The POC triggers `recommendation_source = "RuleBased"` when `confidence_score < 0.50`.
This is a confidence gate, not an AI failure path. No actual rule-only recommendation is
ever constructed without the AI.

**Fix:** Implement a true graceful degradation catch block in `orchestrator.py` for LLM
and BAML exceptions. Build a rule-based `RecommendationOutput` from `get_program_ruleset`
tier rules and the top-priority triggered add-ons. Set `recommendation_source = "RuleBased"`
and `review_required = true`. Rename the current confidence-gate state to
`recommendation_source = "AI_LowConfidence"` to distinguish the two cases.

---

### GAP-R7 — Audit Logger Missing Dimensions

**Severity:** Medium
**Criterion affected:** Security, Privacy & Audit (20%)

The framework's 5-dimension audit log requires:

| Dimension | Required Fields |
|-----------|----------------|
| Who | user_id, user_role |
| When | ISO 8601 timestamp |
| Where | service_id, client_ip |
| What | prompt, masked_context, masked_response, model_id, latency_ms |
| Why | request_context (patient_token, action_type, request_id) |

The POC logs `patient_id` under "Who" instead of the requesting user's `user_id` and
`user_role`. The `WHERE` dimension (`service_id`, `client_ip`) is entirely absent.
`prompt`, `masked_response`, `latency_ms`, `action_type`, and `request_id` are missing
from `WHAT` and `WHY`.

**Fix:** Update `audit.py` `log_recommendation()` to accept `user_id`, `user_role`,
`client_ip`, and `request_id` from the request context; add `prompt`, `masked_response`,
and `latency_ms` to the `WHAT` payload; add `service_id` constant to `WHERE`.

---

### GAP-R8 — Signal Pool Divergence from Framework

**Severity:** Low
**Criterion affected:** Hybrid/MCP (35%)

Two signal pool deviations in `sample_ruleset_tier_config.json`:

1. **ADVANCED low-moderate pool:** Missing `fbs_upward_trend` and `diagnosis_fatty_liver`
   (both in framework §3.2). Has four undocumented additions (`family_hx_early_heart_attack`,
   `symptom_fatigue`, `history_loss_of_consciousness`, `occupational_risk_factory`) with no
   traceability to the framework derivation ledger.

2. **PREMIUM_MULTI_SIGNAL pool:** Missing `diabetes_confirmation_required` and
   `history_syncope` from the framework's moderate-severity pool.

**Fix:** Either add the undocumented signals to the framework derivation ledger with
guideline sources (preferred if clinically valid), or remove them and restore the missing
signals. Confirm with clinical team before JSON change is promoted.

---

## 5. Prioritization

**Priority 1 (Scoring-critical, fix before demo):** GAP-R1, GAP-R2, GAP-R3
**Priority 2 (Completeness, fix in parallel):** GAP-R4, GAP-R5, GAP-R6, GAP-R7
**Priority 3 (Config alignment, lower risk):** GAP-R8

---

## 6. Recommended Closure Strategy

1. Fix BAML schema first (GAP-R3) — downstream validators depend on correct field names.
2. Fix confidence calibrator (GAP-R1) — deterministic and isolated, no dependencies.
3. Restructure safety validator (GAP-R2) — requires GAP-R3 to be done first
   (item_id must exist before removal checks make sense).
4. Add validation rules V2/V7/V9/V10 (GAP-R4) — requires GAP-R3.
5. Complete Stage 2 fields (GAP-R5) — isolated, parallel with GAP-R4.
6. Implement true graceful degradation (GAP-R6) — isolated.
7. Expand audit dimensions (GAP-R7) — isolated, can be done any time.
8. Align signal pools with clinical team (GAP-R8) — lowest risk, schedule last.
