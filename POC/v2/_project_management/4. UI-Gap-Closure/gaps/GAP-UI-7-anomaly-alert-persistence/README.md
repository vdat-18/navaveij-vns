# GAP-UI-7 — Anomaly Alert Persistence

**Title:** Make Acknowledge/Resolve buttons durable or explicitly mark them as non-persistent
**Status:** Not started
**Wave:** 1

---

## Objective
Fix the silent no-op behaviour of anomaly alert status buttons: either persist changes via API call, or explicitly surface to the user that persistence is not yet supported.

## Scope
1. Check if a backend endpoint exists for alert status updates (e.g., `PATCH /api/anomaly-alerts/{alert_id}`)
2. If endpoint exists: add API call in `AnomalyAlertsPanel.tsx`; update local state only on successful API response
3. If endpoint does not exist: disable Acknowledge/Resolve buttons with a tooltip "Persistence not yet supported in this POC version"

## Primary Files
- `src/components/access-monitoring/AnomalyAlertsPanel.tsx`
- `src/services/api.ts`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%
