"""Challenge exported-artifact validation; retain --basetemp for failure inputs."""
import io
import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageDraw
import pytest
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs

from rfqfuzz.contracts import sha256, write_json
from rfqfuzz.validation import inspect_case, measure_step, validate_suite

ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "evidence/M0/bundle/public").is_dir():
    ROOT = ROOT.parents[1]  # isolated implementation worktree, shared pinned inputs
PUBLIC = ROOT / "evidence/M0/bundle/public"
ATTESTATION = ROOT / "evidence/M0/visual-attestation.json"


def copy_case(tmp_path):
    target = tmp_path / "pk-7a1c"
    shutil.copytree(PUBLIC / "pk-7a1c", target)
    return target


def rehash(folder):
    path = folder / "packet.json"
    packet = json.loads(path.read_text(encoding="utf-8"))
    for artifact in packet["artifacts"]:
        artifact["sha256"] = sha256(folder / artifact["path"])
    write_json(path, packet)


def render_png(folder):
    subprocess.run(["pdftoppm", "-singlefile", "-r", "200", "-png", str(folder / "drawing.pdf"),
                    str(folder / "drawing")], capture_output=True, check=True, timeout=60)


def whiteout(folder, box):
    pdf = folder / "drawing.pdf"
    original = PdfReader(pdf)
    stream = io.BytesIO()
    overlay = canvas.Canvas(stream, pagesize=(float(original.pages[0].mediabox.width), float(original.pages[0].mediabox.height)))
    overlay.setFillColorRGB(1, 1, 1)
    overlay.rect(box[0], box[1], box[2] - box[0], box[3] - box[1], fill=1, stroke=0)
    overlay.save()
    writer = PdfWriter(clone_from=original)
    page = writer.pages[0]
    page.merge_page(PdfReader(stream).pages[0])
    with pdf.open("wb") as output:
        writer.write(output)
    render_png(folder)
    rehash(folder)


def test_final_suite_measured_and_attested(tmp_path):
    record = validate_suite(PUBLIC, tmp_path / "validation", ATTESTATION)
    assert record["status"] == "valid", record["failures"]
    assert all(record["invariants"].values())
    assert sorted(c["expected_conclusion"] for c in record["cases"]) == ["contradiction", "supported_clear", "supported_clear"]
    for case in record["cases"]:
        assert abs(case["geometry"]["volume_error_mm3"]) < 1e-5
        assert case["geometry"]["solid_count"] == 1
        assert len(case["geometry"]["cylinders"]) == 4
        assert case["drawing"]["png_pdf_agreement"]["unmatched_ink_ratio"] < 0.015


def test_without_visual_attestation_never_scorable(tmp_path):
    result = inspect_case(PUBLIC / "pk-7a1c", tmp_path / "unattested")
    assert result["status"] == "pending_visual_attestation"
    assert "expected_conclusion" not in result


def test_hash_mutation_rejected_before_parser(tmp_path):
    folder = copy_case(tmp_path)
    with (folder / "part.step").open("ab") as output:
        output.write(b"\nMUTATION")
    result = inspect_case(folder, tmp_path / "result")
    assert result["status"] == "invalid_fixture"
    assert "hash mismatch" in result["failures"][0]


def test_corrupt_step_even_with_updated_manifest(tmp_path):
    folder = copy_case(tmp_path)
    (folder / "part.step").write_bytes(b"ISO-10303-21;\nBROKEN")
    rehash(folder)
    result = inspect_case(folder, tmp_path / "result")
    assert result["status"] == "invalid_fixture"
    assert "truncated STEP" in result["failures"][0]


def test_actual_step_units_not_packet_metadata(tmp_path):
    folder = copy_case(tmp_path)
    step = folder / "part.step"
    source = step.read_text(encoding="ascii")
    assert ".MILLI.,.METRE." in source
    step.write_text(source.replace(".MILLI.,.METRE.", "$,.METRE."), encoding="ascii")
    rehash(folder)
    result = inspect_case(folder, tmp_path / "result")
    assert result["status"] == "invalid_fixture"
    assert "units" in result["failures"][0]


def test_independently_authored_three_bore_solid_rejected(tmp_path):
    folder = copy_case(tmp_path)
    plate = BRepPrimAPI_MakeBox(gp_Pnt(-40, -25, -4), 80, 50, 8).Shape()
    for x, y in [(-25, -15), (-25, 15), (25, -15)]:
        bore = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, -4), gp_Dir(0, 0, 1)), 3, 8).Shape()
        plate = BRepAlgoAPI_Cut(plate, bore).Shape()
    writer = STEPControl_Writer()
    writer.Transfer(plate, STEPControl_AsIs)
    writer.Write(str(folder / "part.step"))
    rehash(folder)
    result = inspect_case(folder, tmp_path / "result")
    assert result["status"] == "invalid_fixture"
    assert "cylinders=3" in result["failures"][0]


def test_whiteout_preserving_searchable_callout_rejected(tmp_path):
    folder = copy_case(tmp_path)
    original = inspect_case(folder, tmp_path / "before")
    box = original["drawing"]["callout"]["box_pt"]
    whiteout(folder, [box[0] - 2, box[1] - 2, box[2] + 2, box[3] + 2])
    assert "6.8" in PdfReader(folder / "drawing.pdf").pages[0].extract_text()
    result = inspect_case(folder, tmp_path / "after")
    assert result["status"] == "invalid_fixture"
    assert "lacks visible ink" in result["failures"][0]


def test_whiteout_preserving_stage_text_and_table_rejected(tmp_path):
    folder = copy_case(tmp_path)
    original = inspect_case(folder, tmp_path / "before")
    label = next(t for t in original["drawing"]["tokens"] if "MODEL STAGE:" in t["text"])
    whiteout(folder, label["box_pt"])
    assert "MODEL STAGE: FINISHED" in PdfReader(folder / "drawing.pdf").pages[0].extract_text()
    result = inspect_case(folder, tmp_path / "after")
    assert result["status"] == "invalid_fixture"
    assert "lacks visible ink" in result["failures"][0]


def test_png_whiteout_with_rehashed_manifest_rejected(tmp_path):
    folder = copy_case(tmp_path)
    with Image.open(folder / "drawing.png") as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, image.height), fill="white")
    image.save(folder / "drawing.png")
    rehash(folder)
    result = inspect_case(folder, tmp_path / "result")
    assert result["status"] == "invalid_fixture"
    assert "raster disagreement" in result["failures"][0]


def test_stale_or_false_visual_attestation_rejected(tmp_path):
    attestation = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    entry = next(c for c in attestation["cases"] if c["case_id"] == "pk-7a1c")
    entry["pdf_sha256"] = "0" * 64
    result = inspect_case(PUBLIC / "pk-7a1c", tmp_path / "result", attestation)
    assert result["status"] == "invalid_fixture"
    assert "stale visual attestation" in result["failures"][0]


def test_unsupported_schema_distinct_from_invalid_fixture(tmp_path):
    folder = copy_case(tmp_path)
    packet = json.loads((folder / "packet.json").read_text(encoding="utf-8"))
    packet["schema_version"] = "future.99"
    write_json(folder / "packet.json", packet)
    result = inspect_case(folder, tmp_path / "result")
    assert result["status"] == "unsupported"
    assert "expected_conclusion" not in result
