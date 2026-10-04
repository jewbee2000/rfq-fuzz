"""Separate final-file check using OCP STEP reimport and planar boundary extraction.

SPDX-License-Identifier: MIT
No imports from author script or RFQFuzz generator/validator/reference modules.
Hard-coded analytic values below are comparison claims, never read from metadata.
"""
import hashlib
import json
from pathlib import Path
import re

from OCP.Bnd import Bnd_Box
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GeomAbs import GeomAbs_Plane
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
FOLDER = HERE / "pk-48bd731ca9e2"
TOL = 1e-6


def bounds(shape):
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box, False, False)
    return list(box.Get())


def close(actual, target):
    return len(actual) == len(target) and all(abs(a - b) <= TOL for a, b in zip(actual, target))


def main():
    path = FOLDER / "part.step"
    reader = STEPControl_Reader()
    assert reader.ReadFile(str(path)) == IFSelect_RetDone
    assert reader.TransferRoots() == 1
    shape = reader.OneShape()
    assert not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid()
    ex = TopExp_Explorer(shape, TopAbs_SOLID)
    solids = []
    while ex.More():
        solids.append(TopoDS.Solid_s(ex.Current()))
        ex.Next()
    assert len(solids) == 1
    bbox = bounds(shape)
    assert close(bbox, [-35, -22, -9, 35, 22, 9]), bbox
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props, True)
    assert abs(props.Mass() - 38040.0) <= TOL, props.Mass()
    faces = []
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        face = TopoDS.Face_s(ex.Current())
        surface = BRepAdaptor_Surface(face, True)
        assert surface.GetType() == GeomAbs_Plane
        face_props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, face_props)
        faces.append({"bounds_mm": bounds(face), "area_mm2": face_props.Mass()})
        ex.Next()
    assert len(faces) == 11
    wanted = {
        "pocket_floor": [-25.5, -15, -1, 32.5, 15, -1],
        "pocket_plus_x": [32.5, -15, -1, 32.5, 15, 9],
        "pocket_minus_x": [-25.5, -15, -1, -25.5, 15, 9],
        "pocket_plus_y": [-25.5, 15, -1, 32.5, 15, 9],
        "pocket_minus_y": [-25.5, -15, -1, 32.5, -15, 9],
    }
    measured = {}
    for name, target in wanted.items():
        hits = [f for f in faces if close(f["bounds_mm"], target)]
        assert len(hits) == 1, (name, hits)
        measured[name] = hits[0]
    wall = bbox[3] - measured["pocket_plus_x"]["bounds_mm"][0]
    depth = bbox[5] - measured["pocket_floor"]["bounds_mm"][2]
    assert abs(wall - 2.5) <= TOL and abs(depth - 10) <= TOL
    assert abs(measured["pocket_floor"]["area_mm2"] - 1740) <= TOL
    exported_text = path.read_text(encoding="ascii")
    products = re.findall(r"PRODUCT\('([^']*)'", exported_text)
    assert products == ["TRP-217 REV A"], products
    assert "SI_UNIT(.MILLI.,.METRE.)" in exported_text
    pdf = PdfReader(FOLDER / "drawing.pdf")
    assert len(pdf.pages) == 1
    text = pdf.pages[0].extract_text()
    required = ["DRAWING ID = TRP-217", "DRAWING REV = A", "UNITS = mm", "MATERIAL = 6061-T6",
        "MODEL STAGE = finished", "DRAWING STAGE = finished", "FINISH = none", "TOLERANCE STAGE = after_finish",
        "ENVELOPE = 70.00 x 44.00 x 18.00 mm", "P1 WIDTH = 58.00 mm", "P1 LENGTH = 30.00 mm",
        "P1 DEPTH = 10.00 mm", "W1 THICKNESS = 2.50 mm", "SURFACE ROUGHNESS = 3.20 um",
        "PLAN", "XZ SECTION A-A", "W1 (+X)"]
    for label in required:
        assert label in text, label
    # Actual content stream must contain drawing paths and no image XObjects.
    xobjects = pdf.pages[0].get("/Resources", {}).get("/XObject", {})
    assert not any(x.get_object().get("/Subtype") == "/Image" for x in xobjects.values())
    packet = json.loads((FOLDER / "packet.json").read_text())
    for artifact in packet["artifacts"]:
        assert hashlib.sha256((FOLDER / artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]
    result = {"status": "author_export_checks_passed_not_independent_oracle", "tolerance_mm": TOL,
        "step_valid": True, "roots": 1, "solids": len(solids), "planar_faces": len(faces),
        "bbox_mm": bbox, "volume_mm3": props.Mass(), "pocket_face_measurements": measured,
        "plus_x_wall_mm": wall, "pocket_depth_mm": depth, "step_products": products, "step_units": "mm",
        "pdf_pages": len(pdf.pages), "pdf_vector_no_image_xobjects": True, "required_pdf_text_present": required,
        "artifact_hashes_match": True, "visual_inspection": "Separate required retained note"}
    (HERE / "STEP_PDF_REIMPORT_CHECKS.json").write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "ACTUAL_PDF_TEXT.txt").write_text(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
