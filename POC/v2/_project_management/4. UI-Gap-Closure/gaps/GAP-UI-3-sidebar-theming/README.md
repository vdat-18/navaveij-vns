# GAP-UI-3 — Sidebar Theming

**Title:** Define missing CSS classes and Tailwind tokens; remove dark-mode class conflict
**Status:** Not started
**Wave:** 1

---

## Objective
Fix three theming bugs that make the sidebar transparent and unreadable: the undefined `glass-sidebar` CSS class, the undefined `teal-accent` Tailwind token, and the `className="dark"` conflict on `<html>`.

## Scope
1. Define `glass-sidebar` in `globals.css` — dark semi-transparent background with `backdrop-filter: blur(12px)` and border
2. Add `--color-teal-accent` to `@theme` block in `globals.css` as alias for `--color-navavej-teal`
3. Remove `className="dark"` from `<html>` in `layout.tsx`; ensure sidebar uses explicit colour values rather than dark-palette Tailwind tokens

## Primary Files
- `src/app/globals.css`
- `src/app/layout.tsx`
- `src/components/Sidebar.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%
