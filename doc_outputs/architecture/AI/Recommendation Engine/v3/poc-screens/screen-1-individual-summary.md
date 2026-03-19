# Screen 1 — Individual Summary & Recommendation
## Navavej Health Intelligence Dashboard — POC UI Specification

**Version:** 1.0
**Date:** 2026-03-14
**Audience:** Physician, Nurse (primary clinical workflow screen)
**Reference patient:** Somchai W., 54yo male (`patient_token: tok_hmac_56291047`)
**Data source contracts:** `recommendation-output-schema.md`, `signal-store-contract.md`

**POC evaluation criteria addressed:**
- **35%** — Hybrid mechanism: Rule engine tier vs AI tier displayed side-by-side (panel D)
- **25%** — Pluggable AI architecture: Model ID, template version, latency shown (panel B)
- **20%** — XAI / Explainability: Full `reasoning_trace` + `confidence_score` gauge (panels D + E)

---

## User Journey

A physician opens this screen after selecting a patient who has been referred for annual checkup planning. The AI recommendation has already been generated in the background. The physician reviews:
1. The patient's active alerts and missing data gaps (panel C)
2. Whether the AI agreed with the rule engine's tier assessment, and how confident it is (panel D)
3. The AI's full chain-of-thought reasoning to understand *why* the recommendation was made (panel E)
4. The prioritised list of add-on tests, each with clinical rationale and Navavej product price (panel F)
5. The ready-to-use patient communication script in the patient's language (panel G)

---

## Wireframe

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  [A] NAVIGATION BAR                                                         ║
║  🏥 Navavej Health Intelligence    Somchai W. ▾    🔴 3 alerts    ⚙ Admin  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [B] PATIENT HEADER STRIP                                                   ║
║                                                                              ║
║  Somchai W.    54 yo  ♂    tok_hmac_562****47                               ║
║  📦 Platinum — Men  ฿8,700     Generated: 2026-03-13 07:41 UTC              ║
║  Source: [ AI MODEL ✓ ]   Model: claude-3-5-sonnet   Latency: 4,812 ms     ║
║  Ruleset: v2026.03.1   Signal pipeline: pipe_20260312_0300                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [C] PATIENT ALERT BANNER                                              ████  ║
║                                                                              ║
║  ⚠  HIGH PRIORITY ALERTS  (3)                                               ║
║  ─────────────────────────────────────────────────────────────────────────  ║
║  🔴  LDCT lung cancer screening eligible — NEVER performed                   ║
║      Age 54, 22 pack-years, quit 3yr — USPSTF 2021 annual LDCT indicated   ║
║                                                                              ║
║  🔴  Colonoscopy overdue 2,557 days                                          ║
║      First-degree family history: brother diagnosed colon cancer age 48     ║
║      5-year screening interval applies — last performed June 2019            ║
║                                                                              ║
║  🔴  First-degree family history: premature CAD                              ║
║      Father: MI age 51 (below male threshold of 55) — ACC/AHA risk enhancer ║
║                                                                              ║
║  ─────────────────────────────────────────────────────────────────────────  ║
║  ⚠  MISSING DATA  (2 actionable)                                            ║
║  ⬜  STOP-BANG questionnaire not completed                                   ║
║      Impact: BMI 26.7 + Stage 1 HTN → 2 STOP-BANG criteria already met;    ║
║      if total ≥ 3, Full Sleep Test (PSG) add-on should be added             ║
║  ⬜  Physical activity questionnaire not completed                            ║
║      Impact: sedentary risk adjustment may be underestimated                 ║
╠═══════════════════════════════════════╦══════════════════════════════════════╣
║  [D] TIER RESOLUTION & CONFIDENCE     ║  [E] AI REASONING TRACE (XAI)       ║
║                                       ║                                      ║
║  TIER RESOLUTION                      ║  "Patient is a 54-year-old Thai male ║
║                                       ║  presenting with a complex           ║
║  Rule Engine         AI Model         ║  multi-system risk profile. I will   ║
║  ┌─────────────┐     ┌─────────────┐  ║  address each signal cluster in turn.║
║  │  Advanced   │  =  │  Advanced   │  ║                                      ║
║  └─────────────┘     └─────────────┘  ║  Tier determination: The Clinical    ║
║  ✓  Agreement — no deviation          ║  Signal Engine pre-computed           ║
║                                       ║  rule_preliminary_tier as 'Advanced' ║
║  ─────────────────────────────────    ║  via rule ADVANCED_METABOLIC_OR_CVD  ║
║  CONFIDENCE SCORE                     ║  (matched: prediabetes_confirmed).   ║
║                                       ║  I agree with this tier assignment.  ║
║  ████████░░  0.823  HIGH              ║  The patient does not meet           ║
║              ●                        ║  PREMIUM_SEVERE_SINGLE criteria...   ║
║                                       ║                                      ║
║  Supporting signals:  20              ║  Metabolic / pre-diabetes cluster:   ║
║  Missing signals:      4              ║  FBS velocity is +6 mg/dL/year       ║
║                                       ║  (96→102→108 over 3 years). HbA1c   ║
║  ─────────────────────────────────    ║  6.1% confirms pre-diabetic range... ║
║  DEVIATION STATE (not shown here)     ║                                      ║
║  When AI ≠ Rule tier: yellow band     ║  Cancer screening cluster:           ║
║  + tier_deviation_justification text  ║  Colonoscopy gap is most urgent:     ║
║  shown between the two tier boxes     ║  7 years overdue on 5-year interval  ║
║                                       ║  (FDR colon ca age 48). Red-priority.║
║                                       ║  LDCT never initiated despite full   ║
║                                       ║  USPSTF 2021 eligibility...          ║
║                                       ║                                      ║
║                                       ║               [Expand full trace ↓]  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [F] RECOMMENDED ADD-ONS  (13 items)                                        ║
║                                                                              ║
║  SORT BY: [ Priority ▾ ]    FILTER: [ All categories ▾ ]    [ Expand all ] ║
║                                                                              ║
║  🔴  CRITICAL  ──────────────────────────────────────────────────────────── ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │  🔴  Colonoscopy — Colorectal Cancer Screening                         │ ║
║  │       Navavej: Endoscopy Package (Upper GI)  ENDO_UPPER      ฿ 9,500  │ ║
║  │       Triggered by: colonoscopy_overdue_2557d · family_hx_colon_ca    │ ║
║  │                                                                         │ ║
║  │       "Colonoscopy is 7 years 1 month overdue (last performed June     │ ║
║  │        2019). Patient's brother was diagnosed with colon cancer at age │ ║
║  │        48, which triggers a 5-year screening interval per USPSTF 2021. │ ║
║  │        The current overdue duration of 2,557 days substantially        │ ║
║  │        exceeds even the standard 10-year interval. This is the         │ ║
║  │        highest-urgency screening gap in this patient's profile."       │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │  🔴  Low-Dose CT Chest — Lung Cancer Screening                         │ ║
║  │       Navavej: Low-Dose CT Chest (Lung Ca / PM2.5)  LDCT_LUNG ฿ 3,900 │ ║
║  │       Triggered by: lung_ct_threshold_met                              │ ║
║  │                                                                         │ ║
║  │       "Patient has never had a low-dose CT lung cancer screening. He   │ ║
║  │        meets all USPSTF 2021 eligibility criteria: age 54 (50–80),    │ ║
║  │        22 pack-years (≥20 threshold), and former smoker who quit 3     │ ║
║  │        years ago (within the 15-year quit window). Annual LDCT is      │ ║
║  │        indicated and was never initiated."                              │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  🟠  URGENT  ──────────────────────────────────────────────────────────── ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │  🟠  Influenza Vaccine (Annual)                                         │ ║
║  │       Navavej: Influenza Vaccine  VAC-FLU-ANNUAL              ฿ 650   │ ║
║  │       Triggered by: influenza_overdue_428d                             │ ║
║  │       "Overdue 428 days. Last received October 2024; patient missed    │ ║
║  │        the Oct/Nov 2025 seasonal dose. Annual influenza vaccination     │ ║
║  │        recommended for all adults per CDC ACIP 2024."                  │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │  🟠  Shingrix Vaccine (Dose 1 of 2)                                     │ ║
║  │       Navavej: Shingrix (RZV) Series            [price_thb: enquire]  │ ║
║  │       Triggered by: shingrix_not_started                               │ ║
║  │       "Never received. Eligible since age 50 — now 4 years overdue    │ ║
║  │        from eligibility. 2-dose RZV series (0, 2–6 months) is the     │ ║
║  │        preferred zoster vaccine for adults ≥50 per CDC ACIP 2017."    │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║                              🟠 URGENT  [2 more items ▾]                   ║
║                                                                              ║
║  🟡  RECOMMENDED  [5 items ▾]      🟢  OPTIONAL  [2 items ▾]               ║
║                                                                              ║
║  [ Add to checkup plan ]   [ Print full add-on list ]   [ Review all ↓ ]   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [G] COMMUNICATION SCRIPT                                                   ║
║                                                                              ║
║  [ Health Summary ]   Recommendation   Add-on Highlights   Next Steps       ║
║  ─────────────────────────────────────────────────────────────────────────  ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │  "Your overall health profile shows several areas that deserve          │ ║
║  │  attention. Your blood sugar has been gradually rising over the past    │ ║
║  │  three years and is now in the pre-diabetic range, and your blood       │ ║
║  │  pressure remains slightly above the recommended level despite          │ ║
║  │  medication. Your cholesterol, particularly LDL, has also been          │ ║
║  │  increasing. On the positive side, your kidney function is normal       │ ║
║  │  and your thyroid is healthy.                                            │ ║
║  │                                                                          │ ║
║  │  The most important finding today is that your colorectal cancer         │ ║
║  │  screening is significantly overdue, and you are also eligible for a    │ ║
║  │  lung cancer screening that you have not yet had."                       │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║  [ Copy to clipboard ]  [ Print ]  [ Save to patient record ]               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Field-to-Contract Mapping

| Panel | UI Element | Displayed Value (Somchai W.) | Source Contract | Source Field |
|-------|-----------|------------------------------|----------------|--------------|
| B | Patient display name | Somchai W. | recommendation-output-schema | `metadata.patient_token` → de-identified display name resolved by UI layer |
| B | Age | 54 yo | signal-store-contract | `get_hard_constraints → patient_demographics.age` |
| B | Gender | ♂ | signal-store-contract | `get_hard_constraints → patient_demographics.gender` |
| B | Patient token (masked) | tok_hmac_562****47 | recommendation-output-schema | `metadata.patient_token` — first 10 + last 2 chars displayed |
| B | Package name | Platinum — Men | recommendation-output-schema | `resolved_package.package_name` |
| B | Package price | ฿8,700 | recommendation-output-schema | `resolved_package.price_thb` |
| B | Generated timestamp | 2026-03-13 07:41 UTC | recommendation-output-schema | `metadata.generated_at` |
| B | Source badge | AI MODEL ✓ | recommendation-output-schema | `recommendation_source` = "AI" |
| B | Model ID | claude-3-5-sonnet | recommendation-output-schema | `metadata.model_id` |
| B | Latency | 4,812 ms | recommendation-output-schema | `metadata.latency_ms` |
| B | Ruleset version | v2026.03.1 | recommendation-output-schema | `metadata.ruleset_version` |
| B | Pipeline run ID | pipe_20260312_0300 | recommendation-output-schema | `metadata.signal_store_pipeline_run_id` |
| C | Critical alert #1 label | LDCT lung screening eligible — NEVER performed | recommendation-output-schema | `patient_high_alert.critical_signals[0].label` |
| C | Critical alert #1 detail | Age 54, 22 pack-years… USPSTF 2021 | recommendation-output-schema | `patient_high_alert.critical_signals[0].clinical_note` |
| C | Critical alert #2 label | Colonoscopy overdue 2,557 days | recommendation-output-schema | `patient_high_alert.critical_signals[1].label` |
| C | Critical alert #2 detail | FDR: brother colon cancer age 48… last June 2019 | recommendation-output-schema | `patient_high_alert.critical_signals[1].clinical_note` |
| C | Critical alert #3 label | First-degree family history: premature CAD | recommendation-output-schema | `patient_high_alert.critical_signals[2].label` |
| C | Critical alert #3 detail | Father: MI age 51 — ACC/AHA risk enhancer | recommendation-output-schema | `patient_high_alert.critical_signals[2].clinical_note` |
| C | Missing data #1 | STOP-BANG questionnaire not completed | recommendation-output-schema | `patient_high_alert.missing_data_alerts[0].label` |
| C | Missing data #1 impact | BMI 26.7 + Stage 1 HTN… if ≥3 add PSG | recommendation-output-schema | `patient_high_alert.missing_data_alerts[0].recommendation_impact` |
| C | Missing data #2 | Physical activity questionnaire not completed | recommendation-output-schema | `patient_high_alert.missing_data_alerts[1].label` |
| D | Rule engine tier | Advanced | recommendation-output-schema | `rule_preliminary_tier` |
| D | AI model tier | Advanced | recommendation-output-schema | `ai_recommended_tier` |
| D | Agreement indicator | ✓ Agreement — no deviation | recommendation-output-schema | derived: `rule_preliminary_tier == ai_recommended_tier` → `tier_deviation_justification` is null |
| D | Confidence bar fill | ████████░░ (8/10 segments) | recommendation-output-schema | `confidence_score` = 0.823 |
| D | Confidence value | 0.823 | recommendation-output-schema | `confidence_score` |
| D | Confidence tier label | HIGH | recommendation-output-schema | `confidence_tier` |
| D | Supporting signals count | 20 | recommendation-output-schema | `supporting_signals[].length` |
| D | Missing signals count | 4 | recommendation-output-schema | `missing_signals[].length` |
| E | AI reasoning trace | Full paragraph text | recommendation-output-schema | `reasoning_trace` (full text, truncated with expand control) |
| F | Section header count | 13 items | recommendation-output-schema | `add_ons[].length` |
| F | Card 1: priority badge | 🔴 CRITICAL | recommendation-output-schema | `add_ons[0].priority_level` = "Red" |
| F | Card 1: label | Colonoscopy — Colorectal Cancer Screening | recommendation-output-schema | `add_ons[0].label` (Stage 2 enriched) |
| F | Card 1: product name | Endoscopy Package (Upper GI) | recommendation-output-schema | `add_ons[0].navavej_product.product_name` |
| F | Card 1: product code | ENDO_UPPER | recommendation-output-schema | `add_ons[0].navavej_product.product_code` |
| F | Card 1: price | ฿9,500 | recommendation-output-schema | `add_ons[0].navavej_product.price_thb` |
| F | Card 1: triggers | colonoscopy_overdue_2557d · family_hx_colon_ca | recommendation-output-schema | `add_ons[0].trigger_signals_matched[]` |
| F | Card 1: rationale | "Colonoscopy is 7 years 1 month overdue…" | recommendation-output-schema | `add_ons[0].rationale` |
| F | Card 2: priority badge | 🔴 CRITICAL | recommendation-output-schema | `add_ons[1].priority_level` = "Red" |
| F | Card 2: label | Low-Dose CT Chest — Lung Cancer Screening | recommendation-output-schema | `add_ons[1].label` (Stage 2 enriched) |
| F | Card 2: product name | Low-Dose CT Chest (Lung Ca / PM2.5) | recommendation-output-schema | `add_ons[1].navavej_product.product_name` |
| F | Card 2: product code | LDCT_LUNG | recommendation-output-schema | `add_ons[1].navavej_product.product_code` |
| F | Card 2: price | ฿3,900 | recommendation-output-schema | `add_ons[1].navavej_product.price_thb` |
| F | Card 2: trigger | lung_ct_threshold_met | recommendation-output-schema | `add_ons[1].trigger_signals_matched[]` |
| F | Card 2: rationale | "Patient has never had a low-dose CT…" | recommendation-output-schema | `add_ons[1].rationale` |
| F | Card 3 (Orange): label | Influenza Vaccine (Annual) | recommendation-output-schema | `add_ons[2].label` |
| F | Card 3: price | ฿650 | recommendation-output-schema | `add_ons[2].navavej_product.price_thb` |
| F | Card 3: trigger | influenza_overdue_428d | recommendation-output-schema | `add_ons[2].trigger_signals_matched[]` |
| F | Card 4 (Orange): label | Shingrix Vaccine (Dose 1 of 2) | recommendation-output-schema | `add_ons[3].label` |
| F | Card 4: price | enquire (null) | recommendation-output-schema | `add_ons[3].navavej_product.price_thb` = null → "enquire" display |
| G | Active tab: Health Summary | Active (underlined) | recommendation-output-schema | `communication_script` tab index = health_summary |
| G | Health summary text | "Your overall health profile shows…" | recommendation-output-schema | `communication_script.health_summary` |
| G | Recommendation tab text | (inactive, click to view) | recommendation-output-schema | `communication_script.recommendation_explanation` |
| G | Add-on highlights tab | (inactive, 4 bullet items) | recommendation-output-schema | `communication_script.add_on_highlights[]` |
| G | Next steps tab | (inactive) | recommendation-output-schema | `communication_script.next_steps` |

---

## Design Notes

### Tier Deviation State (alternative panel D rendering)

When `ai_recommended_tier ≠ rule_preliminary_tier`, panel D renders differently:

```
  TIER RESOLUTION

  Rule Engine         AI Model
  ┌─────────────┐     ┌─────────────┐
  │   Premium   │  ≠  │  Advanced   │
  └─────────────┘     └─────────────┘
  ⚠  AI deviated from rule engine

  Justification: "While 4 signals qualify for PREMIUM_MULTI_SIGNAL,
  none of the individual conditions are severe enough to warrant
  Diamond-level evaluation. Advanced with targeted add-ons is
  clinically proportionate and cost-appropriate for this patient."
```

The justification text is sourced from `tier_deviation_justification` (non-null when tiers differ).

### Rule-Based Fallback State (when `recommendation_source = "RuleBased"`)

When the AI model fails or `review_required = true`:
- Panel B source badge shows `[ RULE-BASED ]` instead of `[ AI MODEL ✓ ]`
- Panel E (AI Reasoning Trace) shows: "⚠ AI model unavailable. This recommendation was generated by the Rule Engine only. Review required before presenting to patient."
- Panel D shows only the Rule Engine tier (no AI tier box)

### Color System

| Priority | Color code | Usage |
|----------|-----------|-------|
| Red 🔴 | `#DC2626` | Critical add-ons, alert banner background |
| Orange 🟠 | `#EA580C` | Urgent add-ons |
| Yellow 🟡 | `#CA8A04` | Recommended add-ons |
| Green 🟢 | `#16A34A` | Optional add-ons |
| Navy | `#1E3A5F` | Navigation bar, header background |

### Collapsed Add-on Groups

Orange (4 items), Yellow (5 items), and Green (2 items) groups are collapsed by default. Each collapsed group shows the count and a ▾ chevron. Expanding shows the full card list with rationale and product details. The two Red cards are always expanded on load as they require immediate physician attention.

### POC Scope Notes

- The "Add to checkup plan" button and "Save to patient record" action are shown as UI affordances but out of scope for the POC functional implementation — they are represented in the wireframe to show intended integration with the HIS system.
- The audit log entry for this screen view is automatically written by the Audit Logger when the screen is loaded (`action_type: View`, `resource_type: RecommendationOutput`).
- Price display: `price_thb: null` items show "enquire" pending resolution of open questions OQ-10, OQ-HepB, OQ-Pneumo, OQ-Shingrix from the checkpoint.
