"""Independent final-artifact reader for the frozen, finite M0 contract.

This module intentionally imports no generation code. OCCT remains a disclosed
common-mode dependency. Raster ink is a visibility check, not character OCR;
coordinator inspection of the retained crops is part of the M0 oracle.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from pypdf import PdfReader
from pypdf.errors import PdfReadError
import pypdfium2 as pdfium
from OCP.Bnd import Bnd_Box
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TColStd import TColStd_SequenceOfAsciiString
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

from .contracts import OBLIGATION, VERSION, read_packet, sha256, write_json

LENGTH_TOL_MM = 1e-6
VOLUME_TOL_MM3 = 1e-5
RENDER_DPI = 200
CENTERS = [(-25.0, -15.0), (-25.0, 15.0), (25.0, -15.0), (25.0, 15.0)]


class UnsupportedInput(ValueError):
    """Known input outside this finite reader, distinct from corrupt fixture."""


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _near(actual, expected, tolerance=LENGTH_TOL_MM):
    return abs(actual - expected) <= tolerance


def _bbox(shape):
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box, False, False)
    return list(box.Get())


def measure_step(path):
    """Reopen STEP directly through OCCT and derive simple-feature measurements."""
    path = Path(path)
    source = path.read_text(encoding="ascii")
    _require(source.lstrip().startswith("ISO-10303-21;"), "invalid STEP signature")
    _require("END-ISO-10303-21;" in source, "truncated STEP")
    reader = STEPControl_Reader()
    _require(reader.ReadFile(str(path)) == IFSelect_RetDone, "STEP reader failed")
    length, angle, solid_angle = (TColStd_SequenceOfAsciiString() for _ in range(3))
    reader.FileUnits(length, angle, solid_angle)
    units = [length.Value(i).ToCString() for i in range(1, length.Length() + 1)]
    _require(units and set(units) <= {"millimetre", "millimeter"}, f"unsupported STEP length units: {units}")
    _require(re.search(r"SI_UNIT\s*\(\s*\.MILLI\.\s*,\s*\.METRE\.\s*\)", source) is not None,
             "STEP does not explicitly declare millimetres")
    _require(reader.TransferRoots() == 1, "STEP must transfer exactly one root")
    shape = reader.OneShape()
    _require(not shape.IsNull(), "STEP contains null shape")
    valid = BRepCheck_Analyzer(shape).IsValid()
    _require(valid, "STEP BRep is invalid")
    ex = TopExp_Explorer(shape, TopAbs_SOLID)
    solid_count = 0
    while ex.More():
        solid_count += 1
        ex.Next()
    _require(solid_count == 1, f"expected one solid; observed {solid_count}")
    bbox = _bbox(shape)
    envelope = [bbox[i + 3] - bbox[i] for i in range(3)]
    _require(all(_near(a, b) for a, b in zip(envelope, [80, 50, 8])), f"wrong plate envelope: {envelope}")
    _require(all(_near(a, b) for a, b in zip(bbox[:3], [-40, -25, -4])), f"wrong plate origin: {bbox[:3]}")
    properties = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, properties, True, False, False)
    volume = properties.Mass()
    analytic = 80 * 50 * 8 - 4 * math.pi * 3**2 * 8
    cylinders, plane_count, other = [], 0, []
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        face = TopoDS.Face_s(ex.Current())
        surface = BRepAdaptor_Surface(face, True)
        kind = surface.GetType()
        if kind == GeomAbs_Cylinder:
            cylinder = surface.Cylinder()
            loc, axis = cylinder.Location(), cylinder.Axis().Direction()
            bounds = _bbox(face)
            props = GProp_GProps()
            BRepGProp.SurfaceProperties_s(face, props, False, False)
            cylinders.append({
                "radius_mm": cylinder.Radius(), "diameter_mm": cylinder.Radius() * 2,
                "axis": [axis.X(), axis.Y(), axis.Z()],
                "center_xy_mm": [loc.X(), loc.Y()], "z_bounds_mm": [bounds[2], bounds[5]],
                "depth_mm": bounds[5] - bounds[2], "surface_area_mm2": props.Mass(),
                "u_span_rad": surface.LastUParameter() - surface.FirstUParameter(),
            })
        elif kind == GeomAbs_Plane:
            plane_count += 1
        else:
            other.append(str(kind))
        ex.Next()
    _require(len(cylinders) == 4 and plane_count == 6 and not other,
             f"unexpected topology: cylinders={len(cylinders)}, planes={plane_count}, other={other}")
    _require(_near(volume, analytic, VOLUME_TOL_MM3), f"volume differs from analytic four-bore plate: {volume}")
    cylinders.sort(key=lambda c: tuple(c["center_xy_mm"]))
    for c, center in zip(cylinders, CENTERS):
        _require(_near(c["radius_mm"], 3), "wrong bore radius")
        _require(all(_near(a, b) for a, b in zip(c["center_xy_mm"], center)), "wrong bore group centers")
        _require(_near(abs(c["axis"][2]), 1) and _near(c["axis"][0], 0) and _near(c["axis"][1], 0), "bore axis not Z")
        _require(_near(c["z_bounds_mm"][0], -4) and _near(c["z_bounds_mm"][1], 4), "bore is not through plate")
        _require(_near(c["u_span_rad"], 2 * math.pi), "partial cylindrical wall")
        _require(_near(c["surface_area_mm2"], 2 * math.pi * 3 * 8, VOLUME_TOL_MM3), "cylinder area mismatch")
    return {"reader": "OCP.STEPControl_Reader", "units": units, "brep_valid": valid,
            "solid_count": solid_count, "bbox_mm": bbox, "envelope_mm": envelope,
            "volume_mm3": volume, "analytic_volume_mm3": analytic,
            "volume_error_mm3": volume - analytic, "plane_count": plane_count,
            "cylinders": cylinders, "length_tolerance_mm": LENGTH_TOL_MM,
            "volume_tolerance_mm3": VOLUME_TOL_MM3}


def _point(tm, cm, x=0, y=0):
    tx, ty = x * tm[0] + y * tm[2] + tm[4], x * tm[1] + y * tm[3] + tm[5]
    return tx * cm[0] + ty * cm[2] + cm[4], tx * cm[1] + ty * cm[3] + cm[5]


def _text_box(text, cm, tm, fontsize):
    # Font metric estimate is used only to select an ink region, never to read
    # numeric dimensions from pixels. Generous margins are retained in crops.
    width = sum(0.28 if c in " .,:;iIl1" else 0.62 for c in text) * fontsize
    corners = [_point(tm, cm, x, y) for x in (-0.8, width + 1.2) for y in (-fontsize * 0.22, fontsize * 1.05)]
    return [min(p[0] for p in corners), min(p[1] for p in corners), max(p[0] for p in corners), max(p[1] for p in corners)]


def _raster_box(box, image, page_size):
    sx, sy = image.width / page_size[0], image.height / page_size[1]
    return (max(0, math.floor(box[0] * sx)), max(0, math.floor((page_size[1] - box[3]) * sy)),
            min(image.width, math.ceil(box[2] * sx)), min(image.height, math.ceil((page_size[1] - box[1]) * sy)))


def _ink_agreement(a, b):
    _require(abs(a.width - b.width) <= 1 and abs(a.height - b.height) <= 1, "PNG page dimensions mismatch")
    b = b.resize(a.size)
    ma = np.asarray(a.convert("L")) < 160
    mb = np.asarray(b.convert("L")) < 160
    da = np.asarray(Image.fromarray(ma).filter(ImageFilter.MaxFilter(5))) != 0
    db = np.asarray(Image.fromarray(mb).filter(ImageFilter.MaxFilter(5))) != 0
    missing = int(np.count_nonzero(ma & ~db))
    extra = int(np.count_nonzero(mb & ~da))
    ratio = (missing + extra) / max(1, int(ma.sum() + mb.sum()))
    _require(ratio < 0.015, f"PNG/PDF raster disagreement: {ratio:.6f}")
    return {"method": "binary ink <160 with 2-pixel dilation for renderer antialiasing", "unmatched_ink_ratio": ratio,
            "limit": 0.015, "pdf_ink_pixels": int(ma.sum()), "png_ink_pixels": int(mb.sum())}


def inspect_drawing(pdf_path, png_path, outdir):
    pdf_path, png_path, outdir = Path(pdf_path), Path(png_path), Path(outdir)
    _require(pdf_path.read_bytes().startswith(b"%PDF-"), "invalid PDF signature")
    _require(png_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), "invalid PNG signature")
    reader = PdfReader(pdf_path, strict=True)
    _require(not reader.is_encrypted and len(reader.pages) == 1, "expected one unencrypted drawing page")
    page = reader.pages[0]
    _require(int(page.get("/Rotate", 0)) == 0, "unsupported rotated page")
    size = [float(page.mediabox.width), float(page.mediabox.height)]
    _require(size[0] <= 900 and size[1] <= 900, "drawing page limit exceeded")
    tokens = []
    def visitor(text, cm, tm, font, fontsize):
        if text.strip():
            _require("\n" not in text.strip(), "unsupported multiline PDF text item")
            tokens.append({"text": text.strip(), "origin_pt": list(_point(tm, cm)), "font_size_pt": fontsize,
                           "box_pt": _text_box(text.strip(), cm, tm, fontsize)})
    text = page.extract_text(visitor_text=visitor)
    document = pdfium.PdfDocument(str(pdf_path))
    try:
        rendered = document[0].render(scale=RENDER_DPI / 72).to_pil().convert("RGB")
    finally:
        document.close()
    outdir.mkdir(parents=True, exist_ok=True)
    rendered.save(outdir / "rerender.png")
    with Image.open(png_path) as shipped:
        _require(shipped.width * shipped.height < 20_000_000, "PNG size limit exceeded")
        agreement = _ink_agreement(rendered, shipped)
    # Draftwright centers visible note-row paths but left-aligns its invisible
    # search labels at the note table origin. Their X positions therefore are
    # *not* glyph coordinates. Associate those labels to the complete interior
    # row, explicitly excluding border rules; retain that limitation.
    notes = [t for t in tokens if t["text"] == "NOTES" or re.match(r"^\d+  ", t["text"])]
    if notes:
        notes_left = min(t["box_pt"][0] for t in notes)
        notes_right = max(t["box_pt"][2] for t in notes)
        for token in notes:
            token["box_pt"][0], token["box_pt"][2] = notes_left, min(notes_right, size[0] - 25)
            token["position_association"] = "note-table row interior; search-label X does not locate centered visible glyphs"
    # Every extracted label has ink at its actual PDF position. Retain separate
    # count/diameter/tolerance/THRU crops so a searchable whiteout cannot pass.
    for i, token in enumerate(tokens):
        pixel_box = _raster_box(token["box_pt"], rendered, size)
        region = rendered.crop(pixel_box)
        ink = np.asarray(region.convert("L")) < 160
        if token in notes and ink.size:
            # Exclude any long border rule at crop edges. A text whiteout that
            # preserves the table and search layer must still have zero ink.
            ink[np.count_nonzero(ink, axis=1) > ink.shape[1] * 0.75, :] = False
        token["raster_box_px"] = list(pixel_box)
        token["ink_pixels"] = int(ink.sum())
        token["ink_fraction"] = float(ink.mean()) if ink.size else 0
        _require(token["ink_pixels"] >= 15 and token["ink_fraction"] > 0.008,
                 f"PDF searchable label lacks visible ink: {token['text']!r}")
        region.save(outdir / f"label-{i:02d}.png")
        token["crop"] = f"label-{i:02d}.png"
    thru = [t for t in tokens if t["text"] == "THRU"]
    _require(len(thru) == 1, "expected one unambiguous THRU group callout")
    row = sorted([t for t in tokens if abs(t["origin_pt"][1] - thru[0]["origin_pt"][1]) < 0.5], key=lambda t: t["origin_pt"][0])
    joined = " ".join(t["text"] for t in row)
    # Actual Unicode is × / ø / ±. A Windows console may display replacement
    # characters, so retain JSON in UTF-8 rather than parse terminal output.
    match = re.fullmatch(r"(\d+)\s*[xX×]\s+[Øø⌀]\s+(\d+(?:\.\d+)?)\s+(?:±|\+/-)\s*(\d+(?:\.\d+)?)\s+THRU", joined)
    _require(match is not None, f"unsupported or ambiguous bore callout text: {joined!r}")
    count, diameter, tolerance = int(match[1]), float(match[2]), float(match[3])
    _require(count == 4, f"group callout count differs from four STEP bores: {count}")
    _require(_near(tolerance, 0.05), f"unsupported M0 tolerance {tolerance}")
    combined = [min(t["box_pt"][0] for t in row), min(t["box_pt"][1] for t in row),
                max(t["box_pt"][2] for t in row), max(t["box_pt"][3] for t in row)]
    rendered.crop(_raster_box(combined, rendered, size)).save(outdir / "callout.png")
    return {"parser": "pypdf.PdfReader", "renderer": "PDFium (independent of shipped Poppler PNG)",
            "render_dpi": RENDER_DPI, "page_size_pt": size, "raster_size_px": list(rendered.size),
            "text": text, "tokens": tokens, "callout": {"search_text": joined, "count": count,
            "diameter_mm": diameter, "symmetric_tolerance_mm": tolerance, "through": True,
            "box_pt": combined, "crop": "callout.png", "symbol_decode": "Unicode text extracted; raster visual attestation also required"},
            "png_pdf_agreement": agreement, "visual_attestation_required": True}


def _context_checks(packet, drawing, measured_diameter_mm):
    text = drawing["text"].upper()
    m = packet["manufacturing"]
    _require(packet["profile"]["id"] == "m0-package-consistency" and packet["profile"]["synthetic"] is True,
             "unexpected M0 profile")
    _require(packet["obligations"] == [OBLIGATION], "unsupported M0 obligation set")
    _require(len(packet["features"]) == 1 and packet["features"][0]["id"] == "H1", "unsupported feature mapping")
    _require(sorted(tuple(c[:2]) for c in packet["features"][0]["centers_mm"]) == CENTERS, "public group center mismatch")
    _require(m["material"] == "6061-T6" and m["finish"] == "none", "unsupported material/finish premise")
    for label in ("ALL DIMENSIONS IN MM", "H1 = ALL FOUR Z THROUGH BORES", "FINISH: NONE", "6061-T6",
                  f"MODEL STAGE: {m['model_stage'].upper()}", f"DRAWING STAGE: {m['drawing_stage'].upper()}",
                  "VIEWS SHOW SUPPLIED MODEL AT MODEL STAGE",
                  packet["part_id"]):
        _require(label in text, f"public context absent from drawing: {label}")
    assoc = packet["release_association"]
    _require(assoc["model_id"] == assoc["drawing_id"] == packet["part_id"], "part identity mismatch")
    _require([assoc["model_revision"], assoc["drawing_revision"]] in assoc["permitted_pairs"], "unapproved revision association")
    _require(any(t["text"] == assoc["drawing_revision"] for t in drawing["tokens"]), "visible drawing revision absent")
    _require(all(any(t["text"] == str(d) for t in drawing["tokens"]) for d in (80, 50, 8)), "visible envelope dimension text absent")
    transition = m["transition"]
    d = drawing["callout"]["diameter_mm"]
    tolerance = drawing["callout"]["symmetric_tolerance_mm"]
    if m["model_stage"] == m["drawing_stage"]:
        _require(transition is None, "same-stage contract has unexplained transition")
        _require("DRAWING AND MODEL APPLY AT SAME STAGE" in text, "same-stage note absent")
        return "supported_clear" if d - tolerance <= measured_diameter_mm <= d + tolerance else "contradiction"
    _require(m["model_stage"] == "intermediate" and m["drawing_stage"] == "finished", "unsupported stage transition")
    _require(isinstance(transition, dict), "missing explicit later-stage transition")
    _require("REAM" in text and "H1" in text, "ream transition is not visibly declared")
    _require(transition.get("operation") == "ream" and transition.get("feature_id") == "H1"
             and transition.get("from_stage") == "intermediate" and transition.get("to_stage") == "finished"
             and transition.get("target") == "drawing bore callout", "transition does not explicitly apply reaming to H1")
    _require(d - tolerance > measured_diameter_mm, "ream target must exceed measured intermediate bore")
    return "supported_clear"


def _attest(folder, packet, drawing, attestation):
    if attestation is None:
        return None
    if isinstance(attestation, (str, Path)):
        attestation = json.loads(Path(attestation).read_text(encoding="utf-8"))
    entries = [c for c in attestation["cases"] if c["case_id"] == packet["case_id"]]
    _require(len(entries) == 1, "missing or duplicated visual attestation")
    a = entries[0]
    _require(a["pdf_sha256"] == sha256(folder / "drawing.pdf") and a["png_sha256"] == sha256(folder / "drawing.png"), "stale visual attestation hashes")
    callout = drawing["callout"]
    _require(a["visible_count"] == callout["count"] and _near(a["visible_nominal_mm"], callout["diameter_mm"])
             and _near(a["visible_tolerance_mm"], callout["symmetric_tolerance_mm"]), "visual/text callout disagreement")
    _require(a["visible_diameter_symbol"] and a["visible_plus_minus_symbol"] and a["visible_thru"]
             and a["legible_unclipped"], "symbols/legibility not visually attested")
    _require(a["model_stage"] == packet["manufacturing"]["model_stage"] and a["drawing_stage"] == packet["manufacturing"]["drawing_stage"], "visual stage mismatch")
    _require(a["visible_view_stage_note"] == "VIEWS SHOW SUPPLIED MODEL AT MODEL STAGE", "view-stage note not visually attested")
    expected_context = "DRAWING AND MODEL APPLY AT SAME STAGE" if a["model_stage"] == a["drawing_stage"] else "REAM AFTER MODEL STAGE TO DRAWING SIZE"
    _require(a["visible_context"] == expected_context, "stage/transition note not visually attested")
    _require(sorted(a["envelope_labels_mm"]) == [8, 50, 80], "visual envelope labels mismatch")
    return a


def inspect_case(folder, outdir, attestation=None):
    """Write a private observed record, with invalid cases quarantined as failures."""
    folder, outdir = Path(folder), Path(outdir)
    record = {"schema_version": VERSION, "case_id": folder.name, "status": "invalid_fixture", "failures": []}
    try:
        _require(sorted(p.name for p in folder.iterdir()) == ["drawing.pdf", "drawing.png", "packet.json", "part.step"],
                 "public case must contain only the four declared files")
        raw_packet = json.loads((folder / "packet.json").read_text(encoding="utf-8"))
        if "schema_version" in raw_packet and raw_packet["schema_version"] != VERSION:
            raise UnsupportedInput("unsupported PacketSpec version")
        packet = read_packet(folder)
        record["case_id"] = packet["case_id"]
        _require(packet["case_id"] == folder.name, "case ID/folder mismatch")
        record["packet_sha256"] = sha256(folder / "packet.json")
        record["geometry"] = measure_step(folder / "part.step")
        record["drawing"] = inspect_drawing(folder / "drawing.pdf", folder / "drawing.png", outdir)
        record["manufacturing"] = packet["manufacturing"]
        conclusion = _context_checks(packet, record["drawing"], record["geometry"]["cylinders"][0]["diameter_mm"])
        record["visual_attestation"] = _attest(folder, packet, record["drawing"], attestation)
        record["status"] = "valid" if record["visual_attestation"] is not None else "pending_visual_attestation"
        if record["status"] == "valid":
            record["expected_conclusion"] = conclusion
        record["evidence"] = {"inspection": str(outdir / "inspection.json"), "rerender": str(outdir / "rerender.png"),
                              "callout": str(outdir / "callout.png")}
        record["limits"] = ["finite synthetic M0 geometry only", "shared OCCT kernel common-mode risk",
                            "raster ink checks are not OCR; visual attestation remains required", "no process feasibility conclusion"]
    except UnsupportedInput as exc:
        record["status"] = "unsupported"
        record["failures"].append(str(exc))
    except (ValueError, OSError, KeyError, TypeError, RuntimeError, AssertionError, PdfReadError) as exc:
        record["failures"].append(f"{type(exc).__name__}: {exc}")
    write_json(outdir / "inspection.json", record)
    return record


def validate_suite(public_root, outdir, attestation=None):
    """Validate three observed cases and permitted deltas without private labels."""
    public_root, outdir = Path(public_root), Path(outdir)
    folders = sorted(p for p in public_root.iterdir() if p.is_dir())
    cases = [inspect_case(folder, outdir / folder.name, attestation) for folder in folders]
    failures = []
    invariants = {}
    if len(cases) != 3:
        failures.append("M0 suite requires exactly three cases")
    if any(c["status"] == "invalid_fixture" for c in cases):
        failures.append("suite contains quarantined invalid fixture")
    pending = any(c["status"] == "pending_visual_attestation" for c in cases)
    unsupported = any(c["status"] == "unsupported" for c in cases)
    if pending:
        failures.append("suite awaits required visual attestation")
    if unsupported:
        failures.append("suite contains unsupported input")
    if not failures:
        signatures = [{k: c["geometry"][k] for k in ("bbox_mm", "volume_mm3", "cylinders", "plane_count", "solid_count")} for c in cases]
        invariants["identical_measured_geometry"] = all(s == signatures[0] for s in signatures)
        invariants["one_contradiction_two_supported_clear"] = sorted(c["expected_conclusion"] for c in cases) == ["contradiction", "supported_clear", "supported_clear"]
        same_stage = [c for c in cases if c["manufacturing"]["model_stage"] == c["manufacturing"]["drawing_stage"]]
        invariants["two_same_stage_one_transition"] = len(same_stage) == 2
        if len(same_stage) == 2:
            a, b = same_stage
            # Numeric annotation is the only semantic drawing delta between
            # same-stage twins. Draftwright permits nonsemantic layout reflow.
            normalize = lambda d: sorted(re.sub(r"\b(?:6\.8|6(?:\.0)?)\b", "BORE", t["text"]) if "0.05" in t["text"] else t["text"] for t in d["tokens"])
            invariants["same_stage_only_bore_annotation_changed"] = normalize(a["drawing"]) == normalize(b["drawing"])
        def transition_text(case):
            replacements = {"3  MODEL STAGE: INTERMEDIATE": "3  MODEL STAGE: FINISHED",
                            "7  H1: REAM AFTER MODEL STAGE TO DRAWING SIZE": "7  H1: DRAWING AND MODEL APPLY AT SAME STAGE"}
            return sorted(replacements.get(t["text"], t["text"]) for t in case["drawing"]["tokens"])
        transition_cases = [c for c in cases if c["manufacturing"]["model_stage"] != c["manufacturing"]["drawing_stage"]]
        contradiction_cases = [c for c in cases if c["expected_conclusion"] == "contradiction"]
        invariants["transition_only_exact_stage_notes_changed"] = len(transition_cases) == len(contradiction_cases) == 1 and transition_text(transition_cases[0]) == transition_text(contradiction_cases[0])
        packets = [read_packet(f) for f in folders]
        invariant_fields = ("part_id", "release_association", "units", "authority", "profile", "setup", "features", "obligations")
        invariants["public_context_invariants"] = all(all(p[k] == packets[0][k] for k in invariant_fields) for p in packets)
        for name, passed in invariants.items():
            if not passed:
                failures.append(f"suite invariant failed: {name}")
    status = "valid" if not failures else "invalid_fixture"
    if len(cases) == 3 and not any(c["status"] == "invalid_fixture" for c in cases):
        status = "unsupported" if unsupported else "pending_visual_attestation" if pending else status
    record = {"schema_version": VERSION, "status": status, "cases": cases,
              "invariants": invariants, "failures": failures, "visual_attestation_required": True}
    write_json(outdir / "oracle.json", record)
    return record
