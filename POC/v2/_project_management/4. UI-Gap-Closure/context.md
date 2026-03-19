# UI Gap Closure — Context
> **Date:** 2026-03-19 · **Exercise:** 4 of 4 · **Audience:** AI Engineering + Frontend Team

## Background

Exercises 1 (POC-Gap-Closure) and 3 (Rules-Gap-Closure) addressed the backend API surface and clinical rule compliance. This exercise addresses the frontend (UI) layer of the Navavej POC v2.

A full code audit of all 20 source files in `POC/v2/frontend/src/` was conducted on 2026-03-19. The audit confirmed a general assessment that "the UI is messy, buggy, and inconsistent" — and found the issues to be more severe than described, including active patient-safety bugs and security vulnerabilities.

## What Was Found

53 gaps across 9 categories:

| Category | Count | Severity |
|---|---|---|
| Patient Safety / Clinical Data Bugs | 7 | Critical |
| Broken / Invisible UI Components | 3 | Critical |
| Security | 4 | Critical |
| Functional Bugs & Missing UX States | 11 | High |
| Type Safety | 5 | High |
| Code Quality & Consistency | 15 | Medium |
| Layout & Responsiveness | 3 | Medium |
| Accessibility | 4 | Low |
| Zero Test Coverage | 1 (blanket) | High |
| **Total** | **53** | |

## Scope

This exercise covers:
- `POC/v2/frontend/src/` — all 20 TypeScript/TSX source files
- `POC/v2/frontend/src/app/globals.css` — design tokens and global styles

This exercise does NOT cover:
- `POC/v2/backend/` — covered by exercises 1 and 3
- New screens or features not already present in v2

## POC Scoring Impact

| TOR Criterion | Weight | Relevant Gaps |
|---|---|---|
| UX / Explainability (XAI) | 20% | GAP-UI-1, GAP-UI-2, GAP-UI-5, GAP-UI-6, GAP-UI-12, GAP-UI-13 |
| Hybrid Engine + MCP | 35% | GAP-UI-1 (risk gauge), GAP-UI-7 (alert persistence) |
| Security, Privacy & Audit | 20% | GAP-UI-4, GAP-UI-8 |
| Pluggable AI Architecture | 25% | GAP-UI-9 (type safety of API contracts) |

## Key Reference Documents

| Document | Path |
|---|---|
| AI Team Onboarding | `doc_outputs/onboarding/ai-team-onboarding.md` |
| Recommendation Output Schema | `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/recommendation-output-schema.md` |
| Access Monitoring Contract | `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/access-monitoring-contract.md` |
| POC-Gap-Closure | `_project_management/1. POC-Gap-Closure/` |
| Rules-Gap-Closure | `_project_management/3. Rules-Gap-Closure/` |

## Remediation Waves

- **Wave 1 — Stabilise** (GAP-UI-1 through GAP-UI-8): Fix pre-demo blockers — clinical data bugs, broken components, security issues, missing error states. ~2–3 days.
- **Wave 2 — Consolidate** (GAP-UI-9 through GAP-UI-13): Fix type safety, design token system, chart duplication, UX polish, layout. ~2–3 days.
- **Wave 3 — Harden** (GAP-UI-14 through GAP-UI-15): Accessibility and test coverage. ~3–5 days.
