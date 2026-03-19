# Plan: POC Interactive Demo — Full Build Plan

## Context
The v3 folder has 20 specification documents (20 `.md` files) covering architecture, MCP tool contracts, sample data, and screen-by-screen UI specs. No interactive application exists. This plan builds the POC demo from scratch, using every v3 spec as a source of truth.

**POC evaluation scoring:**
- 35% Hybrid Recommendation Engine + MCP
- 25% Pluggable AI + FHIR
- 20% UX/XAI explainability
- 20% Security, Privacy & Audit

---

## Build Order Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 0 (data updates) — run IN PARALLEL with everything else      │
│  • P0-A: update sample_add_on_items.json with confirmed prices       │
│  • P0-B: update __checkpoint.md OQ section                          │
└─────────────────────────────────────────────────────────────────────┘
          │                          │
          ▼                          ▼
┌──────────────────┐      ┌──────────────────────────────┐
│  PHASE 1         │      │  PHASE 2                      │
│  Backend API     │      │  Frontend Scaffold            │
│  (SEQUENTIAL     │      │  (PARALLEL with Phase 1)      │
│   prerequisite   │      │  Vite project, shared         │
│   for Phases     │      │  layout, navigation,          │
│   3-5)           │      │  API client layer             │
└──────────────────┘      └──────────────────────────────┘
          │                          │
          └──────────┬───────────────┘
                     ▼  (both Phase 1 + 2 must be done first)
        ┌────────────┴───────────────────────────────┐
        │  PHASES 3, 4, 5 — run IN PARALLEL          │
        │  • Phase 3: Screen 1 (Recommendation)       │
        │  • Phase 4: Screen 2 (Trend & Timeline)     │
        │  • Phase 5: Screen 3 (Access Monitoring)    │
        └─────────────────────────────────────────────┘
                     │
                     ▼  (all screens must be complete)
             ┌───────────────┐
             │  PHASE 6      │
             │  Integration  │
             │  + Demo Polish│
             └───────────────┘
```

---

## Phase 0 — Data Updates
**Folder:** `v3/samples/`
**Parallel with:** Everything

### Context
`navavej-checkup-package-discovery.md` was created 2026-03-12 and contains confirmed Expo promo prices for 29 add-on programs. `sample_add_on_items.json` currently has `price_thb: null` for most items.

### Functional Requirements
**P0-A: `samples/sample_add_on_items.json`**
- Fill `price_thb` for 29 items from discovery doc §5 (full list in Appendix A)
- Add `"price_note": "5th Anniversary Expo 2026 promo — expires 2026-03-31"` to each filled item
- Retain `price_thb: null` for: `psa_sdm`, `hepatitis_b_vaccine`, `pneumococcal_vaccine`, `shingrix_vaccine`, `unexplained_weight_loss_workup`
- Update `colonoscopy` item: annotate that this maps to Upper GI Endoscopy Package (฿9,500) pending lower GI colonoscopy confirmation
- Update `_open_questions_pending` array: remove items now resolved; retain only the 5 null-price items
- Change file `status` field from `"draft"` to `"partial"`

**P0-B: `__checkpoint.md`**
- OQ-Prices → **Partial**: Expo promo prices now confirmed; post-Expo standard prices still unknown (urgent before 2026-03-31)
- OQ-7 → **Partial**: Upper GI Endoscopy ฿9,500 confirmed; standalone lower GI colonoscopy TBD
- Add **OQ-WeightLoss**: no dedicated single program found; maps to SPOT-MAS (฿15,900) + Thyroid Pro 2 (฿3,395)
- Update Next Steps table: POC demo build is the current work item
- Add `data/navavej-checkup-package-discovery.md` to documents table if not already there

### Client Escalation (no action needed in code — for human follow-up)
| OQ | Urgency | Ask |
|---|---|---|
| OQ-Prices | 🔴 17 days | Standard prices for all packages after 2026-03-31 |
| OQ-7 | Medium | Standalone lower GI colonoscopy program? |
| OQ-10 | Medium | PSA standalone product code + price |
| OQ-HepB | Medium | Hepatitis B vaccine per-dose price |
| OQ-Pneumo | Medium | PCV20 or PCV15+PPSV23? Product code + price? |
| OQ-Shingrix | Medium | Shingrix per-dose price (confirm if offered at all) |
| OQ-HIS | Low | HIS system + FHIR R4 export capability |
| OQ-PackageItems | Low | Full itemized lists: Gold, Platinum M/F, Diamond Men |

### Testing
- `jq '[.[] | select(.price_thb == null)]' sample_add_on_items.json` returns exactly 5 items
- `jq '.status' sample_add_on_items.json` returns `"partial"`

---

## Phase 1 — Backend API
**Folder:** `v3/demo/backend/`
**Must complete before:** Phases 3, 4, 5

### Context
The backend serves as the "Recommendation Platform" from the architecture. For the POC it uses synthetic data instead of live FHIR feeds, but follows the exact same API contracts. The key demo value is proving the AI actually calls MCP tools and produces a structured, schema-valid output.

### Files
```
v3/demo/backend/
├── main.py              ← FastAPI app (all endpoints)
├── requirements.txt     ← dependencies
├── .env.example         ← AI_ACTIVE_CLIENT, ANTHROPIC_API_KEY, OPENAI_API_KEY
├── data/
│   ├── signals.json     ← Somchai W. MCP tool responses (from signal-store-contract)
│   ├── ruleset.json     ← from sample_ruleset_tier_config.json + sample_add_on_items.json
│   ├── timeline.json    ← Somchai W. timeline (from event-timeline-contract example)
│   └── monitoring.json  ← audit logs + anomaly alerts + snapshot (from access-monitoring-contract)
└── prompt_template.txt  ← system prompt from recommendation-output.baml §GenerateRecommendation
```

### Functional Requirements

**`POST /api/recommend`**
- Input: `{ "patient_token": "tok_hmac_56291047" }`
- Step 1 (Mock MCP Phase 1 — fixed baseline): call all 4 MCP tools in sequence:
  1. `get_hard_constraints(patient_token)` → load from `data/signals.json`
  2. `get_clinical_signals(patient_token)` → load from `data/signals.json`
  3. `get_biomarker_trends(patient_token)` → load from `data/signals.json`
  4. `get_program_ruleset(tier, gender, age)` → load from `data/ruleset.json`
- Step 2 (AI inference): assemble system prompt from `prompt_template.txt` + MCP responses → call Claude API with structured output mode
- Step 3 (Stage 2 enrichment): inject `rule_preliminary_tier`, `resolved_package`, `confidence_score` (0.823), `confidence_tier` ("High"), `recommendation_source`, `metadata.model_id`, `metadata.latency_ms`, `metadata.ruleset_version`; enrich each add-on with `label`, `category`, `navavej_product` from ruleset
- Output: full Stage 2 `RecommendationOutput` JSON
- `AI_ACTIVE_CLIENT` env var controls model: `claude` → `claude-sonnet-4-6`; `gpt4o` → `gpt-4o-mini`

**`GET /api/timeline/{patient_token}`**
- Returns event timeline object from `data/timeline.json` (Somchai W. example from event-timeline-contract)

**`GET /api/monitoring-snapshot`**
- Returns `MonitoringSnapshot` from `data/monitoring.json`

**`GET /api/audit-logs`**
- Query params: `user_id`, `patient_token_prefix`, `action_type`, `start_date`, `end_date`, `resource_type`
- Filters the audit log array in `data/monitoring.json` and returns matching entries

**CORS**: allow `http://localhost:5173` (Vite dev server)

### Testing
- `curl -X POST /api/recommend -d '{"patient_token":"tok_hmac_56291047"}'` returns JSON with non-empty `reasoning_trace` and at least 5 `add_ons`
- `reasoning_trace` changes on re-run (confirms live Claude call, not cached)
- Setting `AI_ACTIVE_CLIENT=gpt4o` and re-calling returns response with `metadata.model_id` showing GPT model name
- `GET /api/audit-logs?action_type=VIEW` returns only VIEW-type entries

---

## Phase 2 — Frontend Scaffold
**Folder:** `v3/demo/frontend/`
**Parallel with:** Phase 1

### Context
Vite + React + TypeScript project providing shared layout (top navigation between 3 screens), the API client layer (typed fetch wrappers), and shared UI primitives (badge, card, loading spinner). Screens are empty shells at this phase — filled in Phases 3-5.

### Files
```
v3/demo/frontend/
├── index.html
├── vite.config.ts
├── package.json          ← react, react-dom, recharts, typescript, vite
├── tsconfig.json
└── src/
    ├── main.tsx
    ├── App.tsx            ← screen state, top nav, screen router
    ├── api/
    │   ├── recommend.ts   ← POST /api/recommend → RecommendationOutput
    │   ├── timeline.ts    ← GET /api/timeline/{token}
    │   └── monitoring.ts  ← GET /api/monitoring-snapshot, /api/audit-logs
    ├── types/
    │   └── index.ts       ← TypeScript types mirroring Stage 2 JSON schema
    ├── components/
    │   ├── Badge.tsx      ← priority color badges (Red/Orange/Yellow/Green)
    │   ├── Card.tsx       ← section card wrapper
    │   └── Spinner.tsx    ← loading state
    └── screens/
        ├── Screen1.tsx    ← placeholder (Phase 3)
        ├── Screen2.tsx    ← placeholder (Phase 4)
        └── Screen3.tsx    ← placeholder (Phase 5)
```

### Functional Requirements
- Top nav: 3 tabs — "Recommendation", "Trend & Timeline", "Access Monitoring"
- Active tab highlighted; switching screens does not re-fetch unless explicitly triggered
- `api/recommend.ts`: calls `POST /api/recommend`, returns typed `RecommendationOutput`; exposes `loading`, `error`, `data` states
- TypeScript types must match Stage 2 JSON schema in `schema-contracts/recommendation-output-schema.md`
- Loading spinner shown while API call is in flight
- Error banner shown if API returns non-200

### Testing
- `npm run dev` starts without error
- Switching between 3 nav tabs renders placeholder without crash
- `api/recommend.ts` unit test: mock fetch, assert typed response shape

---

## Phase 3 — Screen 1: Individual Summary & Recommendation
**Folder:** `v3/demo/frontend/src/screens/Screen1.tsx`
**Spec:** `v3/poc-screens/screen-1-individual-summary.md`
**Parallel with:** Phases 4, 5

### Context
Primary clinical workflow screen. Demonstrates the hybrid engine output (rule tier vs AI tier comparison), XAI reasoning trace, and personalized add-on list with pricing. Highest weight in evaluation scoring (contributes to 35% + 25% + 20% UX criteria).

### Functional Requirements
**Panel A — Navigation**: provided by App.tsx (shared)

**Panel B — Patient Header**
- Name (PII-masked as "Somchai W."), age, gender, program type
- `model_id` badge (e.g., "claude-sonnet-4-6"), `latency_ms`, `ruleset_version`
- Source: `metadata` fields from Stage 2 output

**Panel C — Alert Banner**
- Critical signals: red badge list (`patient_high_alert.critical_signals`)
- Missing data warnings: yellow badge list (`patient_high_alert.missing_data_alerts`)
- Collapsible; defaults to expanded if `critical_signals.length > 0`

**Panel D — Tier Resolution**
- Left column: Rule Preliminary Tier (`rule_preliminary_tier`) with badge
- Right column: AI Recommended Tier (`ai_recommended_tier`) with badge
- Agreement indicator: green checkmark if match, amber warning if deviation
- If deviation: show `tier_deviation_justification` in amber callout box
- Confidence gauge: circular meter showing `confidence_score` (0.0–1.0) with `confidence_tier` label
- `recommendation_source` badge ("AI" or "Rule-Based")

**Panel E — AI Reasoning Trace (XAI)**
- Collapsible section (default collapsed)
- Shows full `reasoning_trace` string in monospace, left-bordered callout
- Label: "AI Chain-of-Thought (XAI)"

**Panel F — Add-On Recommendations**
- Sorted by priority: Red → Orange → Yellow → Green
- Each row: priority badge, `label`, `rationale`, `navavej_product.product_code`, `navavej_product.price_thb` formatted as "฿X,XXX"
- `price_thb: null` items: show "Price TBD" in grey
- Count badge on section header (e.g., "13 recommendations")

**Panel G — Communication Script**
- 4 tabs: Health Summary | Recommendation | Add-on Highlights | Next Steps
- Each tab: displays corresponding field from `communication_script`
- Copy-to-clipboard button on each tab

### Testing
- Render with fixture Stage 2 JSON → all 13 add-ons appear
- Tier deviation scenario: if `ai_recommended_tier ≠ rule_preliminary_tier`, amber callout visible
- Confidence gauge renders at 0.823 with "HIGH" label
- Reasoning trace toggle shows/hides content
- "Price TBD" shows for any `price_thb: null` item

---

## Phase 4 — Screen 2: Trend & Timeline
**Folder:** `v3/demo/frontend/src/screens/Screen2.tsx`
**Spec:** `v3/poc-screens/screen-2-trend-timeline.md`
**Parallel with:** Phases 3, 5

### Context
Longitudinal health history view. Demonstrates FHIR sourcing (LOINC codes on each chart) and data-driven clinical reasoning. Key for the 25% FHIR criterion.

### Functional Requirements

**Panel B — Patient Header**: same patient info strip as Screen 1 (shared component)

**Panel C — Biomarker Trend Charts** (6 charts, 2-column grid)
- FBS — LOINC 1558-6 — reference range 70–100 mg/dL
- HbA1c — LOINC 4548-4 — reference range < 5.7%
- LDL Cholesterol — LOINC 13457-7 — reference range < 100 mg/dL
- BMI — LOINC 39156-5 — reference range 18.5–22.9 (Asia-Pacific)
- BP Systolic — LOINC 8480-6 — reference range < 120 mmHg
- eGFR — LOINC 62238-1 — reference range ≥ 60 mL/min/1.73m²
- Each chart: LOINC code shown in subtitle, horizontal reference range band (shaded), slope annotation ("↑ +X.X/yr" or "↓")
- Data source: `get_biomarker_trends` response (loaded from `data/signals.json`)
- Chart library: Recharts `LineChart` + `ReferenceLine`

**Panel D — Clinical Event Timeline**
- Horizontal scrollable track of 12 events from `get_patient_event_timeline` response
- Event types: diagnosis (ICD-10 code shown), abnormal lab (LOINC + value), medication change, screening procedure
- Color-coded by event type; hover tooltip shows full event details
- Data source: `data/timeline.json`

**Panel E — Screening Gap Status**
- List of overdue screenings from `clinical_signals.screening_gaps`
- Each: screening name, days_overdue, next_recommended_date
- Color: red if > 365 days overdue, amber if < 365

**Time-range selector**: 1yr / 3yr / 5yr / All buttons — filters visible data window on all charts

### Testing
- All 6 charts render with correct LOINC code in subtitle
- Reference range band visible on each chart
- Timeline renders 12 events; hover tooltip shows ICD-10 or LOINC code
- "3yr" selector reduces visible data points on all charts simultaneously

---

## Phase 5 — Screen 3: Access Monitoring Dashboard
**Folder:** `v3/demo/frontend/src/screens/Screen3.tsx`
**Spec:** `v3/poc-screens/screen-3-access-monitoring.md`
**Parallel with:** Phases 3, 4

### Context
Admin/DPO security dashboard. Demonstrates PDPA compliance: RBAC, tamper-evident audit logging (SHA-256 hash chain), anomaly detection. Key for the 20% Security criterion.

### Functional Requirements

**Panel A — Live Metrics Bar**
- 7 KPIs from `MonitoringSnapshot`: active_users_now, sessions_today, records_accessed_today, ai_recommendations_today, alert_counts (critical/high/medium/low), safety_validator_failures_today
- Auto-refresh every 30 seconds (re-calls `GET /api/monitoring-snapshot`)

**Panel B — Anomaly Alerts**
- Table of anomaly alerts from `monitoring.json`
- Columns: severity badge, alert_type, user_id, description, detected_at, status (Open/Acknowledged/Resolved)
- Drilldown: click row → expand with full details + Acknowledge / Resolve buttons (UI-only state change for demo)

**Panel C — Audit Log Search**
- Filter bar: user_id, patient_token_prefix, action_type dropdown, start_date, end_date, resource_type
- Results table: who, when, what, patient_token (masked), resource_type
- Row drilldown: 5-dimension view (Who / When / Where / What / Why) + SHA-256 `entry_hash` + `prev_entry_hash`
- Hash chain verify button: client-side SHA-256 computation on the displayed entry's data fields; compare against `entry_hash`; show ✅ or ❌

**Secondary tabs:**
- **Role Management**: table of 5 system roles with permission matrix (physician/nurse/pharmacist/admin/dpo × resource×action)
- **Mapping Tool**: table of LOINC/SNOMED/ICD-10 mappings from `data/monitoring.json`
- **Master Data**: list of checkup programs, alert thresholds, screening intervals (read-only display)

### Testing
- Metrics bar renders all 7 KPIs from snapshot
- Audit log filter by `action_type=VIEW` reduces result set
- Hash chain verification: compute SHA-256 of displayed entry data; assert matches `entry_hash` field
- Role management tab: physician row shows no access to audit_log resource

---

## Phase 6 — Integration & Demo Polish
**Folder:** `v3/demo/` (both backend + frontend)
**Sequential after:** All screens complete

### Functional Requirements
- End-to-end smoke test: full page load → Screen 1 auto-fetches recommendation → all panels populated from API (not hardcoded)
- "Regenerate" button on Screen 1: re-calls `/api/recommend`; new `reasoning_trace` appears (proving live AI call)
- Model switcher (demo mode): dropdown in header toggles `AI_ACTIVE_CLIENT` between Claude and GPT-4o; header `model_id` badge updates
- `VITE_API_BASE_URL` env var for configuring backend URL (supports local dev and hosted demo)
- README in `v3/demo/` with setup instructions: `pip install -r requirements.txt`, `uvicorn main:app`, `npm install`, `npm run dev`

### Testing
- Full end-to-end: start backend, start frontend, load browser → Screen 1 populated with real AI output within 30s (TOR SLA for existing patient)
- Switch model → `model_id` in header changes → reasoning_trace is different style/length
- Screen 1 → Screen 2 navigation: timeline loads; biomarker charts render
- Screen 2 → Screen 3 navigation: monitoring snapshot loads; audit log search works

---

## Appendix A — Confirmed Add-On Prices (from discovery doc §5)

| item_id | price_thb |
|---|---|
| `colonoscopy` (Upper GI Endoscopy) | 9500 |
| `exercise_stress_test` | 2900 |
| `echocardiogram` | 2900 |
| `ct_cac` | 3900 |
| `cardiac_patch_monitor` | 7742 |
| `low_dose_ct_lung` | 3900 |
| `diabetes_screening_pro` | 2134 |
| `hepatitis_abc_screening` | 1900 |
| `fibrotouch` | 1900 |
| `gi_liver_screening` | 3500 |
| `kidney_disease_screening` | 2500 |
| `influenza_vaccine` | 490 |
| `senior_flu_vaccine` | 2300 |
| `mammogram` | 2850 |
| `pap_smear_hpv` | 2300 |
| `dexa_scan` | 1150 |
| `carotid_ultrasound` | 5096 |
| `spot_mas_multi_cancer` | 15900 |
| `spine_mri` | 6500 |
| `thyroid_pro_1` | 2134 |
| `thyroid_pro_2` | 3395 |
| `full_sleep_test` | 10900 |
| `sleep_apnea_cpap` | 12500 |
| `menopause_screening` | 7900 |
| `male_hormone_assessment` | 2900 |
| `abdominal_ultrasound_full` | 2550 |
| `dengue_vaccine` | 2990 |
| `hpv_vaccine` | 6990 |
| `dementia_screening` | 13900 |
