# Context — POC Gap-Closure Exercise

**Date:** 2026-03-18
**Author:** Architecture Review
**Folder:** `project_management/POC-Gap-Closure/`

---

## 1. What Is This Project?

**Navaveij** is a Smart Health Checkup Recommendation Dashboard being built for Navavej International Hospital (Bangkok). The system uses a hybrid Rule + AI model to recommend personalised annual checkup packages and add-on examinations for patients, and presents the output to a physician (ROC Staff) via a web dashboard.

The project was initiated under a Terms of Reference (TOR) defining three core tiers of checkup packages (Standard / Advanced / Premium), a Hybrid Recommendation Engine, a fully pluggable AI layer (switchable between Claude, GPT-4o, Gemini, and local LLMs), FHIR R4 data sourcing, PDPA-compliant audit logging, and an Explainable AI (XAI) dashboard with chain-of-thought reasoning traces. POC evaluation scoring is weighted as:

| Criterion | Weight |
|---|---|
| Hybrid Recommendation Engine + MCP | 35% |
| Pluggable AI + FHIR terminology | 25% |
| UX / XAI Explainability | 20% |
| Security, Privacy & Audit | 20% |

---

## 2. What Is the POC?

The POC is a working interactive demo that the evaluation committee will assess. It is described in full in:

- **Architecture specs:** `doc_outputs/architecture/AI/Recommendation Engine/v3/` (20 `.md` files)
- **Build plan:** `doc_outputs/architecture/AI/Recommendation Engine/v3/plan.md`

The build plan has 6 phases:

| Phase | Description | Current Status |
|---|---|---|
| Phase 0 | Data updates (sample JSON prices) | Not started (out of scope for gap closure) |
| Phase 1 | Backend API (FastAPI, all endpoints) | Complete — v3 contract endpoints delivered (GAP-1/2/3) |
| Phase 2 | Frontend Scaffold (Vite + React) | Not migrated — gap closure continues on Next.js frontend |
| Phase 3 | Screen 1 — Individual Recommendation | Complete — Stage-2 contract-aligned (GAP-1/2) |
| Phase 4 | Screen 2 — Trend & Timeline | Complete — dedicated route and API delivered (GAP-4) |
| Phase 5 | Screen 3 — Access Monitoring | Complete — monitoring dashboard and role-gated API delivered (GAP-5) |
| Phase 6 | Integration & Demo Polish | In verification — frontend build blocked by npm environment; backend regression: 40 passed (GAP-8/9) |

---

## 3. What Has Been Built (The Colleague's POC)

A colleague independently built a Python backend POC located in `POC/v2/`. The POC covers:

- FastAPI backend with clinical recommendation routes and patient registry routes.
- Orchestration manager that performs MCP retrieval, BAML-driven recommendation generation, safety validation, audit logging, and response assembly.
- MCP server with read-focused tools for hard constraints, clinical signals, biomarker trends, and program ruleset retrieval.
- Privacy module implementing PII masking and rehydration workflow.
- Audit logging with hash chaining and dual JSON/JSONL persistence.
- Frontend dashboard (`/`) and audit page (`/audit`) implemented with Next.js.

Current state is **functionally valuable but contract-misaligned** to v3 demo requirements, especially around endpoint shape, Stage-2 output schema completeness, and screen-level contracts.

---

## 5. Scope of This Gap-Closure Exercise

This exercise aims to produce a practical, execution-ready closure path from current POC implementation to v3 requirements used for evaluation.

In scope:

1. Requirement-to-implementation gap analysis (scoring-weighted).
2. Prioritized closure plan with dependencies and acceptance gates.
3. Documentation updates under `_project_management/POC-Gap-Closure/` to guide implementation and verification.

Out of scope:

- Full production hardening beyond POC criteria.
- Upstream HIS/FHIR integration changes owned by other teams.
- Non-essential UI polish not tied to acceptance criteria.

---

## 6. Key Reference Documents

- `doc_outputs/onboarding/ai-team-onboarding.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/plan.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/recommendation-output-schema.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/signal-store-contract.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/event-timeline-contract.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/access-monitoring-contract.md`
- `POC/v2/README.md`
- `POC/v2/backend/src/api/main.py`
- `POC/v2/backend/src/services/orchestrator.py`
- `POC/v2/frontend/src/app/page.tsx`
- `POC/v2/frontend/src/app/audit/page.tsx`
- `POC/v2/_project_management/POC-Gap-Closure/gap-discovery.md`
- `POC/v2/_project_management/POC-Gap-Closure/gap-closure-plan.md`
