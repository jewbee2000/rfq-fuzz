"""Local dimension units govern independently of the drawing's default units."""
import pytest

from rfqfuzz.v1.reference import decisions


@pytest.mark.parametrize("default_unit,callout,expected", [
    ("mm", "0.2362 +/- 0.0020 in", "supported_clear"),
    ("in", "6.00 +/- 0.05 mm", "supported_clear"),
    ("mm", "0.2000 +/- 0.0010 in", "contradiction"),
    ("in", "5.00 +/- 0.01 mm", "contradiction"),
    ("mm", "6.00 mm", "supported_clear"),
])
def test_local_bore_units_and_explicit_tolerance(default_unit, callout, expected):
    packet = {
        "units": {"model": "mm", "drawing": default_unit},
        "authority": {"dimensions": "drawing", "material_precedence": "equal"},
        "manufacturing": {
            "material": "6061-T6", "model_stage": "finished",
            "drawing_stage": "finished", "transition": None,
        },
        "obligations": [{"id": "bore", "category": "diameter_consistency", "feature_id": "H1"}],
    }
    geometry = {"bore_diameter_mm": 6.0, "h1_count": 1}
    drawing = {"annotations": {
        "UNITS": [f"UNITS = {default_unit}"],
        "MATERIAL": ["MATERIAL = 6061-T6"],
        "H1 DIAMETER": [f"H1 DIAMETER = {callout}"],
    }}
    assert decisions(packet, geometry, drawing)[0]["conclusion"] == expected
