"""Independent final-artifact oracle for the finite v1 annotation vocabulary.

No generator or reviewer code is imported. STEP is reopened through direct OCP;
analytic volume uses measured surfaces, not private generator parameters. Shared
OCCT is a common-mode limitation. Native readers run in a bounded child process.
Raster/glyph checks supplement, rather than replace, hash-bound visual review.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

from .contracts import VERSION, digest, load_json, read_packet, require, sha256, validate_oracle, write_json

LENGTH_TOL_MM = 1e-6
VOLUME_TOL_MM3 = 1e-4
RENDER_DPI = 200
PARSER_TIMEOUT_SECONDS = 60
OPERATORS = {"diameter_consistency": "O01", "count_consistency": "O02", "unit_consistency": "O03",
             "material_consistency": "O04", "required_representation": "O05", "release_association": "O06",
             "wall_thickness": "A01", "bore_ratio": "A02", "setup_envelope": "A03", "finish_stage": "A04"}
ALIASES = {"6061-T6": "6061-T6", "AL6061-T6": "6061-T6", "AL 6061-T6": "6061-T6",
           "7075-T6": "7075-T6", "304 STAINLESS": "304 stainless", "ABS": "ABS", "DELRIN": "Delrin", "POM": "Delrin"}


class UnsupportedInput(ValueError):
    """Readable input beyond the intentionally finite geometry/annotation reader."""


def near(a, b, tolerance=LENGTH_TOL_MM):
    return abs(a - b) <= tolerance


def rounded(value):
    # Numeric boundary noise is bounded by the recorded length tolerance.
    return round(float(value), 6)


def number(value):
    return f"{rounded(value):.6f}".rstrip("0").rstrip(".") or "0"


def _bbox(shape):
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box, False, False)
    return list(box.Get())


def measure_step(path, family, features):
    """Derive closed-form cavity geometry from actual exported faces."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
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

    path = Path(path)
    source = path.read_text(encoding="ascii")
    require(source.lstrip().startswith("ISO-10303-21;"), "invalid STEP signature")
    require("END-ISO-10303-21;" in source, "truncated STEP")
    reader = STEPControl_Reader()
    require(reader.ReadFile(str(path)) == IFSelect_RetDone, "STEP reader failed")
    unit_sequences = [TColStd_SequenceOfAsciiString() for _ in range(3)]
    reader.FileUnits(*unit_sequences)
    units = [unit_sequences[0].Value(i).ToCString() for i in range(1, unit_sequences[0].Length() + 1)]
    require(units and set(units) <= {"millimetre", "millimeter"}, f"unsupported STEP length units: {units}")
    require(re.search(r"SI_UNIT\s*\(\s*\.MILLI\.\s*,\s*\.METRE\.\s*\)", source), "STEP units not explicitly millimetres")
    require(reader.TransferRoots() == 1, "STEP must contain one transferable root")
    shape = reader.OneShape()
    require(not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid(), "invalid STEP BRep")
    ex = TopExp_Explorer(shape, TopAbs_SOLID)
    solids = 0
    while ex.More():
        solids += 1
        ex.Next()
    require(solids == 1, f"expected one solid, observed {solids}")
    bounds = _bbox(shape)
    envelope = [bounds[i + 3] - bounds[i] for i in range(3)]
    if not (20 - LENGTH_TOL_MM <= envelope[0] <= 240 + LENGTH_TOL_MM and
            20 - LENGTH_TOL_MM <= envelope[1] <= 160 + LENGTH_TOL_MM and
            3 - LENGTH_TOL_MM <= envelope[2] <= 80 + LENGTH_TOL_MM):
        raise UnsupportedInput("geometry envelope outside documented v1 bounds")
    require(all(near(bounds[i], -envelope[i] / 2) for i in range(3)), "unsupported translated/oriented solid")
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props, True, False, False)
    volume = props.Mass()
    cylinders, planes = [], []
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        face = TopoDS.Face_s(ex.Current())
        surface = BRepAdaptor_Surface(face, True)
        b = _bbox(face)
        if surface.GetType() == GeomAbs_Cylinder:
            cyl = surface.Cylinder()
            center, axis = cyl.Location(), cyl.Axis().Direction()
            require(near(abs(axis.Z()), 1) and near(axis.X(), 0) and near(axis.Y(), 0), "cylinder axis must be Z")
            require(near(surface.LastUParameter() - surface.FirstUParameter(), 2 * math.pi), "partial cylindrical wall")
            cylinders.append({"diameter_mm": 2 * cyl.Radius(), "center_xy_mm": [center.X(), center.Y()], "z_bounds_mm": [b[2], b[5]]})
        elif surface.GetType() == GeomAbs_Plane:
            normal = surface.Plane().Axis().Direction()
            require(any(near(abs(v), 1) for v in (normal.X(), normal.Y(), normal.Z())), "nonorthogonal plane")
            planes.append({"bbox_mm": b, "normal": [normal.X(), normal.Y(), normal.Z()]})
        else:
            raise UnsupportedInput("unsupported nonplanar/noncylindrical face")
        ex.Next()
    cylinders.sort(key=lambda c: (c["diameter_mm"], *c["center_xy_mm"]))
    result = {"reader": "OCP.STEPControl_Reader", "units": units, "solid_count": solids,
              "bbox_mm": bounds, "envelope_mm": list(map(rounded, envelope)), "volume_mm3": volume,
              "cylinders": cylinders, "planes": planes, "length_tolerance_mm": LENGTH_TOL_MM,
              "volume_tolerance_mm3": VOLUME_TOL_MM3}
    cavity = 0.
    if family == "plate":
        require(len(cylinders) in {1, 2, 4} and len(planes) == 6, "unsupported plate topology")
        for cyl in cylinders:
            require(near(cyl["z_bounds_mm"][0], bounds[2]) and near(cyl["z_bounds_mm"][1], bounds[5]), "plate bore is not through")
            cavity += math.pi * (cyl["diameter_mm"] / 2) ** 2 * envelope[2]
        group = next((f for f in features if f["id"] == "H1"), None)
        require(group is not None and bool(group.get("centers_mm")), "missing scoped H1 center mapping")
        mapped = []
        for center in group["centers_mm"]:
            hits = [c for c in cylinders if all(near(a, b) for a, b in zip(c["center_xy_mm"], center[:2]))]
            require(len(hits) == 1 and hits[0] not in mapped, "ambiguous/unmapped H1 membership")
            mapped.append(hits[0])
        require(all(near(c["diameter_mm"], mapped[0]["diameter_mm"]) for c in mapped), "mixed-diameter H1 group unsupported")
        result.update(bore_diameter_mm=rounded(mapped[0]["diameter_mm"]), bore_depth_mm=rounded(envelope[2]),
                      h1_count=len(mapped), total_bore_count=len(cylinders))
    elif family == "bore_block":
        require(len(cylinders) == 2 and len(planes) == 8, "unsupported blind/counterbore topology")
        small, large = cylinders
        require(all(near(x, 0) for c in cylinders for x in c["center_xy_mm"]), "counterbore is not central/coaxial")
        for feature_id in ("H1", "C1"):
            mapping = [f for f in features if f["id"] == feature_id]
            require(len(mapping) == 1 and mapping[0].get("centers_mm") == [[0., 0., 0.]], "unmapped public blind/counterbore correspondence")
        require(small["diameter_mm"] < large["diameter_mm"] and near(large["z_bounds_mm"][1], bounds[5])
                and near(small["z_bounds_mm"][1], large["z_bounds_mm"][0]), "disconnected or reversed counterbore steps")
        depth = bounds[5] - small["z_bounds_mm"][0]
        cb_depth = bounds[5] - large["z_bounds_mm"][0]
        require(0 < cb_depth < depth < envelope[2], "blind bore must leave floor and distinct step")
        cavity = math.pi * (small["diameter_mm"] / 2) ** 2 * depth + math.pi * ((large["diameter_mm"] / 2) ** 2 - (small["diameter_mm"] / 2) ** 2) * cb_depth
        result.update(bore_diameter_mm=rounded(small["diameter_mm"]), bore_depth_mm=rounded(depth), h1_count=1,
                      counterbore_diameter_mm=rounded(large["diameter_mm"]), counterbore_depth_mm=rounded(cb_depth))
    elif family == "pocket_block":
        require(not cylinders and len(planes) == 11, "unsupported open-pocket topology")
        floors = [p for p in planes if near(abs(p["normal"][2]), 1) and bounds[2] + LENGTH_TOL_MM < p["bbox_mm"][2] < bounds[5] - LENGTH_TOL_MM]
        require(len(floors) == 1, "ambiguous pocket floor")
        floor = floors[0]["bbox_mm"]
        mapping = [f for f in features if f["id"] == "P1"]
        actual_center = [(floor[0] + floor[3]) / 2, (floor[1] + floor[4]) / 2]
        require(len(mapping) == 1 and len(mapping[0].get("centers_mm", [])) == 1
                and all(near(a, b) for a, b in zip(actual_center, mapping[0]["centers_mm"][0][:2])), "unmapped public pocket correspondence")
        width, length, depth = floor[3] - floor[0], floor[4] - floor[1], bounds[5] - floor[2]
        wall = bounds[3] - floor[3]
        require(width > 0 and length > 0 and depth > 0 and wall >= .2 - LENGTH_TOL_MM
                and floor[0] > bounds[0] and floor[1] > bounds[1] and floor[4] < bounds[4], "pocket lacks bounded open cavity/side walls")
        cavity = width * length * depth
        result.update(pocket_width_mm=rounded(width), pocket_length_mm=rounded(length), pocket_depth_mm=rounded(depth), wall_mm=rounded(wall))
    else:
        raise UnsupportedInput("unknown bounded family")
    analytic = math.prod(envelope) - cavity
    require(abs(volume - analytic) <= VOLUME_TOL_MM3, "STEP volume disagrees with independent measured-face analytic volume")
    identity = re.search(r"PRODUCT\('([^']*)','[^']*',''", source)
    require(identity is not None, "missing STEP product identity")
    result.update(analytic_volume_mm3=analytic, volume_error_mm3=volume - analytic, product_identity=identity[1])
    return result


def inspect_drawing(pdf_path, png_path, outdir):
    """Read real annotation strings and verify every glyph against rendered ink."""
    import numpy as np
    from PIL import Image, ImageFilter
    from pypdf import PdfReader
    import pypdfium2 as pdfium
    pdf_path, png_path, outdir = Path(pdf_path), Path(png_path), Path(outdir)
    require(pdf_path.read_bytes().startswith(b"%PDF-"), "invalid PDF signature")
    require(png_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), "invalid PNG signature")
    reader = PdfReader(pdf_path, strict=True)
    require(not reader.is_encrypted and len(reader.pages) == 1, "expected one unencrypted PDF page")
    page = reader.pages[0]
    require(int(page.get("/Rotate", 0)) == 0, "unsupported rotated drawing")
    size = [float(page.mediabox.width), float(page.mediabox.height)]
    require(all(0 < x <= 900 for x in size), "PDF page size limit exceeded")
    tokens = []
    def visitor(text, cm, tm, font, fontsize):
        text = text.strip()
        if not text:
            return
        require("\n" not in text and len(text) <= 8192, "unsupported multiline/oversized text item")
        x, y = tm[4] * cm[0] + tm[5] * cm[2] + cm[4], tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
        require(0 <= x <= size[0] and 0 <= y <= size[1], "clipped/off-page drawing text")
        tokens.append({"text": text, "origin_pt": [x, y], "font_size_pt": float(fontsize)})
    text = page.extract_text(visitor_text=visitor)
    require(len(tokens) <= 256 and len(text) <= 32000, "PDF annotation count limit exceeded")
    outdir.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(pdf_path))
    glyphs = []
    try:
        pdfpage = document[0]
        rendered = pdfpage.render(scale=RENDER_DPI / 72).to_pil().convert("RGB")
        tp = pdfpage.get_textpage()
        require(tp.count_chars() <= 32000, "PDF glyph count limit exceeded")
        def raster_box(box):
            return (max(0, math.floor(box[0] * rendered.width / size[0])), max(0, math.floor((size[1] - box[3]) * rendered.height / size[1])),
                    min(rendered.width, math.ceil(box[2] * rendered.width / size[0])), min(rendered.height, math.ceil((size[1] - box[1]) * rendered.height / size[1])))
        for i in range(tp.count_chars()):
            char = tp.get_text_range(i, 1)
            if not char or char.isspace():
                continue
            box = list(tp.get_charbox(i))
            require(0 <= box[0] < box[2] <= size[0] and 0 <= box[1] < box[3] <= size[1], "clipped/off-page PDF glyph")
            pixels = np.asarray(rendered.crop(raster_box(box)).convert("L"))
            ink = int(np.count_nonzero(pixels < 180))
            require(ink >= 1, f"PDF glyph lacks visible ink: {char!r} at {box}")
            glyphs.append({"char": char, "box_pt": box, "ink_pixels": ink})
        tp.close()
    finally:
        document.close()
    rendered.save(outdir / "rerender.png")
    with Image.open(png_path) as shipped:
        require(shipped.width * shipped.height <= 20_000_000, "PNG pixel limit exceeded")
        require(abs(shipped.width - rendered.width) <= 1 and abs(shipped.height - rendered.height) <= 1, "PNG page dimensions disagree with PDF")
        shipped = shipped.convert("L").resize(rendered.size)
        a, b = np.asarray(rendered.convert("L")) < 160, np.asarray(shipped) < 160
        da = np.asarray(Image.fromarray(a).filter(ImageFilter.MaxFilter(5))) != 0
        db = np.asarray(Image.fromarray(b).filter(ImageFilter.MaxFilter(5))) != 0
        ratio = int(np.count_nonzero(a & ~db) + np.count_nonzero(b & ~da)) / max(1, int(a.sum() + b.sum()))
        require(ratio < .015, f"PNG/PDF raster disagreement {ratio}")
    annotations = {}
    for i, token in enumerate(tokens):
        line = token["text"]
        if " = " not in line:
            continue
        key = line.split(" = ", 1)[0]
        require(key not in annotations or key == "MATERIAL", f"ambiguous duplicate annotation {key}")
        annotations.setdefault(key, []).append(line)
        x, y = token["origin_pt"]
        row_glyphs = [g for g in glyphs if abs(g["box_pt"][1] - y) < token["font_size_pt"] and g["box_pt"][0] >= x - 1]
        require(bool(row_glyphs), f"annotation lacks associated visible glyphs: {key}")
        box = [min(g["box_pt"][0] for g in row_glyphs), min(g["box_pt"][1] for g in row_glyphs),
               max(g["box_pt"][2] for g in row_glyphs), max(g["box_pt"][3] for g in row_glyphs)]
        # Annotation rows are 16 points apart; the exact text values are parsed
        # independently above. Crops include only associated row glyph boxes.
        token["box_pt"] = box
        token["crop"] = f"label-{i:02d}.png"
        rendered.crop(raster_box([box[0] - 2, box[1] - 2, box[2] + 2, box[3] + 2])).save(outdir / token["crop"])
    for key in ("DRAWING ID", "DRAWING REV", "UNITS", "MATERIAL", "MODEL STAGE", "DRAWING STAGE", "FINISH", "TOLERANCE STAGE"):
        require(key in annotations, f"missing required visible public context: {key}")
    return {"parser": "pypdf.PdfReader", "renderer": "PDFium independent of shipped Poppler PNG", "render_dpi": RENDER_DPI,
            "page_size_pt": size, "text": text, "tokens": tokens, "annotations": annotations,
            "glyphs_checked": len(glyphs), "glyph_visibility": "every non-whitespace PDFium tight character box has visible ink; visual attestation still required",
            "png_pdf_unmatched_ink_ratio": ratio, "visual_attestation_required": True}


def line(drawing, key):
    return drawing["annotations"].get(key, [None])[0]


def value(drawing, key):
    item = line(drawing, key)
    return item.split(" = ", 1)[1] if item else None


def witness(artifact, quote, region=None):
    result = {"artifact": artifact, "quote": quote}
    if region is not None:
        result["region"] = region
    return result


def context_witness(packet, *keys):
    values = {}
    for key in keys:
        node = packet
        for piece in key.split("."):
            node = node[piece]
        values[key] = node
    return witness("packet.json", json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def step_witness(geometry, feature, fields):
    return witness("part.step", feature + " " + "; ".join(f"{label}={number(geometry[key])}" for label, key in fields))


def _parse_dimension(drawing, key):
    item = value(drawing, key)
    if item is None:
        return None
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)(?: \+/- ([0-9]+(?:\.[0-9]+)?))? (mm|in)( REF)?", item)
    if not match:
        raise UnsupportedInput(f"unsupported numeric annotation {key}: {item}")
    scale = 25.4 if match[3] == "in" else 1
    return {"nominal_mm": float(match[1]) * scale, "tolerance_mm": float(match[2] or 0) * scale,
            "units": match[3], "ref": bool(match[4])}


def _advisory(packet, geometry, rule_id, resolved_material=None, unresolved_material=False):
    """Independent finite implementation of the public rule-card comparisons."""
    rule = next(r for r in packet["profile"]["rules"] if r["id"] == rule_id)
    contracts = {
        "A01": ("mm", "advisory", "wall_mm < class threshold; equality is clear for this rule"),
        "A02": ("dimensionless depth/diameter", "advisory", "bore_depth_mm / bore_diameter_mm > class threshold; equality is clear for this rule"),
        "A03": ("mm XYZ total occupied extent", "profile_exclusion", "any envelope_mm + stock_allowance_mm + fixture_allowance_mm axis > capacity; equality is included"),
        "A04": ("manufacturing stage", "missing_information", "explicit before_finish/after_finish first; otherwise public profile default; otherwise missing_information"),
    }
    if (rule["units"], rule["severity"], rule["comparison"]) != contracts[rule_id]:
        return "unsupported"
    m, setup, threshold = packet["manufacturing"], packet["setup"], rule["threshold"]
    materials = rule["applicability"].get("materials", {})
    if unresolved_material:
        return "missing_information"
    if resolved_material is not None:
        m = dict(m, material=resolved_material, material_class=materials.get(resolved_material))
    if m["material"] not in materials or m["material_class"] not in rule["applicability"].get("material_classes", []):
        return "missing_information"
    if materials[m["material"]] != m["material_class"]:
        return "unsupported"
    if rule_id == "A01":
        return "advisory" if geometry["wall_mm"] < threshold[m["material_class"]] else "supported_clear"
    if rule_id == "A02":
        return "advisory" if geometry["bore_depth_mm"] / geometry["bore_diameter_mm"] > threshold[m["material_class"]] else "supported_clear"
    if rule_id == "A03":
        require(threshold.get("allowance_convention") == "total_added_extent_per_axis", "unsupported occupied-extent convention")
        if setup["orientation"] != threshold["orientation"]:
            return "unsupported"
        occupied = [rounded(geometry["envelope_mm"][i] + setup["stock_allowance_mm"][i] + setup["fixture_allowance_mm"][i]) for i in range(3)]
        return "profile_exclusion" if any(a > b for a, b in zip(occupied, threshold["envelope_mm"])) else "supported_clear"
    if not m["finish"].strip() or m["finish"].casefold() in {"unknown", "unspecified", "tbd"}:
        return "missing_information"
    return "supported_clear" if m["tolerance_stage"] is not None or threshold.get("default_tolerance_stage") is not None else "missing_information"


def derive_expectations(packet, geometry, drawing):
    """Observe conclusions from public authority and actual artifact content."""
    m, authority, release = packet["manufacturing"], packet["authority"], packet["release_association"]
    for key, expected in (("MODEL STAGE", m["model_stage"]), ("DRAWING STAGE", m["drawing_stage"]), ("FINISH", m["finish"]),
                          ("TOLERANCE STAGE", m["tolerance_stage"] or "UNSPECIFIED")):
        require(value(drawing, key) == expected, f"drawing/public context disagrees: {key}")
    require(value(drawing, "UNITS") == packet["units"]["drawing"], "drawing unit declaration disagrees with public unit premise")
    require(geometry["product_identity"] == f"{release['model_id']} REV {release['model_revision']}", "STEP product identity disagrees with public association")
    unit = value(drawing, "UNITS")
    if unit not in {"mm", "in"}:
        raise UnsupportedInput("unsupported drawing units")
    env_line = value(drawing, "ENVELOPE")
    units_conclusion = "supported_clear"
    if env_line:
        match = re.fullmatch(r"([0-9.]+) x ([0-9.]+) x ([0-9.]+) (mm|in)", env_line)
        require(match is not None and match[4] == unit, "ambiguous envelope/local-unit context")
        scale = 25.4 if unit == "in" else 1
        # 4-decimal inch rounding contributes up to 0.00127 mm of uncertainty.
        display_tol = .0013 if unit == "in" else .00501
        if not all(abs(float(match[i + 1]) * scale - geometry["envelope_mm"][i]) <= display_tol + LENGTH_TOL_MM for i in range(3)):
            units_conclusion = "contradiction"
    elif authority["dimensions"] != "step":
        units_conclusion = "missing_information"
    # Check supporting finite annotations even when no separate scored duty is
    # defined for them. This catches collateral depth/pocket edits in a baseline
    # rather than quietly accepting them as an incidental reviewer problem.
    ancillary = {"H1 DEPTH": "bore_depth_mm", "C1 DIAMETER": "counterbore_diameter_mm",
                 "C1 DEPTH": "counterbore_depth_mm", "P1 WIDTH": "pocket_width_mm",
                 "P1 LENGTH": "pocket_length_mm", "P1 DEPTH": "pocket_depth_mm", "W1 THICKNESS": "wall_mm"}
    if units_conclusion != "contradiction":
        for key, metric in ancillary.items():
            if metric not in geometry or not line(drawing, key):
                continue
            observed = _parse_dimension(drawing, key)
            tolerance = .0013 if observed["units"] == "in" else .00501
            require(observed["units"] == unit and abs(observed["nominal_mm"] - geometry[metric]) <= tolerance + LENGTH_TOL_MM,
                    f"collateral visible {key} disagrees with independently measured STEP")
    if line(drawing, "H1 TYPE"):
        require(value(drawing, "H1 TYPE") == ("THROUGH" if packet["family"] == "plate" else "BLIND"), "visible bore topology disagrees with STEP family")
    # Manufacturing rules are conditional on the resolved global material.
    # Equal-authority contradictions cannot be silently resolved by privileging
    # the contract declaration. Drawing precedence selects its single resolved
    # visible declaration; material/class applicability remains the rule's map.
    declared_materials = [s.split(" = ", 1)[1] for s in drawing["annotations"]["MATERIAL"]]
    canonical_materials = [ALIASES.get(s.upper()) for s in [m["material"]] + declared_materials]
    unresolved_material = False
    resolved_material = None
    if authority["material_precedence"] == "equal":
        unresolved_material = any(s is None for s in canonical_materials) or len(set(canonical_materials)) > 1
    elif authority["material_precedence"] == "drawing":
        visible_materials = canonical_materials[1:]
        unresolved_material = any(s is None for s in visible_materials) or len(set(visible_materials)) != 1
        if not unresolved_material:
            resolved_material = visible_materials[0]
    expectations, suppressed = [], []
    for obligation in packet["obligations"]:
        category, feature = obligation["category"], obligation["feature_id"]
        operator = OPERATORS[category]
        evidence, conclusion, rule_id = [], "supported_clear", None
        if category == "unit_consistency":
            conclusion = units_conclusion
            evidence = [witness("drawing.pdf", line(drawing, "UNITS")), context_witness(packet, "units")]
            if env_line:
                evidence.append(witness("drawing.pdf", line(drawing, "ENVELOPE")))
                evidence.append(witness("part.step", "document envelope_mm=[" + ", ".join(number(x) for x in geometry["envelope_mm"]) + "]"))
        elif category == "diameter_consistency":
            if units_conclusion == "contradiction":
                suppressed.append(obligation["id"])
                continue
            d = _parse_dimension(drawing, "H1 DIAMETER")
            evidence = [step_witness(geometry, "H1", [("diameter_mm", "bore_diameter_mm"), ("count", "h1_count")]),
                        context_witness(packet, "authority.dimensions", "manufacturing.model_stage", "manufacturing.drawing_stage", "manufacturing.transition")]
            if d:
                evidence.append(witness("drawing.pdf", line(drawing, "H1 DIAMETER")))
            if authority["dimensions"] == "step" or (d and d["ref"]):
                conclusion = "supported_clear"
            elif d is None:
                conclusion = "missing_information"
            elif m["model_stage"] != m["drawing_stage"]:
                transition = m["transition"]
                if not transition:
                    conclusion = "missing_information"
                elif (m["model_stage"] == "intermediate" and m["drawing_stage"] == "finished"
                      and transition.get("operation") == "ream" and transition.get("feature_id") == "H1"
                      and transition.get("from_stage") == "intermediate" and transition.get("to_stage") == "finished"
                      and transition.get("target") in {"drawing bore callout", "drawing H1 diameter callout"} and line(drawing, "TRANSITION")):
                    evidence.append(witness("drawing.pdf", line(drawing, "TRANSITION")))
                    conclusion = "supported_clear" if d["nominal_mm"] - d["tolerance_mm"] > geometry["bore_diameter_mm"] else "contradiction"
                else:
                    conclusion = "unsupported"
            else:
                conclusion = "supported_clear" if d["nominal_mm"] - d["tolerance_mm"] - LENGTH_TOL_MM <= geometry["bore_diameter_mm"] <= d["nominal_mm"] + d["tolerance_mm"] + LENGTH_TOL_MM else "contradiction"
        elif category == "count_consistency":
            count = value(drawing, "H1 COUNT")
            evidence = [step_witness(geometry, "H1", [("count", "h1_count")]), context_witness(packet, "features", "authority.dimensions")]
            if count:
                require(re.fullmatch(r"[1-9][0-9]*", count), "unsupported H1 count annotation")
                evidence.append(witness("drawing.pdf", line(drawing, "H1 COUNT")))
                conclusion = "supported_clear" if int(count) == geometry["h1_count"] else "contradiction"
            else:
                conclusion = "supported_clear" if authority["dimensions"] == "step" else "missing_information"
            if packet["family"] == "plate":
                labels = re.findall(r"\bH1\.\d+\b", drawing["text"])
                require(len(labels) == geometry["h1_count"], "visible H1 scope does not match public membership")
                require(drawing["text"].count("OTHER") == geometry["total_bore_count"] - geometry["h1_count"], "visible OTHER scope inconsistent")
        elif category == "material_consistency":
            declared = [s.split(" = ", 1)[1] for s in drawing["annotations"]["MATERIAL"]]
            evidence = [witness("drawing.pdf", s) for s in drawing["annotations"]["MATERIAL"]] + [context_witness(packet, "manufacturing.material", "authority.material_precedence")]
            canonical = [ALIASES.get(s.upper()) for s in [m["material"]] + declared]
            if authority["material_precedence"] == "equal":
                conclusion = "missing_information" if any(s is None for s in canonical) else "supported_clear" if len(set(canonical)) == 1 else "contradiction"
            elif authority["material_precedence"] == "drawing" and len({ALIASES.get(s.upper(), s) for s in declared}) > 1:
                conclusion = "contradiction"
        elif category == "required_representation":
            evidence = [context_witness(packet, "requirements")]
            for requirement in packet["requirements"]:
                description = requirement["description"]
                if requirement["representation"] in {"step", "either"} and "geometry" in description.lower():
                    evidence.append(witness("part.step", f"document solid_count={geometry['solid_count']}"))
                    continue
                if "SURFACE ROUGHNESS" not in description:
                    raise UnsupportedInput("requirement vocabulary outside declared surface-roughness obligation")
                roughness = line(drawing, "SURFACE ROUGHNESS")
                alternative = line(drawing, "SURFACE FINISH") if "SURFACE FINISH" in description else None
                representation = roughness or alternative
                if representation:
                    require((roughness and value(drawing, "SURFACE ROUGHNESS") == "3.20 um") or (alternative and value(drawing, "SURFACE FINISH") == "Ra 3.20 um"), "critical roughness value differs from finite declared contract")
                    evidence.append(witness("drawing.pdf", representation))
                else:
                    conclusion = "contradiction"
        elif category == "release_association":
            drawing_id, drawing_rev = value(drawing, "DRAWING ID"), value(drawing, "DRAWING REV")
            evidence = [witness("drawing.pdf", line(drawing, "DRAWING ID")), witness("drawing.pdf", line(drawing, "DRAWING REV")),
                        witness("part.step", geometry["product_identity"]), context_witness(packet, "release_association")]
            conclusion = "supported_clear" if drawing_id == release["drawing_id"] == release["model_id"] and [release["model_revision"], drawing_rev] in release["permitted_pairs"] else "contradiction"
        else:
            rule_id = operator
            conclusion = _advisory(packet, geometry, rule_id, resolved_material, unresolved_material)
            evidence = [context_witness(packet, "profile", "manufacturing", "setup")]
            if rule_id == "A01":
                evidence.append(step_witness(geometry, "W1", [("wall_mm", "wall_mm")]))
            elif rule_id == "A02":
                evidence.append(step_witness(geometry, "H1", [("depth_mm", "bore_depth_mm"), ("diameter_mm", "bore_diameter_mm")]))
            elif rule_id == "A03":
                evidence.append(witness("part.step", "document envelope_mm=[" + ", ".join(number(x) for x in geometry["envelope_mm"]) + "]"))
            else:
                evidence.extend([witness("drawing.pdf", line(drawing, "FINISH")), witness("drawing.pdf", line(drawing, "TOLERANCE STAGE"))])
        expectations.append({"obligation_id": obligation["id"], "track": obligation["track"], "category": category, "feature_id": feature,
                             "conclusion": conclusion, "rule_id": rule_id, "evidence": evidence, "root_cause": f"{packet['case_id']}:{obligation['id']}", "operator": operator})
    return expectations, suppressed


def _native(folder, outdir):
    packet = read_packet(folder)
    geometry = measure_step(Path(folder) / "part.step", packet["family"], packet["features"])
    drawing = inspect_drawing(Path(folder) / "drawing.pdf", Path(folder) / "drawing.png", outdir)
    expectations, suppressed = derive_expectations(packet, geometry, drawing)
    return {"measurements": geometry, "drawing": drawing, "expectations": expectations, "suppressed_unit_dependents": suppressed}


def inspect_case(folder, outdir, timeout=PARSER_TIMEOUT_SECONDS):
    """Retain observations; no expected answer is scorable before visual review."""
    require(type(timeout) in (int,float) and 0 < timeout <= 300,"native parser timeout outside configured bounds (0,300]")
    folder, outdir = Path(folder).resolve(), Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    record = {"schema_version": VERSION, "oracle_version": "1.0-observed-1", "case_id": folder.name,
              "packet_sha256": "0" * 64, "status": "invalid_fixture", "reasons": [], "measurements": {}, "drawing": {}, "expectations": [],
              "isolation": {"status": "not_checked", "common_mode_limit": "shared OCCT kernel", "visual_attestation_required": True,"native_parser_timeout_seconds":timeout}}
    try:
        require(sorted(p.name for p in folder.iterdir()) == ["drawing.pdf", "drawing.png", "packet.json", "part.step"], "unexpected public sidecar/files")
        packet = read_packet(folder)
        require(packet["case_id"] == folder.name, "case ID/folder mismatch")
        record["packet_sha256"] = sha256(folder / "packet.json")
        record["isolation"]["public_context"] = {k: packet[k] for k in ("part_id", "family", "units", "release_association", "authority", "manufacturing", "setup", "profile", "features", "requirements", "obligations")}
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
        command = [sys.executable, "-m", "rfqfuzz.v1.validation", "--native", str(folder), str(outdir)]
        process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env)
        (outdir / "native-process.txt").write_text(process.stdout + process.stderr, encoding="utf-8")
        require(process.returncode == 0, f"native parser failure exit {process.returncode}")
        observed = load_json(outdir / "native.json")
        if "error" in observed:
            if observed.get("unsupported"):
                raise UnsupportedInput(observed["error"])
            raise ValueError(observed["error"])
        record["measurements"], record["drawing"] = observed["measurements"], observed["drawing"]
        record["drawing"]["observed_expectations"] = observed["expectations"]
        record["isolation"]["suppressed_unit_dependents"] = observed["suppressed_unit_dependents"]
        record["status"] = "unverified"
        record["reasons"] = ["Actual drawing glyph/raster checks passed; hash-bound independent visual attestation remains required"]
    except subprocess.TimeoutExpired as exc:
        record["status"] = "timeout"
        record["reasons"] = [f"native parser timeout after {timeout}s; child terminated"]
        (outdir / "native-process.txt").write_text(str(exc), encoding="utf-8")
    except UnsupportedInput as exc:
        record["status"] = "unsupported_input"
        record["reasons"] = [str(exc)]
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        record["reasons"] = [f"{type(exc).__name__}: {exc}"]
    validate_oracle(record)
    write_json(outdir / "inspection.json", record)
    return record


def attest_case(record, folder, attestation):
    """Promote only an observed case bound to inspected actual artifact bytes."""
    if record["status"] != "unverified":
        return record
    entries = [a for a in attestation.get("cases", []) if a.get("case_id") == record["case_id"]]
    require(len(entries) == 1, "visual attestation missing or duplicated")
    entry = entries[0]
    require(entry.get("pdf_sha256") == sha256(Path(folder) / "drawing.pdf") and entry.get("png_sha256") == sha256(Path(folder) / "drawing.png"), "stale visual attestation")
    require(entry.get("legible_unclipped") is True and entry.get("view_associations_checked") is True and bool(entry.get("reviewer", "").strip()), "visual review incomplete")
    require(sorted(entry.get("visible_annotation_lines", [])) == sorted(s for lines in record["drawing"]["annotations"].values() for s in lines), "visual annotation/text disagreement")
    record["expectations"] = record["drawing"].pop("observed_expectations")
    record["status"], record["reasons"] = "valid", []
    record["isolation"]["visual_attestation"] = entry
    return validate_oracle(record)


def _quarantine(case, reason):
    case["status"] = "invalid_fixture"
    case["reasons"].append(reason)
    case["expectations"] = []


def _isolation(cases, mutations):
    """Check observed twins; private intent supplies labels, never numbers."""
    lookup = {m["case_id"]: m for m in mutations}
    groups = {}
    for case in cases:
        m = lookup.get(case["case_id"])
        if m is None:
            _quarantine(case, "missing private mutation/isolation contract")
            continue
        groups.setdefault(m["ancestry"], []).append(case)
        observed = case["expectations"] or case["drawing"].get("observed_expectations", [])
        issue_ops = {e["operator"] for e in observed if e["conclusion"] in {"contradiction", "advisory", "profile_exclusion"}}
        if issue_ops - {m["operator"]}:
            _quarantine(case, f"collateral independently observed issue operators: {sorted(issue_ops - {m['operator']})}")
        intended = [e for e in observed if e["operator"] == m["operator"]]
        if m["variant"] == "defective" and case["measurements"]:
            required_class = {"contradiction"} if m["operator"].startswith("O") else {"advisory", "profile_exclusion", "missing_information"}
            if not any(e["conclusion"] in required_class for e in intended):
                _quarantine(case, "declared mutation defect not independently established in final artifacts")
        if m["variant"] in {"repaired", "valid_alternative", "profile_alternative"} and case["measurements"]:
            if not any(e["conclusion"] == "supported_clear" for e in intended):
                _quarantine(case, "declared repaired/legitimate target not independently established")
        case["isolation"]["status"] = "observed_delta_checked"
    allowed_lines = {"O01": {"H1 DIAMETER", "MODEL STAGE", "DRAWING STAGE", "TRANSITION"}, "O02": {"H1 COUNT"},
                     "O03": {"UNITS", "ENVELOPE", "H1 DIAMETER", "H1 DEPTH", "C1 DIAMETER", "C1 DEPTH", "P1 WIDTH", "P1 LENGTH", "P1 DEPTH", "W1 THICKNESS"},
                     "O04": {"MATERIAL"}, "O05": {"SURFACE ROUGHNESS", "SURFACE FINISH"}, "O06": {"DRAWING REV", "DRAWING ID"}}
    for group in groups.values():
        repaired = [c for c in group if lookup[c["case_id"]]["variant"] == "repaired" and c["measurements"]]
        if not repaired:
            continue
        baseline = repaired[0]
        for case in group:
            if not case["measurements"]:
                continue
            op = lookup[case["case_id"]]["operator"]
            if op.startswith("O"):
                geo = lambda c: {k: c["measurements"][k] for k in ("bbox_mm", "volume_mm3", "cylinders", "planes")}
                if geo(case) != geo(baseline):
                    _quarantine(case, "objective mutation altered unrelated measured STEP geometry")
                def invariant_lines(c):
                    return {k: v for k, v in c["drawing"].get("annotations", {}).items() if k not in allowed_lines[op]}
                if invariant_lines(case) != invariant_lines(baseline):
                    _quarantine(case, "objective mutation altered undeclared visible annotation")
                def invariant_context(c):
                    context = json.loads(json.dumps(c["isolation"]["public_context"]))
                    if op == "O01":
                        context["authority"].pop("dimensions")
                        for key in ("model_stage", "drawing_stage", "transition"):
                            context["manufacturing"].pop(key)
                    elif op == "O02":
                        context.pop("features")
                    elif op == "O03":
                        context.pop("units")
                    elif op == "O04":
                        context["authority"].pop("material_precedence")
                    elif op == "O05":
                        context.pop("requirements")
                    elif op == "O06":
                        context.pop("release_association")
                    return context
                if invariant_context(case) != invariant_context(baseline):
                    _quarantine(case, "objective mutation altered undeclared public authority/profile/setup/context")


def validate_suite(suite_root, out, attestation=None, parser_timeout=PARSER_TIMEOUT_SECONDS):
    suite_root, out = Path(suite_root).resolve(), Path(out).resolve()
    public = suite_root / "public" if (suite_root / "public").is_dir() else suite_root
    require(not out.exists(), "validation output exists; preserve prior evidence")
    folders = sorted(p for p in public.iterdir() if p.is_dir())
    require(bool(folders) and len(folders) <= 256, "suite case count outside limits")
    cases = [inspect_case(folder, out / folder.name,timeout=parser_timeout) for folder in folders]
    if attestation is not None:
        attestation = load_json(attestation) if isinstance(attestation, (str, Path)) else attestation
        for folder, case in zip(folders, cases):
            try:
                attest_case(case, folder, attestation)
            except (ValueError, KeyError, TypeError, OSError) as exc:
                _quarantine(case, str(exc))
    mutation_path = suite_root / "private" / "mutations.json"
    if mutation_path.is_file():
        data = load_json(mutation_path)
        mutations = data["mutations"] if isinstance(data, dict) else data
        _isolation(cases, mutations)
    for case in cases:
        validate_oracle(case)
        write_json(out / case["case_id"] / "inspection.json", case)
    states = {c["status"] for c in cases}
    status = "valid" if states == {"valid"} else "unverified" if states <= {"valid", "unverified"} else "contains_quarantine"
    record = {"schema_version": VERSION, "oracle_version": "1.0-observed-1", "status": status, "cases": cases,
              "counts": {state: sum(c["status"] == state for c in cases) for state in sorted(states)},
              "limitations": ["Finite authored ASCII annotation grammar", "Shared OCCT kernel", "Character ink is a visibility signal, not infallible OCR", "Hash-bound independent visual review required", "No manufactured-part or general process-feasibility evidence"]}
    write_json(out / "oracle.json", record)
    return record


if __name__ == "__main__":
    require(len(sys.argv) == 4 and sys.argv[1] == "--native", "native reader arguments required")
    target = Path(sys.argv[3])
    try:
        native = _native(sys.argv[2], target)
    except Exception as exc:
        native = {"error": f"{type(exc).__name__}: {exc}", "unsupported": isinstance(exc, UnsupportedInput)}
    write_json(target / "native.json", native)
