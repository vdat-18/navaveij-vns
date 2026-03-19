# MIG-5 — Frontend: Hybrid AI/Rules Toggle

**Status:** Implemented (runtime verification partially blocked by local Node/npm availability)
**Priority:** P2
**POC Scoring Impact:** XAI 20%
**Depends on:** MIG-4

## Objective

Add a "Mode: Hybrid AI / Fallback: Rules" toggle button in the Screen 1 dashboard header that sends `force_rule_based` to `/api/recommend` and re-fetches the recommendation on toggle.

## Files Changed

- `POC/v2/frontend/src/app/page.tsx`
- `POC/v2/frontend/src/services/api.ts`
- `POC/v2/frontend/src/components/dashboard/RecommendationPanel.tsx`
- `POC/v2/scripts/tests/test_frontend_reliability_contract.py`

## Acceptance Gate

- Toggle button visible in header utility bar
- Toggling button triggers a new recommendation fetch
- When ON (amber, "Fallback: Rules"): response `recommendation_source` is "RuleBased"
- When OFF (white, "Mode: Hybrid AI"): response `recommendation_source` is "AI"
- All three existing screens remain navigable

## v3 Reference

- `POC/v3/frontend/src/app/page.tsx` — lines 28-31 (state), 88-101 (button)

## Implementation Notes

1. Added header utility toggle pill in Screen 1:
   - OFF: `Mode: Hybrid AI`
   - ON: `Fallback: Rules`
2. Added `isRuleBasedForced` state in dashboard page and passed it to `RecommendationPanel`.
3. Updated `clinicalService.getRecommendation(patientToken, forceRuleBased = false)` to include `force_rule_based` in request payload.
4. Updated `RecommendationPanel` to:
   - accept `isRuleBasedForced` prop,
   - pass it to `getRecommendation(...)`,
   - include it in `useEffect` dependencies for re-fetch.
5. Preserved remount behavior by keeping `key={patientToken}` unchanged (patient change remount only).
6. Added frontend reliability contract checks for MIG-5 wiring:
   - page-level toggle state/prop pass-through,
   - panel re-fetch dependency and stable key behavior,
   - API payload includes `force_rule_based`.
