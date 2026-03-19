# GAP-8 — Create Canonical Demo Patient Record (Somchai W.)

**Severity:** 🟠 Medium
**Execution order:** Step 2 — do this immediately after GAP-1; unblocks all integration testing
**Estimated effort:** 30–45 minutes (data transcription)
**Category:** Data

---

## Why This Matters

`POST /recommend {"patient_token": "tok_hmac_56291047"}` currently returns a "Record not found" warning because no file in `assets/synthesis/` has `"patient_token": "tok_hmac_56291047"`.

The demo patient **Somchai W.** (age 54, male) is the canonical POC demo case referenced throughout all v3 specs:
- Expected tier: Advanced → `Platinum — Men` (฿8,700)
- Expected `confidence_score`: 0.823 (High)
- Has the `mammogram` eligibility exclusion — critical for the GAP-3 safety revocation demo

Without this record, integration testing from GAP-2 onwards cannot be verified. All end-to-end checklist items in `gap-closure-plan.md` require this patient token.

---

## Dependencies

- **Depends on:** GAP-1 (security fixes committed first)
- **Unblocks:** GAP-2, GAP-3, GAP-4, GAP-5, GAP-6 (all integration testing)

---

## How the Token Lookup Works

Understanding this prevents confusion about why the file name and directory matter:

```
API receives:  { "patient_token": "tok_hmac_56291047" }
                          │
                          ▼
  load_signal_store_record("tok_hmac_56291047")
  in POC/src/mcp_server/utils.py
                          │
                          ▼
  Globs:  assets/synthesis/**/record_*.json   (recursive)
  Reads each file, checks:  record["patient_token"] == "tok_hmac_56291047"
  Returns the first match
```

**Important:** The file must be named `record_*.json` (matches the glob) and must contain `"patient_token": "tok_hmac_56291047"` as a top-level field.

---

## Context Discovery

Read these files before creating the new record:

| File | What to look for |
|---|---|
| `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/signal-store-contract.md` | The complete Somchai W. example record — all section values to transcribe |
| `assets/synthesis/HealthyRoutineCheckup/record_000.json` | Structural reference — see the JSON shape of a complete signal store record |
| `POC/src/mcp_server/utils.py` | `load_signal_store_record()` — confirm the glob pattern and matching logic |

---

## What Already Exists (Don't Rewrite)

- `load_signal_store_record()` in `utils.py` already globs `**/record_*.json` recursively — **no code change needed**
- The existing `record_000.json` shows the exact JSON structure to follow

---

## Step-by-Step Instructions

### Create `assets/synthesis/canonical/record_somchai.json`

This is a **data transcription task only**. Transcribe the Somchai W. example from `signal-store-contract.md` into the file with the following top-level structure:

```json
{
  "patient_token": "tok_hmac_56291047",
  "hard_constraints": { ... },
  "clinical_signals": { ... },
  "biomarker_trends": { ... },
  "_meta": {
    "signal_coverage": 0.667,
    "data_completeness_ratio": 0.889,
    "populated_fields": 40,
    "total_key_fields": 45,
    "signals_fired_count": 22,
    "applicable_signals_count": 33
  }
}
```

**Key values to transcribe exactly (do not fabricate):**

**`hard_constraints.eligibility_exclusions`:**
```json
["mammogram", "pap_smear_hpv", "cervical_cancer_hpv_screen", "hpv_vaccine", "dexa_bone_density", "breast_ultrasound"]
```

**`clinical_signals.rule_preliminary_tier`:** `"Advanced"`

**`clinical_signals.signals_fired`:** 22 entries (full list in `signal-store-contract.md`)

**`clinical_signals.applicable_signals`:** 33 entries

**`biomarker_trends.labs.fbs`:**
```json
{ "current_value": 108, "velocity_per_year": 6, "unit": "mg/dL", "loinc_code": "1558-6" }
```

**`biomarker_trends.labs.hba1c`:**
```json
{ "current_value": 6.1, "unit": "%", "loinc_code": "4548-4" }
```

**Other key biomarkers:**
- LDL: 148 mg/dL
- eGFR: 82 mL/min/1.73m²
- BMI: 26.7 kg/m²
- BP: 138/88 mmHg

> All values must be taken verbatim from `signal-store-contract.md`. Do not invent values.

---

## Verification

```bash
# From the repo root (navaveij/), not from POC/
python -c "
import sys; sys.path.insert(0, 'POC')
from src.mcp_server.utils import load_signal_store_record
r = load_signal_store_record('tok_hmac_56291047')
print(r['patient_token'], r['clinical_signals']['rule_preliminary_tier'])
"
```

Expected output:
```
tok_hmac_56291047 Advanced
```
