# Latest Test Results

Status: Updated

## Targeted GAP-7 verification

- Command:
  - `uv run pytest scripts/tests/test_timeline_contract_payload.py scripts/tests/test_access_monitoring_contract.py scripts/tests/test_api_contract_routes.py scripts/tests/test_frontend_terminology_visibility.py -v`
- Result:
  - `22 passed in 0.48s`
- Coverage highlights:
  - strict non-empty terminology checks for timeline diagnosis/lab/procedure payload sections
  - mapping systems include `LOINC`, `SNOMED_CT`, `ICD10`, and `CPT`
  - frontend terminology visibility checks for timeline and mapping components

## Regression context

- Command:
  - `uv run pytest scripts/tests -v`
- Result:
  - `33 passed, 1 failed`
- Failure:
  - `scripts/tests/test_end_to_end.py::test_with_synthesized_data`
  - root cause is external LLM service unavailability (`503 Service Unavailable`) and is not a GAP-7 terminology contract failure.
