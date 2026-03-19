# Discovery

Status: Complete

## Findings

- Monitoring security relied on client-controlled role header and defaulted to admin when header was missing.
- API entrypoints lacked centralized authenticated-context checks for authorization decisions.
- Existing tests validated basic role behavior only and lacked 401/403 coverage for missing auth and missing scope paths.

## Decisions

- Added centralized auth-context dependency with explicit `X-Auth-*` claim headers for POC evidence mode.
- Enforced role + scope checks on `/api` monitoring routes and recommendation/timeline contract routes.
- Applied equivalent recommendation access checks to legacy `/api/v1/clinical` recommendation and audit routes.
- Aligned frontend request headers to auth-context model and removed runtime role impersonation selector from Screen-3 page.
