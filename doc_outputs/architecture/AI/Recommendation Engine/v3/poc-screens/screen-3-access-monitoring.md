# Screen 3 — Access Monitoring Dashboard
## Navavej Health Intelligence Dashboard — POC UI Specification

**Version:** 1.0
**Date:** 2026-03-14
**Audience:** Admin, DPO — Data Protection Officer (this screen is NOT accessible to physicians or nurses)
**Data source contracts:** `access-monitoring-contract.md` (all 6 sub-schemas)

**POC evaluation criteria addressed:**
- **20%** — Security, Privacy & Auditing: real-time anomaly detection, tamper-evident audit log, RBAC role management, PDPA-compliant data masking (panels B, C, D, E)

---

## User Journey

The DPO opens this dashboard as part of their daily compliance review. The physician/nurse workflow screens (1 and 2) are not accessible from here — this is a separate access-controlled application. The DPO:
1. Checks the live metrics bar for today's system activity summary (panel B)
2. Reviews open anomaly alerts and investigates any High/Critical severity cases (panel C)
3. Searches the audit log to investigate specific patients or users on request from a data subject or regulator (panel D)
4. Navigates to secondary tabs for role management, code mapping, and master data administration (panel E)

---

## Sample Data (from `access-monitoring-contract.md`)

**MonitoringSnapshot:**
- `active_users_now`: 7
- `sessions_today`: 43
- `patient_records_accessed_today`: 118
- `ai_recommendations_generated_today`: 31
- `alert_counts`: { critical: 0, high: 2, medium: 5, low: 11 }
- `safety_validator_failures_today`: 0

**AnomalyAlerts (sample, 3 shown):**
1. Nurse Supawan K. — `high_volume` — High — 18 records (baseline 4.2) — triggered 02:31 — Open
2. Pharmacist Prasert T. — `out_of_department` — High — Cardiology (baseline: Health Checkup Center) — triggered 01:15 — Open
3. Nurse Nattaya P. — `off_hours` — Medium — access at 23:58 (baseline: 08–17) — triggered 23:58 — Open

**AuditLogEntries (sample, 4 shown):**
1. Dr. Arisa Thanapon — View — RecommendationOutput — tok_hmac_562****47 — 15:42 ICT — safety_pass
2. Nrs. Supawan K. — Export — RecommendationOutput — tok_hmac_562****47 — 16:15 ICT
3. Dr. Arisa Thanapon — Generate — RecommendationOutput — tok_hmac_831****12 — 16:55 ICT — latency 4,812ms
4. Admin usr-admin-00001 — Admin — MasterData — (no patient) — 17:02 ICT

---

## Wireframe

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  [A] ADMIN DASHBOARD HEADER                                                 ║
║  🔒 Navavej Health Intelligence — Access Monitoring                         ║
║  Logged in: usr-admin-00001  (Admin)    Session expires: 16:00 ICT         ║
║  Last refreshed: 2026-03-14 14:00 ICT    [Auto-refresh: 60s ▾]  [⟳ Now]   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [B] LIVE METRICS BAR                                                       ║
║                                                                              ║
║  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌───────────┐ ║
║  │  Active Users  │  │ Sessions Today │  │ Records Today  │  │   Alerts  │ ║
║  │                │  │                │  │                │  │           │ ║
║  │       7        │  │       43       │  │      118       │  │ 🔴  0     │ ║
║  │    online now  │  │    sessions    │  │  patient rec.  │  │ 🟠  2     │ ║
║  │                │  │                │  │                │  │ 🟡  5     │ ║
║  │                │  │                │  │                │  │ 🟢 11     │ ║
║  └────────────────┘  └────────────────┘  └────────────────┘  └───────────┘ ║
║                                                                              ║
║  AI Recommendations today: 31    |    Safety Validator Failures: 0   ✓     ║
╠══════════════════════════════════╦═══════════════════════════════════════════╣
║  [C] ANOMALY ALERTS              ║  [D] AUDIT LOG SEARCH                    ║
║                                  ║                                          ║
║  OPEN ALERTS (18 total)          ║  ┌────────────────────────────────────┐  ║
║  SORT: [ Severity ▾ ]  [ Filter ]║  │  User ID:                          │  ║
║                                  ║  │  [__________________________]      │  ║
║  Sev  User         Type   Time   ║  │                                    │  ║
║  ────────────────────────────    ║  │  Patient token prefix (min 8 chr): │  ║
║  🟠H  Supawan K.   vol   02:31  ║  │  [__________________________]      │  ║
║       18 rec / avg 4.2           ║  │                                    │  ║
║       [Acknowledge] [Session ↗]  ║  │  Date from: [ 2026-03-01 ]         │  ║
║                                  ║  │  Date to:   [ 2026-03-14 ]         │  ║
║  🟠H  Prasert T.   dept  01:15  ║  │                                    │  ║
║       Cardiology (base: CheckUp) ║  │  Action: [ All types      ▾ ]      │  ║
║       [Acknowledge] [Session ↗]  ║  │  Resource: [ All resources ▾ ]     │  ║
║                                  ║  └────────────────────────────────────┘  ║
║  🟡M  Nattaya P.   hours 23:58  ║                  [ 🔍 Search ]            ║
║       Off-hrs: 23:58 (08–17)     ║                                          ║
║       [Acknowledge] [Session ↗]  ║  RESULTS  (24 entries)   Page 1 of 1    ║
║                                  ║  ──────────────────────────────────────  ║
║  🟡M  Wirat K.     hours 22:43  ║  Time(ICT)  Who          What   Patient  ║
║       [Acknowledge] [Session ↗]  ║  ────────   ────────     ─────  ────────  ║
║                                  ║  15:42      Dr.Arisa     View   562****  ║
║  🟢L  Sunisa M.    hours 21:30  ║  16:15      Nrs.Supwn    Export 562****  ║
║       [Acknowledge] [Session ↗]  ║  16:55      Dr.Arisa     Gen    831****  ║
║                                  ║  17:02      Admin        Admin   —       ║
║  [+ 13 more ▾]                   ║                                          ║
║                                  ║  [ Load more… ]                          ║
║  ─────────────────────────────── ║  ─────────────────────────────────────── ║
║  Resolution log:                 ║  [ Export results: CSV ]  [ PDF ]        ║
║  Today: 3 resolved, 2 false-pos  ║                                          ║
╠══════════════════════════════════╩═══════════════════════════════════════════╣
║  [E] NAVIGATION TABS — SECONDARY FEATURES                                   ║
║                                                                              ║
║  [ Active Alerts & Audit Log ]  |  Role Management  |  Mapping Tool  |  Master Data ║
║  ────────────────────────────────────────────────────────────────────────── ║
║  (Active tab above. Other tabs described below — shown collapsed in POC)    ║
║                                                                              ║
║  ROLE MANAGEMENT tab (collapsed):                                            ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  Roles: physician | nurse | pharmacist | admin | dpo                │   ║
║  │  + [Create custom role]   [Assign role to user]   [View assignments]│   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║  MAPPING TOOL tab (collapsed):                                               ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  HIS local code → [ LOINC | SNOMED_CT | ICD10 | CPT | CVX | PROD ] │   ║
║  │  Filter: [ pending_review ▾ ]  [+ Add mapping]  [Import CSV]        │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║  MASTER DATA tab (collapsed):                                                ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  [ Checkup Programs ] [ Alert Thresholds ] [ Screening Intervals ]  │   ║
║  │  [ Vaccine Schedule ] [ Safety Rules ]                              │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Alert Detail Drilldown (Panel C — expanded view on click)

```
╔═════════ ALERT DETAIL — anm-20260314-001 ══════════════════════════════════╗
║  User:       Nurse Supawan K.  (usr-nurse-74920183)                        ║
║  Department: Health Checkup Center                                          ║
║  Alert type: high_volume                                                    ║
║  Severity:   🟠 High                                                        ║
║  Triggered:  2026-03-14 02:31 UTC (09:31 ICT)                              ║
║  Status:     Open                                                           ║
║                                                                              ║
║  DETAIL                                                                     ║
║  ────────────────────────────────────────────────────────────────────────── ║
║  Records accessed in session:   18                                          ║
║  User's 30-day baseline avg:     4.2 records/session                       ║
║  Ratio (actual / baseline):      4.3×  [threshold: > 3.0×]                 ║
║  Session ID:                     sess-20260314-74920183-001                 ║
║  Affected patients (masked):                                                ║
║    tok_hmac_562****47  |  tok_hmac_831****12  |  tok_hmac_194****88  |  …  ║
║    (18 patient tokens — click to view full list in audit search)            ║
║                                                                              ║
║  AUDIT TRAIL FOR THIS SESSION                                               ║
║  ────────────────────────────────────────────────────────────────────────── ║
║  [View all 18 audit log entries for session sess-20260314-74920183-001 ↗]   ║
║                                                                              ║
║  RESOLUTION                                                                 ║
║  Status:  [ Open  ▾ ]   → [ Acknowledge ]  [ Resolve ]                     ║
║  Note:    [__________________________ Required to mark Resolved ___________] ║
║                                                                              ║
║  Hash chain integrity:  ✓ VALID  (prev_entry_hash verified)                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Audit Log Row Drilldown (Panel D — expanded view on click)

```
╔═════════ AUDIT LOG ENTRY — alog-20260311-001847 ═══════════════════════════╗
║  Entry ID:    alog-20260311-001847                                          ║
║  Chain hash:  a3f29d1b7c0e4f82...d7e  ✓ (verified against prev entry)      ║
║                                                                              ║
║  WHO    Dr. Arisa Thanapon  (usr-dr-98102847)  |  Physician  |  Internal Med║
║  WHEN   2026-03-11 15:42:17 ICT  (08:42:17 UTC)                            ║
║  WHERE  recommendation-dashboard-ui  |  web_browser  |  IP: [hashed]       ║
║  WHAT   View  →  RecommendationOutput  |  Patient: tok_hmac_562****47      ║
║         Model: claude-3-5-sonnet  |  Template: claude-3-5::v2              ║
║         Latency: 4,812 ms  |  Safety Validator: ✓ pass                     ║
║  WHY    annual_checkup_rec  |  "Annual checkup recommendation — patient    ║
║         initiated"                                                           ║
║                                                                              ║
║  Retention expires: 2029-03-11                                              ║
║  [ ← Back to search results ]                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Field-to-Contract Mapping

### Panel B — Live Metrics Bar

| UI Element | Value | Source Contract | Source Field |
|-----------|-------|----------------|--------------|
| Active Users | 7 | access-monitoring-contract | `MonitoringSnapshot.active_users_now` |
| Sessions Today | 43 | access-monitoring-contract | `MonitoringSnapshot.sessions_today` |
| Records Today | 118 | access-monitoring-contract | `MonitoringSnapshot.patient_records_accessed_today` |
| Alert count 🔴 | 0 | access-monitoring-contract | `MonitoringSnapshot.alert_counts.critical` |
| Alert count 🟠 | 2 | access-monitoring-contract | `MonitoringSnapshot.alert_counts.high` |
| Alert count 🟡 | 5 | access-monitoring-contract | `MonitoringSnapshot.alert_counts.medium` |
| Alert count 🟢 | 11 | access-monitoring-contract | `MonitoringSnapshot.alert_counts.low` |
| AI Recommendations | 31 | access-monitoring-contract | `MonitoringSnapshot.ai_recommendations_generated_today` |
| Safety Validator Failures | 0 ✓ | access-monitoring-contract | `MonitoringSnapshot.safety_validator_failures_today` |
| Last refreshed timestamp | 2026-03-14 14:00 ICT | access-monitoring-contract | `MonitoringSnapshot.snapshot_at` (converted to ICT) |

### Panel C — Anomaly Alerts

| UI Element | Value | Source Contract | Source Field |
|-----------|-------|----------------|--------------|
| Open alerts count | 18 total | access-monitoring-contract | `AnomalyAlert[status=Open].length` |
| Row 1: severity badge | 🟠H (High) | access-monitoring-contract | `AnomalyAlert[0].severity` |
| Row 1: user name | Supawan K. | access-monitoring-contract | `AnomalyAlert[0].user_display_name` |
| Row 1: alert type | vol (high_volume) | access-monitoring-contract | `AnomalyAlert[0].alert_type` |
| Row 1: trigger time | 02:31 | access-monitoring-contract | `AnomalyAlert[0].triggered_at` (UTC → ICT display) |
| Row 1: detail | 18 rec / avg 4.2 | access-monitoring-contract | `AnomalyAlert[0].detail.session_record_count`, `.baseline_avg` |
| Row 1: status | Open → Acknowledge | access-monitoring-contract | `AnomalyAlert[0].status` = "Open" |
| Row 2: severity | 🟠H | access-monitoring-contract | `AnomalyAlert[1].severity` |
| Row 2: user | Prasert T. | access-monitoring-contract | `AnomalyAlert[1].user_display_name` |
| Row 2: type | dept (out_of_department) | access-monitoring-contract | `AnomalyAlert[1].alert_type` |
| Row 2: detail | Cardiology (base: CheckUp) | access-monitoring-contract | `AnomalyAlert[1].detail.patient_department`, `user baseline.primary_department_affinity` |
| Row 3: severity | 🟡M (Medium) | access-monitoring-contract | `AnomalyAlert[2].severity` |
| Row 3: user | Nattaya P. | access-monitoring-contract | `AnomalyAlert[2].user_display_name` |
| Row 3: type | hours (off_hours) | access-monitoring-contract | `AnomalyAlert[2].alert_type` |
| Row 3: detail | Off-hrs: 23:58 (08–17) | access-monitoring-contract | `AnomalyAlert[2].detail.access_hour_ict`, `user baseline.typical_access_hour_range` |
| Resolution log | 3 resolved, 2 false-pos | access-monitoring-contract | `AnomalyAlert[status=Resolved].length` for today (system-computed) |
| Alert detail: ratio | 4.3× (threshold 3.0×) | access-monitoring-contract | `AnomalyAlert.detail.ratio`, `.threshold` |
| Alert detail: session ID | sess-20260314-74920183-001 | access-monitoring-contract | `AnomalyAlert.detail.session_id` |
| Alert detail: patient tokens | tok_hmac_562****47 … | access-monitoring-contract | `AnomalyAlert.detail.affected_patient_tokens_masked[]` |
| Alert detail: hash chain | ✓ VALID | access-monitoring-contract | verified: `AuditLogEntry.sha256_hash` + `prev_entry_hash` chain integrity |
| Resolution status dropdown | Open → Acknowledge → Resolve | access-monitoring-contract | `AnomalyAlert.status` enum lifecycle |
| Resolution note field | Required for Resolved | access-monitoring-contract | `AnomalyAlert.resolution_note` (non-null required for status=Resolved) |

### Panel D — Audit Log Search

| UI Element | Value | Source Contract | Source Field |
|-----------|-------|----------------|--------------|
| Filter: User ID | text input | access-monitoring-contract | `search_audit_logs.filters.user_id` |
| Filter: Patient token prefix | text input (min 8 chars) | access-monitoring-contract | `search_audit_logs.filters.patient_token_prefix` |
| Filter: Date from | 2026-03-01 | access-monitoring-contract | `search_audit_logs.filters.date_from` |
| Filter: Date to | 2026-03-14 | access-monitoring-contract | `search_audit_logs.filters.date_to` |
| Filter: Action type | All / View / Generate / Export / Admin | access-monitoring-contract | `search_audit_logs.filters.action_type` |
| Filter: Resource type | All / RecommendationOutput / … | access-monitoring-contract | `search_audit_logs.filters.resource_type` |
| Results count | 24 entries | access-monitoring-contract | `search_audit_logs response.total_matches` |
| Row 1: time | 15:42 ICT | access-monitoring-contract | `AuditLogEntry.when.local_timestamp_ict` |
| Row 1: who | Dr. Arisa | access-monitoring-contract | `AuditLogEntry.who.user_display_name` |
| Row 1: what | View | access-monitoring-contract | `AuditLogEntry.what.action_type` |
| Row 1: patient | 562**** | access-monitoring-contract | `AuditLogEntry.what.patient_token_masked` |
| Row 2: who | Nrs. Supwn | access-monitoring-contract | `AuditLogEntry.who.user_display_name` |
| Row 2: what | Export | access-monitoring-contract | `AuditLogEntry.what.action_type` |
| Row 3: what | Gen (Generate) | access-monitoring-contract | `AuditLogEntry.what.action_type` = "Generate" |
| Row 4: who | Admin | access-monitoring-contract | `AuditLogEntry.who.user_role` = "admin" |
| Row 4: what | Admin | access-monitoring-contract | `AuditLogEntry.what.action_type` = "Admin" |
| Row 4: resource | MasterData | access-monitoring-contract | `AuditLogEntry.what.resource_type` = "MasterData" |
| Row 4: patient | — | access-monitoring-contract | `AuditLogEntry.what.patient_token_masked` = null (Admin actions have no patient) |
| Entry detail: WHO | Dr. Arisa Thanapon, Physician, Internal Med | access-monitoring-contract | `AuditLogEntry.who.user_display_name`, `.user_role`, `.department` |
| Entry detail: WHEN | 2026-03-11 15:42:17 ICT | access-monitoring-contract | `AuditLogEntry.when.local_timestamp_ict` |
| Entry detail: WHERE | recommendation-dashboard-ui, web_browser | access-monitoring-contract | `AuditLogEntry.where.service_id`, `.user_agent_class` |
| Entry detail: WHAT | View, RecommendationOutput, 562****, claude-3-5-sonnet, 4812ms, ✓ pass | access-monitoring-contract | `AuditLogEntry.what.{action_type, resource_type, patient_token_masked, model_id, latency_ms, safety_validator_result}` |
| Entry detail: WHY | annual_checkup_rec | access-monitoring-contract | `AuditLogEntry.why.indication_code` |
| Entry detail: retention | 2029-03-11 | access-monitoring-contract | `AuditLogEntry.retention_expiry` |
| Chain hash verification | ✓ verified | access-monitoring-contract | `AuditLogEntry.sha256_hash` verified against computed hash of content fields |
| Export CSV / PDF | triggers Export action | access-monitoring-contract | logged as `action_type: Export, resource_type: AuditLog` |

### Panel E — Navigation Tabs (secondary features)

| Tab | What it manages | Source Contract | Sub-schema |
|-----|----------------|----------------|-----------|
| Role Management | `Role` records + `UserRoleAssignment` records | access-monitoring-contract | Sub-schema 4: RBAC Data Model |
| Mapping Tool | `MappingEntry` records (local ↔ LOINC/SNOMED/ICD10/CPT/CVX/NAVAVEJ_PRODUCT) | access-monitoring-contract | Sub-schema 5: Mapping Table Schema |
| Master Data | `checkup_program`, `alert_threshold`, `screening_interval`, `vaccine_schedule`, `safety_rule` | access-monitoring-contract | Sub-schema 6: Master Data Record Types |

---

## Design Notes

### Role-Based Access to This Screen

Only `admin` and `dpo` roles can access Screen 3. Within Screen 3, there is an access distinction:

| Feature | Admin | DPO |
|---------|-------|-----|
| Live metrics (panel B) | ✓ | ✓ |
| Anomaly alerts (panel C) | ✓ | — (not shown) |
| Audit log search (panel D) | ✓ | ✓ |
| Role Management tab | ✓ | — |
| Mapping Tool tab | ✓ | — |
| Master Data tab | ✓ | — |

This access boundary is enforced by the Admin API (role check per `access-monitoring-contract.md §4 RBAC`). The DPO view shows panels B and D only — the anomaly alerts and admin tabs are hidden.

### Hash Chain Display

The hash chain verification badge (`✓ VALID` or `⚠ CHAIN BROKEN`) in the alert detail drilldown is a frontend verification. The client recomputes `sha256_hash` from the displayed content fields and checks it against the stored hash, then checks that `prev_entry_hash` matches the preceding entry's hash. A broken chain automatically triggers a `Critical` anomaly alert of type `integrity_violation`.

### Anomaly Alert Lifecycle

```
Open → (Admin acknowledges) → Acknowledged → (Admin resolves + note) → Resolved
         [Acknowledge btn]                    [Resolve btn + required note field]
```

Once `Resolved`, the alert record is immutable — it remains in the audit trail with the resolution note and who resolved it.

### Auto-Refresh Behaviour

The monitoring snapshot (panel B) and open alert count refresh every 60 seconds by default (configurable in Master Data `safety_rule` record `monitoring_refresh_interval`). The audit log results do not auto-refresh — they show the result set at search time.

### POC Scope Notes

- The Mapping Tool and Master Data tabs are shown as navigation affordances. In the POC, they present the data schema in list form; the full CRUD management UI is a post-POC implementation item.
- The "Export results: CSV / PDF" button generates a file of the filtered audit log entries. This Export action is itself logged (`action_type: Export, resource_type: AuditLog`) — creating an audit record of the audit export.
- The hash chain integrity check requires access to the full sequential audit log — in the POC, this is demonstrated with the Somchai W. sample entries from `access-monitoring-contract.md §1a`.
