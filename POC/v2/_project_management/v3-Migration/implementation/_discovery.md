# Discovery — v3 Migration

_Findings and architecture decisions made during implementation. Updated as work progresses._

---

## Pre-Migration Discovery (2026-03-19)

### v3 vs v2 Feature Comparison

Conducted full inspection of both `POC/v3` and `POC/v2` codebases. Key findings:

**v3 new features not present in improved v2:**

| Area | v3 Addition | Notes |
|---|---|---|
| BAML | 3-agent pipeline (`AnalyzeClinicalRisks`, `MatchProgramRules`, `ComposeRecommendation`) | Replaces single `GenerateRecommendation()` |
| BAML | `synthesis/enrichment.baml` with `EnrichHealthyPatientRecord()` | Not present in v2 |
| Workflow | `force_rule_based` parameter | v2 has no bypass path |
| Workflow | RuleEvaluator integration (always runs first) | v2 calls AI directly without deterministic baseline |
| Workflow | Graceful fallback to rule-based on AI failure | v2 has no structured fallback |
| Orchestrator | `security_metadata` in response (rehydration_map + masked_ai_output) | v2 only returns rehydrated output |
| Frontend | Hybrid AI/Rules mode toggle button | v2 has no mode toggle |
| Frontend | PII Privacy Mode toggle (masked vs physician view) | v2 always shows rehydrated data |
| Frontend | `getDisplayValue()` helper using rehydration_map | v2 has no such helper |
| Scripts | 4 enrichment scripts (`enrich_*.py`) | v2 has only `sync_registry.py` |

**v2 features NOT present in v3 (must preserve):**

| Area | v2 Feature |
|---|---|
| API | Full contracts router (`/api/recommend`, `/api/timeline`, `/api/monitoring-snapshot`, `/api/audit-logs`, etc.) |
| Frontend | Screen 2 — Trend & Timeline |
| Frontend | Screen 3 — Access Monitoring |
| Backend | Cache service (TTL recommendation cache) |
| Backend | Security/RBAC auth middleware |
| Tests | 40-test regression suite |

### Critical Mapping Concern

`_normalize_stage2()` in `contracts.py` expects these keys from the AI output dict. The new `_map_final_to_ai_output()` function (MIG-2) must produce all of them:

- `ai_recommended_tier`
- `tier_deviation_justification`
- `add_ons[]` (with `item_id`, `label`, `rationale`, `priority`, `product_code`, `price_thb`, `category`)
- `reasoning_trace`
- `supporting_signals[]`
- `missing_signals[]`
- `communication_script` (with `health_summary`, `recommendation_rationale`, `addon_highlights`, `next_steps`)
- `rule_preliminary_tier`

### RuleEvaluator Status

Needs verification during MIG-2: does `backend/src/services/rules.py` exist in v2? Explorer confirmed it exists in v3. If absent from v2, copy verbatim.
