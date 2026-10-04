"""Challenge actual STEP/PDF/PNG content, without private numeric answer keys."""
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess

import pytest
from PIL import Image, ImageDraw
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

from rfqfuzz.v1.contracts import sha256, write_json
from rfqfuzz.v1.generation import generate_case
from rfqfuzz.v1.profiles import profile
from rfqfuzz.v1.validation import (_native, _isolation, attest_case, inspect_case, inspect_drawing,
                                    measure_step, validate_suite, LENGTH_TOL_MM)


def generated(tmp_path, name="pk-0123456789ab", family="plate", **kwargs):
    folder = tmp_path / name
    packet = generate_case(folder, name, family, **kwargs)
    return folder, packet


def rehash(folder):
    packet = json.loads((folder / "packet.json").read_text())
    for artifact in packet["artifacts"]:
        artifact["sha256"] = sha256(folder / artifact["path"])
    write_json(folder / "packet.json", packet)


def render(folder):
    subprocess.run(["pdftoppm", "-singlefile", "-r", "200", "-png", str(folder / "drawing.pdf"), str(folder / "drawing")], check=True, capture_output=True, timeout=60)


def whiteout(folder, box):
    original = PdfReader(folder / "drawing.pdf")
    stream = io.BytesIO()
    overlay = canvas.Canvas(stream, pagesize=(842, 595))
    overlay.setFillColorRGB(1, 1, 1)
    overlay.rect(box[0], box[1], box[2] - box[0], box[3] - box[1], fill=1, stroke=0)
    overlay.save()
    writer = PdfWriter(clone_from=original)
    writer.pages[0].merge_page(PdfReader(stream).pages[0])
    with (folder / "drawing.pdf").open("wb") as output:
        writer.write(output)
    render(folder)
    rehash(folder)


def conclusions(observed):
    return {e["obligation_id"]: e["conclusion"] for e in observed["expectations"]}


def test_attestation(folder, record):
    # A synthetic contract test, expressly not evidence of real visual review.
    return {"cases": [{"case_id": record["case_id"], "pdf_sha256": sha256(folder / "drawing.pdf"),
                       "png_sha256": sha256(folder / "drawing.png"), "legible_unclipped": True,
                       "view_associations_checked": True, "reviewer": "synthetic test attestation; never release evidence",
                       "visible_annotation_lines": [s for v in record["drawing"]["annotations"].values() for s in v]}]}
test_attestation.__test__ = False


@pytest.mark.parametrize("family,values", [("plate", {"bore_diameter_mm": 6, "h1_count": 4}),
                                          ("bore_block", {"bore_depth_mm": 24, "counterbore_depth_mm": 4}),
                                          ("pocket_block", {"wall_mm": 5, "pocket_depth_mm": 12})])
def test_independent_measured_surfaces_and_analytic_volume(tmp_path, family, values):
    folder, packet = generated(tmp_path, family=family)
    geometry = measure_step(folder / "part.step", family, packet["features"])
    assert geometry["solid_count"] == 1 and abs(geometry["volume_error_mm3"]) < 1e-4
    for key, expected in values.items():
        assert abs(geometry[key] - expected) <= LENGTH_TOL_MM
    observed = _native(folder, tmp_path / "native")
    assert all(c == "supported_clear" for c in conclusions(observed).values())
    assert observed["drawing"]["glyphs_checked"] > 200


def test_hash_bound_visual_gate_stale_disagreement_and_no_auto_pass(tmp_path):
    folder, _ = generated(tmp_path)
    record = inspect_case(folder, tmp_path / "observed")
    assert record["status"] == "unverified" and record["expectations"] == []
    a = test_attestation(folder, record)
    stale = copy.deepcopy(a); stale["cases"][0]["pdf_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="stale"):
        attest_case(copy.deepcopy(record), folder, stale)
    disagreement = copy.deepcopy(a); disagreement["cases"][0]["visible_annotation_lines"].pop()
    with pytest.raises(ValueError, match="disagreement"):
        attest_case(copy.deepcopy(record), folder, disagreement)
    promoted = attest_case(record, folder, a)
    assert promoted["status"] == "valid" and promoted["expectations"]


@pytest.mark.parametrize("kwargs,expected", [
    ({"drawing_overrides": {"h1_diameter": 6.8}}, {"obj-diameter": "contradiction"}),
    ({"drawing_overrides": {"h1_count": 3}}, {"obj-count": "contradiction"}),
    ({"drawing_overrides": {"h1_count": 2, "h1_group_members": [0, 1]}}, {"obj-count": "supported_clear"}),
    ({"drawing_overrides": {"diameter_ref": True, "h1_diameter": 6.8}, "context_overrides": {"authority": {"dimensions": "step"}}}, {"obj-diameter": "supported_clear"}),
    ({"drawing_overrides": {"drawing_units": "in"}}, {"obj-units": "supported_clear", "obj-diameter": "supported_clear"}),
    ({"drawing_overrides": {"drawing_units": "in", "convert_dimensions": False}}, {"obj-units": "contradiction"}),
    ({"drawing_overrides": {"drawing_material": "7075-T6"}}, {"obj-material": "contradiction"}),
    ({"drawing_overrides": {"drawing_material": "AL6061-T6"}}, {"obj-material": "supported_clear"}),
    ({"drawing_overrides": {"drawing_material": "7075-T6"}, "context_overrides": {"authority": {"material_precedence": "contract"}}}, {"obj-material": "supported_clear"}),
    ({"drawing_overrides": {"omit": ["SURFACE ROUGHNESS"]}}, {"obj-requirement": "contradiction"}),
    ({"drawing_overrides": {"omit": ["SURFACE ROUGHNESS"]}, "context_overrides": {"requirements": []}}, {"obj-requirement": "supported_clear"}),
    ({"drawing_overrides": {"drawing_revision": "B"}}, {"obj-release": "contradiction"}),
    ({"drawing_overrides": {"drawing_revision": "B"}, "context_overrides": {"release_association": {"drawing_revision": "B", "permitted_pairs": [["A", "B"]]}}}, {"obj-release": "supported_clear"}),
    ({"drawing_overrides": {"omit": ["H1 DIAMETER"]}}, {"obj-diameter": "missing_information"}),
    ({"drawing_overrides": {"sparse": True}, "context_overrides": {"authority": {"dimensions": "step"}}}, {"obj-diameter": "supported_clear", "obj-count": "supported_clear"}),
])
def test_objective_defects_and_valid_alternatives_from_actual_content(tmp_path, kwargs, expected):
    folder, _ = generated(tmp_path, **kwargs)
    observed = _native(folder, tmp_path / "observed")
    actual = conclusions(observed)
    for key, conclusion in expected.items():
        assert actual[key] == conclusion
    if expected.get("obj-units") == "contradiction":
        assert "obj-diameter" not in actual and observed["suppressed_unit_dependents"] == ["obj-diameter"]


@pytest.mark.parametrize("transition,expected", [(None, "missing_information"),
    ({"operation": "ream", "feature_id": "H1", "from_stage": "intermediate", "to_stage": "finished", "target": "drawing bore callout"}, "supported_clear"),
    ({"operation": "ream", "feature_id": "H1", "from_stage": "intermediate", "to_stage": "finished", "target": "drawing H1 diameter callout"}, "supported_clear")])
def test_explicit_stage_transition_and_unknown(tmp_path, transition, expected):
    folder, _ = generated(tmp_path, drawing_overrides={"h1_diameter": 6.8}, context_overrides={"manufacturing": {"model_stage": "intermediate", "transition": transition}})
    assert conclusions(_native(folder, tmp_path / "native"))["obj-diameter"] == expected


@pytest.mark.parametrize("family,kwargs,obligation,expected", [
    ("pocket_block", {"parameters": {"wall": .6}}, "cnc-wall", "advisory"),
    ("pocket_block", {"parameters": {"wall": .8}}, "cnc-wall", "supported_clear"),
    ("pocket_block", {"parameters": {"wall": .6}, "profile": profile("relaxed")}, "cnc-wall", "supported_clear"),
    ("bore_block", {"parameters": {"depth": 26}}, "cnc-depth", "advisory"),
    ("bore_block", {"parameters": {"depth": 24}}, "cnc-depth", "supported_clear"),
    ("plate", {"parameters": {"width": 118}, "context_overrides": {"setup": {"stock_allowance_mm": [2, 0, 0], "fixture_allowance_mm": [1, 0, 0]}}}, "cnc-envelope", "profile_exclusion"),
    ("plate", {"parameters": {"width": 120}}, "cnc-envelope", "supported_clear"),
    ("plate", {"context_overrides": {"manufacturing": {"material": "unknown", "material_class": "unknown"}}}, "cnc-envelope", "missing_information"),
    ("plate", {"context_overrides": {"manufacturing": {"tolerance_stage": None, "finish": "anodize"}}, "profile": profile("relaxed")}, "cnc-stage", "missing_information"),
    ("plate", {"context_overrides": {"manufacturing": {"tolerance_stage": None, "finish": "anodize"}}}, "cnc-stage", "supported_clear"),
])
def test_conditional_advisories_boundaries_and_alternate_profiles(tmp_path, family, kwargs, obligation, expected):
    folder, _ = generated(tmp_path, family=family, **kwargs)
    assert conclusions(_native(folder, tmp_path / "observed"))[obligation] == expected


@pytest.mark.parametrize("precedence,expected", [("equal", "missing_information"), ("contract", "supported_clear"), ("drawing", "missing_information")])
def test_conflicting_global_material_never_assumed_for_cnc_rules(tmp_path, precedence, expected):
    folder, _ = generated(tmp_path, drawing_overrides={"drawing_material": "7075-T6"}, context_overrides={"authority": {"material_precedence": precedence}})
    actual = conclusions(_native(folder, tmp_path / "observed"))
    assert actual["cnc-envelope"] == expected and actual["cnc-stage"] == expected
    assert actual["obj-material"] == ("contradiction" if precedence == "equal" else "supported_clear")


def test_corrupt_step_signature_units_and_stale_hash_retained(tmp_path):
    folder, _ = generated(tmp_path)
    original = (folder / "part.step").read_text()
    (folder / "part.step").write_text("ISO-10303-21;\nBROKEN")
    record = inspect_case(folder, tmp_path / "stale")
    assert record["status"] == "invalid_fixture" and "hash mismatch" in record["reasons"][0]
    rehash(folder)
    record = inspect_case(folder, tmp_path / "corrupt")
    assert record["status"] == "invalid_fixture" and "truncated STEP" in record["reasons"][0]
    (folder / "part.step").write_text(original.replace(".MILLI.,.METRE.", "$,.METRE."))
    rehash(folder)
    record = inspect_case(folder, tmp_path / "units")
    assert record["status"] == "invalid_fixture" and "units" in record["reasons"][0]


def test_single_digit_whiteout_preserving_search_text_rejected(tmp_path):
    import pypdfium2 as pdfium
    folder, _ = generated(tmp_path)
    doc = pdfium.PdfDocument(str(folder / "drawing.pdf")); tp = doc[0].get_textpage()
    alltext = tp.get_text_range()
    target = alltext.index("H1 DIAMETER = 6.00") + len("H1 DIAMETER = ")
    box = tp.get_charbox(target)
    tp.close(); doc.close()
    whiteout(folder, [box[0] - .2, box[1] - .2, box[2] + .2, box[3] + .2])
    assert "H1 DIAMETER = 6.00" in PdfReader(folder / "drawing.pdf").pages[0].extract_text()
    with pytest.raises(ValueError, match="glyph lacks visible ink"):
        inspect_drawing(folder / "drawing.pdf", folder / "drawing.png", tmp_path / "whiteout")


def test_png_whiteout_and_bounded_timeout(tmp_path):
    folder, _ = generated(tmp_path)
    with Image.open(folder / "drawing.png") as image:
        image = image.convert("RGB")
    ImageDraw.Draw(image).rectangle((0, 0, image.width, image.height), fill="white")
    image.save(folder / "drawing.png"); rehash(folder)
    with pytest.raises(ValueError, match="raster disagreement"):
        inspect_drawing(folder / "drawing.pdf", folder / "drawing.png", tmp_path / "blank-png")
    timed = inspect_case(folder, tmp_path / "timeout", timeout=.001)
    assert timed["status"] == "timeout" and timed["expectations"] == []
    assert (tmp_path / "timeout" / "native-process.txt").is_file()


def test_actual_clipped_pdf_glyph_rejected(tmp_path):
    folder, _ = generated(tmp_path)
    writer = PdfWriter(clone_from=PdfReader(folder / "drawing.pdf"))
    writer.pages[0].mediabox.upper_right = (600, 595)
    with (folder / "drawing.pdf").open("wb") as output:
        writer.write(output)
    render(folder); rehash(folder)
    with pytest.raises(ValueError, match="clipped/off-page"):
        inspect_drawing(folder / "drawing.pdf", folder / "drawing.png", tmp_path / "clipped")


def test_independently_added_bore_topology_quarantined(tmp_path):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
    folder, _ = generated(tmp_path)
    reader = STEPControl_Reader(); reader.ReadFile(str(folder / "part.step")); reader.TransferRoots()
    bore = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, -4), gp_Dir(0, 0, 1)), 2, 8).Shape()
    altered = BRepAlgoAPI_Cut(reader.OneShape(), bore).Shape()
    writer = STEPControl_Writer(); writer.Transfer(altered, STEPControl_AsIs); writer.Write(str(folder / "part.step"))
    rehash(folder)
    record = inspect_case(folder, tmp_path / "extra-bore")
    assert record["status"] == "invalid_fixture" and record["expectations"] == []
    assert "plate topology" in record["reasons"][0]


def test_private_numeric_intent_ignored_but_actual_collateral_quarantined(tmp_path):
    root = tmp_path / "suite"; public = root / "public"
    base, _ = generated(public, "pk-0123456789ab")
    bad, _ = generated(public, "pk-0123456789ac", drawing_overrides={"h1_diameter": 6.8, "drawing_material": "7075-T6"})
    mutations = [{"case_id": base.name, "ancestry": "same-source", "variant": "repaired", "operator": "O01", "source_parameters": {"diameter": 999}},
                 {"case_id": bad.name, "ancestry": "same-source", "variant": "defective", "operator": "O01", "source_parameters": {"diameter": 999}}]
    write_json(root / "private" / "mutations.json", {"mutations": mutations})
    record = validate_suite(root, tmp_path / "validated")
    good = next(c for c in record["cases"] if c["case_id"] == base.name)
    invalid = next(c for c in record["cases"] if c["case_id"] == bad.name)
    assert good["measurements"]["bore_diameter_mm"] == 6
    assert good["status"] == "unverified"
    assert invalid["status"] == "invalid_fixture" and invalid["expectations"] == []
    assert any("collateral" in reason or "undeclared" in reason for reason in invalid["reasons"])


@pytest.mark.parametrize("context", [{"manufacturing": {"material": "ABS", "material_class": "plastic"}},
                                     {"setup": {"stock_allowance_mm": [1, 0, 0]}},
                                     {"profile": profile("relaxed")}])
def test_clean_collateral_public_context_changes_still_quarantined(tmp_path, context):
    root = tmp_path / "suite"; public = root / "public"
    base, _ = generated(public, "pk-0123456789ab")
    bad, _ = generated(public, "pk-0123456789ac", drawing_overrides={"h1_diameter": 6.8}, context_overrides=context)
    mutations = [{"case_id": base.name, "ancestry": "same-source", "variant": "repaired", "operator": "O01"},
                 {"case_id": bad.name, "ancestry": "same-source", "variant": "defective", "operator": "O01"}]
    write_json(root / "private" / "mutations.json", {"mutations": mutations})
    record = validate_suite(root, tmp_path / "validated")
    invalid = next(c for c in record["cases"] if c["case_id"] == bad.name)
    assert invalid["status"] == "invalid_fixture"
    assert any("undeclared" in reason for reason in invalid["reasons"])


def test_declared_defect_accidentally_clear_not_a_valid_fixture(tmp_path):
    root = tmp_path / "suite"; public = root / "public"
    folder, _ = generated(public)
    write_json(root / "private" / "mutations.json", {"mutations": [{"case_id": folder.name, "ancestry": "source", "variant": "defective", "operator": "O01"}]})
    case = validate_suite(root, tmp_path / "validated")["cases"][0]
    assert case["status"] == "invalid_fixture" and case["expectations"] == []
    assert any("not independently established" in reason for reason in case["reasons"])


@pytest.mark.parametrize("operator,kwargs", [
    ("O02", {"drawing_overrides": {"h1_count": 2, "h1_group_members": [0, 1]}}),
    ("O04", {"drawing_overrides": {"drawing_material": "7075-T6"}, "context_overrides": {"authority": {"material_precedence": "contract"}}}),
    ("O06", {"drawing_overrides": {"drawing_revision": "B"}, "context_overrides": {"release_association": {"drawing_revision": "B", "permitted_pairs": [["A", "B"]]}}}),
])
def test_legitimate_scoped_context_deltas_preserved(tmp_path, operator, kwargs):
    root = tmp_path / "suite"; public = root / "public"
    base, _ = generated(public, "pk-0123456789ab")
    alternative, _ = generated(public, "pk-0123456789ac", **kwargs)
    mutations = [{"case_id": base.name, "ancestry": "source", "variant": "repaired", "operator": operator},
                 {"case_id": alternative.name, "ancestry": "source", "variant": "valid_alternative", "operator": operator}]
    write_json(root / "private" / "mutations.json", {"mutations": mutations})
    record = validate_suite(root, tmp_path / "validated")
    assert all(c["status"] == "unverified" for c in record["cases"])


def test_production_validator_has_no_generation_or_reference_import():
    source = Path(__file__).resolve().parents[2] / "src/rfqfuzz/v1/validation.py"
    import ast
    imports = [node.module or "" for node in ast.walk(ast.parse(source.read_text())) if isinstance(node, ast.ImportFrom)]
    assert not any("generation" in name or "reference" in name or "profiles" in name for name in imports)
