"""Inspect actual smoke exports without reading generator output metadata."""
import hashlib
import json
import math
from pathlib import Path
import sys
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from PIL import Image, ImageChops
from pypdf import PdfReader

root = Path(sys.argv[1])
reader = STEPControl_Reader()
assert reader.ReadFile(str(root / 'part.step')) == IFSelect_RetDone
assert reader.TransferRoots() == 1
shape = reader.OneShape()
properties = GProp_GProps()
BRepGProp.VolumeProperties_s(shape, properties)
explorer = TopExp_Explorer(shape, TopAbs_SOLID)
solids = 0
while explorer.More():
    solids += 1
    explorer.Next()
expected_volume = 40 * 30 * 8 - math.pi * 3 ** 2 * 8
assert solids == 1
assert abs(properties.Mass() - expected_volume) < 1e-6
pdf = PdfReader(root / 'drawing.pdf')
text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
assert len(pdf.pages) == 1
assert 'Export smoke' in text and 'SM-001' in text and 'THRU' in text
with Image.open(root / 'drawing.png') as image:
    image.load()
    pixels = image.convert('RGB')
    ink_bounds = ImageChops.difference(pixels, Image.new('RGB', pixels.size, 'white')).getbbox()
    assert ink_bounds is not None
    png_size = image.size
record = {
    'step_reader': 'OCP.STEPControl.STEPControl_Reader (shares OCCT kernel with generator)',
    'step_solids': solids,
    'measured_volume_mm3': properties.Mass(),
    'analytic_volume_mm3': expected_volume,
    'tolerance_mm3': 1e-6,
    'pdf_pages': len(pdf.pages),
    'pdf_text': text,
    'png_size': png_size,
    'png_ink_bounds': ink_bounds,
    'sha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in ('part.step', 'drawing.pdf', 'drawing.png')},
    'result': 'smoke_semantics_confirmed',
    'limits': 'Readiness check only; not final RFQFuzz workflow acceptance. PNG visual inspection recorded separately.'
}
Path(sys.argv[2]).write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in record.items() if k != 'pdf_text'}, indent=2))
