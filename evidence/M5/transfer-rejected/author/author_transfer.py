"""Own-source synthetic RFQ author; no RFQFuzz generator/validator imports.

SPDX-License-Identifier: MIT
Copyright (c) 2026 RFQFuzz contributors
Uses the public PacketSpec contract and copies only the selected public profile.
Author intent is written outside the public packet directory.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.StepBasic import StepBasic_Product
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.TCollection import TCollection_HAsciiString
from reportlab.lib import colors
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASE_ID = "pk-48bd731ca9e2"
PART_ID = "TRP-217"
PUBLIC = HERE / CASE_ID
W, L, H = 70.0, 44.0, 18.0
PW, PL, PD = 58.0, 30.0, 10.0
WALL = 2.5
PCX = W / 2 - WALL - PW / 2
STOCK = [2.0, 2.0, 2.0]
FIXTURE = [4.0, 4.0, 6.0]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_step():
    body = BRepPrimAPI_MakeBox(gp_Pnt(-W / 2, -L / 2, -H / 2), W, L, H).Shape()
    # Extend the cutter above the body to avoid a coincident top-face boolean.
    cutter = BRepPrimAPI_MakeBox(
        gp_Pnt(PCX - PW / 2, -PL / 2, H / 2 - PD), PW, PL, PD + 1.0
    ).Shape()
    cut = BRepAlgoAPI_Cut(body, cutter)
    cut.Build()
    if not cut.IsDone():
        raise RuntimeError("Own-source pocket boolean failed")
    writer = STEPControl_Writer()
    for key, value in (("write.step.unit", "MM"), ("write.step.product.name", f"{PART_ID} REV A")):
        if not Interface_Static.SetCVal_s(key, value):
            raise RuntimeError(f"STEP setting unavailable: {key}")
    if writer.Transfer(cut.Shape(), STEPControl_AsIs) != IFSelect_RetDone:
        raise RuntimeError("STEP transfer failed")
    # OCCT adds a numeric suffix to unnamed shapes. Set the actual PRODUCT
    # entities through its supported model interface before ordinary export.
    model = writer.Model()
    products = 0
    for i in range(1, model.NbEntities() + 1):
        entity = model.Value(i)
        if isinstance(entity, StepBasic_Product):
            entity.SetId(TCollection_HAsciiString(f"{PART_ID} REV A"))
            entity.SetName(TCollection_HAsciiString(f"{PART_ID} REV A"))
            products += 1
    if products != 1:
        raise RuntimeError("Unexpected STEP PRODUCT count")
    if writer.Write(str(PUBLIC / "part.step")) != IFSelect_RetDone:
        raise RuntimeError("STEP write failed")
    text = (PUBLIC / "part.step").read_text(encoding="ascii")
    if not re.search(r"PRODUCT\('TRP-217 REV A'", text):
        raise RuntimeError("Exported STEP PRODUCT identity not present")


def drawing():
    # New fixed layout: metadata/dimension rail at left; stacked views at right.
    c = canvas.Canvas(str(PUBLIC / "drawing.pdf"), pagesize=(900, 650), invariant=1)
    c.setTitle(f"{PART_ID} REV A - RFQ geometry and release sheet")
    c.setAuthor("RFQFuzz independent synthetic packet author")
    c.setSubject("Finite public RFQ context; no manufacturing certification")
    ink = colors.HexColor("#172d3a")
    pale = colors.HexColor("#f1f5f6")
    c.setStrokeColor(ink)
    c.setFillColor(ink)
    c.setLineWidth(0.8)
    c.rect(20, 20, 860, 610)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(36, 605, "RFQ GEOMETRY AND RELEASE SHEET")
    c.setFont("Helvetica", 9)
    c.drawString(36, 588, "Open pocket body | One solid | Dimensions govern at the named stage")
    c.drawRightString(864, 605, "SHEET 1 / 1")
    c.line(20, 578, 880, 578)
    c.setFillColor(pale)
    c.rect(28, 49, 252, 518, stroke=0, fill=1)
    c.setFillColor(ink)

    def rail_heading(y, text):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(39, y, text)
        c.line(39, y - 7, 268, y - 7)

    def rail_line(y, text, bold=False, size=10):
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(39, y, text)

    rail_heading(549, "RELEASE + PROCESS")
    for y, text in zip(range(524, 338, -21), [
        f"DRAWING ID = {PART_ID}", "REV = A", "UNITS = mm", "MATERIAL = 6061-T6",
        "MODEL STAGE = finished", "DRAWING STAGE = finished", "FINISH = none",
        "TOLERANCE STAGE = after_finish",
    ]):
        rail_line(y, text)
    rail_heading(341, "DIMENSION REGISTER")
    rail_line(316, "ENVELOPE = 70.00 x 44.00 x 18.00 mm", size=9)
    for y, text in zip(range(294, 190, -22), [
        "P1 WIDTH = 58.00 mm", "P1 LENGTH = 30.00 mm", "P1 DEPTH = 10.00 mm",
        "W1 THICKNESS = 2.50 mm", "SURFACE ROUGHNESS = 3.20 um",
    ]):
        rail_line(y, text, size=9.5)
    rail_heading(178, "DECLARED SETUP")
    for y, text in zip(range(154, 73, -17), [
        "Orientation = XYZ (fixed)", "Stock allowance = [2, 2, 2] mm",
        "Fixture allowance = [4, 4, 6] mm", "Allowances are TOTAL added extent.",
        "Profile = synthetic-standard 1.0.0",
    ]):
        rail_line(y, text, size=8.5)

    def view_title(y, text):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(310, y, text)
        c.setFont("Helvetica", 8)

    def arrow(x, y, dx, dy):
        # Filled arrow points toward x,y; direction has unit length.
        p = c.beginPath()
        p.moveTo(x, y)
        p.lineTo(x - 5 * dx + 2 * dy, y - 5 * dy - 2 * dx)
        p.lineTo(x - 5 * dx - 2 * dy, y - 5 * dy + 2 * dx)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def horiz_dim(x1, x2, y, reference_y, label):
        c.setLineWidth(0.45)
        c.line(x1, reference_y, x1, y + 4)
        c.line(x2, reference_y, x2, y + 4)
        c.line(x1, y, x2, y)
        arrow(x1, y, -1, 0)
        arrow(x2, y, 1, 0)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.white)
        c.rect((x1 + x2) / 2 - 34, y - 5, 68, 11, fill=1, stroke=0)
        c.setFillColor(ink)
        c.drawCentredString((x1 + x2) / 2, y - 3, label)

    # PLAN uses X right, Y up at 5 pt/mm, directly projected from analytic edges.
    sx, sy, scale = 577, 439, 5
    px = lambda x: sx + scale * x
    py = lambda y: sy + scale * y
    xmin, xmax, ymin, ymax = -35, 35, -22, 22
    pmin, pmax, qmin, qmax = -25.5, 32.5, -15, 15
    view_title(557, "PLAN - LOOKING FROM +Z")
    c.setLineWidth(1)
    c.rect(px(xmin), py(ymin), scale * W, scale * L)
    c.rect(px(pmin), py(qmin), scale * PW, scale * PL)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(px(PCX), py(0) + 5, "P1")
    c.setFont("Helvetica", 9)
    c.drawCentredString(px(PCX), py(0) - 9, "TOP-OPEN RECTANGULAR POCKET")
    horiz_dim(px(pmin), px(pmax), py(qmin) + 17, py(qmin), "58.00")
    # Section-cut trace through Y=0 is visually separate from the dimension line.
    c.setDash([6, 3, 1, 3])
    c.setLineWidth(0.5)
    c.line(px(xmin) - 12, py(0), px(xmax) + 12, py(0))
    c.setDash()
    c.setFont("Helvetica-Bold", 10)
    c.drawString(px(xmin) - 24, py(0) - 3, "A")
    c.drawString(px(xmax) + 18, py(0) - 3, "A")
    # External leader identifies the narrow +X wall without putting text in it.
    c.setLineWidth(0.6)
    c.line(px(33.75), py(12), 790, 521)
    c.line(790, 521, 843, 521)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(790, 526, "W1 (+X)")
    c.setFont("Helvetica", 8.5)
    c.drawString(790, 510, "2.50 mm")
    # Axis key.
    c.line(333, 479, 369, 479)
    arrow(369, 479, 1, 0)
    c.line(333, 479, 333, 511)
    arrow(333, 511, 0, 1)
    c.setFont("Helvetica", 8)
    c.drawString(373, 476, "+X")
    c.drawString(327, 515, "+Y")
    c.drawString(310, 315, "P1 centered at X=+3.50, Y=0.00 mm; open on +Z face.")

    # XZ SECTION through Y=0: actual material boundary as one concave polygon.
    view_title(280, "XZ SECTION A-A - THROUGH Y=0")
    z0 = 184
    pz = lambda z: z0 + scale * z
    coords = [(-35, -9), (35, -9), (35, 9), (32.5, 9), (32.5, -1),
              (-25.5, -1), (-25.5, 9), (-35, 9)]
    path = c.beginPath()
    for i, (x, z) in enumerate(coords):
        (path.moveTo if i == 0 else path.lineTo)(px(x), pz(z))
    path.close()
    c.setFillColor(colors.HexColor("#dfe8ed"))
    c.setLineWidth(1)
    c.drawPath(path, fill=1, stroke=1)
    c.setFillColor(ink)
    c.setFont("Helvetica", 9)
    c.drawCentredString(px(0), pz(-5), "SOLID MATERIAL / 8.00 mm FLOOR")
    c.drawCentredString(px(PCX), pz(4), "P1 - REMOVED VOLUME")
    c.setLineWidth(0.5)
    c.line(780, pz(-1), 780, pz(9))
    c.line(px(pmax), pz(-1), 787, pz(-1))
    c.line(px(pmax), pz(9), 787, pz(9))
    arrow(780, pz(-1), 0, -1)
    arrow(780, pz(9), 0, 1)
    c.setFont("Helvetica", 9)
    c.drawString(791, 202, "P1 DEPTH")
    c.drawString(791, 187, "10.00 mm")
    horiz_dim(px(xmin), px(xmax), 118, pz(-9), "70.00")
    c.setFont("Helvetica", 8.5)
    c.drawString(310, 88, "Body origin at envelope center. Model X/Y/Z extents: +/-35, +/-22, +/-9 mm.")
    c.drawString(310, 73, "Drawing dimensions are in mm. Exact STEP geometry is the geometry authority.")
    c.setFont("Helvetica", 7.5)
    c.drawString(36, 33, "Agent-authored synthetic fixture; no human engineer review or physical manufacture is claimed.")
    c.drawRightString(864, 33, f"{PART_ID} / A")
    c.showPage()
    c.save()


def make_packet():
    example = json.loads((ROOT / "evidence/M2/generator-artifacts-v2/pk-000000000003/packet.json").read_text())
    # Public profile only. No source parameters, existing artifact bytes or answers.
    profile = example["profile"]
    obligations = [
        ("obj-units", "package_consistency", "unit_consistency", "document", ["step", "pdf", "context"]),
        ("obj-material", "package_consistency", "material_consistency", "document", ["pdf", "context"]),
        ("obj-requirement", "package_consistency", "required_representation", "document", ["pdf", "context"]),
        ("obj-release", "package_consistency", "release_association", "document", ["step", "pdf", "context"]),
        ("cnc-wall", "cnc_advisory", "wall_thickness", "W1", ["step", "context"]),
        ("cnc-envelope", "cnc_advisory", "setup_envelope", "document", ["step", "context"]),
        ("cnc-stage", "cnc_advisory", "finish_stage", "document", ["pdf", "context"]),
    ]
    p = {
        "schema_version": "1.0", "case_id": CASE_ID, "part_id": PART_ID, "family": "pocket_block",
        "units": {"model": "mm", "drawing": "mm"},
        "release_association": {"model_id": PART_ID, "model_revision": "A", "drawing_id": PART_ID,
            "drawing_revision": "A", "permitted_pairs": [["A", "A"]]},
        "authority": {"geometry": "step", "dimensions": "drawing", "material_precedence": "equal",
            "process": "Public manufacturing contract and visible notes apply at their named stages",
            "release": "Only the explicitly permitted model/drawing revision pair is approved"},
        "manufacturing": {"model_stage": "finished", "drawing_stage": "finished", "transition": None,
            "material": "6061-T6", "material_class": "metal", "finish": "none", "tolerance_stage": "after_finish"},
        "setup": {"orientation": "XYZ", "stock_allowance_mm": STOCK, "fixture_allowance_mm": FIXTURE},
        "profile": profile,
        "features": [
            {"id": "P1", "type": "open_rectangular_pocket", "centers_mm": [[PCX, 0.0, 0.0]],
             "drawing_association": "PLAN and XZ SECTION A-A: single +Z top-open P1 pocket; width along X, length along Y, depth along Z"},
            {"id": "W1", "type": "planar_wall",
             "drawing_association": "PLAN W1 (+X) leader and XZ SECTION A-A: wall between P1 +X face and body +X face"}],
        "requirements": [{"id": "RQ1", "representation": "drawing",
            "description": "A visible SURFACE ROUGHNESS = 3.20 um note is required for release. STEP geometry alone does not represent this requirement."}],
        "obligations": [dict(zip(("id", "track", "category", "feature_id", "required_modalities"), o)) for o in obligations],
        "artifacts": [{"path": name, "sha256": sha(PUBLIC / name), "media_type": media}
            for name, media in (("part.step", "model/step"), ("drawing.pdf", "application/pdf"), ("drawing.png", "image/png"))],
        "render": {"renderer": "Independent ReportLab vector drawing; Poppler pdftoppm 26.07.0 rasterized actual PDF", "dpi": 200},
    }
    write_json(PUBLIC / "packet.json", p)
    write_json(HERE / "PRIVATE_AUTHOR_EXPECTATIONS.json", {
        "case_id": CASE_ID, "author_intent_only": True, "independent_oracle": False,
        "scope": "Agent-authored synthetic source/layout diagnostic; not industrial generalization, engineer review or manufacturing evidence",
        "analytic_geometry": {
            "body_bounds_mm": [-35, -22, -9, 35, 22, 9], "body_envelope_mm": [W, L, H],
            "pocket_bounds_mm": [-25.5, -15, -1, 32.5, 15, 9], "pocket_dimensions_mm": [PW, PL, PD],
            "floor_mm": 8.0, "plus_x_wall_mm": WALL, "minus_x_wall_mm": 9.5, "y_wall_mm": 7.0,
            "solid_volume_mm3": W * L * H - PW * PL * PD,
            "occupied_extent_mm": [v + s + f for v, s, f in zip([W, L, H], STOCK, FIXTURE)],
        },
        "intended_conclusions": {o[0]: "supported_clear" for o in obligations},
        "rationale": "Matching units/material/requirement/release; 2.50 mm W1 exceeds selected 0.80 mm metal advisory; occupied [76,50,26] fits selected [120,80,50]; explicit after_finish stage.",
        "public_packet_sha256": sha(PUBLIC / "packet.json"),
    })
    write_json(HERE / "AUTHOR_ENVIRONMENT.json", {
        "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
        "dependencies": {n: importlib.metadata.version(n) for n in ["build123d", "cadquery-ocp", "reportlab", "pypdf"]},
        "poppler": subprocess.run([shutil.which("pdftoppm"), "-v"], capture_output=True, text=True).stderr.strip(),
        "commit_at_start": "66a996bb9496021972bc381281fce76907762aaa",
    })


def main():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    build_step()
    drawing()
    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise RuntimeError("Poppler unavailable; actual PDF raster required")
    subprocess.run([renderer, "-png", "-r", "200", "-singlefile", str(PUBLIC / "drawing.pdf"), str(PUBLIC / "drawing")], check=True, timeout=60)
    make_packet()
    print(json.dumps({"public_folder": str(PUBLIC), "packet_sha256": sha(PUBLIC / "packet.json"), "artifacts": {n: sha(PUBLIC / n) for n in ["part.step", "drawing.pdf", "drawing.png"]}}, indent=2))


if __name__ == "__main__":
    main()
