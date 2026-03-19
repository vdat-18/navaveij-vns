# GAP-7 — Create Monitoring Fixture Data

**Severity:** 🟠 Medium
**Execution order:** Step 7 — can be done in parallel with GAP-5 and GAP-6
**Estimated effort:** 45 minutes (data transcription/composition)
**Category:** Data

---

## Why This Matters

`GET /api/monitoring-snapshot` (GAP-6) reads from `assets/synthesis/canonical/monitoring.json`. This file doesn't exist. Without it, Screen 3 (Access Monitoring Dashboard) has no data to display.

Screen 3 covers three tabs and panels sourced from this file:
- Panel A: Live KPI metrics (`snapshot` object)
- Panel B: Anomaly alert table (`anomaly_alerts` array)
- Role Management tab: RBAC permission matrix (`roles` array)
- Mapping Tool tab: Terminology code mappings (`mapping_table` array)

**POC evaluation impact:** 20% Security/Privacy criterion (Screen 3 is one of the three evaluated screens)

---

## Dependencies

- **Depends on:** Nothing (pure data file — no code dependencies)
- **Unblocks:** GAP-6 (`GET /api/monitoring-snapshot` will 500 without this file)

---

## Context Discovery

Read these files before creating the fixture:

| File | What to look for |
|---|---|
| `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/access-monitoring-contract.md` | **Primary reference** — exact field definitions, `MonitoringSnapshot` object, `AnomalyAlert` schema, RBAC role schema, mapping table schema; all example values in this document should be used verbatim |
| `doc_outputs/architecture/AI/Recommendation Engine/v3/data/navavej-checkup-package-discovery.md` | LOINC codes and HIS codes for the mapping_table entries |
| `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/signal-store-contract.md` | LOINC codes used in Somchai W. labs — use these same codes in the mapping table for consistency |

---

## What Already Exists (Don't Rewrite)

Nothing — this is a net new data file. But the structure is fully specified in `access-monitoring-contract.md`.

---

## Step-by-Step Instructions

### Create `assets/synthesis/canonical/monitoring.json`

Build the file with 4 top-level keys: `snapshot`, `anomaly_alerts`, `roles`, `mapping_table`.

#### `snapshot` — Live KPI metrics

```json
{
  "snapshot_id": "snap_20260316_001",
  "generated_at": "2026-03-16T09:00:00Z",
  "active_users_now": 7,
  "sessions_today": 43,
  "patient_records_accessed_today": 118,
  "ai_recommendations_generated_today": 31,
  "alert_counts": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 11
  },
  "safety_validator_failures_today": 0,
  "top_active_departments": ["Cardiology", "Internal Medicine", "Oncology"]
}
```

#### `anomaly_alerts` — 3 alerts with mixed severity

Include at minimum:

1. **High severity** — high volume access (from `access-monitoring-contract.md` examples):
   ```json
   {
     "alert_id": "anm-20260314-001",
     "severity": "High",
     "alert_type": "high_volume",
     "user_id": "usr_supawan_k",
     "description": "User accessed 18 records in one session (4.3× baseline of 4.2)",
     "detected_at": "2026-03-14T14:23:00Z",
     "status": "Open",
     "baseline_value": 4.2,
     "observed_value": 18,
     "ratio": 4.3
   }
   ```

2. **Medium severity** — off-hours access pattern

3. **Low severity** — cross-department access (borderline)

> Use exact field names and severities from `access-monitoring-contract.md`. The Screen 3 frontend will render severity badges keyed on these exact strings.

#### `roles` — 5 RBAC roles

Include these roles (details from `access-monitoring-contract.md` RBAC section):
- `physician` — can view recommendations, approve/reject
- `nurse` — can view recommendations, read-only
- `pharmacist` — can view medication-relevant sections
- `admin` — can view monitoring dashboard, manage permissions
- `dpo` (Data Protection Officer) — can view full audit logs, export

Each role entry:
```json
{
  "role_id": "physician",
  "display_name": "Physician",
  "permissions": {
    "view_recommendations": true,
    "approve_recommendations": true,
    "view_patient_history": true,
    "export_data": false,
    "view_audit_logs": false,
    "manage_permissions": false
  }
}
```

#### `mapping_table` — 10 terminology mappings

Include mappings covering the key LOINC codes from Somchai W.'s biomarkers:

| HIS Code | LOINC | Display Name |
|---|---|---|
| `HIS-LAB-0042` | `1558-6` | Fasting Glucose |
| `HIS-LAB-0043` | `4548-4` | HbA1c |
| `HIS-LAB-0044` | `2089-1` | LDL Cholesterol |
| `HIS-LAB-0045` | `2085-9` | HDL Cholesterol |
| `HIS-LAB-0046` | `2571-8` | Triglycerides |
| `HIS-LAB-0047` | `33914-3` | eGFR |
| `HIS-LAB-0048` | `718-7` | Hemoglobin |
| `HIS-LAB-0049` | `2160-0` | Creatinine |
| `HIS-COND-0010` | `73211009` (SNOMED) | Diabetes Mellitus |
| `HIS-COND-0011` | `38341003` (SNOMED) | Hypertension |

Each entry:
```json
{
  "mapping_id": "map-001",
  "his_code": "HIS-LAB-0042",
  "target_system": "LOINC",
  "target_code": "1558-6",
  "display_name": "Fasting Glucose",
  "mapping_type": "exact",
  "status": "active",
  "last_updated": "2026-03-01"
}
```

---

## Verification

```bash
# Validate JSON structure
python -c "
import json
with open('assets/synthesis/canonical/monitoring.json') as f:
    d = json.load(f)
print('snapshot.alert_counts.high:', d['snapshot']['alert_counts']['high'])
print('anomaly_alerts count:', len(d['anomaly_alerts']))
print('roles count:', len(d['roles']))
print('mapping_table count:', len(d['mapping_table']))
"
```

Expected output:
```
snapshot.alert_counts.high: 2
anomaly_alerts count: 3
roles count: 5
mapping_table count: 10
```
