# GAP-UI-4 — Auth & Security

**Title:** Remove auth credentials from client-side JS; fix hardcoded physician identity and silent privilege escalation
**Status:** Not started
**Wave:** 1

---

## Objective
Fix four security issues: auth credentials exposed in `NEXT_PUBLIC_*` env vars, a hardcoded physician ID that breaks the audit trail, a raw patient token visible in the UI, and a silent privilege escalation to admin for unknown roles.

## Scope
1. Move `AUTH_USER_ID`, `AUTH_ROLE`, `AUTH_SCOPES` out of `NEXT_PUBLIC_*` env vars — read from a Next.js server-side API route (`/api/auth/context`) instead
2. Replace hardcoded `physician_id: "dr-admin-001"` in `api.ts` with authenticated user ID from auth context
3. Remove `patientToken` from visible display in `TrendTimelineScreen.tsx` header (line 153)
4. In `access-monitoring/page.tsx`: unknown roles show access-denied state rather than silently defaulting to `"admin"`

## Primary Files
- `src/services/api.ts`
- `src/app/access-monitoring/page.tsx`
- `src/components/trend-timeline/TrendTimelineScreen.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
Security, Privacy & Audit 20% · TOR §5.1 / §3.4
