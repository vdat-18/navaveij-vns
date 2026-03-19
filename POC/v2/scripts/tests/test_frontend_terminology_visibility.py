from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_timeline_component_renders_terminology_labels():
    source = _read("frontend/src/components/trend-timeline/ClinicalEventTimeline.tsx")
    assert "ICD10" in source
    assert "SNOMED" in source
    assert "LOINC" in source
    assert "CPT" in source
    assert "row.terminology" in source


def test_mapping_component_renders_target_terminology_columns():
    source = _read("frontend/src/components/access-monitoring/MappingToolTab.tsx")
    assert "Target System" in source
    assert "Target Label" in source
    assert "Map Type" in source
    assert "mapping.target_system" in source
    assert "mapping.target_code" in source
    assert "mapping.mapping_type" in source
