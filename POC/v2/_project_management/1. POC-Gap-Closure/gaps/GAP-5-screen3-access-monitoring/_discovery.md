# Discovery

Status: Complete

## Contract and API discoveries

- Existing `/api/monitoring-snapshot` and `/api/audit-logs` were narrower than Screen-3 requirements.
- Added fixture-backed Screen-3 data source at `assets/monitoring.json` for snapshot, anomaly, RBAC, mapping, and master data domains.
- Added role-gated endpoints for `/api/monitoring-snapshot`, `/api/audit-logs`, `/api/anomaly-alerts`, `/api/rbac`, `/api/mapping-codes`, and `/api/master-programs`.
- Added admin aliases for contract alignment:
  - `/api/admin/monitoring/snapshot`
  - `/api/admin/audit-logs/search`
  - `/api/admin/anomaly-alerts`
  - `/api/admin/rbac`
  - `/api/admin/mapping-codes`
  - `/api/admin/master-programs`

## Screen-3 implementation discoveries

- Implemented dedicated route `frontend/src/app/access-monitoring/page.tsx` with role selector (admin/dpo).
- Implemented screen panels:
  - Live metrics bar
  - Anomaly alerts panel with acknowledge/resolve demo state
  - Audit log search with row drilldown and client-side hash verification
  - Role management tab
  - Mapping tool tab
  - Master data tab
- Kept `/audit` route as compatibility page rendering the new Screen-3 component.

## Hash verification discovery

- Backend now normalizes audit entries and computes deterministic `sha256_hash` over canonical fields.
- Frontend verifies selected entry hash using stable sorted-key serialization + browser SHA-256 digest.
