"""Independent read-only STEP/PDF examination of the standalone public cases."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import sys

from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_SOLID
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Circle, GeomAbs_Plane
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "review-output"
OUT.mkdir(exist_ok=True)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def xyz(obj):
    return [obj.X(), obj.Y(), obj.Z()]

def circular_edges(face):
    found = []
    exp = TopExp_Explorer(face, TopAbs_EDGE)
    while exp.More():
        edge = TopoDS.Edge_s(exp.Current())
        curve = BRepAdaptor_Curve(edge)
        if curve.GetType() == GeomAbs_Circle:
            circle = curve.Circle()
            found.append({"center_mm": xyz(circle.Location()), "radius_mm": circle.Radius(),
                          "axis": xyz(circle.Axis().Direction()),
                          "parameter_interval": [curve.FirstParameter(), curve.LastParameter()]})
        exp.Next()
    return found

def read_step(path, centers):
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP ReadFile failed: {status}")
    transferred = reader.TransferRoots()
    shape = reader.OneShape()
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    solids = 0
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    while exp.More():
        solids += 1
        exp.Next()
    cylinders, planes = [], []
    face_count = 0
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face_count += 1
        face = TopoDS.Face_s(exp.Current())
        surface = BRepAdaptor_Surface(face)
        if surface.GetType() == GeomAbs_Cylinder:
            cylinder = surface.Cylinder()
            cylinders.append({
                "face_index": face_count,
                "radius_mm": cylinder.Radius(), "diameter_mm": 2*cylinder.Radius(),
                "axis_location_mm": xyz(cylinder.Location()),
                "axis_direction": xyz(cylinder.Axis().Direction()),
                "u_interval_rad": [surface.FirstUParameter(), surface.LastUParameter()],
                "v_interval_mm": [surface.FirstVParameter(), surface.LastVParameter()],
                "face_orientation": str(face.Orientation()),
                "circular_boundaries": circular_edges(face),
            })
        elif surface.GetType() == GeomAbs_Plane:
            plane = surface.Plane()
            planes.append({"face_index": face_count, "location_mm": xyz(plane.Location()),
                           "normal": xyz(plane.Axis().Direction()),
                           "circular_boundaries": circular_edges(face)})
        exp.Next()
    classifications = []
    bounds = list(box.Get())
    z_low, z_high = bounds[2] + 1e-7, bounds[5] - 1e-7
    z_mid = (z_low + z_high) / 2
    for x, y, _ in centers:
        for z in [z_low+0.1, z_mid, z_high-0.1]:
            classifier = BRepClass3d_SolidClassifier(shape, gp_Pnt(x, y, z), 1e-7)
            classifications.append({"point_mm": [x, y, z], "state": str(classifier.State())})
    classifier = BRepClass3d_SolidClassifier(shape, gp_Pnt(0, 0, z_mid), 1e-7)
    classifications.append({"point_mm": [0, 0, z_mid], "state": str(classifier.State())})
    return {"read_status": str(status), "transferred_root_count": transferred,
            "valid_shape": BRepCheck_Analyzer(shape).IsValid(),
            "solid_count": solids, "face_count": face_count,
            "bounding_box_mm_with_kernel_tolerance": bounds,
            "volume_mm3": props.Mass(), "cylindrical_faces": cylinders,
            "planar_faces": planes, "point_classifications": classifications}

versions = {}
for name in ["cadquery-ocp", "build123d", "pypdf", "pypdfium2", "Pillow"]:
    try:
        versions[name] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        versions[name] = "distribution version unavailable"
report = {"provenance": {"python": platform.python_version(), "python_executable": sys.executable,
                         "packages": versions,
                         "script": "review-output/measure.py",
                         "method": "STEPControl_Reader reload; kernel validity/topology, analytical cylinder surfaces and circle boundaries, solid point classifications; pypdf text extraction; PDFium rendering and visual inspection"},
          "cases": []}
for folder in sorted((ROOT / "public").iterdir()):
    if not folder.is_dir():
        continue
    packet = json.loads((folder / "packet.json").read_text(encoding="utf-8"))
    text = "\n\n".join(page.extract_text() or "" for page in PdfReader(folder / "drawing.pdf").pages)
    (OUT / f"{folder.name}-pdf-text.txt").write_text(text, encoding="utf-8")
    doc = pdfium.PdfDocument(folder / "drawing.pdf")
    rendered = []
    for index in range(len(doc)):
        page = doc[index]
        img = page.render(scale=2.0).to_pil()
        output_path = OUT / f"{folder.name}-pdf-page-{index+1}.png"
        img.save(output_path)
        rendered.append({"page": index+1, "page_size_points": list(page.get_size()),
                         "render_size_pixels": list(img.size), "render_path": str(output_path.relative_to(ROOT))})
    with Image.open(folder / "drawing.png") as source_png:
        png_info = {"size_pixels": list(source_png.size), "mode": source_png.mode}
    report["cases"].append({"case_id": packet["case_id"],
         "actual_file_sha256": {name: digest(folder / name) for name in ["packet.json", "part.step", "drawing.pdf", "drawing.png"]},
         "declared_artifact_hashes_match": all(digest(folder / a["path"]) == a["sha256"] for a in packet["artifacts"]),
         "step_measurements": read_step(folder / "part.step", packet["features"][0]["centers_mm"]),
         "pdf_text": text, "pdf_render": rendered, "supplied_png": png_info})
    doc.close()
(OUT / "measurements.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({"provenance": report["provenance"], "cases": [
    {"case_id": c["case_id"], "actual_file_sha256": c["actual_file_sha256"],
     "declared_artifact_hashes_match": c["declared_artifact_hashes_match"],
     "valid_shape": c["step_measurements"]["valid_shape"],
     "solid_count": c["step_measurements"]["solid_count"],
     "bounding_box_mm_with_kernel_tolerance": c["step_measurements"]["bounding_box_mm_with_kernel_tolerance"],
     "bore_diameters_mm": [f["diameter_mm"] for f in c["step_measurements"]["cylindrical_faces"]],
     "point_classifications": c["step_measurements"]["point_classifications"],
     "pdf_text": c["pdf_text"], "pdf_render": c["pdf_render"]}
    for c in report["cases"]]}, indent=2))
