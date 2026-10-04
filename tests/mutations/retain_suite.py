"""Retain the complete generated suite and exported artifact accounting."""
from pathlib import Path
import sys
from build123d import import_step
from pypdf import PdfReader
from rfqfuzz.v1.contracts import read_packet, sha256, write_json
from rfqfuzz.v1.mutations import generate_suite


def main(dest):
    dest = Path(dest)
    summary = generate_suite(dest)
    rows = []
    for folder in sorted((dest / "public").iterdir()):
        packet = read_packet(folder)
        part = import_step(folder / "part.step")
        pdf = PdfReader(folder / "drawing.pdf")
        rows.append({"case_id": packet["case_id"], "packet_sha256": sha256(folder / "packet.json"),
                     "solid_count": len(part.solids()), "is_valid": part.is_valid,
                     "actual_envelope_mm": list(part.bounding_box().size), "actual_volume_mm3": part.volume,
                     "actual_pdf_pages": len(pdf.pages), "actual_pdf_text": pdf.pages[0].extract_text(),
                     "actual_hashes": {a["path"]: a["sha256"] for a in packet["artifacts"]}})
    assert len(rows) == 145 and all(row["solid_count"] == 1 and row["is_valid"] and row["actual_pdf_pages"] == 1 for row in rows)
    write_json(dest / "private" / "authoring-export-check.json", {"status": "generated_not_oracle_validated", "summary": summary, "rows": rows})
    print(f"Generated {len(rows)} opaque public presentations; actual exported STEP/PDF and hashes reopened. Independent oracle acceptance remains T08.")
    print(summary)


if __name__ == "__main__":
    main(sys.argv[1])
