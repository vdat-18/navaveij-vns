# MIG-6 — Frontend: PII Privacy Mode Toggle

**Status:** Not started
**Priority:** P2
**POC Scoring Impact:** Security 20% + XAI 20%
**Depends on:** MIG-4

## Objective

Add a "Privacy Mode" toggle in the Screen 1 dashboard that switches between:
- **Physician View** (default, green, unlocked): Real names, IDs, contact info, rehydrated reasoning trace
- **AI Masked View** (privacy mode ON, red, locked, pulsing): UUID tokens for all PII fields, masked reasoning trace

## Files Changed

- `POC/v2/frontend/src/app/page.tsx`
- `POC/v2/frontend/src/components/dashboard/RecommendationPanel.tsx`

## Acceptance Gate

- Privacy Mode toggle button visible (Eye/EyeOff icon, red/green)
- Patient name/ID/MRN/phone/email switch to UUID tokens when Privacy Mode is ON
- Reasoning trace in RecommendationPanel switches to masked version when Privacy Mode is ON
- Toggling back restores real values
- `security_metadata.rehydration_map` must be populated in the API response (requires MIG-3/MIG-4 complete)

## v3 Reference

- `POC/v3/frontend/src/app/page.tsx` — lines 30 (state), 34-44 (getDisplayValue), 253-264 (toggle button)
- `POC/v3/frontend/src/components/dashboard/RecommendationPanel.tsx` — line 547 (masked trace render)
