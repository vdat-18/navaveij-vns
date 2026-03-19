# GAP-UI-8 — Crypto Audit Guard

**Title:** Add availability guard and error handling for crypto.subtle hash verification
**Status:** Not started
**Wave:** 1

---

## Objective
Prevent silent failures in the audit log hash verification feature by adding a `crypto.subtle` availability check, a user-facing message for HTTP contexts, and a try/catch error boundary.

## Scope
1. Add `if (!crypto?.subtle)` check before calling `crypto.subtle.digest()` in `AuditLogSearchPanel.tsx`
2. When `crypto.subtle` is unavailable: show inline message "Hash verification requires a secure (HTTPS) connection"
3. Wrap the entire verification logic in `try/catch`; display inline error on exception

## Primary Files
`src/components/access-monitoring/AuditLogSearchPanel.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
Security, Privacy & Audit 20% · TOR §5.3
