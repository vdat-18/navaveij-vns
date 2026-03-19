# Context — POC Gap-Closure Exercise

**Date:** 2026-03-16
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

| Phase | Description | Status as of 2026-03-16 |
|---|---|---|
| Phase 0 | Data updates (sample JSON prices) | ✅ Complete |
| Phase 1 | Backend API (FastAPI, all endpoints) | 🔶 Partial — see gap-discovery.md |
| Phase 2 | Frontend Scaffold (Vite + React) | ❌ Not started |
| Phase 3 | Screen 1 — Individual Recommendation | ❌ Not started |
| Phase 4 | Screen 2 — Trend & Timeline | ❌ Not started |
| Phase 5 | Screen 3 — Access Monitoring | ❌ Not started |
| Phase 6 | Integration & Demo Polish | ❌ Not started |

Phases 2–6 are blocked until Phase 1 backend gaps are closed.

---

## 3. What Has Been Built (The Colleague's POC)

A colleague independently built a Python backend POC located in `POC/`. The POC covers:

- **MCP Server** (`POC/src/mcp_server/`) — 4 FastMCP tools reading from pre-synthesized JSON Signal Store records
- **Orchestration Manager** (`POC/src/orchestrator/core/manager.py`) — coordinates MCP, workflow, safety, and audit
- **Clinical Reasoning Workflow** (`POC/src/orchestrator/workflows/clinical.py`) — 5-phase flow: baseline → signals → trends → BAML AI inference → finalize
- **BAML Structured Output** (`baml_src/clinical/recommendation_output.baml`) — forces AI to emit a typed, schema-validated recommendation
- **PII Masking / Rehydration** (`POC/src/orchestrator/privacy/`) — pseudonymises patient data before AI sees it; restores identifiers for display
- **Confidence Calibrator** (`POC/src/orchestrator/validation/confidence_calibrator.py`) — deterministic formula: `0.4×signal_coverage + 0.4×data_completeness + 0.2×rule_agreement`
- **Output Enricher** (`POC/src/orchestrator/enrichment/output_enricher.py`) — injects system-owned fields post-AI (tier, package, product metadata)
- **SHA-256 Hash-Chained Audit Logger** (`POC/src/orchestrator/logger/audit.py`) — immutable, tamper-evident log
- **Safety Validator** (`POC/src/orchestrator/safety/validator.py`) — currently LLM-based critic
- **Synthesis Pipeline** (`POC/src/synthesis/`) — generates synthetic patient Signal Store records for testing
- **FastAPI endpoint** (`POC/src/api/main.py`) — `POST /recommend` is the only API endpoint

The POC has been run successfully against real LLM providers (Gemini, meta-llama local). Audit logs in `POC/logs/audit.jsonl` confirm end-to-end operation.

---

## 4. What Prompted This Review

During architecture review on 2026-03-16, a systematic comparison was made between:

1. The v3 specification documents (ground truth)
2. The colleague's POC implementation (actual code)

The review revealed that while all the right components exist as classes, several are **not wired into the canonical API call path**. The richer `ClinicalOrchestrator` in `agents/orchestrator.py` (which includes confidence scoring, output enrichment, and PII rehydration) is not called by the API — the simpler `OrchestrationManager` path is, and it bypasses most of those components. Additionally, three of the four required demo API endpoints are missing, the canonical demo patient record does not exist as a data file, the safety validator is non-deterministic, and the audit log structure diverges from the 5-dimension spec.

These gaps would result in a demo that:
- Returns raw, unenriched AI output (no `confidence_score`, no `resolved_package`, no add-on labels/prices)
- Cannot demonstrate the Mammogram-revocation safety rule deterministically
- Cannot populate Screen 2 (Timeline) or Screen 3 (Monitoring) — two of the three evaluated screens
- Has audit log entries that fail the 5-dimension PDPA compliance check
- Contains a hardcoded API key in source code

---

## 5. Scope of This Gap-Closure Exercise

This gap-closure exercise is **backend-only**. It covers:

- ✅ Wiring existing components that are implemented but disconnected
- ✅ Creating missing fixture data files (Somchai W. record, timeline, monitoring)
- ✅ Adding 3 missing API endpoints
- ✅ Adding the 5th MCP tool (`get_patient_event_timeline`)
- ✅ Fixing the deterministic safety validator
- ✅ Fixing the audit log 5-dimension structure
- ✅ Removing the hardcoded API key security issue
- ❌ Frontend (Phases 2–6) — out of scope here, scheduled separately

Upon completion of this exercise, Phase 1 will be fully complete and Phases 2–6 (frontend) can begin.

---

## 6. Key Reference Documents

| Document | Path |
|---|---|
| POC Build Plan (Phase 1–6 detail) | `doc_outputs/architecture/AI/Recommendation Engine/v3/plan.md` |
| Component Inventory & Architecture | `doc_outputs/architecture/AI/Recommendation Engine/v3/component-inventory-solution-approach.md` |
| Recommendation Output Schema | `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/recommendation-output-schema.md` |
| Signal Store Contract | `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/signal-store-contract.md` |
| Ruleset Store Contract | `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/ruleset-store-contract.md` |
| Event Timeline Contract | `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/event-timeline-contract.md` |
| Access Monitoring Contract | `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/access-monitoring-contract.md` |
| Navavej Package Discovery | `doc_outputs/architecture/AI/Recommendation Engine/v3/data/navavej-checkup-package-discovery.md` |
