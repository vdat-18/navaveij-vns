# Client Open Questions — Navavej Smart Health Checkup Recommendation Dashboard

**Document version:** 1.0
**Prepared:** 2026-03-16
**Prepared by:** System Architect (Smart Health POC team)
**For:** Navavej International Hospital — Health Checkup Program Office
**Contact:** 1507 / +66 2-483-9999 · info@navavej.com · Line: @navavej

---

## Purpose

This document lists questions that must be confirmed directly with Navavej before the Smart Health Checkup Recommendation Dashboard can be deployed to production. It is intended for a structured client meeting or email inquiry session.

Questions are grouped by urgency. **Section 1 is time-critical and must be resolved before 2026-03-31.**

---

## Section 1 — URGENT: Pricing After Expo Promotional Period (Deadline: 2026-03-31)

> **Background:** All package prices currently in the system reflect the 5th Anniversary Wellbeing Expo 2026 promotional rates, which expire on **2026-03-31** (15 days from the date of this document). If the system goes live with Expo prices after that date, every quoted price will be incorrect.

**Please provide the standard (non-promotional) prices for the following packages:**

| Package | Expo Promo Price | Standard Price (needed) |
|---|---|---|
| Basic (16 items) | ฿2,871 | ❓ |
| Afternoon (18 items) | ฿3,690 | ❓ |
| Gold | ฿5,900 | ❓ |
| Platinum — Men | ฿8,700 | ❓ |
| Platinum — Women | ฿13,500 | ❓ |
| Diamond — Men | ฿15,000 | ❓ |
| Diamond — Women | ฿19,000–฿21,990 | ❓ (฿22,671 found — please confirm) |
| Diamond Couple | ฿26,000–฿34,000 | ❓ |

**Also confirm:** Does Navavej plan to run any promotions or pricing adjustments immediately after the Expo period, or will standard pricing apply starting 2026-04-01?

---

## Section 2 — Add-On Catalog Items with Missing Prices

The following add-on programs appear in the recommendation engine's catalog but have no confirmed price or product code. Each one can be recommended to patients and will display "Price TBD" until resolved.

---

### OQ-10 — Standalone PSA Test

| Field | Current Value | Needed |
|---|---|---|
| Product name | PSA Standalone Test | Confirm or correct |
| Product code | TBD | ❓ Confirm product code (e.g., `PSA_STANDALONE`) |
| Price per test | null | ❓ Confirm price in THB |

**Context:** The PSA (Prostate-Specific Antigen) blood test is recommended as a shared-decision-making discussion item for male patients aged 50–69 (and from age 40 for those with a first-degree family history of prostate cancer). The system needs to quote a specific price for patients who elect to add this test.

**Important note:** If PSA is already included within the Diamond — Men package, it should NOT appear as a separate billable add-on for Diamond patients. Please confirm:
- Is PSA included in Diamond — Men?
- Is PSA included in Platinum — Men?
- If yes to either: should it only appear as an add-on for patients in Basic, Afternoon, or Gold tiers?

---

### OQ-HepB — Hepatitis B Vaccine Per-Dose Price

| Field | Current Value | Needed |
|---|---|---|
| Product name | Hepatitis B Vaccine | Confirm or correct |
| Product code | VAX_HEPB | Confirm product code |
| Price per dose | null | ❓ Confirm price per dose in THB |

**Context:** The Hepatitis B vaccination series (3-dose: months 0, 1, 6 — or 2-dose Heplisav-B: months 0, 1) is recommended for unvaccinated adult patients. The system shows this as an add-on when the patient's vaccination history indicates an incomplete or missing series.

**Please also confirm:**
1. Which schedule does Navavej offer — 3-dose standard series, 2-dose Heplisav-B, or both?
2. Is the price the same per dose regardless of dose number in the series?
3. Is there a combined "full series" package price (vs. per-dose billing)?

---

### OQ-Pneumo — Pneumococcal Vaccine

| Field | Current Value | Needed |
|---|---|---|
| Product name | Pneumococcal Vaccine | Confirm or correct |
| Product code | TBD | ❓ Confirm product code |
| Price | null | ❓ Confirm price in THB |

**Context:** CDC ACIP 2022 guidelines recommend pneumococcal vaccination for adults aged 65+ and for younger high-risk adults (e.g., those with diabetes, CKD, or immunosuppression). Two regimen options exist:

- **Option A — PCV20 (Prevnar 20):** Single dose. One-and-done.
- **Option B — PCV15 (Vaxneuvance) + PPSV23 (Pneumovax 23):** Two doses, 1 year apart.

**Please confirm:**
1. Which product(s) does Navavej carry — PCV20, PCV15, PPSV23, or a combination?
2. Product code and price for each product carried.
3. Which regimen does the hospital recommend for its patient population?

---

### OQ-Shingrix — Shingrix (RZV) Zoster Vaccine

| Field | Current Value | Needed |
|---|---|---|
| Product name | Shingrix (RZV) — Zoster Vaccine | Confirm or correct |
| Product code | VAX_SHINGRIX | Confirm product code |
| Price per dose | null | ❓ Confirm price per dose in THB |

**Context:** Shingrix (recombinant zoster vaccine, RZV) is the CDC ACIP preferred shingles vaccine for adults aged 50+ — a 2-dose series given 2–6 months apart. It has ≥91% efficacy against shingles.

**Please confirm:**
1. Does Navavej currently stock and administer Shingrix?
2. If yes: price per dose (dose 1 and dose 2 — are they the same price?).
3. If Shingrix is NOT available: does Navavej offer the older Zostavax (ZVL) as an alternative? (Note: ZVL is less effective and the system would note this distinction.)

---

### OQ-WeightLoss — Unexplained Weight Loss Workup Panel

| Field | Current Value | Needed |
|---|---|---|
| Product name | Tumor Marker Panel + Thyroid Pro 2 | Confirm or correct |
| Product code | TBD_WEIGHT_LOSS_PANEL | ❓ Confirm product code(s) |
| Price | null | ❓ Confirm price in THB |

**Context:** The TOR specification (§3.1) maps the symptom "unexplained weight loss" to a workup combining Tumor Marker tests and Thyroid Function. When a patient reports unexplained weight loss in the intake questionnaire, the system recommends this workup.

**Please confirm:**
1. Does Navavej offer a bundled "unexplained weight loss workup" package (single product code)?
2. If no bundle exists: should this be two separate add-on items — **Tumor Marker Panel** (provide product code + price) and **Thyroid Pro 2** (already in system as `THYRO_PRO2`, ฿3,395) — recommended together?
3. If a bundle exists: provide product name, product code, and price.

---

## Section 3 — Endoscopy Program (Lower GI / Colonoscopy)

### OQ-7 — Standalone Colonoscopy (Lower GI) Product

**Current system state:** The colonoscopy add-on item currently maps to the **Upper GI Endoscopy Package** (฿9,500, product code `ENDO_UPPER`) as a placeholder. This is incorrect — colonoscopy is a lower GI procedure.

**Please confirm:**
1. Does Navavej offer a standalone **colonoscopy** (lower GI / colorectal) program as a separate product from the Upper GI Endoscopy package?
2. If yes: provide the product name, product code, and price.
3. If colonoscopy is only available bundled with upper GI endoscopy (i.e., a combined GI package): provide that bundle's product name, product code, and price.

**Why this matters:** The system recommends colonoscopy for patients aged 45–85 as colorectal cancer screening (USPSTF 2021 — Grade A for ages 45–75; shared decision-making for 76–85). If colonoscopy is not a standalone service, the recommendation and pricing will need to be adjusted.

---

## Section 4 — Full Package Itemizations (Non-Urgent; Needed for Deduplication Logic)

### OQ-PackageItems — Gold, Platinum M/F, Diamond Men Package Contents

**Background:** The system knows the full 47-item itemization of **Diamond — Women** and the 16-item list for **Basic**. However, it does not have confirmed item lists for the following packages:

| Package | What We Need |
|---|---|
| Gold | Full item list (reported as ~30 items) |
| Platinum — Men | Full item list |
| Platinum — Women | Full item list |
| Diamond — Men | Full item list (analogous to Diamond Women but male-specific) |

**Why this matters:** When the system recommends add-on tests to a patient, it must avoid recommending tests that are already included in their chosen base package. Without knowing what's in each package, patients could be charged twice for the same test.

**Preferred format:** A spreadsheet or PDF with one column for test/service name and one column for the specific package(s) it appears in. The HDmall or Lazada product listing pages for each package would also suffice.

---

## Section 5 — HIS System & Data Integration (Non-Urgent for POC; Required for Production)

### OQ-HIS — Hospital Information System and FHIR Capability

**Please provide:**

1. **HIS vendor and version:** Which Hospital Information System does Navavej use? (e.g., HealthLink, InterSystems TrakCare, ISMED, Dimak Pro, or other)

2. **FHIR R4 export capability:** Does the HIS support FHIR R4 API endpoints for reading patient data?
   - If yes: can it export patient records as FHIR R4 resources (Observation, Condition, MedicationRequest, Procedure, Patient, Immunization)?
   - If yes: is the FHIR API currently exposed to authorized integrations, or would this require a configuration request with the HIS vendor?

3. **Lab result storage:** Are lab results (CBC, lipid panel, HbA1c, eGFR, liver enzymes, etc.) stored in a structured, queryable format with LOINC codes, or as free-text/scanned PDFs?

4. **Vaccination record storage:** Are patient vaccination histories (influenza, Hepatitis B, Shingrix, etc.) stored in the HIS with CVX codes or as free-text entries?

5. **Preferred integration path:** If FHIR R4 is not natively supported, what alternative integration mechanism does the IT team prefer?
   - HL7 v2 message feed
   - Direct SQL/database query (read-only)
   - Batch CSV export + scheduled import
   - Custom REST API from the HIS vendor

**Impact:** The answer to this question determines the entire data pipeline design. For the POC, synthetic data is used and this is non-blocking. For production deployment, the data pipeline must be built to match the actual HIS integration method.

---

## Summary Table — Open Question Priority

| OQ ID | Topic | Urgency | Impact if Unresolved |
|---|---|---|---|
| OQ-Prices | Post-Expo standard pricing | 🔴 **URGENT** (before 2026-03-31) | All package prices wrong in production |
| OQ-7 | Lower GI colonoscopy product | 🟠 High | Incorrect product + price shown to patients |
| OQ-10 | Standalone PSA product code + price | 🟠 High | "Price TBD" displayed; PSA not deduplicated from Diamond Men |
| OQ-HepB | Hepatitis B vaccine price | 🟠 High | "Price TBD" displayed; dosing schedule unclear |
| OQ-Pneumo | Pneumococcal vaccine product + price | 🟠 High | "Price TBD" displayed; wrong vaccine regime recommended |
| OQ-Shingrix | Shingrix per-dose price | 🟠 High | "Price TBD" displayed; may not be offered at all |
| OQ-WeightLoss | Weight loss workup composite code | 🟡 Medium | "Price TBD" displayed; may need to split into 2 items |
| OQ-PackageItems | Gold / Platinum / Diamond Men itemizations | 🟡 Medium | Duplicate test deduplication not possible |
| OQ-HIS | HIS system + FHIR capability | 🟢 Low (POC non-blocking) | Data pipeline design blocked for production |

---

## Recommended Meeting Agenda (60 min)

| Time | Topic | Owner |
|---|---|---|
| 0–5 min | Introductions; confirm purpose of meeting | Both |
| 5–15 min | **Section 1:** Post-Expo standard pricing (walk through table row by row) | Navavej Finance / Package Team |
| 15–30 min | **Section 2:** Add-on catalog — PSA, HepB vaccine, Pneumococcal, Shingrix, Weight Loss panel | Navavej Health Checkup Program Manager |
| 30–35 min | **Section 3:** Colonoscopy / Lower GI product clarification | Navavej GI / Endoscopy Department |
| 35–45 min | **Section 4:** Package itemizations — Gold, Platinum M/F, Diamond Men | Navavej Health Checkup Program Manager |
| 45–55 min | **Section 5:** HIS system and FHIR integration capability | Navavej IT Department |
| 55–60 min | Summary of answers; confirm follow-up items | Both |

---

## Document Maintenance

When answers are received, update the following files:

| File | What to update |
|---|---|
| `samples/sample_add_on_items.json` | Fill `price_thb` and `product_code` for null/TBD items; update `_open_questions_pending` array |
| `data/navavej-checkup-package-discovery.md` | Add standard prices to §2 tier table; update §5 with confirmed package itemizations |
| `__checkpoint.md` | Update OQ status column: 🔴 → 🟡 → ✅ as each question is resolved |
| `schema-contracts/ruleset-store-contract.md` | Update add-on library example response with confirmed prices/codes |

**When all OQs are resolved:** Change `sample_add_on_items.json` top-level `status` field from `"partial"` to `"active"` and advance version to `v2026.xx.x-active`.
