# Gap Discovery Report — POC vs. v3 Architecture Specs

**Date:** 2026-03-16
**Review method:** Line-by-line comparison of `POC/src/` against `doc_outputs/architecture/AI/Recommendation Engine/v3/` spec documents
**Reviewer:** Architecture Review

---

## Summary Table

| ID | Severity | Category | Title | Spec Reference | POC File(s) |
|---|---|---|---|---|---|
| GAP-1 | 🔴 Critical (Security) | Security | Hardcoded API key in source + hardcoded secret salt | TOR §5.2 | `POC/scripts/test_api.py:5`, `POC/src/shared/settings.py:51` |
| GAP-2 | 🔴 High | Architecture | ConfidenceCalibrator + OutputEnricher + PIIRehydrator not wired to API path | component-inventory §8,12 / recommendation-output-schema.md Stage 2 | `POC/src/orchestrator/core/manager.py`, `POC/src/orchestrator/workflows/clinical.py` |
| GAP-3 | 🔴 High | Safety | Safety validator is LLM-only — cannot deterministically enforce hard constraints | component-inventory §10 | `POC/src/orchestrator/safety/validator.py` |
| GAP-4 | 🟠 Medium | Audit / PDPA | Audit log has 4 non-standard dimensions instead of required 5 | component-inventory §9 / TOR §5.3 | `POC/src/orchestrator/logger/audit.py` |
| GAP-5 | 🟠 Medium | MCP | 5th MCP tool `get_patient_event_timeline` missing | event-timeline-contract.md | `POC/src/mcp_server/server.py` |
| GAP-6 | 🟠 Medium | API | 3 of 4 required demo API endpoints missing; no CORS | plan.md Phase 1 | `POC/src/api/main.py` |
| GAP-7 | 🟠 Medium | Data | Monitoring fixture data missing (blocks Screen 3) | access-monitoring-contract.md | `assets/synthesis/` (missing) |
| GAP-8 | 🟠 Medium | Data | Canonical demo patient (Somchai W.) Signal Store record missing | signal-store-contract.md | `assets/synthesis/` (missing) |
| GAP-9 | 🟡 Low | AI Config | BAML client only supports Google AI; pluggable model switch not operational | TOR §4.3 / component-inventory §4 | `baml_src/clients.baml` |
| GAP-10 | 🟡 Low | Code Quality | Dual orchestrator — `ClinicalOrchestrator` is dead code not used by API | — | `POC/src/orchestrator/agents/orchestrator.py` |

---

## GAP-1 — Hardcoded API Key & Secret Salt

### Evidence

**`POC/scripts/test_api.py` (line 4–5):**
```python
# api_key="AIzaSyBWKGlVTGseZFyfgzjeuo4-Lra_sYJhrnA",
api_key="AIzaSyAcgGGUvybk7xww0Yuk1uoiiKcU0MfQwW0",
```
A live Google AI Studio API key is hardcoded. The previous key is commented out, suggesting a key rotation already occurred with the old key left in history.

**`POC/src/shared/settings.py` (line 51):**
```python
patient_token_secret_salt: str = "navavej-clinical-recommendation-engine-secret-salt-2026"
```
The HMAC secret used to generate patient tokens is hardcoded as a class default. Anyone who reads the source code knows the salt, and can reverse patient tokens to correlate records.

### Spec requirement
Component-inventory §2.7: "API keys referenced via secret manager (e.g. HashiCorp Vault / AWS Secrets Manager); no hardcoded keys." TOR §5.2: "PII Masking — map never persisted or logged." The salt is functionally a PII protection key.

### Impact
If either key is committed to version control (which `test_api.py` currently is), it is exposed in git history permanently. The salt exposure partially undermines the patient token de-identification scheme.

---

## GAP-2 — ConfidenceCalibrator + OutputEnricher + PIIRehydrator Not Wired

### Root cause: Two orchestrator implementations

There are **two complete orchestration paths** in the POC:

| Path | Entry Point | Calls | Used by API? |
|---|---|---|---|
| **Canonical (API path)** | `OrchestrationManager.generate_recommendation()` | `ClinicalReasoningWorkflow` → 4 MCP tools → BAML | ✅ Yes (`POST /recommend`) |
| **Rich path (dead code)** | `ClinicalOrchestrator.generate_recommendation()` | 5 MCP tools → BAML → `ConfidenceCalibrator` → `OutputEnricher` → `PIIRehydrator` | ❌ No |

### What the canonical API path returns today

**`POC/src/orchestrator/core/manager.py` (lines 43–60):**
```python
context = await workflow.execute(patient_id)
safety_result = await self.safety_guard.validate(context.ai_output, context.raw_context)
context.ai_output["safety_check"] = safety_result
self.audit_logger.log_recommendation(...)
return context.ai_output
```

The manager calls `workflow.execute()` then immediately returns `context.ai_output` — the raw BAML output. It never calls `ConfidenceCalibrator`, `OutputEnricher`, or `PIIRehydrator`.

### What is missing from the output

| Field | Source | Status |
|---|---|---|
| `confidence_score` | `ConfidenceCalibrator.compute_confidence_score()` | ❌ Missing |
| `confidence_tier` | `ConfidenceCalibrator.compute_confidence_tier()` | ❌ Missing |
| `rule_preliminary_tier` | `OutputEnricher.enrich_output()` → `clinical_signals.rule_preliminary_tier` | ❌ Missing |
| `resolved_package` | `OutputEnricher.enrich_output()` → `ruleset_response.resolved_package` | ❌ Missing |
| `recommendation_source` | `OutputEnricher.enrich_output()` | ❌ Missing |
| `patient_high_alert` | `OutputEnricher.enrich_output()` | ❌ Wrong type (bool instead of structured object) |
| `add_ons[].label` | `OutputEnricher.enrich_add_ons()` | ❌ Missing |
| `add_ons[].category` | `OutputEnricher.enrich_add_ons()` | ❌ Missing |
| `add_ons[].navavej_product` | `OutputEnricher.enrich_add_ons()` (price in ฿) | ❌ Missing |
| PII rehydration | `PIIRehydrator.rehydrate()` | ❌ Missing — response still has UUID tokens |

### OutputEnricher bug (independent of wiring)

**`POC/src/orchestrator/enrichment/output_enricher.py` (line 93):**
```python
"patient_high_alert": len(clinical_signals.get("missing_signals", [])) > 5,
```
`patient_high_alert` is emitted as a `bool`. The spec (`recommendation-output-schema.md`) defines it as a structured `PatientHighAlert` object with `critical_signals: string[]` and `missing_data_alerts: MissingDataAlert[]`. Screen 1 Panel C renders individual badges from these arrays — a boolean cannot drive that UI.

### Spec requirement
`recommendation-output-schema.md` Stage 2 fields table; component-inventory §8 (Confidence Calibrator), §12 (PII Rehydration).

---

## GAP-3 — Safety Validator Is LLM-Only (Non-Deterministic)

### Evidence

**`POC/src/orchestrator/safety/validator.py` (entire file, 37 lines):**
```python
class ClinicalSafetyGuard:
    async def validate(self, ai_output: dict, raw_context: dict) -> dict:
        result = await b.ValidateRecommendation(context=context_str, recommendation=recommendation_str)
        output = {
            "is_safe": result.is_safe,
            "critic_score": result.critic_score,
            "findings": result.findings,
            ...
        }
        if not output["is_safe"]:
            logger.warning("Clinical safety validation failed via BAML Critic.")
        return output
```

The validator calls the LLM critic and returns a report — but **does not modify `ai_output`**. Even if `is_safe = False`, the violating add-ons remain in the output.

**`POC/src/orchestrator/safety/rules.py`:**
```python
GENDER_EXCLUSIONS = {
    "male": ["mammogram", "pap smear", "cervical", "ovarian", "pregnancy test"],
    "female": ["prostate", "testicular"],
}
```
The gender exclusion rules are defined but **never imported by `validator.py`**.

**`POC/src/mcp_server/utils.py`:** `filter_add_ons_by_demographics()` correctly filters the add-on *library* before passing it to the AI. However, the AI can still output an item that was in the original library but excluded by hard constraints (e.g., a borderline case where the AI hallucinates an item code). The Safety Rule Validator must catch this post-inference.

### What the spec requires

`component-inventory-solution-approach.md §2.6`:
> "The violating item is **silently removed** from `add_ons[]` or the `ai_recommended_tier` is reverted to the constrained tier. A **conflict event is written synchronously** to the Audit Logger."
> "**On violation: The violating item is silently removed** — violations are not surfaced in any UI view."

The current implementation does not remove any items. The LLM critic may or may not flag the violation, and even if it does, nothing is revoked.

### Demo impact
The evaluation committee will test the Mammogram/male scenario specifically (it's the canonical hard-constraint demo case). If the validator doesn't revoke it deterministically, the 20% security criterion is at risk.

---

## GAP-4 — Audit Log Missing `where` Dimension

### Evidence

**`POC/src/orchestrator/logger/audit.py` (lines 65–76) — current payload structure:**
```python
payload = {
    "timestamp": timestamp,
    "who": {"patient_id": patient_id},
    "what": {"input_context_snapshot": masked_context},
    "why": {"reasoning_trace": ..., "decision": ...},
    "how": {"model_provider": ..., "model_id": model_id},   # ← non-spec dimension
    "confidence": ai_output.get("confidence_score"),         # ← top-level, not in spec
    "metadata": {"environment": ...},                        # ← non-spec
    "previous_hash": self.last_hash,
}
```

### What the spec requires

`component-inventory-solution-approach.md §2.7`:

| Dimension | Required Content |
|---|---|
| **Who** | User ID + role + SMART on FHIR session token |
| **When** | ISO 8601 timestamp (UTC) |
| **Where** | Service ID + source IP + request ID |
| **What** | Post-masking prompt · context · AI response · model ID · template version · MCP tool-call trace · latency · Safety Validator result · confidence_score |
| **Why** | Patient session token (masked) + indication/reason code |

### Deviations found

1. **`where` dimension is entirely absent** — no service ID, no source IP, no request ID
2. **`how` is used instead of `where`** — it carries model info (which belongs in `what`)
3. **`when` is not a top-level key** — `timestamp` is used instead
4. **`who` contains `patient_id`** — should contain `user_id` + `role` (the requesting clinician, not the patient)
5. **`confidence` is a top-level orphan** — should be nested inside `what`

### Demo impact
Screen 3 (Access Monitoring, 20% criterion) renders the 5-dimension drilldown view. The SHA-256 hash-chain verify button re-hashes entry fields and compares against `entry_hash`. If the field names don't match the spec, Screen 3 Panel C cannot be built to spec.

---

## GAP-5 — 5th MCP Tool Missing: `get_patient_event_timeline`

### Evidence

**`POC/src/mcp_server/server.py` (entire file):**
```python
mcp.tool()(get_hard_constraints)
mcp.tool()(get_clinical_signals)
mcp.tool()(get_biomarker_trends)
mcp.tool()(get_program_ruleset)
```
Four tools registered. No `get_patient_event_timeline`.

**`POC/src/mcp_server/tools/` directory:** Contains `hard_constraints.py`, `clinical_signals.py`, `biomarker_trends.py`, `program_ruleset.py`. No `event_timeline.py`.

### What the spec requires

`event-timeline-contract.md` defines a 5th MCP tool:
```
get_patient_event_timeline(patient_token: str) -> EventTimelineResponse
```
Returns: `diagnoses[]`, `hospitalizations[]`, `significant_lab_events[]`, `screening_procedure_history[]`, `medication_changes[]`, `timeline_span`

This tool is specifically called by the Phase 1 `GET /api/timeline/{patient_token}` endpoint and is the sole data source for Screen 2 (Trend & Timeline) Panel D (Clinical Event Timeline).

### Demo impact
Screen 2 (Trend & Timeline) Panel D cannot be built. `GET /api/timeline/{patient_token}` has no backend implementation.

---

## GAP-6 — Three Demo API Endpoints Missing; No CORS

### Evidence

**`POC/src/api/main.py` — complete route list:**
```python
@app.get("/")           # health check
@app.post("/recommend") # the only data endpoint
```

### What the spec requires (plan.md Phase 1)

| Endpoint | Purpose | Screen |
|---|---|---|
| `POST /api/recommend` | Full recommendation | Screen 1 |
| `GET /api/timeline/{patient_token}` | Event timeline | Screen 2 |
| `GET /api/monitoring-snapshot` | Live KPI metrics | Screen 3 |
| `GET /api/audit-logs` | Filtered audit log search | Screen 3 |

Three of four endpoints are missing. The existing `/recommend` is also at the wrong path (`/recommend`, not `/api/recommend`) and accepts `patient_id` instead of `patient_token`.

**No CORS middleware** — `fastapi.middleware.cors.CORSMiddleware` is not configured. The Vite frontend at `http://localhost:5173` will be blocked by the browser on every API call.

### Demo impact
Screens 2 and 3 have no API to call. Screen 1 will fail CORS immediately when the frontend is started.

---

## GAP-7 — Monitoring Fixture Data File Missing

### Evidence

```
assets/synthesis/
├── HealthyRoutineCheckup/
│   └── record_000.json
├── Test/
│   └── record_test.json
└── seeds/
    └── (seed files)
```

No `monitoring.json` exists anywhere.

### What the spec requires

`access-monitoring-contract.md` defines the `MonitoringSnapshot` object (7 KPIs), `AnomalyAlert` records, RBAC role records, and mapping table entries. These are needed for:
- `GET /api/monitoring-snapshot` — Panel A live metrics
- Screen 3 Panel B — anomaly alert table
- Screen 3 Role Management tab — permission matrix
- Screen 3 Mapping Tool tab — LOINC/ICD-10 mappings

---

## GAP-8 — Canonical Demo Patient (Somchai W.) Signal Store Record Missing

### Evidence

The demo patient specified throughout all v3 specs is:
- **Name:** Somchai W. (PII-masked display)
- **Age:** 54, Male
- **Patient token:** `tok_hmac_56291047`
- **Expected tier:** Advanced → `Platinum — Men` (฿8,700)
- **Expected confidence:** 0.823 (High)

**`POST /recommend {"patient_token": "tok_hmac_56291047"}`** currently returns a "Record not found" warning from `load_signal_store_record()` in `utils.py`, because no `assets/synthesis/**/record_*.json` file has `"patient_token": "tok_hmac_56291047"`.

The existing synthesized records (`record_000.json`, `record_test.json`) have different patient tokens and different clinical profiles. They cannot be used as the demo patient.

### What is needed

A file `assets/synthesis/canonical/record_somchai.json` containing the complete Somchai W. Signal Store record as documented in `signal-store-contract.md` sections:
- `hard_constraints` — with `eligibility_exclusions: ["mammogram", "pap_smear_hpv", ...]`
- `clinical_signals` — 22 signals_fired / 33 applicable, `rule_preliminary_tier: "Advanced"`
- `biomarker_trends` — FBS 108, HbA1c 6.1%, LDL 148, eGFR 82, BMI 26.7, BP 138/88
- `_meta` — `data_completeness_ratio: 0.889`, `signal_coverage: 0.667`

The existing `load_signal_store_record()` globs `**/record_*.json` recursively, so no code change is needed — only the data file.

---

## GAP-9 — BAML Client Only Supports Google AI

### Evidence

**`baml_src/clients.baml` (entire file):**
```
client<llm> NavaveijClient {
  provider google-ai
  options {
    api_key env.GOOGLE_API_KEY
    model env.LLM_MODEL
  }
}
```
One client, Google AI only. Reads `GOOGLE_API_KEY` — but `.env.example` sets `LLM_API_KEY` (OpenAI-compatible), not `GOOGLE_API_KEY`.

**`POC/.env.example`:**
```
LLM_API_KEY=          # Can be empty for local
LLM_BASE_URL=http://127.0.0.1:1234/v1/
LLM_MODEL=meta-llama-3.1-8b-instruct
LLM_PROVIDER=local
```
The `.env.example` is set up for OpenAI-compatible local LLM — but the BAML client expects `GOOGLE_API_KEY`. The POC apparently works because `.env` (not checked in) has the correct Google key set directly.

### What the spec requires

`component-inventory-solution-approach.md §2.4`:
> "Swapping models requires only an admin panel update — no code change, no redeployment."

The Phase 6 "model switcher" demo requires switching between Claude and GPT-4o via a dropdown in the header. Currently, switching providers requires editing `clients.baml` and re-running `baml-cli generate`.

---

## GAP-10 — Dual Orchestrator: `ClinicalOrchestrator` Is Dead Code

### Evidence

`POC/src/orchestrator/agents/orchestrator.py` defines `ClinicalOrchestrator` (214 lines). It is the *correct* implementation: it calls 4 MCP tools, runs BAML, calls `ConfidenceCalibrator`, calls `OutputEnricher`, calls `PIIRehydrator`, calls `AuditLogger`. It is more complete than the canonical path.

**It is never called by any production code.** The only caller is `test_orchestrator.py` (a root-level integration test script), which is also not part of the test suite.

The `ClinicalOrchestrator` also calls `get_patient_context` (line 58), a deprecated MCP tool that no longer exists in `server.py`, meaning it would crash on that line if called.

### Impact
Developer confusion: engineers reading the code cannot determine which orchestrator is authoritative. The richer logic in `ClinicalOrchestrator` gives a false impression that the API produces enriched output.

---

## Non-Gaps (Things That Are Correct)

The following areas were reviewed and found **spec-compliant**:

| Area | Finding |
|---|---|
| BAML `GenerateRecommendation` prompt | Fully spec-compliant; instructs AI on all 5 steps; references `rule_preliminary_tier` from ruleset |
| BAML `RecommendationOutput` schema | Matches Stage 1 fields in `recommendation-output-schema.md`; includes `Orange` priority level |
| `ConfidenceCalibrator` formula | Exactly `0.4×signal_coverage + 0.4×data_completeness + 0.2×rule_agreement`; tier thresholds correct |
| `PIIMasker` + `PIIRehydrator` | UUID-token mapping; map never persisted; correct field list |
| SHA-256 hash chain in `AuditLogger` | Correct: `payload_str = json.dumps(payload, sort_keys=True)` → `sha256` → stored as `current_hash` and read as `previous_hash` for next entry |
| Signal Store loading (`utils.py`) | `load_signal_store_record()` correctly globs `**/record_*.json` |
| Demographic filtering (`utils.py`) | `filter_add_ons_by_demographics()` correctly enforces `gender_constraint`, `age_min`, `age_max` |
| 4 MCP tools | All 4 tools correctly read from Signal Store and Ruleset Store JSON files |
| `OutputEnricher.enrich_add_ons()` | Correctly enriches with `label`, `category`, `navavej_product`, `trigger_signals_matched` |
| `ClinicalReasoningWorkflow` 5 phases | Correct phase structure; correctly calls all 4 MCP tools; assembles context for BAML |
| `pyproject.toml` / dependencies | All required packages present |
