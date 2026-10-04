"""T01 export spike; run from repository root with the local Python 3.12 venv."""
from pathlib import Path
import json
from build123d import Box, Cylinder, export_step, import_step
from draftwright import build_drawing
from pypdf import PdfReader
from PIL import Image
import subprocess

out = Path("evidence/M0/smoke")
out.mkdir(parents=True, exist_ok=True)
part = Box(40, 30, 8) - Cylinder(3, 12)
export_step(part, out / "part.step")
build_drawing(part, title="Export smoke", number="SM-001").export(str(out / "drawing"), formats=("pdf",))
subprocess.run(["pdftoppm", "-singlefile", "-r", "150", "-png", str(out / "drawing.pdf"), str(out / "drawing")], check=True, timeout=60)
reopened = import_step(out / "part.step")
record = {
    "solids": len(reopened.solids()), "volume_mm3": reopened.volume,
    "pdf_pages": len(PdfReader(out / "drawing.pdf").pages),
    "png_size": list(Image.open(out / "drawing.png").size),
    "render_command": "pdftoppm -singlefile -r 150 -png evidence/M0/smoke/drawing.pdf evidence/M0/smoke/drawing",
}
(out / "result.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
