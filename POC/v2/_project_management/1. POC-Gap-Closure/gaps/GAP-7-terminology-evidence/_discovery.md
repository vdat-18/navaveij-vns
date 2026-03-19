# Discovery

Status: Complete

## Findings

- Existing mapping table and endpoint were present but did not provide full v3-aligned terminology evidence fields.
- Timeline synthesis populated diagnosis/procedure terminology keys with empty values for signal-store derived records.
- Trend timeline UI rendered limited terminology detail and mapping table did not highlight target-system evidence clearly.

## Decisions

- Normalize mapping records in backend to emit v3-aligned target fields while keeping compatibility keys.
- Seed explicit LOINC, SNOMED_CT, ICD10, and CPT mapping records in monitoring fixture for visible evidence.
- Resolve terminology codes in timeline synthesis using source values first and deterministic fallback dictionaries.
- Expand frontend timeline and mapping displays to surface terminology identifiers directly in row-level UI.
