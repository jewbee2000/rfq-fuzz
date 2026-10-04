"""Own direct artifact reader; no rfqfuzz source, oracle or mutation imports."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box
from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from PIL import Image, ImageChops
from pypdf import PdfReader

packet_root = Path(sys.argv[1])
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
packet = json.loads((packet_root / 'packet.json').read_text())
def xyz(point):
    return [point.X(), point.Y(), point.Z()]
def bounds(shape):
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, False)
    return list(box.Get())
reader = STEPControl_Reader()
assert reader.ReadFile(str(packet_root / 'part.step')) == IFSelect_RetDone
assert reader.TransferRoots() >= 1
shape = reader.OneShape()
props = GProp_GProps()
BRepGProp.VolumeProperties_s(shape, props)
solids = 0
ex = TopExp_Explorer(shape, TopAbs_SOLID)
while ex.More():
    solids += 1
    ex.Next()
faces = []
ex = TopExp_Explorer(shape, TopAbs_FACE)
while ex.More():
    face = TopoDS.Face_s(ex.Current())
    surf = BRepAdaptor_Surface(face, True)
    record = {'surface_type': str(surf.GetType()), 'bounds_mm': bounds(face)}
    if surf.GetType() == GeomAbs_Plane:
        plane = surf.Plane()
        record.update({'plane_location_mm': xyz(plane.Location()), 'normal': xyz(plane.Axis().Direction())})
    elif surf.GetType() == GeomAbs_Cylinder:
        cyl = surf.Cylinder()
        record.update({'radius_mm': cyl.Radius(), 'axis_location_mm': xyz(cyl.Axis().Location()), 'axis_direction': xyz(cyl.Axis().Direction())})
    faces.append(record)
    ex.Next()
pdf = PdfReader(packet_root / 'drawing.pdf')
pdf_text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
subprocess.run(['pdftoppm', '-singlefile', '-r', '200', '-png', str(packet_root / 'drawing.pdf'), str(out / 'rerendered')], check=True, timeout=60)
with Image.open(packet_root / 'drawing.png') as original, Image.open(out / 'rerendered.png') as rendered:
    original.load(); rendered.load()
    pixel_delta = ImageChops.difference(original.convert('RGB'), rendered.convert('RGB')).getbbox() if original.size == rendered.size else 'different_size'
    image_record = {'provided_size': list(original.size), 'rerendered_size': list(rendered.size), 'pixel_delta_bounds': pixel_delta}
hashes = {name: hashlib.sha256((packet_root / name).read_bytes()).hexdigest() for name in ('packet.json', 'part.step', 'drawing.pdf', 'drawing.png')}
for artifact in packet['artifacts']:
    assert hashes[artifact['path']] == artifact['sha256']
step_text = (packet_root / 'part.step').read_text(errors='replace')
record = {'reader': 'Own OCP STEPControl reader; shares OCCT with generator, no toolkit validator/reference imported',
          'input_public_path': str(packet_root), 'case_id': packet['case_id'], 'hashes': hashes,
          'solids': solids, 'volume_mm3': props.Mass(), 'shape_bounds_mm': bounds(shape),
          'faces': faces, 'step_header': step_text.splitlines()[:30],
          'step_unit_lines': [line for line in step_text.splitlines() if 'SI_UNIT' in line or 'CONVERSION_BASED_UNIT' in line],
          'pdf_pages': len(pdf.pages), 'pdf_text': pdf_text, 'png_check': image_record,
          'measurement_tolerance_mm': 1e-6}
(out / 'measurements.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
(out / 'pdf-text.txt').write_text(pdf_text, encoding='utf-8')
print(json.dumps(record, indent=2))
