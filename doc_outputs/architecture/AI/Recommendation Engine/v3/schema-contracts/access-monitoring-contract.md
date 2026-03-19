# Access Monitoring Contract
## Smart Health Checkup Recommendation Dashboard — Admin / DPO Dashboard Schema Specification

**Version:** 1.0
**Date:** 2026-03-14
**Audience:** Admin Dashboard UI implementation team, Backend Audit Logger implementation team, DPO (Data Protection Officer), Security/Compliance team
**Depends on:** `component-inventory-solution-approach.md` (§2.7 Audit Logger), TOR §3.4, TOR §5.3
**Related contracts:** `signal-store-contract.md`, `recommendation-output-schema.md`

---

## Overview

The Access Monitoring Dashboard is the **Admin / DPO-facing view** of the system. It fulfils PDPA compliance obligations and the security requirements in TOR §3.4 and §5.3. This document defines all data structures needed to build Screen 3 of the POC.

The dashboard is served by a separate **Admin API** — distinct from the MCP Server and Inference Orchestrator. It has its own authentication layer (admin-scoped SMART on FHIR token + RBAC role check).

```
┌────────────────────────────────────────────┐
│  Admin Dashboard (Screen 3)                │
│  Audience: Admin, DPO                      │
│                                            │
│  ┌──────────────┐  ┌─────────────────────┐ │
│  │ Live Metrics │  │ Anomaly Alert Table │ │
│  └──────────────┘  └─────────────────────┘ │
│  ┌──────────────────────────────────────┐  │
│  │ Audit Log Search Panel               │  │
│  └──────────────────────────────────────┘  │
│  ┌────────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Role Mgmt  │  │Mapping  │  │ Master  │ │
│  │ (tab)      │  │Tool(tab)│  │Data(tab)│ │
│  └────────────┘  └─────────┘  └─────────┘ │
└────────────────────────────────────────────┘
              ↑
        Admin API
              ↑
   ┌──────────────────────┐
   │  Audit Log Store     │  (append-only, tamper-evident)
   │  Anomaly Engine      │  (rolling baseline + alert generation)
   │  RBAC Store          │
   │  Mapping Table Store │
   │  Master Data Store   │
   └──────────────────────┘
```

This contract covers **6 sub-schemas**, each corresponding to a feature area in TOR §3.4:

| # | Sub-schema | TOR Reference | POC Screen |
|---|-----------|--------------|------------|
| 1 | Audit Log Record + Search API | §3.4.3, §5.3 | Screen 3 — Audit Log Panel |
| 2 | Anomaly Detection | §3.4.2 | Screen 3 — Alert Table |
| 3 | Real-Time Monitoring Metrics | §3.4.1 | Screen 3 — Live Metrics Bar |
| 4 | RBAC Data Model | §3.4.4 | Screen 3 — Role Mgmt tab |
| 5 | Mapping Table Schema | §3.4.5 | Screen 3 — Mapping Tool tab |
| 6 | Master Data Record Types | §3.4.6 | Screen 3 — Master Data tab |

---

## Sub-schema 1 — Audit Log Record + Search API

### 1a. Audit Log Record

Every action taken by any user (Physician, Nurse, Pharmacist, Admin, DPO) against any AI-generated output, patient signal, or admin resource is written as an immutable audit log entry. The Audit Logger (component-inventory §2.7) is the sole writer.

**Tamper-evidence mechanism:** Each entry includes a `sha256_hash` of its own content fields and a `prev_entry_hash` linking to the immediately preceding entry for this user. This forms a per-user hash chain — any deletion or modification breaks the chain and is detectable.

**Retention:** 3 years minimum (PDPA §40; adjustable via `retention_expiry`).

#### Example Audit Log Entry — Physician views Somchai W.'s recommendation

```json
{
  "entry_id": "alog-20260311-001847",
  "sha256_hash": "a3f29d1b7c0e4f82a9d3c5b17e0f4a28b6c1d9e3f5a7b2c8d4e6f0a1b3c5d7e",
  "prev_entry_hash": "f7e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4",

  "who": {
    "user_id": "usr-dr-98102847",
    "user_display_name": "Dr. Arisa Thanapon",
    "user_role": "physician",
    "department": "Internal Medicine",
    "smart_fhir_session_token_hash": "sha256_of_session_token_not_token_itself"
  },

  "when": {
    "iso_timestamp_utc": "2026-03-11T08:42:17Z",
    "local_timestamp_ict": "2026-03-11T15:42:17+07:00"
  },

  "where": {
    "service_id": "recommendation-dashboard-ui",
    "source_ip_hash": "sha256_of_source_ip",
    "request_id": "req-20260311-084217-001",
    "user_agent_class": "web_browser"
  },

  "what": {
    "action_type": "View",
    "resource_type": "RecommendationOutput",
    "patient_token": "tok_hmac_56291047",
    "patient_token_masked": "tok_hmac_562****47",
    "prompt_hash": "sha256_of_prompt_sent_to_ai",
    "context_hash": "sha256_of_mcp_context_assembled",
    "response_hash": "sha256_of_ai_response",
    "model_id": "claude-sonnet-4-6",
    "template_version": "v3.1",
    "latency_ms": 2847,
    "safety_validator_result": "pass",
    "recommendation_source": "AI"
  },

  "why": {
    "request_context": "Annual checkup recommendation — patient initiated",
    "indication_code": "annual_checkup_rec"
  },

  "retention_expiry": "2029-03-11"
}
```

#### Example Audit Log Entry — Export action

```json
{
  "entry_id": "alog-20260311-003291",
  "sha256_hash": "b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4",
  "prev_entry_hash": "a3f29d1b7c0e4f82a9d3c5b17e0f4a28b6c1d9e3f5a7b2c8d4e6f0a1b3c5d7e",

  "who": {
    "user_id": "usr-nurse-74920183",
    "user_display_name": "Nurse Supawan K.",
    "user_role": "nurse",
    "department": "Health Checkup Center",
    "smart_fhir_session_token_hash": "sha256_of_session_token"
  },

  "when": {
    "iso_timestamp_utc": "2026-03-11T09:15:04Z",
    "local_timestamp_ict": "2026-03-11T16:15:04+07:00"
  },

  "where": {
    "service_id": "recommendation-dashboard-ui",
    "source_ip_hash": "sha256_of_source_ip",
    "request_id": "req-20260311-091504-002",
    "user_agent_class": "web_browser"
  },

  "what": {
    "action_type": "Export",
    "resource_type": "RecommendationOutput",
    "patient_token": "tok_hmac_56291047",
    "patient_token_masked": "tok_hmac_562****47",
    "prompt_hash": null,
    "context_hash": null,
    "response_hash": null,
    "model_id": null,
    "template_version": null,
    "latency_ms": 312,
    "safety_validator_result": null,
    "recommendation_source": null
  },

  "why": {
    "request_context": "Printed for patient counselling session",
    "indication_code": "patient_counselling_export"
  },

  "retention_expiry": "2029-03-11"
}
```

#### JSON Schema — Audit Log Entry

```jsonschema
{
  "$schema": "https://json-schema.org/draft/2020-12",
  "$id": "admin-api/audit-log/entry",
  "type": "object",
  "required": ["entry_id", "sha256_hash", "prev_entry_hash", "who", "when", "where", "what", "why", "retention_expiry"],
  "properties": {

    "entry_id": {
      "type": "string",
      "description": "Globally unique entry ID. Format: alog-{YYYYMMDD}-{sequence}."
    },
    "sha256_hash": {
      "type": "string",
      "description": "SHA-256 hash of all content fields in this entry (excluding sha256_hash itself). Enables tamper detection."
    },
    "prev_entry_hash": {
      "type": "string",
      "description": "sha256_hash of the immediately preceding audit log entry for this user (user_id chain). First entry for a user has a sentinel value of 64 zero characters."
    },

    "who": {
      "type": "object",
      "required": ["user_id", "user_role", "department"],
      "properties": {
        "user_id":                      { "type": "string", "description": "Internal user identifier. Never contains Thai national ID or personal identity." },
        "user_display_name":            { "type": "string", "description": "Display name for audit log readability. DPO-visible." },
        "user_role":                    { "type": "string", "enum": ["physician", "nurse", "pharmacist", "admin", "dpo"], "description": "Role at time of action." },
        "department":                   { "type": "string" },
        "smart_fhir_session_token_hash":{ "type": "string", "description": "SHA-256 of the SMART on FHIR session token — never the token itself." }
      }
    },

    "when": {
      "type": "object",
      "required": ["iso_timestamp_utc"],
      "properties": {
        "iso_timestamp_utc":    { "type": "string", "format": "date-time", "description": "Canonical timestamp in UTC. Used for all sorting and retention calculations." },
        "local_timestamp_ict":  { "type": "string", "description": "Thailand time (UTC+7) for human readability in audit reports." }
      }
    },

    "where": {
      "type": "object",
      "required": ["service_id", "request_id"],
      "properties": {
        "service_id":       { "type": "string", "description": "Originating service/component name." },
        "source_ip_hash":   { "type": "string", "description": "SHA-256 of the client IP address. Original IP is never stored." },
        "request_id":       { "type": "string", "description": "Unique request correlation ID — traceable across service logs." },
        "user_agent_class": { "type": "string", "enum": ["web_browser", "mobile_app", "api_client", "system"], "description": "Broad device/access category." }
      }
    },

    "what": {
      "type": "object",
      "required": ["action_type", "resource_type", "patient_token_masked"],
      "properties": {
        "action_type":             { "type": "string", "enum": ["View", "Generate", "Export", "Admin"], "description": "View=read-only access; Generate=AI recommendation triggered; Export=PDF/print; Admin=master data or RBAC change." },
        "resource_type":          { "type": "string", "enum": ["RecommendationOutput", "AuditLog", "MasterData", "MappingTable", "UserRole"], "description": "What was accessed or modified." },
        "patient_token":          { "type": "string", "description": "Full pseudonymous patient token. Stored only in the secure audit log — not displayed in UI by default." },
        "patient_token_masked":   { "type": "string", "description": "Partial mask for UI display (first 10 and last 2 chars, middle replaced with ****)." },
        "prompt_hash":            { "type": ["string", "null"], "description": "SHA-256 of the AI prompt sent. Non-null only for action_type=Generate." },
        "context_hash":           { "type": ["string", "null"], "description": "SHA-256 of the assembled MCP context. Non-null only for action_type=Generate." },
        "response_hash":          { "type": ["string", "null"], "description": "SHA-256 of the AI response received. Non-null only for action_type=Generate." },
        "model_id":               { "type": ["string", "null"] },
        "template_version":       { "type": ["string", "null"] },
        "latency_ms":             { "type": ["integer", "null"], "description": "End-to-end request latency in milliseconds." },
        "safety_validator_result":{ "type": ["string", "null"], "enum": ["pass", "fail", "skipped", null] },
        "recommendation_source":  { "type": ["string", "null"], "enum": ["AI", "RuleBased", null] }
      }
    },

    "why": {
      "type": "object",
      "required": ["indication_code"],
      "properties": {
        "request_context":  { "type": "string", "description": "Free-text context captured from UI or API call. For human audit readability." },
        "indication_code":  { "type": "string", "description": "Structured code for the business reason. Enables programmatic filtering." }
      }
    },

    "retention_expiry": {
      "type": "string",
      "format": "date",
      "description": "Date after which this entry may be purged. Computed as created_date + 3 years (PDPA §40 minimum). Admin-configurable minimum."
    }
  }
}
```

#### Field Dictionary — Audit Log

| Field | Type | Description |
|-------|------|-------------|
| `entry_id` | string | Unique entry identifier. Format: `alog-{YYYYMMDD}-{6-digit-seq}`. |
| `sha256_hash` | string | Hash of all content fields (excluding itself). Recomputable — breaking chain = tamper detected. |
| `prev_entry_hash` | string | Links to previous entry for this user. Sentinel for first entry: 64 zeros. |
| `who.user_role` | enum | physician / nurse / pharmacist / admin / dpo |
| `who.smart_fhir_session_token_hash` | string | Hashed session token — proves the SMART on FHIR session was valid at time of access without storing the credential. |
| `where.source_ip_hash` | string | Hashed IP address. Raw IP is never stored — only the hash (PDPA compliance). |
| `what.action_type` | enum | View / Generate / Export / Admin |
| `what.patient_token_masked` | string | Safe for UI display. Full token is stored in the secure log only. |
| `what.prompt_hash` | string\|null | Non-null only for Generate actions. The actual prompt is never stored — only its hash. |
| `why.indication_code` | string | Machine-readable reason code. Used for audit search filtering. |
| `retention_expiry` | date | Auto-calculated at write time. Configurable minimum via Master Data `admin` settings. |

---

### 1b. Audit Log Search API — `search_audit_logs(filters)`

```
POST /admin/audit-logs/search
Authorization: Bearer {admin_scoped_smart_fhir_token}
Required role: admin OR dpo
```

#### Request Body

```json
{
  "filters": {
    "user_id":       "usr-dr-98102847",
    "patient_token_prefix": "tok_hmac_562",
    "date_from":     "2026-03-01",
    "date_to":       "2026-03-14",
    "action_type":   "View",
    "resource_type": "RecommendationOutput"
  },
  "pagination": {
    "page":     1,
    "per_page": 50
  },
  "sort": {
    "field": "when.iso_timestamp_utc",
    "order": "desc"
  }
}
```

#### Response Envelope

```json
{
  "total_matches": 24,
  "page": 1,
  "per_page": 50,
  "entries": [ /* array of AuditLogEntry objects */ ],
  "query_id": "qry-20260314-001",
  "searched_at": "2026-03-14T07:00:00Z"
}
```

#### Filter Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Exact match on `who.user_id`. |
| `patient_token_prefix` | string | Prefix match on `what.patient_token` (min 8 chars). Allows DPO to find all access to a patient without knowing the full token. |
| `date_from` / `date_to` | date | Inclusive range on `when.iso_timestamp_utc`. |
| `action_type` | enum | View / Generate / Export / Admin |
| `resource_type` | enum | RecommendationOutput / AuditLog / MasterData / MappingTable / UserRole |
| `department` | string | Filters by `who.department`. |
| `safety_validator_result` | enum | `fail` filter surfaces all recommendation safety violations. |

---

## Sub-schema 2 — Anomaly Detection

The Anomaly Engine runs as a background service. It ingests the audit log stream and computes a **rolling 30-day behavioral baseline** per user, then emits `AnomalyAlert` records when deviation thresholds are crossed.

### User Baseline Model

A per-user baseline is recomputed nightly from the preceding 30 calendar days of audit log entries.

```json
{
  "user_id": "usr-nurse-74920183",
  "baseline_window_days": 30,
  "computed_at": "2026-03-14T00:00:00Z",
  "metrics": {
    "avg_records_per_session": 4.2,
    "avg_sessions_per_day": 1.8,
    "typical_access_hour_range": { "start_hour_ict": 8, "end_hour_ict": 17 },
    "primary_department_affinity": "Health Checkup Center",
    "top_access_patterns": ["View", "Export"]
  }
}
```

### Anomaly Signal Types (3)

| Signal | Trigger Condition | Default Severity |
|--------|------------------|-----------------|
| `high_volume` | Records accessed in session > 3× `avg_records_per_session` | High |
| `out_of_department` | Patient's registered department ≠ user's `primary_department_affinity` AND session record count > 3 | Medium |
| `off_hours` | Access hour (ICT) outside `[start_hour_ict - 1, end_hour_ict + 1]` range AND access count > 1 | Low |

Severity is admin-configurable via Master Data `safety_rule` records.

### AnomalyAlert Record

```json
{
  "alert_id": "anm-20260314-001",
  "user_id": "usr-nurse-74920183",
  "user_display_name": "Nurse Supawan K.",
  "department": "Health Checkup Center",
  "alert_type": "high_volume",
  "severity": "High",
  "triggered_at": "2026-03-14T02:31:00Z",
  "detail": {
    "session_record_count": 18,
    "baseline_avg": 4.2,
    "ratio": 4.3,
    "threshold": 3.0,
    "session_id": "sess-20260314-74920183-001",
    "affected_patient_tokens_masked": ["tok_hmac_562****47", "tok_hmac_831****12"]
  },
  "status": "Open",
  "acknowledged_by": null,
  "acknowledged_at": null,
  "resolved_by": null,
  "resolved_at": null,
  "resolution_note": null
}
```

#### JSON Schema — AnomalyAlert

```jsonschema
{
  "$schema": "https://json-schema.org/draft/2020-12",
  "$id": "admin-api/anomaly/alert",
  "type": "object",
  "required": ["alert_id", "user_id", "alert_type", "severity", "triggered_at", "detail", "status"],
  "properties": {
    "alert_id":             { "type": "string", "description": "Unique alert ID. Format: anm-{YYYYMMDD}-{seq}." },
    "user_id":              { "type": "string" },
    "user_display_name":    { "type": "string" },
    "department":           { "type": "string" },
    "alert_type":           { "type": "string", "enum": ["high_volume", "out_of_department", "off_hours"] },
    "severity":             { "type": "string", "enum": ["Low", "Medium", "High", "Critical"], "description": "Admin-configurable thresholds determine severity level." },
    "triggered_at":         { "type": "string", "format": "date-time" },
    "detail": {
      "type": "object",
      "description": "Signal-specific detail object. Fields depend on alert_type.",
      "properties": {
        "session_record_count":             { "type": "integer" },
        "baseline_avg":                     { "type": "number" },
        "ratio":                            { "type": "number", "description": "session_record_count / baseline_avg" },
        "threshold":                        { "type": "number", "description": "Configured multiplier that was exceeded (default 3.0 for high_volume)." },
        "session_id":                       { "type": "string" },
        "affected_patient_tokens_masked":   { "type": "array", "items": { "type": "string" } },
        "access_hour_ict":                  { "type": "integer", "description": "Present for off_hours alerts." },
        "patient_department":               { "type": "string", "description": "Present for out_of_department alerts." }
      }
    },
    "status":           { "type": "string", "enum": ["Open", "Acknowledged", "Resolved"] },
    "acknowledged_by":  { "type": ["string", "null"] },
    "acknowledged_at":  { "type": ["string", "null"], "format": "date-time" },
    "resolved_by":      { "type": ["string", "null"] },
    "resolved_at":      { "type": ["string", "null"], "format": "date-time" },
    "resolution_note":  { "type": ["string", "null"], "description": "Free-text note written by admin/DPO when resolving. Required for Resolved status." }
  }
}
```

#### Field Dictionary — AnomalyAlert

| Field | Type | Description |
|-------|------|-------------|
| `alert_type` | enum | `high_volume` / `out_of_department` / `off_hours` |
| `severity` | enum | Low / Medium / High / Critical. Threshold-to-severity mapping is admin-configurable in Master Data. |
| `detail.ratio` | number | Computed at alert generation time. `session_record_count / baseline_avg`. |
| `detail.threshold` | number | Configured multiplier that was exceeded. Default 3.0 (admin-adjustable). |
| `status` | enum | Open → Acknowledged → Resolved lifecycle. |
| `resolution_note` | string\|null | Required (non-null) when status transitions to Resolved. |

---

## Sub-schema 3 — Real-Time Monitoring Metrics

Served by `GET /admin/monitoring/snapshot` — refreshes every 60 seconds (configurable).

### MonitoringSnapshot Record

```json
{
  "snapshot_at": "2026-03-14T07:00:00Z",
  "refresh_interval_seconds": 60,
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
  "top_active_departments": [
    { "department": "Health Checkup Center", "active_users": 4 },
    { "department": "Internal Medicine",      "active_users": 2 },
    { "department": "Cardiology",             "active_users": 1 }
  ]
}
```

#### JSON Schema — MonitoringSnapshot

```jsonschema
{
  "$schema": "https://json-schema.org/draft/2020-12",
  "$id": "admin-api/monitoring/snapshot",
  "type": "object",
  "required": ["snapshot_at", "active_users_now", "sessions_today", "patient_records_accessed_today", "alert_counts"],
  "properties": {
    "snapshot_at":                          { "type": "string", "format": "date-time" },
    "refresh_interval_seconds":             { "type": "integer", "default": 60 },
    "active_users_now":                     { "type": "integer", "description": "Users with an active SMART on FHIR session in the past 5 minutes." },
    "sessions_today":                       { "type": "integer", "description": "Total sessions initiated since midnight UTC." },
    "patient_records_accessed_today":       { "type": "integer", "description": "Distinct patient_token values accessed via any MCP tool today." },
    "ai_recommendations_generated_today":   { "type": "integer", "description": "Count of action_type=Generate audit log entries today." },
    "alert_counts": {
      "type": "object",
      "required": ["critical", "high", "medium", "low"],
      "properties": {
        "critical": { "type": "integer" },
        "high":     { "type": "integer" },
        "medium":   { "type": "integer" },
        "low":      { "type": "integer" }
      },
      "description": "Count of Open AnomalyAlert records by severity."
    },
    "safety_validator_failures_today": { "type": "integer", "description": "Count of audit log entries where safety_validator_result=fail today." },
    "top_active_departments": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "department":    { "type": "string" },
          "active_users":  { "type": "integer" }
        }
      }
    }
  }
}
```

---

## Sub-schema 4 — RBAC Data Model

### Role Record

```json
{
  "role_id": "role-physician",
  "role_name": "Physician",
  "description": "Treating physician with full read access to recommendation outputs for their department's patients.",
  "permissions": [
    { "resource_type": "RecommendationOutput", "actions": ["View", "Generate", "Export"] },
    { "resource_type": "AuditLog",             "actions": [] }
  ],
  "is_system_role": true,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

### Predefined System Roles

| Role | resource_type: RecommendationOutput | resource_type: AuditLog | resource_type: MasterData | resource_type: MappingTable |
|------|--------------------------------------|------------------------|--------------------------|----------------------------|
| `physician` | View, Generate, Export | — | — | — |
| `nurse` | View, Export | — | — | — |
| `pharmacist` | View | — | — | — |
| `admin` | View, Generate, Export | View | View, Edit | View, Edit |
| `dpo` | — | View | — | — |

> `—` = empty actions array (no access). Enforced at Admin API and MCP Server middleware.

### UserRoleAssignment Record

```json
{
  "assignment_id": "ura-001",
  "user_id": "usr-dr-98102847",
  "user_display_name": "Dr. Arisa Thanapon",
  "role_id": "role-physician",
  "department": "Internal Medicine",
  "assigned_by": "usr-admin-00001",
  "assigned_at": "2026-01-15T09:00:00Z",
  "expires_at": null,
  "is_active": true
}
```

#### JSON Schema — Role

```jsonschema
{
  "$schema": "https://json-schema.org/draft/2020-12",
  "$id": "admin-api/rbac/role",
  "type": "object",
  "required": ["role_id", "role_name", "permissions", "is_system_role"],
  "properties": {
    "role_id":         { "type": "string" },
    "role_name":       { "type": "string" },
    "description":     { "type": "string" },
    "permissions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["resource_type", "actions"],
        "properties": {
          "resource_type": { "type": "string", "enum": ["RecommendationOutput", "AuditLog", "MasterData", "MappingTable", "UserRole"] },
          "actions":       { "type": "array", "items": { "type": "string", "enum": ["View", "Generate", "Export", "Edit"] } }
        }
      }
    },
    "is_system_role":  { "type": "boolean", "description": "System roles cannot be deleted. Admin-created custom roles have is_system_role=false." },
    "created_at":      { "type": "string", "format": "date-time" },
    "updated_at":      { "type": "string", "format": "date-time" }
  }
}
```

---

## Sub-schema 5 — Mapping Table Schema

The Mapping Tool lets Admins manage bidirectional code translations between the hospital's HIS internal codes and standard vocabularies (LOINC, SNOMED CT, ICD-10, CPT, CVX, Navavej product codes).

This is the same mapping layer referenced in `fhir-discovery-report.md` §4 (FHIR mapping gaps) — the tool provides a UI to manage these mappings without redeploying the pipeline.

### MappingEntry Record

```json
{
  "mapping_id": "map-001",
  "local_code": "HIS-LAB-0042",
  "local_label": "น้ำตาลในเลือด (งดอาหาร)",
  "target_system": "LOINC",
  "target_code": "1558-6",
  "target_label": "Fasting glucose [Mass/volume] in Serum or Plasma",
  "mapping_type": "exact",
  "status": "active",
  "validated_by": "usr-admin-00001",
  "validated_at": "2026-02-01T09:00:00Z",
  "last_updated_by": "usr-admin-00001",
  "last_updated_at": "2026-02-01T09:00:00Z",
  "notes": "Primary FBS mapping. Covers both tubes (SST and NaF)."
}
```

#### JSON Schema — MappingEntry

```jsonschema
{
  "$schema": "https://json-schema.org/draft/2020-12",
  "$id": "admin-api/mapping-table/entry",
  "type": "object",
  "required": ["mapping_id", "local_code", "local_label", "target_system", "target_code", "target_label", "mapping_type", "status"],
  "properties": {
    "mapping_id":       { "type": "string" },
    "local_code":       { "type": "string", "description": "HIS-internal code (lab order code, diagnosis code, procedure code, or package code)." },
    "local_label":      { "type": "string", "description": "HIS display label. May be in Thai." },
    "target_system":    { "type": "string", "enum": ["LOINC", "SNOMED_CT", "ICD10", "CPT", "CVX", "NAVAVEJ_PRODUCT"], "description": "Standard vocabulary being mapped to." },
    "target_code":      { "type": "string", "description": "Standard code in the target vocabulary." },
    "target_label":     { "type": "string", "description": "Official label in the target vocabulary. In English." },
    "mapping_type":     { "type": "string", "enum": ["exact", "broad", "narrow", "approximate"], "description": "FHIR ConceptMap equivalence type. 'exact' = preferred; others require clinical review." },
    "status":           { "type": "string", "enum": ["active", "pending_review", "deprecated"] },
    "validated_by":     { "type": "string", "description": "Admin user who validated this mapping. Required for status=active." },
    "validated_at":     { "type": ["string", "null"], "format": "date-time" },
    "last_updated_by":  { "type": "string" },
    "last_updated_at":  { "type": "string", "format": "date-time" },
    "notes":            { "type": "string", "description": "Free-text notes for clinical context or known caveats." }
  }
}
```

#### Field Dictionary — MappingEntry

| Field | Type | Description |
|-------|------|-------------|
| `local_code` | string | HIS-internal code. Different HIS systems use different formats — this is the raw code from the source system (OQ-HIS from checkpoint is directly relevant here). |
| `target_system` | enum | LOINC (labs), SNOMED_CT (diagnoses, procedures), ICD10 (diagnoses), CPT (procedures), CVX (vaccines), NAVAVEJ_PRODUCT (package/add-on codes). |
| `mapping_type` | enum | Based on FHIR ConceptMap equivalence. Only `exact` mappings are used by the Data Pipeline without a warning flag. |
| `status` | enum | `pending_review` = imported but not yet validated; `active` = validated and in use; `deprecated` = superseded by another mapping. |

---

## Sub-schema 6 — Master Data Record Types

Admins manage 5 categories of master data that configure the system's clinical logic without requiring code deployment.

### Type 1 — `checkup_program`

Defines which Navavej checkup packages are active and their tier mapping. Directly feeds the Ruleset Store `package_resolution_map`.

```json
{
  "record_type": "checkup_program",
  "program_id": "prog-platinum-men-54",
  "program_name": "Platinum Men (Age 51–55)",
  "tier": "Advanced",
  "gender": "male",
  "age_band_min": 51,
  "age_band_max": 55,
  "navavej_product_code": "CP-PLT-M-5155",
  "price_thb": 8700,
  "is_active": true,
  "effective_from": "2026-04-01",
  "effective_to": null,
  "updated_by": "usr-admin-00001",
  "updated_at": "2026-03-01T00:00:00Z"
}
```

### Type 2 — `alert_threshold`

Lab ULN/LLN overrides for hospital-specific reference ranges. Overrides the defaults in `clinical-guidelines-reference.md` when the hospital uses different lab equipment or population norms.

```json
{
  "record_type": "alert_threshold",
  "threshold_id": "thr-ldl-001",
  "lab_id": "LDL",
  "loinc_code": "2089-1",
  "metric": "LDL Cholesterol",
  "override_uln": 130,
  "override_lln": null,
  "unit": "mg/dL",
  "applies_to_gender": "all",
  "applies_to_age_min": 0,
  "applies_to_age_max": 120,
  "guideline_reference": "ACC/AHA 2018 Cholesterol Guidelines",
  "is_active": true,
  "updated_by": "usr-admin-00001",
  "updated_at": "2026-01-15T00:00:00Z"
}
```

### Type 3 — `screening_interval`

Admin-configurable overrides for screening recurrence intervals. Overrides defaults from `clinical-guidelines-reference.md` (e.g., if hospital policy mandates annual colonoscopy for high-risk patients vs. guideline's 10-year default).

```json
{
  "record_type": "screening_interval",
  "interval_id": "si-colon-001",
  "screening_code": "colonoscopy",
  "label": "Colonoscopy (colorectal cancer screening)",
  "default_interval_years": 10,
  "override_interval_years": 5,
  "applies_to_risk_group": "high_risk_colorectal",
  "guideline_reference": "ACG Colorectal Cancer Screening Guidelines 2021",
  "is_active": true,
  "updated_by": "usr-admin-00001",
  "updated_at": "2026-02-01T00:00:00Z"
}
```

### Type 4 — `vaccine_schedule`

Active vaccine list with CVX codes and admin-configurable age/gender eligibility overrides.

```json
{
  "record_type": "vaccine_schedule",
  "vaccine_id": "vacc-influenza-001",
  "vaccine_name": "Influenza Vaccine (annual)",
  "cvx_code": "141",
  "dose_schedule": "Annual, 1 dose",
  "eligible_age_min": 18,
  "eligible_age_max": 120,
  "eligible_gender": "all",
  "priority_level": "Orange",
  "navavej_product_code": "VAC-FLU-ANNUAL",
  "price_thb": 650,
  "is_active": true,
  "updated_by": "usr-admin-00001",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

### Type 5 — `safety_rule`

Admin-configurable overrides for gender/age eligibility rules and anomaly detection thresholds. Allows clinical customisation without code deployment.

```json
{
  "record_type": "safety_rule",
  "rule_id": "sr-anomaly-high-volume-001",
  "rule_category": "anomaly_threshold",
  "rule_label": "High Volume Access — multiplier threshold",
  "parameter_key": "high_volume_multiplier",
  "parameter_value": "3.0",
  "parameter_type": "float",
  "description": "Sessions where records_accessed > (baseline_avg × this_value) trigger a High severity alert.",
  "is_active": true,
  "updated_by": "usr-admin-00001",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

#### Master Data Common Fields

All 5 master data record types share these base fields:

| Field | Type | Description |
|-------|------|-------------|
| `record_type` | enum | `checkup_program` / `alert_threshold` / `screening_interval` / `vaccine_schedule` / `safety_rule` |
| `is_active` | boolean | Soft-delete flag. Inactive records are excluded from pipeline runs but preserved for audit. |
| `updated_by` | string | Admin `user_id` who last modified this record. |
| `updated_at` | datetime | UTC timestamp of last modification. |
| `effective_from` / `effective_to` | date\|null | Optional validity window. Pipeline applies records where `effective_from ≤ run_date ≤ effective_to` (null `effective_to` = no expiry). |

---

## Admin API — Endpoint Summary

| Method | Path | Required Role | Description |
|--------|------|--------------|-------------|
| `POST` | `/admin/audit-logs/search` | admin, dpo | Search audit log entries |
| `GET` | `/admin/monitoring/snapshot` | admin, dpo | Live metrics snapshot |
| `GET` | `/admin/anomaly/alerts` | admin, dpo | List open anomaly alerts (filterable by severity, status) |
| `PATCH` | `/admin/anomaly/alerts/{alert_id}` | admin | Acknowledge or resolve an alert |
| `GET` | `/admin/rbac/roles` | admin | List all roles |
| `POST` | `/admin/rbac/roles` | admin | Create custom role |
| `PUT` | `/admin/rbac/roles/{role_id}` | admin | Update role permissions |
| `GET` | `/admin/rbac/assignments` | admin | List user role assignments |
| `POST` | `/admin/rbac/assignments` | admin | Assign role to user |
| `DELETE` | `/admin/rbac/assignments/{assignment_id}` | admin | Revoke role assignment |
| `GET` | `/admin/mapping-table` | admin | List mapping entries (filterable by target_system, status) |
| `POST` | `/admin/mapping-table` | admin | Create mapping entry |
| `PUT` | `/admin/mapping-table/{mapping_id}` | admin | Update mapping entry |
| `GET` | `/admin/master-data/{record_type}` | admin | List master data records by type |
| `POST` | `/admin/master-data/{record_type}` | admin | Create master data record |
| `PUT` | `/admin/master-data/{record_type}/{record_id}` | admin | Update master data record |

> All endpoints require a valid admin-scoped SMART on FHIR bearer token. Every request is logged by the Audit Logger (action_type=Admin for write operations, action_type=View for reads).
