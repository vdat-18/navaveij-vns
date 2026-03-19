# Context — Rules Gap-Closure Exercise

**Date:** 2026-03-19
**Author:** Architecture Review
**Folder:** `_project_management/3. Rules-Gap-Closure/`

---

## 1. What Is This Exercise?

The POC-Gap-Closure exercise (folder `1. POC-Gap-Closure/`) aligned the POC v2 implementation
with the v3 API contracts, screen layouts, and security requirements. That exercise is complete.

This exercise addresses a distinct, orthogonal layer: **whether the POC correctly applies the
clinical Rule Synthesis Framework** defined in:

- `doc_outputs/architecture/AI/Recommendation Engine/v3/samples/rule-synthesis-framework.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/data/clinical-guidelines-reference.md`
- `doc_outputs/onboarding/ai-team-onboarding.md`

These documents define how tier selection rules, add-on items, safety constraints, confidence
scoring, output schema validation, and audit logging must behave. The framework is the source of
truth for the AI team's correctness, not just the API surface.

---

## 2. Why This Matters for Evaluation

The POC evaluation scoring has two criteria directly affected by rules correctness:

| Criterion | Weight | Rules Gap Impact |
|-----------|--------|-----------------|
| Hybrid Recommendation Engine + MCP | 35% | Confidence calibrator formula, safety validator architecture, graceful degradation path |
| Security, Privacy & Audit | 20% | Audit logger dimensions (WHO captures patient not user; WHERE missing) |

Additionally, the BAML output schema gaps affect all four criteria because they reduce the
AI's ability to produce complete, validator-checkable Stage 1 output.

---

## 3. What the POC-Gap-Closure Exercise Already Fixed

- API route surface (GAP-1)
- Stage-2 response assembly with confidence score, resolved package, metadata (GAP-2)
- MCP token parameter normalization (GAP-3)
- Screen 2 and Screen 3 contracts (GAP-4, GAP-5)
- Security / RBAC enforcement (GAP-6)
- FHIR terminology evidence (GAP-7)
- Frontend reliability (GAP-8)
- Verification pack (GAP-9)
- Backend TTL cache (GAP-10)

---

## 4. Scope of This Exercise

In scope:

1. Rules framework compliance gap analysis (all 12 gaps, grouped into 8 closure items).
2. Prioritized closure plan with dependencies and acceptance gates.
3. Documentation under `_project_management/3. Rules-Gap-Closure/` to guide implementation.

Out of scope:

- API contract changes already delivered in POC-Gap-Closure.
- Frontend screen layout changes.
- Upstream Clinical Signal Engine or Data Pipeline changes (owned by Data Platform team).
- Changes to the rule synthesis framework itself (framework changes require clinical team sign-off).

---

## 5. Key Reference Documents

- `doc_outputs/onboarding/ai-team-onboarding.md` (§7 Output Schema, §8 Tier Logic, §10 Performance SLAs)
- `doc_outputs/architecture/AI/Recommendation Engine/v3/samples/rule-synthesis-framework.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/data/clinical-guidelines-reference.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/recommendation-output-schema.md`
- `POC/v2/backend/src/api/routes/contracts.py` (confidence calibrator, Stage 2 assembly)
- `POC/v2/backend/src/services/safety.py` (Safety Rule Validator)
- `POC/v2/backend/src/services/audit.py` (Audit Logger)
- `POC/v2/backend/src/mcp_server/tools/program_ruleset.py` (pre-AI demographic filtering)
- `POC/v2/baml_src/clinical/recommendation_output.baml` (Stage 1 BAML schema)
- `POC/v3/assets/synthesis/rulesets/sample_ruleset_tier_config.json`
- `POC/v3/assets/synthesis/rulesets/sample_add_on_items.json`
