"""Bounded analytic CAD and authored schematic drawings, not an oracle.

Only the final ordinary STEP/PDF/PNG artifacts enter validation. Geometry uses
build123d/OCCT; ReportLab supplies a deliberately finite vector drafting layout.
Numeric annotations govern the drawing stage. The schematic views locate the
declared features and sections; dimensions must never be inferred from pixels.
"""
from __future__ import annotations

from copy import deepcopy
from importlib.metadata import version as distribution_version
from functools import lru_cache
import math
from pathlib import Path
import re
import shutil
import subprocess

from build123d import Box, Cylinder, Pos, export_step
from reportlab.pdfgen import canvas
from .contracts import VERSION, require, sha256, validate_packet, write_json

DEFAULTS = {
    "plate": {"width": 80., "length": 50., "height": 8., "diameter": 6., "count": 4},
    "bore_block": {"width": 60., "length": 40., "height": 35., "diameter": 6., "depth": 24., "counterbore_diameter": 12., "counterbore_depth": 4.},
    "pocket_block": {"width": 60., "length": 40., "height": 20., "pocket_width": 50., "pocket_length": 30., "pocket_depth": 12., "wall": 5.},
}
DRAWING_KEYS = {"h1_diameter", "h1_tolerance", "h1_count", "h1_group_members", "drawing_units", "convert_dimensions", "drawing_material", "drawing_revision", "drawing_id", "diameter_ref", "omit", "surface_roughness", "extra_notes", "sparse"}


def parameters_for(family, parameters=None):
    """Refuse edits outside the finite topology before CAD operations."""
    require(family in DEFAULTS, "unsupported part family")
    parameters = parameters or {}
    require(isinstance(parameters, dict) and parameters.keys() <= DEFAULTS[family].keys(), "unsupported parameter/topology edit")
    p = dict(DEFAULTS[family], **parameters)
    for key, value in p.items():
        require(type(value) in (int, float) and math.isfinite(value), f"invalid parameter {key}")
    require(20 <= p["width"] <= 240 and 20 <= p["length"] <= 160 and 3 <= p["height"] <= 80, "envelope outside bounded family")
    if family == "plate":
        require(type(p["count"]) is int and p["count"] in {1, 2, 4}, "plate count must be 1, 2 or 4")
        require(2 <= p["diameter"] <= 16 and p["diameter"] < min(p["width"], p["length"]) / 3, "unsupported overlapping/edge bores")
    elif family == "bore_block":
        require(2 <= p["diameter"] <= 16, "bore diameter outside bounds")
        require(p["diameter"] + 1 <= p["counterbore_diameter"] <= min(p["width"], p["length"]) - 4, "counterbore must be larger and leave side walls")
        require(1 <= p["counterbore_depth"] < p["depth"] <= p["height"] - 1, "blind depths must leave floor and distinct counterbore")
    else:
        require(8 <= p["pocket_width"] <= p["width"] - .4 and 8 <= p["pocket_length"] <= p["length"] - .4, "pocket dimensions outside bounds")
        require(.2 <= p["wall"] <= p["width"] - p["pocket_width"] - .2, "pocket wall must leave both sides")
        require(1 <= p["pocket_depth"] <= p["height"] - 1, "pocket depth must leave a floor")
    return p


def hole_centers(p):
    positions = [(-p["width"] * .3125, -p["length"] * .3, 0.), (-p["width"] * .3125, p["length"] * .3, 0.),
                 (p["width"] * .3125, -p["length"] * .3, 0.), (p["width"] * .3125, p["length"] * .3, 0.)]
    return [(0., 0., 0.)] if p["count"] == 1 else positions[:p["count"]]


def build_part(family, parameters=None):
    p = parameters_for(family, parameters)
    part = Box(p["width"], p["length"], p["height"])
    if family == "plate":
        for center in hole_centers(p):
            part -= Pos(*center) * Cylinder(p["diameter"] / 2, p["height"] + 2)
    elif family == "bore_block":
        top = p["height"] / 2
        part -= Pos(0, 0, top - p["depth"] / 2) * Cylinder(p["diameter"] / 2, p["depth"])
        part -= Pos(0, 0, top - p["counterbore_depth"] / 2) * Cylinder(p["counterbore_diameter"] / 2, p["counterbore_depth"])
    else:
        x = p["width"] / 2 - p["wall"] - p["pocket_width"] / 2
        part -= Pos(x, 0, p["height"] / 2 - p["pocket_depth"] / 2) * Box(p["pocket_width"], p["pocket_length"], p["pocket_depth"])
    require(len(part.solids()) == 1 and part.is_valid, "generator produced invalid or multiple solids")
    return part


def _merge(target, overrides):
    for key, value in overrides.items():
        require(key in target, f"unsupported context field {key}")
        if isinstance(value, dict) and isinstance(target[key], dict):
            _merge(target[key], value)
        else:
            target[key] = deepcopy(value)


def _features(family, p):
    if family == "plate":
        return [{"id": "H1", "type": "through_bore_group", "centers_mm": [list(c) for c in hole_centers(p)], "drawing_association": "PLAN: all numbered H1 Z bores; H1 grouped diameter/count annotations"}]
    if family == "bore_block":
        return [{"id": "H1", "type": "blind_bore", "centers_mm": [[0., 0., 0.]], "drawing_association": "PLAN and SECTION A-A: central smaller bore; H1 diameter/depth from top"},
                {"id": "C1", "type": "counterbore", "centers_mm": [[0., 0., 0.]], "drawing_association": "PLAN and SECTION A-A: coaxial larger entry bore; C1 diameter/depth from top"}]
    return [{"id": "P1", "type": "open_rectangular_pocket", "centers_mm": [[p["width"] / 2 - p["wall"] - p["pocket_width"] / 2, 0., 0.]], "drawing_association": "PLAN and SECTION A-A: single top-open pocket, P1 width/length/depth"},
            {"id": "W1", "type": "planar_wall", "drawing_association": "PLAN and SECTION A-A: +X side wall from pocket edge to outer side, W1 thickness"}]


def _obligations(family):
    rows = [("obj-units", "package_consistency", "unit_consistency", "document", ["step", "pdf", "context"]),
            ("obj-material", "package_consistency", "material_consistency", "document", ["pdf", "context"]),
            ("obj-requirement", "package_consistency", "required_representation", "document", ["pdf", "context"]),
            ("obj-release", "package_consistency", "release_association", "document", ["step", "pdf", "context"]),
            ("cnc-envelope", "cnc_advisory", "setup_envelope", "document", ["step", "context"]),
            ("cnc-stage", "cnc_advisory", "finish_stage", "document", ["pdf", "context"])]
    if family in {"plate", "bore_block"}:
        rows.extend([("obj-diameter", "package_consistency", "diameter_consistency", "H1", ["step", "pdf", "context"]),
                     ("obj-count", "package_consistency", "count_consistency", "H1", ["step", "pdf", "context"])])
    if family == "bore_block":
        rows.append(("cnc-depth", "cnc_advisory", "bore_ratio", "H1", ["step", "context"]))
    if family == "pocket_block":
        rows.append(("cnc-wall", "cnc_advisory", "wall_thickness", "W1", ["step", "context"]))
    return [dict(zip(("id", "track", "category", "feature_id", "required_modalities"), row)) for row in rows]


def _annotations(family, p, packet, overrides):
    unit = overrides.get("drawing_units", packet["units"]["drawing"])
    divisor = 25.4 if unit == "in" and overrides.get("convert_dimensions", True) else 1.
    def n(value):
        return f"{value / divisor:.4f}" if unit == "in" else f"{value / divisor:.2f}"
    release, m = packet["release_association"], packet["manufacturing"]
    lines = [f"DRAWING ID = {overrides.get('drawing_id', release['drawing_id'])}",
             f"DRAWING REV = {overrides.get('drawing_revision', release['drawing_revision'])}",
             f"UNITS = {unit}", f"MATERIAL = {overrides.get('drawing_material', m['material'])}",
             f"MODEL STAGE = {m['model_stage']}", f"DRAWING STAGE = {m['drawing_stage']}",
             f"FINISH = {m['finish']}", f"TOLERANCE STAGE = {m['tolerance_stage'] or 'UNSPECIFIED'}",
             f"ENVELOPE = {n(p['width'])} x {n(p['length'])} x {n(p['height'])} {unit}",
             f"SURFACE ROUGHNESS = {overrides.get('surface_roughness', 3.2):.2f} um"]
    if family in {"plate", "bore_block"}:
        ref = " REF" if overrides.get("diameter_ref") else ""
        lines.extend([f"H1 DIAMETER = {n(overrides.get('h1_diameter', p['diameter']))} +/- {n(overrides.get('h1_tolerance', .05))} {unit}{ref}",
                      f"H1 COUNT = {overrides.get('h1_count', p.get('count', 1))}",
                      f"H1 TYPE = {'THROUGH' if family == 'plate' else 'BLIND'}"])
    if family == "bore_block":
        lines.extend([f"H1 DEPTH = {n(p['depth'])} {unit}", f"C1 DIAMETER = {n(p['counterbore_diameter'])} {unit}", f"C1 DEPTH = {n(p['counterbore_depth'])} {unit}"])
    if family == "pocket_block":
        lines.extend([f"P1 WIDTH = {n(p['pocket_width'])} {unit}", f"P1 LENGTH = {n(p['pocket_length'])} {unit}",
                      f"P1 DEPTH = {n(p['pocket_depth'])} {unit}", f"W1 THICKNESS = {n(p['wall'])} {unit}"])
    if m["transition"]:
        t = m["transition"]
        lines.append(f"TRANSITION = {t.get('operation', 'declared')} {t.get('feature_id', 'document')} to drawing stage")
    lines.extend(overrides.get("extra_notes", []))
    omit = set(overrides.get("omit", []))
    require(all(isinstance(x, str) for x in omit), "invalid omitted labels")
    if overrides.get("sparse"):
        omit |= {"ENVELOPE", "H1 DIAMETER", "H1 COUNT", "H1 TYPE", "H1 DEPTH", "C1 DIAMETER", "C1 DEPTH", "P1 WIDTH", "P1 LENGTH", "P1 DEPTH", "W1 THICKNESS"}
    lines = [line for line in lines if line.split(" = ", 1)[0] not in omit]
    require(len(lines) <= 27 and all(isinstance(x, str) and len(x) <= 104 and x.isascii() and "\n" not in x for x in lines), "drawing annotation exceeds bounded visible layout")
    return lines


def _draft(path, family, p, lines, group_centers=None):
    # Fixed A4 landscape layout with separate view/annotation regions. It is not
    # automatic drafting; explicit bounded diagrams supply public correspondence.
    c = canvas.Canvas(str(path), pagesize=(842, 595), invariant=1, pageCompression=1)
    c.setTitle("Part drawing")
    c.setAuthor("RFQ author")
    c.setSubject("Authored schematic engineering drawing")
    c.setCreator("RFQFuzz bounded vector drafting")
    c.setLineWidth(.7)
    c.rect(20, 20, 802, 555)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(35, 552, "PART DRAWING")
    c.setFont("Helvetica", 9)
    c.drawString(35, 534, "SCHEMATIC VIEWS. NUMERIC ANNOTATIONS GOVERN; DO NOT MEASURE PIXELS.")
    c.drawString(35, 518, "Views depict supplied STEP at model stage. Depths measured from top (+Z).")
    c.line(395, 35, 395, 503)
    c.setFont("Helvetica", 10)
    for i, line in enumerate(lines):
        require(c.stringWidth(line, "Helvetica", 10) < 407, "annotation too wide for visible region")
        c.drawString(408, 486 - i * 16, line)
    s = min(300 / p["width"], 150 / p["length"])
    x0, y0 = 208 - p["width"] * s / 2, 405 - p["length"] * s / 2
    c.setFont("Helvetica-Bold", 11)
    c.drawString(48, 492, "PLAN (+Z)")
    c.rect(x0, y0, p["width"] * s, p["length"] * s)
    c.setFont("Helvetica", 10)
    if family == "plate":
        for i, (x, y, _) in enumerate(hole_centers(p)):
            px, py = x0 + (x + p["width"] / 2) * s, y0 + (y + p["length"] / 2) * s
            c.circle(px, py, p["diameter"] * s / 2)
            label = f"H1.{i + 1}" if group_centers is None or [x, y, 0.] in group_centers else "OTHER"
            c.drawString(px + p["diameter"] * s / 2 + 3, py + 4, label)
    elif family == "bore_block":
        px, py = x0 + p["width"] * s / 2, y0 + p["length"] * s / 2
        c.circle(px, py, p["diameter"] * s / 2)
        c.circle(px, py, p["counterbore_diameter"] * s / 2)
        c.drawString(px + p["counterbore_diameter"] * s / 2 + 8, py + 8, "C1 / H1")
    else:
        px = x0 + (p["width"] - p["wall"] - p["pocket_width"]) * s
        py = y0 + (p["length"] - p["pocket_length"]) * s / 2
        c.rect(px, py, p["pocket_width"] * s, p["pocket_length"] * s)
        c.drawString(px + 6, py + 8, "P1")
        c.drawString(x0 + p["width"] * s + 5, y0 + p["length"] * s / 2 + 25, "W1 +X")
    c.setDash(3, 2)
    c.line(x0 - 10, 405, x0 + p["width"] * s + 10, 405)
    c.setDash()
    c.drawString(x0 - 18, 410, "A")
    c.drawString(x0 + p["width"] * s + 13, 410, "A")
    # A cut across X through Y=0, with both blind depth steps exposed.
    c.setFont("Helvetica-Bold", 11)
    c.drawString(48, 278, "SECTION A-A (X-Z)")
    ss = min(300 / p["width"], 140 / p["height"])
    left, bottom = 208 - p["width"] * ss / 2, 188 - p["height"] * ss / 2
    right, top = left + p["width"] * ss, bottom + p["height"] * ss
    c.rect(left, bottom, right - left, top - bottom)
    c.setFillColorRGB(1, 1, 1)
    if family == "plate":
        # The Y=0 section does not intersect the four pattern bores. Explicitly
        # name that condition; one-hole variants do intersect their central bore.
        if p["count"] == 1:
            c.rect(208 - p["diameter"] * ss / 2, bottom, p["diameter"] * ss, top - bottom, fill=1)
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(48, 83, "H1 through all thickness; plan maps every group member.")
        if p["count"] != 1:
            c.drawString(48, 67, "Section Y=0 does not intersect off-axis H1 pattern bores.")
    elif family == "bore_block":
        d, cb = p["diameter"] * ss, p["counterbore_diameter"] * ss
        c.rect(208 - d / 2, top - p["depth"] * ss, d, p["depth"] * ss, fill=1, stroke=0)
        c.rect(208 - cb / 2, top - p["counterbore_depth"] * ss, cb, p["counterbore_depth"] * ss, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        points = [(208 - cb / 2, top), (208 - cb / 2, top - p["counterbore_depth"] * ss), (208 - d / 2, top - p["counterbore_depth"] * ss), (208 - d / 2, top - p["depth"] * ss), (208 + d / 2, top - p["depth"] * ss), (208 + d / 2, top - p["counterbore_depth"] * ss), (208 + cb / 2, top - p["counterbore_depth"] * ss), (208 + cb / 2, top)]
        for a, b in zip(points, points[1:]):
            c.line(*a, *b)
        c.setFont("Helvetica", 10)
        c.drawString(208 + cb / 2 + 8, top - p["counterbore_depth"] * ss - 8, "C1")
        c.drawString(208 + d / 2 + 8, top - p["depth"] * ss + 8, "H1 blind floor")
    else:
        pl = left + (p["width"] - p["wall"] - p["pocket_width"]) * ss
        pr = right - p["wall"] * ss
        floor = top - p["pocket_depth"] * ss
        c.rect(pl, floor, pr - pl, top - floor, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        c.line(pl, top, pl, floor)
        c.line(pl, floor, pr, floor)
        c.line(pr, floor, pr, top)
        c.setFont("Helvetica", 10)
        c.drawString(pl + 8, floor + 8, "P1 open pocket")
        c.drawString(right + 5, top - 12, "W1")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    c.drawString(408, 39, "Declared finite requirements and setup/profile are in packet.json.")
    c.showPage()
    c.save()


@lru_cache(maxsize=1)
def _renderer():
    renderer = shutil.which("pdftoppm")
    require(renderer is not None, "Poppler pdftoppm is required on PATH")
    result = subprocess.run([renderer, "-v"], capture_output=True, text=True, check=True, timeout=10)
    description = (result.stdout + result.stderr).splitlines()[0]
    return renderer, description


def generate_case(dest, case_id, family, parameters=None, drawing_overrides=None, context_overrides=None, profile=None):
    """Write a fresh neutral public presentation and return its PacketSpec."""
    dest = Path(dest)
    require(not dest.exists() or not any(dest.iterdir()), "generation destination is not empty; preserve prior evidence")
    require(re.fullmatch(r"pk-[0-9a-f]{12}", case_id) is not None, "opaque case ID required")
    p = parameters_for(family, parameters)
    overrides = drawing_overrides or {}
    require(isinstance(overrides, dict) and overrides.keys() <= DRAWING_KEYS, "unsupported drawing edit")
    if profile is None:
        from .profiles import profile as profile_factory
        profile = profile_factory()
    packet = {"schema_version": VERSION, "case_id": case_id, "part_id": "PT-001", "family": family,
              "units": {"model": "mm", "drawing": overrides.get("drawing_units", "mm")},
              "release_association": {"model_id": "PT-001", "model_revision": "A", "drawing_id": "PT-001", "drawing_revision": "A", "permitted_pairs": [["A", "A"]]},
              "authority": {"geometry": "step", "dimensions": "drawing", "material_precedence": "equal", "process": "Public manufacturing contract and visible notes apply at their named stages", "release": "Only explicitly permitted model/drawing revision pairs are approved"},
              "manufacturing": {"model_stage": "finished", "drawing_stage": "finished", "transition": None, "material": "6061-T6", "material_class": "metal", "finish": "none", "tolerance_stage": "after_finish"},
              "setup": {"orientation": "XYZ", "stock_allowance_mm": [0., 0., 0.], "fixture_allowance_mm": [0., 0., 0.]},
              "profile": deepcopy(profile), "features": _features(family, p),
              "requirements": [{"id": "RQ1", "representation": "drawing", "description": "A visible SURFACE ROUGHNESS = 3.20 um note is required for release. STEP geometry alone does not represent this requirement."}],
              "obligations": _obligations(family), "artifacts": [],
              "render": {"renderer": f"ReportLab {distribution_version('reportlab')} bounded vector template; Poppler pdftoppm", "dpi": 200}}
    _merge(packet, context_overrides or {})
    if "h1_group_members" in overrides:
        require(family == "plate", "scoped member selection supports plate only")
        members = overrides["h1_group_members"]
        require(isinstance(members, list) and bool(members) and all(type(i) is int and 0 <= i < p["count"] for i in members) and len(set(members)) == len(members), "invalid scoped bore group")
        packet["features"][0]["centers_mm"] = [list(hole_centers(p)[i]) for i in members]
        packet["features"][0]["drawing_association"] = "PLAN: only bores explicitly labeled H1 belong to this group; OTHER bores are excluded"
    lines = _annotations(family, p, packet, overrides)
    dest.mkdir(parents=True, exist_ok=True)
    part = build_part(family, p)
    export_step(part, dest / "part.step")
    # Include public model identity in ordinary STEP descriptive product metadata.
    step = dest / "part.step"
    text = step.read_text(encoding="utf-8")
    release = packet["release_association"]
    identity = f"{release['model_id']} REV {release['model_revision']}"
    require(re.fullmatch(r"[A-Za-z0-9 _.:-]{1,96}", identity) is not None, "unsafe STEP identity")
    text = re.sub(r"PRODUCT\('([^']*)','([^']*)',''", lambda m: f"PRODUCT('{identity}','{identity}',''", text, count=1)
    step.write_text(text, encoding="utf-8")
    _draft(dest / "drawing.pdf", family, p, lines, packet["features"][0].get("centers_mm") if family == "plate" else None)
    renderer, renderer_description = _renderer()
    packet["render"]["renderer"] += "; " + renderer_description
    subprocess.run([renderer, "-singlefile", "-r", "200", "-png", str(dest / "drawing.pdf"), str(dest / "drawing")], check=True, timeout=60, capture_output=True)
    packet["artifacts"] = [{"path": name, "sha256": sha256(dest / name), "media_type": media} for name, media in (("part.step", "model/step"), ("drawing.pdf", "application/pdf"), ("drawing.png", "image/png"))]
    validate_packet(packet)
    write_json(dest / "packet.json", packet)
    return packet
