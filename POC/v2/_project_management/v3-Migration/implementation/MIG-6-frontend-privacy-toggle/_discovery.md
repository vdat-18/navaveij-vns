# MIG-6 Discovery

## v3 Implementation Pattern

**State (page.tsx):**
```typescript
const [privacyMode, setPrivacyMode] = useState(false);
```

**getDisplayValue helper (page.tsx):**
```typescript
const getDisplayValue = (originalValue: string, fallbackToken: string) => {
    if (!privacyMode) return originalValue || "N/A";
    const map = clinicalData?.security_metadata?.rehydration_map;
    if (map && originalValue) {
        const token = Object.keys(map).find(key => map[key] === originalValue);
        if (token) return token;
    }
    return fallbackToken;
};
```

**Toggle button (page.tsx):**
```typescript
<button onClick={() => setPrivacyMode(!privacyMode)}
  className={cn(
    "flex items-center gap-2 px-4 py-2 rounded-full font-black text-[10px] ...",
    privacyMode
      ? "bg-navavej-red text-white hover:bg-navavej-red/90"
      : "bg-navavej-gray-light text-navavej-gray-dark hover:bg-navavej-border"
  )}>
  {privacyMode ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
  {privacyMode ? "Switch to Physician View" : "Switch to Raw AI View"}
</button>
```

**Masked reasoning trace (RecommendationPanel.tsx):**
```typescript
const trace = privacyMode
    ? data.security_metadata?.masked_ai_output?.reasoning_trace
    : data.reasoning_trace;
// Render trace instead of data.reasoning_trace directly
```

**PII fields replaced with getDisplayValue():**
- `selectedPatient.patient_name` → `getDisplayValue(selectedPatient.patient_name, "tok_named_entity")`
- `selectedPatient.patient_id` → `getDisplayValue(selectedPatient.patient_id, "tok_id_entity")`
- `selectedPatient.mrn` → `getDisplayValue(selectedPatient.mrn, "tok_mrn_entity")`
- `selectedPatient.phone` → `getDisplayValue(selectedPatient.phone, "tok_phone_entity")`
- `selectedPatient.email` → `getDisplayValue(selectedPatient.email, "tok_email_entity")`

## Notes for v2

- `clinicalData` in v2's page.tsx is the state that holds the recommendation API response — same pattern.
- The `rehydration_map` key order reversal (find token by value) works correctly as long as no two PII fields have the same value, which is guaranteed by the PIIMasker UUID generation.
- If `security_metadata` is null (e.g., from a cached response before MIG-3 was applied), `getDisplayValue` safely falls back to `fallbackToken`.
