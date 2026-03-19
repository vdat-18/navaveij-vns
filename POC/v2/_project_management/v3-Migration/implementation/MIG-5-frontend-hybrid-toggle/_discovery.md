# MIG-5 Discovery

## v3 Implementation Pattern

**State (page.tsx):**
```typescript
const [isRuleBasedForced, setIsRuleBasedForced] = useState(false);
```

**Button (page.tsx):**
```typescript
<button onClick={() => setIsRuleBasedForced(!isRuleBasedForced)}
  className={cn(
    "... rounded-full font-black text-[10px] uppercase tracking-widest ...",
    isRuleBasedForced
      ? "bg-amber-500 text-white border-amber-600 animate-pulse"
      : "bg-white text-navavej-gray-med border-navavej-border hover:border-amber-400"
  )}>
  <Activity className="w-4 h-4" />
  {isRuleBasedForced ? "Fallback: Rules" : "Mode: Hybrid AI"}
</button>
```

**API call (api.ts):**
```typescript
getRecommendation: async (patientToken: string, forceRuleBased: boolean = false) => {
    const response = await api.post("/recommend", {
        patient_token: patientToken,
        force_rule_based: forceRuleBased
    });
    return response.data;
}
```

**RecommendationPanel:** receives `isRuleBasedForced` as prop; include in `useEffect` dependency array so re-fetch triggers on toggle.

## Notes for v2

- v2 `api.ts` currently uses `patient_token` in the POST body — consistent with the contract route. Just add `force_rule_based`.
- v2's RecommendationPanel fetches based on `patientToken` prop — also add `isRuleBasedForced` to dependency.

## Implementation Confirmation

- Header toggle implemented in `page.tsx` utility controls and wired to `isRuleBasedForced` state.
- `RecommendationPanel` now accepts `isRuleBasedForced` and re-fetches when toggle state changes.
- `clinicalService.getRecommendation(...)` now sends `force_rule_based` in request payload.
- Existing remount key (`key={patientToken}`) remained unchanged to avoid toggle-triggered remounts.
