# GAP-R7 — Audit Logger 5-Dimension Expansion

**Title:** Audit log captures patient identity instead of requesting user; missing dimensions
**Status:** Not started

---

## Objective

Expand `AuditLogger.log_recommendation()` to capture all 5 framework dimensions with the
correct fields, including the requesting user's identity and the full request context.

## Scope

- Add to WHO: `user_id`, `user_role` (from auth context, not patient record)
- Add WHERE dimension: `service_id` (constant), `client_ip` (from FastAPI request)
- Add to WHAT: `prompt`, `masked_response`, `latency_ms`
- Add to WHY: `action_type`, `request_id`
- Thread auth-context fields from FastAPI route through orchestrator to audit logger

## Primary Files

- `POC/v2/backend/src/services/audit.py`
- `POC/v2/backend/src/services/orchestrator.py`
- `POC/v2/backend/src/api/routes/contracts.py`

## Checkpoint Files

- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## Framework Reference

`doc_outputs/onboarding/ai-team-onboarding.md` Component 9 (Audit Logger), §9.3 PDPA
