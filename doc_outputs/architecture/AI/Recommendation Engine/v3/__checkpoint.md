# Checkpoint — Recommendation Engine v3

**Last updated:** 2026-03-14 (all 3 POC screens complete)
**Reference patient:** Somchai W., 54yo male (`patient_token: tok_hmac_56291047`)

---

## Documents Produced (in order)

| # | File | Status | Summary |
|---|------|--------|---------|
| 1 | `very-high-level.md` | ✅ Done | 6-block Mermaid diagram: Hospital Networks → Data Pipeline → Data Stores → Recommendation Platform → Output Layer → Feedback Store |
| 2 | `high-level.md` | ✅ Done | Detailed Mermaid LR flowchart with all components, subgraphs, color legend, architectural separation of concerns table, MCP tool→requirement mapping |
| 3 | `component-inventory-solution-approach.md` | ✅ Done | 12-component inventory table (role / inputs / outputs / tech / TOR criterion) + 7 solution approach sections (Hybrid Engine, MCP ReAct loop, PII Masking, Pluggable AI, XAI output schema, Safety Validator, Audit Logger) + query-time data flow narrative + requirement coverage matrix |
| 4 | `data/navavej-checkup-package-discovery.md` | ✅ Done | Hospital research: 8 core package tiers (Basic → Diamond), itemized Basic (16) and Diamond Women (47) packages, 12-section add-on program catalog with prices and TOR triggers, tier resolution table, add-on trigger cross-reference, gender/age hard constraints, 10 open questions for client |
| 5 | `data/fhir-discovery-report.md` | ✅ Done | 13 FHIR R4 resources inventoried with example payloads; full signal→FHIR path→LOINC/CPT/CVX mapping table; key LOINC codes reference; 8 gaps + mitigations; DE pipeline implications (extraction queries, derived computations, update frequency, data quality, patient token de-identification) |
| 6 | `data/clinical-guidelines-reference.md` | ✅ Done | 13 sections covering lab reference ranges (FBS, HbA1c, lipids, liver enzymes, eGFR, TSH, PSA, uric acid), BP classification (ACC/AHA 2017), BMI (WHO/Asia-Pacific), cancer screening intervals (mammogram, cervical, colorectal, lung, DEXA, HCC), ASCVD risk + EST indications, diabetes follow-up, kidney monitoring, liver disease, vaccination schedules (influenza, HepB, HPV, pneumococcal, zoster), smoking/lung, occupational/lifestyle, echocardiogram, sleep apnea (STOP-BANG); consolidated signal processing rules appendix |
| 7 | `signal-store-contract.md` | ✅ Done | 3 MCP tool specs: `get_hard_constraints`, `get_clinical_signals`, `get_biomarker_trends` — each with purpose, full JSON example response (Somchai W.), JSON Schema, and field dictionary; Signal Store DB record structure; Confidence Calibrator formula with Somchai example computation (score: 0.823 → High); complete signal ID catalog (40 signals) |
| 8 | `ruleset-store-contract.md` | ✅ Done | `get_program_ruleset` MCP tool spec — 4 tier selection rules (PREMIUM_SEVERE_SINGLE, PREMIUM_MULTI_SIGNAL, ADVANCED_METABOLIC_OR_CVD, STANDARD_DEFAULT) with full JSON example (Somchai W.); package resolution map (Standard/Advanced/Premium × male/female × age bands); 24 add-on items with trigger signals, priority defaults, Navavej product metadata, gender/age constraints, admin-configurable fields; JSON Schema; field dictionary; Ruleset Store DB schema (2 record types); admin configurability guide; BAML connection diagram; worked tier resolution example |
| 9 | `samples/rule-synthesis-framework.md` | ✅ Done | Methodology for translating clinical guidelines into Ruleset Store records; derivation ledger for all 28 add-on items; validation checklist |
| 10 | `samples/medical-expert-review.md` | ✅ Done | Non-technical plain-language version of the ruleset for physician review; all clinical logic in plain language without technical syntax |
| 11 | `samples/sample_ruleset_tier_config.json` | ✅ Done | Machine-readable Ruleset Store DB record: 4 tier selection rules in JSON |
| 12 | `samples/sample_add_on_items.json` | ✅ Done | Machine-readable Ruleset Store DB records: all 28 add-on items in JSON |
| 13 | `samples/sample_patient_checkup.json` | ✅ Done | Reference patient input record (Somchai W.) in normalized FHIR-derived format |
| 14 | `schema-contracts/recommendation-output-schema.md` | ✅ Done | Framework-agnostic output schema: enums (Tier, PriorityLevel, ConfidenceTier, RecommendationSource, AddOnCategory), 8 sub-types, main RecommendationOutput type with [AI]/[SYS]/[ENRICH] field annotations; 10 validation rules; field responsibility matrix; complete worked example Stage 1 (AI output) + Stage 2 (enriched); BAML conversion notes |
| 15 | `schema-contracts/recommendation-output.baml` | ✅ Done | BAML schema file (Stage 1 AI output only): 4 pluggable LLM clients (GPT4o, Claude35Sonnet, Claude3Opus, LocalLlama) + ActiveModel fallback client driven by `AI_ACTIVE_CLIENT` env var; Tier + PriorityLevel enums; AddOnItem, CommunicationScript, RecommendationOutput classes with inline constraints and field documentation; `GenerateRecommendation` function with full system prompt covering all 5 reasoning steps; test case reference pointing to Somchai W. worked example |
| 16 | `schema-contracts/event-timeline-contract.md` | ✅ Done | 5th MCP tool `get_patient_event_timeline(patient_token)` — display-only (UI layer, not AI input); 5-array response: `diagnoses[]` (FHIR Condition, ICD-10+SNOMED, onset_type), `hospitalizations[]` (FHIR Encounter inpatient/emergency), `significant_lab_events[]` (abnormal FHIR Observations only, 5-year lookback, LOINC-coded), `screening_procedure_history[]` (completed FHIR Procedures, CPT-coded, days_ago aligned with signal-store screening_gaps), `medication_changes[]` (started/stopped/dose_change, RxNorm); full JSON example (Somchai W. — 4 diagnoses, 5 lab events, 1 screening, 2 medication starts); JSON Schema; field dictionary; Event Timeline Store DB record; UI consumption notes cross-referencing Screen 2 chart elements |
| 17 | `schema-contracts/access-monitoring-contract.md` | ✅ Done | Admin/DPO dashboard schema covering all 6 TOR §3.4 sub-features: (1) Audit log record — 5-dimension Who/When/Where/What/Why + SHA-256 per-entry hash + per-user hash chain for tamper evidence; `search_audit_logs` API with 7 filter fields; full JSON examples (View + Export actions); (2) Anomaly Detection — rolling 30-day user baseline model; 3 signal types (high_volume/out_of_department/off_hours) with configurable thresholds; AnomalyAlert record with Open→Acknowledged→Resolved lifecycle; (3) MonitoringSnapshot — live metrics (active_users_now, sessions_today, records_accessed_today, alert_counts by severity, safety_validator_failures); (4) RBAC — Role + UserRoleAssignment records; predefined system roles table (physician/nurse/pharmacist/admin/dpo) with resource×action permission matrix; (5) MappingEntry — HIS local code → LOINC/SNOMED_CT/ICD10/CPT/CVX/NAVAVEJ_PRODUCT; mapping_type (exact/broad/narrow/approximate); status (active/pending_review/deprecated); (6) Master data — 5 record types: checkup_program, alert_threshold, screening_interval, vaccine_schedule, safety_rule; Admin API endpoint summary (16 endpoints) |
| 18 | `poc-screens/screen-1-individual-summary.md` | ✅ Done | Screen 1 mockup: Physician/Nurse view — 7 panels (A nav, B patient header, C alert banner, D tier+confidence, E AI reasoning trace, F add-on list, G communication script); all fields traced to recommendation-output-schema; full Somchai W. data (13 add-ons shown with rationale, product code, price; AI/Rule tier side-by-side; confidence 0.823 High; 3 critical alerts; 2 missing data alerts; 4-tab communication script); tier deviation and rule-based fallback states documented |
| 19 | `poc-screens/screen-2-trend-timeline.md` | ✅ Done | Screen 2 mockup: Physician/Nurse longitudinal view — 5 panels (A nav, B header, C 6-chart biomarker grid, D clinical event timeline track, E screening gap status); all charts annotated with LOINC codes and field paths from signal-store-contract; all 12 timeline events (4 diagnoses × ICD-10, 5 abnormal labs × LOINC + threshold, 2 medication changes, 1 colonoscopy screening) traced to event-timeline-contract; screening gap panel cross-references both contracts via days_ago alignment; slope annotations, chart rendering notes, zoom/tooltip interaction spec |
| 20 | `poc-screens/screen-3-access-monitoring.md` | ✅ Done | Screen 3 mockup: Admin/DPO view — 5 panels (A header, B live metrics bar, C anomaly alerts, D audit log search, E secondary tabs); all 9 MonitoringSnapshot fields mapped; 3 anomaly alert rows with drilldown (alert detail + resolution lifecycle + hash chain verification); audit log search with 6 filter fields + 4 result rows + entry drilldown (5-dimension Who/When/Where/What/Why display); role-access boundary table (Admin vs DPO); hash chain integrity check spec; audit-of-the-audit (export action self-logging) noted; secondary tabs: Role Management (RBAC sub-schema 4), Mapping Tool (sub-schema 5), Master Data (sub-schema 6) |
| 21 | `data/client-open-questions.md` | ✅ Done | Formal client questionnaire for Navavej: 5 sections covering all 9 production-blocking OQs — Section 1 (URGENT: post-Expo standard pricing for all 8 packages, deadline 2026-03-31), Section 2 (add-on catalog nulls: PSA, HepB vaccine, Pneumococcal, Shingrix, Weight Loss workup — each with context + sub-questions), Section 3 (colonoscopy lower GI product clarification), Section 4 (full itemizations: Gold, Platinum M/F, Diamond Men), Section 5 (HIS system + FHIR R4 integration capability); includes 9-row priority summary table, 60-minute meeting agenda template, and document maintenance guide |

---

## MCP Tools — Complete Inventory (5 tools)

| # | Tool | Contract | Caller | Purpose |
|---|------|----------|--------|---------|
| 1 | `get_hard_constraints(patient_token)` | signal-store-contract.md | Inference Orchestrator | Gender/age exclusions, safety flags, tier ceiling |
| 2 | `get_clinical_signals(patient_token)` | signal-store-contract.md | Inference Orchestrator | Risk flags, screening gaps, vaccination gaps |
| 3 | `get_biomarker_trends(patient_token)` | signal-store-contract.md | Inference Orchestrator | Lab history arrays, trend direction, slope |
| 4 | `get_program_ruleset(tier, gender, age)` | ruleset-store-contract.md | Inference Orchestrator | Package resolution map, add-on items |
| 5 | `get_patient_event_timeline(patient_token)` | event-timeline-contract.md | Dashboard UI (Screen 2 only) | Clinical event history for timeline track |

Tools 1–4 are AI inference inputs. Tool 5 is display-only — the AI model never receives it.

---

## What the AI Emits (Stage 1 — BAML scope)

```
RecommendationOutput (Stage 1)
  ai_recommended_tier               Tier enum
  tier_deviation_justification?     string | null
  add_ons[]                         AddOnItem[]
  reasoning_trace                   string
  supporting_signals[]              string[]
  missing_signals[]                 string[]
  communication_script              CommunicationScript

AddOnItem (AI core)
  item_code                         string
  priority_level                    PriorityLevel enum
  rationale                         string

CommunicationScript
  opening                           string
  health_summary                    string
  recommendation_explanation        string
  add_on_highlights[]               string[]
  next_steps                        string
```

## What the System Injects (Stage 2 — backend only)

```
rule_preliminary_tier               from Signal Store
resolved_package                    from Ruleset Store package_resolution_map
confidence_score                    Confidence Calibrator (formula in component-inventory §2.5)
confidence_tier                     derived from score (High ≥0.75, Medium ≥0.50, Low <0.50)
review_required                     Graceful Degradation flag
recommendation_source               "AI" | "RuleBased"
patient_high_alert                  critical_signals[] + missing_data_alerts[]
metadata                            request_id, model_id, template_version, etc.
add_ons[].label                     Ruleset Store enrichment
add_ons[].category                  Ruleset Store enrichment
add_ons[].navavej_product           Ruleset Store enrichment
add_ons[].trigger_signals_matched[] intersection of trigger_signals ∩ signals_fired
```

---

## Key Design Decisions (settled)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Priority levels | 4: Red / Orange / Yellow / Green | Consistent with Ruleset Store contract; Orange needed for vaccination gaps |
| Confidence score | Computed by system, not AI | AI self-reported confidence is miscalibrated |
| Communication script | AI-generated, structured sections | Ensures hospital-standard consistency; not free-form |
| Patient High Alert | System-computed post-AI | Deterministic from Signal Store; dashboard renders directly |
| BAML scope | Stage 1 only (AI output) | Stage 2 types are backend-only; no BAML needed |
| Tier deviation | Requires explicit justification | Mandatory non-null string when AI deviates from rule tier |

---

## Next Steps

| Priority | Task | Status |
|----------|------|--------|
| ✅ Complete | UI mockup specs — all 3 screens specified (docs 18–20) | Done |
| ✅ Complete | Client questionnaire for all 9 OQs — `data/client-open-questions.md` | Done |
| 🔜 In Progress | **POC interactive demo** — FastAPI backend + React frontend | Building now |
| ⏳ Blocked on client | OQ escalation — standard pricing + vaccine prices + HIS confirmation | Awaiting client |

**POC deliverable status:**
| Criterion | Weight | Architecture Docs | Interactive Demo |
|---|---|---|---|
| Process Flow Architecture | — | ✅ `high-level.md` + `component-inventory` | — |
| Mockup Screens (min 3) | — | ✅ Specs in `poc-screens/` | 🔜 Building |
| Architecture & Data Standard Strategy (FHIR R4 + MCP + Pluggable AI) | 25% + 35% | ✅ All contracts complete | 🔜 Building |
| Security, Privacy & Audit | 20% | ✅ `access-monitoring-contract.md` | 🔜 Building |
| UX / XAI | 20% | ✅ `screen-1-individual-summary.md` | 🔜 Building |

**Demo build plan:** `demo/backend/` (FastAPI + Claude API) + `demo/frontend/` (Vite + React). See plan file for full phase breakdown.

---

## Open Questions

| ID | Status | Question | Impact |
|----|--------|----------|--------|
| OQ-7 | 🟡 Partial | Standalone colonoscopy (lower GI) program? Current mapping uses Upper GI Endoscopy (฿9,500, ENDO_UPPER) as placeholder — confirmed available. Ask client: is there a separate lower GI colonoscopy product? | Product code accuracy for colonoscopy trigger |
| OQ-10 | 🔴 Open | Standalone PSA test product code + price? | `psa_sdm` item has `price_thb: null`, `product_code: "TBD"` |
| OQ-HepB | 🔴 Open | Hepatitis B vaccine per-dose price? | `hepatitis_b_vaccine` item has `price_thb: null` |
| OQ-Pneumo | 🔴 Open | Pneumococcal vaccine product: PCV20 or PCV15+PPSV23? Product code + price? | `pneumococcal_vaccine` item has `price_thb: null`, `product_code: "TBD"` |
| OQ-Shingrix | 🔴 Open | Shingrix (RZV) per-dose price? Confirm whether offered at Navavej at all. | `shingrix_vaccine` item has `price_thb: null` |
| OQ-Prices | 🟡 Partial | Post-Expo standard prices after 2026-03-31? Expo promo prices now confirmed from `navavej-checkup-package-discovery.md` (all filled in `sample_add_on_items.json`). Standard prices still unknown. **Urgent: Expo pricing expires 2026-03-31.** | All `price_thb` values will be incorrect for production use after March 31 |
| OQ-HIS | 🔴 Open | HIS system in use? FHIR R4 export capability? | Entire data pipeline design; non-blocking for POC |
| OQ-PackageItems | 🔴 Open | Full itemization of Gold, Platinum (M/F), Diamond Men packages? | Duplicate-test deduplication logic; non-blocking for POC |
| OQ-WeightLoss | 🔴 Open | Composite product code for unexplained weight loss workup (Tumor Markers + Thyroid Pro 2)? No dedicated single program found in discovery doc. | `unexplained_weight_loss_workup` item has `price_thb: null`, `product_code: "TBD_WEIGHT_LOSS_PANEL"` |

**POC-blocking OQs:** None — POC uses synthetic data for Somchai W.
**Production-blocking OQs:** OQ-Prices (urgent), OQ-10, OQ-HepB, OQ-Pneumo, OQ-Shingrix, OQ-HIS, OQ-PackageItems, OQ-WeightLoss.

**Client questionnaire:** `data/client-open-questions.md` — formal document covering all 9 OQs with context, sub-questions, a 60-min meeting agenda, and a document maintenance guide. Use this for the next client meeting or email to the Navavej Health Checkup Program Office.
