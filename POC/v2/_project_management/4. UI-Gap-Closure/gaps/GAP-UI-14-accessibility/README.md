# GAP-UI-14 — Accessibility

**Title:** Add ARIA attributes, fix image component, and add root ErrorBoundary
**Status:** Not started
**Wave:** 3

---

## Objective
Address the four accessibility gaps identified in the audit: missing ARIA landmarks and current-page indicators on the sidebar, an unlabelled search input, a bare `<img>` causing layout shift, and the absence of an error boundary at the root layout.

## Scope
1. Add `aria-current="page"` to the active `<Link>` in `Sidebar.tsx`
2. Add `aria-label="Main navigation"` to the `<aside>` element in `Sidebar.tsx`
3. Add `aria-label="Search patients"` to the search `<input>` in `PatientList.tsx`
4. Replace `<img src="/logo-navavej.png" ...>` with Next.js `<Image src="/logo-navavej.png" width={120} height={48} alt="Navavej" ...>` in `Sidebar.tsx`
5. Create a simple React `ErrorBoundary` class component and wrap `{children}` in `layout.tsx`

## Primary Files
- `src/components/Sidebar.tsx`
- `src/components/dashboard/PatientList.tsx`
- `src/app/layout.tsx`
- `src/components/ErrorBoundary.tsx` (new)

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%
