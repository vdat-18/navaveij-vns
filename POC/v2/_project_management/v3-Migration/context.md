# Context — v3 Migration Exercise

**Date:** 2026-03-19
**Author:** Architecture Review
**Folder:** `_project_management/v3-Migration/`

---

## 1. What Is This Project?

**Navaveij** is a Smart Health Checkup Recommendation Dashboard being built for Navavej International Hospital (Bangkok). The system uses a hybrid Rule + AI model to recommend personalised annual checkup packages and add-on examinations for patients, and presents the output to a physician (ROC Staff) via a web dashboard.

The POC evaluation scoring is weighted as:

| Criterion | Weight |
|---|---|
| Hybrid Recommendation Engine + MCP | 35% |
| Pluggable AI + FHIR terminology | 25% |
| UX / XAI Explainability | 20% |
| Security, Privacy & Audit | 20% |

---

## 2. What Is This Migration?

The **improved v2** (`POC/v2`) is the primary codebase — it has a complete 3-screen frontend, full contract routes, Stage-2 schema, security/RBAC, caching, and 40+ passing tests. All gaps (GAP-0 through GAP-10) are closed.

Separately, a colleague built **v3** (`POC/v3`) on top of the original v2 baseline. The v3 introduced three new capabilities:

1. **3-Agent BAML Pipeline** — Replaces the single `GenerateRecommendation()` call with three chained specialist agents:
   - `AnalyzeClinicalRisks()` → clinical risk profile
   - `MatchProgramRules()` → tier and add-on selection
   - `ComposeRecommendation()` → patient-facing communication
   This improves AI explainability, demonstrates pluggable architecture, and produces more granular reasoning traces.

2. **Hybrid AI / Rules Toggle** — A UI mode button that sends `force_rule_based: bool` to the API, live-demonstrating the graceful degradation path without needing to kill the AI service.

3. **PII Privacy Mode Toggle** — A UI toggle that switches between the physician view (rehydrated real names/IDs) and the raw AI view (UUID masked tokens), using a `security_metadata` object the backend returns alongside the recommendation. This provides a live POC demonstration of the privacy architecture.

Additionally, v3 includes enrichment BAML functions and scripts for generating richer synthetic patient data across clinical scenarios.

The goal of this migration is to bring these three features into the improved v2, without disrupting any of the existing closed gaps.

---

## 3. What the Migration Does NOT Bring from v3

| v3 Element | Reason NOT Migrated |
|---|---|
| v3's simplified API (no contracts router) | v2's full contract routes are required for POC scoring |
| v3's hardcoded `CORS: ["*"]` | v2's configurable CORS via settings is more correct |
| v3's 2-screen frontend | v2's 3-screen frontend is the target state |

---

## 4. Scope of This Migration

In scope:

1. BAML schema update — 3-agent pipeline.
2. Workflow update — chained agents, RuleEvaluator integration, force_rule_based, graceful fallback.
3. Orchestrator update — force_rule_based parameter, security_metadata in response.
4. API (contracts.py) update — accept force_rule_based, pass security_metadata through response.
5. Frontend — Hybrid AI/Rules toggle and PII Privacy Mode toggle.
6. Synthesis — enrichment.baml and enrichment scripts.

Out of scope:

- Full production hardening beyond POC criteria.
- Upstream HIS/FHIR integration changes owned by other teams.
- Non-essential UI polish not tied to acceptance criteria.
- Changing any existing test contract behavior.

---

## 5. Key Reference Documents

- `doc_outputs/onboarding/ai-team-onboarding.md`
- `POC/v2/_project_management/POC-Gap-Closure/gap-closure-plan.md`
- `POC/v2/_project_management/v3-Migration/migration-plan.md`
- `POC/v3/baml_src/clinical/recommendation_output.baml`
- `POC/v3/backend/src/services/workflows/clinical.py`
- `POC/v3/backend/src/services/orchestrator.py`
- `POC/v3/frontend/src/app/page.tsx`
- `POC/v3/frontend/src/components/dashboard/RecommendationPanel.tsx`
- `POC/v2/backend/src/api/routes/contracts.py`
- `POC/v2/backend/src/services/workflows/clinical.py`
- `POC/v2/_project_management/v3-Migration/implementation/_development_summary.md`
- `POC/v2/_project_management/v3-Migration/implementation/_lastest_test_results.md`
