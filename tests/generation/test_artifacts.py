from pathlib import Path
import pytest
from build123d import import_step
from PIL import Image
from pypdf import PdfReader
from rfqfuzz.v1.contracts import read_packet
from rfqfuzz.v1.generation import generate_case


@pytest.mark.parametrize("family", ["plate", "bore_block", "pocket_block"])
def test_real_public_artifact_triplets(tmp_path, family):
    packet = generate_case(tmp_path / family, "pk-0123456789ab", family)
    assert read_packet(tmp_path / family) == packet
    assert import_step(tmp_path / family / "part.step").is_valid
    assert "PT-001 REV A" in (tmp_path / family / "part.step").read_text()
    pdf = PdfReader(tmp_path / family / "drawing.pdf")
    assert len(pdf.pages) == 1 and not pdf.pages[0].images
    text = pdf.pages[0].extract_text()
    for label in ["DRAWING ID = PT-001", "DRAWING REV = A", "UNITS = mm", "MATERIAL = 6061-T6", "SURFACE ROUGHNESS = 3.20 um", "PLAN (+Z)", "SECTION A-A (X-Z)"]:
        assert label in text
    if family == "bore_block":
        assert "H1 DEPTH = 24.00 mm" in text and "C1 DEPTH = 4.00 mm" in text
    elif family == "pocket_block":
        assert "P1 DEPTH = 12.00 mm" in text and "W1 THICKNESS = 5.00 mm" in text
    image = Image.open(tmp_path / family / "drawing.png")
    assert image.size == (2339, 1653)
    assert image.convert("L").getextrema() == (0, 255)
    assert packet["render"]["dpi"] == 200
    assert set(p.name for p in (tmp_path / family).iterdir()) == {"part.step", "drawing.pdf", "drawing.png", "packet.json"}


def test_authoritative_equivalent_inches_are_converted_and_visible(tmp_path):
    generate_case(tmp_path / "inches", "pk-0123456789ab", "plate", drawing_overrides={"drawing_units": "in"})
    text = PdfReader(tmp_path / "inches" / "drawing.pdf").pages[0].extract_text()
    assert "H1 DIAMETER = 0.2362 +/- 0.0020 in" in text
    assert "ENVELOPE = 3.1496 x 1.9685 x 0.3150 in" in text


def test_ref_sparse_and_overflow_edit_refusals(tmp_path):
    generate_case(tmp_path / "ref", "pk-0123456789ab", "plate", drawing_overrides={"diameter_ref": True})
    assert "0.05 mm REF" in PdfReader(tmp_path / "ref" / "drawing.pdf").pages[0].extract_text()
    generate_case(tmp_path / "sparse", "pk-0123456789ab", "plate", drawing_overrides={"sparse": True}, context_overrides={"authority": {"dimensions": "step"}})
    assert "H1 DIAMETER" not in PdfReader(tmp_path / "sparse" / "drawing.pdf").pages[0].extract_text()
    with pytest.raises(ValueError, match="not empty"):
        generate_case(tmp_path / "ref", "pk-0123456789ab", "plate")
    with pytest.raises(ValueError, match="unsupported drawing"):
        generate_case(tmp_path / "unknown", "pk-0123456789ab", "plate", drawing_overrides={"hidden_label": True})
    with pytest.raises(ValueError, match="bounded visible|too wide"):
        generate_case(tmp_path / "overflow", "pk-0123456789ab", "plate", drawing_overrides={"extra_notes": ["LONG NOTE = " + "X" * 100]})


def test_scoped_group_excludes_other_equal_diameter_bores(tmp_path):
    p = generate_case(tmp_path / "subset", "pk-0123456789ab", "plate", drawing_overrides={"h1_group_members": [0, 1], "h1_count": 2})
    text = PdfReader(tmp_path / "subset" / "drawing.pdf").pages[0].extract_text()
    assert len(p["features"][0]["centers_mm"]) == 2
    assert text.count("OTHER") == 2
    assert "H1 COUNT = 2" in text and "H1.3" not in text
