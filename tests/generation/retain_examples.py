"""Reproduce retained generator evidence; not a scoring oracle."""
from pathlib import Path
import sys
from build123d import import_step
from pypdf import PdfReader
from rfqfuzz.v1.contracts import write_json
from rfqfuzz.v1.generation import generate_case


def main(dest):
    dest = Path(dest)
    examples = [("plate", {}, {}), ("bore_block", {}, {}), ("pocket_block", {}, {}),
                ("pocket_block", {"wall": .6}, {}), ("plate", {}, {"h1_group_members": [0, 1], "h1_count": 2}),
                ("plate", {}, {"drawing_units": "in"})]
    rows = []
    for i, (family, params, drawing) in enumerate(examples):
        case_id = f"pk-{i + 1:012x}"
        packet = generate_case(dest / case_id, case_id, family, params, drawing)
        part = import_step(dest / case_id / "part.step")
        pdf = PdfReader(dest / case_id / "drawing.pdf")
        rows.append({"case_id": case_id, "family": family, "solid_count": len(part.solids()), "valid_solid": part.is_valid,
                     "actual_volume_mm3": part.volume, "actual_envelope_mm": list(part.bounding_box().size),
                     "actual_face_types": sorted({f.geom_type.name for f in part.faces()}), "actual_pdf_pages": len(pdf.pages),
                     "actual_visible_text_to_inspect": pdf.pages[0].extract_text(), "artifacts": packet["artifacts"], "render": packet["render"]})
    write_json(dest / "exported-measurements.json", {"warning": "Generator evidence is not a scoring oracle; final visibility/isolation verified independently by T08", "rows": rows})
    print(f"Retained {len(rows)} actual STEP/PDF/PNG presentations and reimported measurements in {dest}")


if __name__ == "__main__":
    main(sys.argv[1])
