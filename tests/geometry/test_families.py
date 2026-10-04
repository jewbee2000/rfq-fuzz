"""Final STEP round trips and independent closed-form geometry checks (R03)."""
import math
import pytest
from build123d import export_step, import_step
from rfqfuzz.v1.generation import build_part, parameters_for, hole_centers

CASES = [
    ("plate", {}), ("bore_block", {}), ("pocket_block", {}),
    ("plate", dict(width=20, length=20, height=3, diameter=2, count=1)),
    ("plate", dict(width=240, length=160, height=80, diameter=16, count=4)),
    ("bore_block", dict(width=20, length=20, height=3, diameter=2, depth=2, counterbore_diameter=4, counterbore_depth=1)),
    ("bore_block", dict(width=240, length=160, height=80, diameter=16, depth=79, counterbore_diameter=60, counterbore_depth=10)),
    ("pocket_block", dict(width=20, length=20, height=3, pocket_width=8, pocket_length=8, pocket_depth=2, wall=.2)),
    ("pocket_block", dict(width=240, length=160, height=80, pocket_width=239.6, pocket_length=159.6, pocket_depth=79, wall=.2)),
]


@pytest.mark.parametrize("family,params", CASES)
def test_exported_reimported_geometry_agrees_with_analytic_volume_and_envelope(tmp_path, family, params):
    p = parameters_for(family, params)
    target = tmp_path / "part.step"
    export_step(build_part(family, params), target)
    measured = import_step(target)
    assert len(measured.solids()) == 1 and measured.is_valid
    assert {face.geom_type.name for face in measured.faces()} <= {"PLANE", "CYLINDER"}
    expected = p["width"] * p["length"] * p["height"]
    if family == "plate":
        expected -= len(hole_centers(p)) * math.pi * (p["diameter"] / 2)**2 * p["height"]
    elif family == "bore_block":
        expected -= math.pi * (p["diameter"] / 2)**2 * p["depth"]
        expected -= math.pi * ((p["counterbore_diameter"] / 2)**2 - (p["diameter"] / 2)**2) * p["counterbore_depth"]
    else:
        expected -= p["pocket_width"] * p["pocket_length"] * p["pocket_depth"]
    assert measured.volume == pytest.approx(expected, abs=1e-6)
    box = measured.bounding_box()
    assert list(box.size) == pytest.approx([p["width"], p["length"], p["height"]], abs=1e-6)


@pytest.mark.parametrize("family,params", [
    ("freeform", {}), ("plate", {"fillet": 2}), ("plate", {"count": 3}),
    ("plate", {"diameter": 100}), ("bore_block", {"depth": 35}),
    ("bore_block", {"counterbore_diameter": 5}), ("pocket_block", {"wall": 0}),
    ("pocket_block", {"pocket_depth": 20}), ("plate", {"width": float("nan")}),
])
def test_unsupported_topology_and_invalid_bounds_explicitly_refused(family, params):
    with pytest.raises(ValueError):
        build_part(family, params)
