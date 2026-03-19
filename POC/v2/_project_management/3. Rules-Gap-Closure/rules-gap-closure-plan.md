# Rules Gap-Closure Plan — Framework Compliance

**Date:** 2026-03-19
**Input discovery:** `rules-gap-discovery.md`
**Goal:** Bring POC v2 into full compliance with the Rule Synthesis Framework and AI Team
Onboarding contracts, covering confidence calibration, safety validation architecture,
BAML output schema, output validation rules, Stage 2 completeness, graceful degradation,
audit logging, and signal pool traceability.

---

## 1. Planning Principles

1. **Framework-first correctness**
   - Every change is traceable to a specific clause in `rule-synthesis-framework.md`
     or `ai-team-onboarding.md`. No speculative improvements.

2. **Schema before behaviour**
   - Fix BAML output schema (GAP-R3) before implementing validation rules that
     depend on it (GAP-R4) or safety removal that checks field values (GAP-R2).

3. **Determinism over LLM judgement for safety and validation**
   - Safety enforcement and output validation use rule engines, not LLM critics.
     The BAML critic remains available as an advisory layer only.

4. **Evidence-driven completion**
   - Every closed gap must produce passing test output captured in
     `_lastest_test_results.md`.

5. **Clinical team sign-off for signal pool changes**
   - GAP-R8 requires clinical team confirmation before the JSON is changed.
     Do not unilaterally resolve signal pool membership.

---

## 2. Target End State

At completion, the POC must demonstrate:

- Confidence score computed with the exact formula in `ai-team-onboarding.md` §8.
- Safety Rule Validator running deterministically post-AI, with pre-AI filtering removed.
- Stage 1 BAML schema producing all required `AddOnItem` and `CommunicationScript` fields.
- Validation rules V2, V7, V9, V10 enforced post-BAML with graceful degradation on failure.
- Stage 2 output including `patient_high_alert`, `metadata.template_version`, and
  `metadata.latency_ms`.
- Graceful degradation triggered on AI failure (not on low confidence) producing a
  rule-only recommendation from `get_program_ruleset`.
- Audit log entries capturing all 5 framework dimensions including requesting user identity,
  client_ip, prompt, masked_response, and latency_ms.
- Signal pool JSON aligned with derivation ledger (pending clinical review for GAP-R8).

---

## 3. Workstream Overview

### WS-A — Core Inference Correctness

**Covers:** GAP-R1, GAP-R2, GAP-R3
**Priority:** P0

Deliverables:
- Corrected confidence calibrator formula in `contracts.py`.
- Deterministic post-AI `SafetyRuleValidator` in `safety.py` with silent item removal and
  audit conflict events.
- Pre-AI demographic filtering removed from `program_ruleset.py`.
- Updated BAML `AddOnItem` and `CommunicationScript` schemas in `recommendation_output.baml`.

Acceptance checks:
- Unit test: AI tier deviation produces `confidence_score` ≤ 0.60 (rule_agreement = 0.0).
- Unit test: Female-only add-on recommended for male patient is silently removed post-AI;
  conflict event appears in audit log.
- BAML test: `AddOnItem` output contains `item_id`, `label`, `product_code`, `price_thb`,
  `category`.

### WS-B — Output Validation and Stage 2 Completeness

**Covers:** GAP-R4, GAP-R5
**Priority:** P1 (after WS-A schema fixes)

Deliverables:
- Post-BAML Python validator enforcing V2, V7, V9, V10.
- `patient_high_alert` object in Stage 2 output.
- `metadata.template_version` and `metadata.latency_ms` in Stage 2 output.

Acceptance checks:
- Validator test: AI output with unknown item_id triggers graceful degradation.
- Validator test: AI output with invented price_thb triggers graceful degradation.
- Response test: `/api/recommend` includes `patient_high_alert.critical_signals[]` for
  Somchai W. (multiple High signals).
- Response test: `metadata.template_version` and `metadata.latency_ms` are non-null.

### WS-C — Resilience and Observability

**Covers:** GAP-R6, GAP-R7
**Priority:** P1 (parallel with WS-B)

Deliverables:
- True graceful degradation path in `orchestrator.py` for LLM/BAML exceptions.
- Rule-only `RecommendationOutput` built from `get_program_ruleset` without AI.
- Expanded audit log record with all 5 framework dimensions.

Acceptance checks:
- Failure simulation test: bad LLM API key produces `recommendation_source = "RuleBased"`
  with a valid rule-tier recommendation structure.
- Audit test: log entry includes `user_id`, `user_role`, `client_ip`, `prompt`,
  `masked_response`, `action_type`, `request_id`, `latency_ms`.

### WS-D — Signal Pool Alignment

**Covers:** GAP-R8
**Priority:** P2 (requires clinical team input)

Deliverables:
- Updated `sample_ruleset_tier_config.json` with corrected signal pools (or updated
  derivation ledger if undocumented signals are clinically valid).

Acceptance checks:
- Pre-production gate checklist §9 of `rule-synthesis-framework.md` passes.
- All signal IDs in both pools exist verbatim in `signal-store-contract.md` Field Dictionary.

---

## 4. Execution Sequence

### Step 1 — BAML Schema Fix (WS-A entry point)

- Update `AddOnItem` in `recommendation_output.baml`: rename fields, add missing fields.
- Update `CommunicationScript`: remove extra field, rename two fields.
- Update BAML prompt instructions to match new field names.
- Run BAML generation; verify compile success.

Gate: BAML client regenerates without errors.

### Step 2 — Confidence Calibrator Correction (WS-A, parallel)

- In `contracts.py` `_normalize_stage2()`:
  - Set `rule_agreement = 0.0` on tier disagreement.
  - Recompute `signal_coverage` from biomarker data availability.
  - Recompute `data_completeness` from required schema field presence.

Gate: Unit tests verify formula produces expected scores for known inputs.

### Step 3 — Safety Validator Restructure (WS-A, after Step 1)

- Remove `filter_add_ons_by_demographics()` call from `program_ruleset.py` tool response.
- Implement `SafetyRuleValidator.validate_and_filter()` in `safety.py`:
  - Input: AI `add_ons[]` + `get_hard_constraints` response.
  - For each add-on: check gender_constraint, age_min/max, safety_contraindication_signals.
  - On violation: remove item, append conflict event to audit log.
  - Output: filtered `add_ons[]` + conflict_events[].
- Wire into `orchestrator.py` post-BAML, pre-rehydration.
- Retain BAML safety critic as optional advisory (non-blocking).

Gate: Post-AI removal test passes; male patient does not receive mammogram in final output.

### Step 4 — Validation Rules V2/V7/V9/V10 (WS-B, after Step 1)

- Implement `OutputValidator.validate()` in a new `validator.py` or within `contracts.py`.
- Check V2: each item_id exists in ruleset add-on library.
- Check V7: each supporting_signal_id exists in applicable_signals from clinical signals.
- Check V9: add_ons not empty when signals_fired is non-empty.
- Check V10: each price_thb matches ruleset or is null.
- On failure: trigger graceful degradation.

Gate: Validator unit tests for each rule pass with deliberate invalid AI output.

### Step 5 — Stage 2 Completeness (WS-B, parallel with Step 4)

- In `contracts.py` `_normalize_stage2()`:
  - Derive `patient_high_alert.critical_signals[]` from risk_flags where severity = "high".
  - Derive `patient_high_alert.missing_data_alerts[]` from AI `missing_signals[]`.
  - Add `metadata.template_version = "v1.0"`.
  - Thread `latency_ms` from Phase 4 timing in `clinical.py` workflow context.

Gate: `/api/recommend` response includes `patient_high_alert` and full metadata for
Somchai W. reference patient.

### Step 6 — True Graceful Degradation (WS-C)

- In `orchestrator.py`, wrap BAML call in try/except for `InfrastructureError`,
  `ClinicalProcessError`, and BAML validation failures.
- On exception: call `get_program_ruleset` directly; apply tier rules to fired signals;
  select top-priority triggered add-ons from the library; build a valid
  `RecommendationOutput` struct; set `recommendation_source = "RuleBased"`,
  `review_required = true`.
- Rename existing confidence-gate state: `recommendation_source = "AI_LowConfidence"`.

Gate: Failure simulation test produces a structurally valid rule-only recommendation.

### Step 7 — Audit Logger Expansion (WS-C, parallel)

- Add `user_id`, `user_role`, `client_ip`, `request_id` parameters to
  `AuditLogger.log_recommendation()`.
- Add `prompt`, `masked_response` to the `WHAT` payload.
- Add `service_id`, `client_ip` to a `WHERE` sub-object.
- Add `action_type` and `request_id` to the `WHY` sub-object.
- Thread `latency_ms` from workflow context into `WHAT`.
- Thread auth-context fields from the FastAPI request into the orchestrator call chain.

Gate: Audit log entry test verifies all 5 dimensions with required fields.

### Step 8 — Signal Pool Alignment (WS-D, pending clinical input)

- Verify `sample_ruleset_tier_config.json` signal pools against signal-store-contract.md
  Field Dictionary.
- For 4 undocumented signals in ADVANCED pool: escalate to clinical team for guideline
  source confirmation or removal decision.
- For 2 missing signals in PREMIUM_MULTI_SIGNAL pool (`diabetes_confirmation_required`,
  `history_syncope`): add if clinical team confirms.
- Run pre-production gate checklist §9 of `rule-synthesis-framework.md`.

Gate: All signal IDs in both pools exist verbatim in the Field Dictionary.

---

## 5. Gap-to-Task Mapping

| Gap | Closure Task | Depends On | Exit Evidence |
|-----|-------------|------------|---------------|
| GAP-R1 | Fix confidence formula (3 sub-items) | None | Unit test: correct scores for known inputs |
| GAP-R2 | Deterministic post-AI safety validator | GAP-R3 | Male patient does not receive female-only items |
| GAP-R3 | BAML AddOnItem + CommunicationScript fix | None | BAML compile + field presence test |
| GAP-R4 | Implement V2/V7/V9/V10 validators | GAP-R3 | Validator unit tests for each rule |
| GAP-R5 | Stage 2 patient_high_alert + metadata | None | Response field presence test for Somchai W. |
| GAP-R6 | True graceful degradation path | None | Failure simulation test |
| GAP-R7 | Audit logger 5-dimension expansion | None | Audit log dimension test |
| GAP-R8 | Signal pool JSON alignment | Clinical team | Pre-production gate checklist pass |

---

## 6. Risks and Mitigations

1. **BAML field rename breaks existing integration tests**
   - Mitigation: Run full regression after Step 1 before proceeding; update any
     test fixtures that reference old field names.

2. **Pre-AI filter removal causes AI hallucination of ineligible items**
   - Mitigation: This is the intended architectural trade-off per Decision 6.
     The post-AI SafetyRuleValidator is the correctness gate.
     Monitor removal conflict event rate in audit log during testing.

3. **Graceful degradation rule-only output may have lower clinical quality**
   - Mitigation: This is expected and by design — `review_required = true` flags it
     for physician review. The rule-only path is a safety net, not a peer of the AI path.

4. **Signal pool changes require clinical review before production**
   - Mitigation: GAP-R8 is P2 and gated on clinical team input. Do not unilaterally
     add or remove signals. Use placeholder pending status until confirmed.

5. **Audit logger expansion requires auth-context threading throughout call chain**
   - Mitigation: Audit the full call chain from FastAPI route → orchestrator → audit logger
     before implementation. Add `user_id`, `user_role`, `client_ip` to the workflow context
     object rather than individual function signatures.

---

## 7. Definition of Done

The rules gap-closure effort is complete when:

- All P0 gaps (GAP-R1, GAP-R2, GAP-R3) are closed with test evidence.
- All P1 gaps (GAP-R4, GAP-R5, GAP-R6, GAP-R7) are closed with test evidence.
- GAP-R8 is either closed or explicitly pending clinical team input with documented status.
- End-to-end recommendation flow for Somchai W. produces output that satisfies the
  pre-production validation checklist in `rule-synthesis-framework.md` §9.

---

## 8. Closure Status (as of 2026-03-19)

| Gap | Status | Test Evidence |
|-----|--------|---------------|
| GAP-R1 | Not started | — |
| GAP-R2 | Not started | — |
| GAP-R3 | Not started | — |
| GAP-R4 | Not started | — |
| GAP-R5 | Not started | — |
| GAP-R6 | Not started | — |
| GAP-R7 | Not started | — |
| GAP-R8 | Not started — pending clinical team input | — |
