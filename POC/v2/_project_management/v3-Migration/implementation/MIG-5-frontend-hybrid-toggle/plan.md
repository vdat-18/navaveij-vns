# MIG-5 Execution Plan — Frontend Hybrid AI/Rules Toggle

**Date:** 2026-03-19  
**Scope:**  
- `POC/v2/frontend/src/app/page.tsx`  
- `POC/v2/frontend/src/components/dashboard/RecommendationPanel.tsx`  
- `POC/v2/frontend/src/services/api.ts`  
**Status:** Executed (implementation completed; runtime command verification partially blocked by environment)

## Goal

Add a Screen 1 toggle that switches recommendation fetch mode between Hybrid AI and Rule-based fallback by sending `force_rule_based` to `/api/recommend`, while preserving current patient-change remount behavior.

## Confirmed Preconditions

1. MIG-4 backend contract already supports:
   - `force_rule_based` in request.
   - `recommendation_source` and `review_required` in response.
   - `security_metadata` in response.
2. `RecommendationPanel` currently remounts on patient change via `key={patientToken}`.
3. Toggle change must trigger re-fetch via effect dependency only, not by changing key.

## UI Options

1. **Option A (Recommended): Header Pill Toggle**
   - Location: top-right utility controls in `page.tsx` header.
   - OFF state: neutral/white, label `Mode: Hybrid AI`.
   - ON state: amber, label `Fallback: Rules`.
   - Benefit: closest to migration reference and lowest implementation risk.

2. **Option B: Segmented Mode Switch Near Recommendation Panel**
   - Location: just above `RecommendationPanel`.
   - Labels: `Hybrid AI` and `Rule-based Fallback`.
   - Benefit: stronger local context.
   - Tradeoff: more layout change and visual footprint.

## Planned Implementation Choice

Use **Option A** to stay aligned with migration reference and minimize layout churn.

## In-Scope Changes

1. `page.tsx`
   - Add state: `isRuleBasedForced`.
   - Render toggle control in header utility area.
   - Pass `isRuleBasedForced` into `RecommendationPanel`.

2. `api.ts`
   - Update `clinicalService.getRecommendation(patientToken, forceRuleBased = false)`.
   - Include `force_rule_based` in POST body.

3. `RecommendationPanel.tsx`
   - Extend props with `isRuleBasedForced: boolean`.
   - Pass force flag into `clinicalService.getRecommendation(...)`.
   - Add force flag to `useEffect` dependency array.
   - Keep `key={patientToken}` unchanged to preserve patient-only remount behavior.

## Non-Goals for MIG-5

- No Privacy Mode (MIG-6).
- No backend contract/orchestrator changes.
- No navigation structure changes beyond adding one toggle control.

## Implementation Steps

1. Add toggle state and header button in `page.tsx`.
2. Update `RecommendationPanel` invocation to pass new prop.
3. Update `api.ts` recommendation method signature and payload.
4. Update `RecommendationPanel` props, fetch call, and effect dependencies.
5. Keep animation/remount behavior:
   - remount on patient change (`key={patientToken}`)
   - no remount on mode toggle.
6. Add/extend frontend reliability tests to assert:
   - API call includes `force_rule_based`,
   - toggle-driven re-fetch dependency is present.
7. Update MIG-5 artifacts with status and evidence.

## Acceptance Gates

1. Toggle is visible in Screen 1 header utility area.
2. Toggling mode triggers a recommendation re-fetch for selected patient.
3. Response mode reflects selected state:
   - OFF → `recommendation_source: "AI"`
   - ON → `recommendation_source: "RuleBased"`
4. Patient-change remount behavior remains intact.
5. Existing routes/screens remain navigable.

## Risks and Mitigations

1. **Risk:** Toggle updates UI but data does not re-fetch.  
   **Mitigation:** Include `isRuleBasedForced` in panel `useEffect` dependencies.
2. **Risk:** Accidental full remount on toggle resets panel state/scroll.  
   **Mitigation:** Do not alter `key={patientToken}` logic.
3. **Risk:** API call omits force flag due signature drift.  
   **Mitigation:** Update method signature and call site together; verify by tests.
4. **Risk:** Visual style inconsistency in header control.  
   **Mitigation:** Reuse existing design tokens and control style from current header patterns.

## Verification Plan

1. Targeted tests:
   - frontend reliability contract tests for fetch dependency and service payload contract.
2. Manual checks (Screen 1):
   - select patient → load recommendation;
   - toggle OFF/ON and confirm recommendation refresh + source shift;
   - switch patient and confirm remount animation still occurs.
3. Regression checks:
   - `/trend-timeline`, `/access-monitoring`, `/audit` remain navigable.

## Exit Evidence to Capture

- Diffs for `page.tsx`, `RecommendationPanel.tsx`, and `api.ts`.
- Test output showing contract/reliability checks for toggle wiring.
- Updated MIG-5 artifact files:
  - `README.md`
  - `_discovery.md`
  - `_development_summary.md`
  - `_lastest_test_results.md`
