"""One-time retained-evidence extension; preserves the original 144-case history."""
from pathlib import Path
import shutil
import sys
from build123d import import_step
from pypdf import PdfReader
from rfqfuzz.v1.contracts import digest, load_json, read_packet, require, sha256, write_json
from rfqfuzz.v1.generation import generate_case
from rfqfuzz.v1.mutations import specifications, suite_summary
from rfqfuzz.v1.profiles import profile


def main(dest):
    dest = Path(dest)
    specs = specifications()
    old_specs = load_json(dest / "private" / "mutations.json")["mutations"]
    authoring_keys = {"case_id", "operator", "variant", "ancestry", "partition", "seed", "source_parameters"}
    require(len(old_specs) == 144 and all({k: old[k] for k in authoring_keys} == {k: new[k] for k in authoring_keys}
                                        for old, new in zip(old_specs, specs[:-1])),
            "extension only applies to the retained original 144-case authoring configuration")
    checks = load_json(dest / "private" / "authoring-export-check.json")
    for row in checks["rows"]:
        folder = dest / "public" / row["case_id"]
        read_packet(folder)
        require(sha256(folder / "packet.json") == row["packet_sha256"], "original packet changed; refuse extension")
    row = specs[-1]
    source = row["source_parameters"]
    folder = dest / "public" / row["case_id"]
    packet = generate_case(folder, row["case_id"], source["family"], source["parameters"], source["drawing_overrides"], source["context_overrides"], profile(source["profile_name"]))
    part = import_step(folder / "part.step")
    pdf = PdfReader(folder / "drawing.pdf")
    require(len(part.solids()) == 1 and part.is_valid and len(pdf.pages) == 1, "invalid supplemental export")
    text = pdf.pages[0].extract_text()
    require("H1 DIAMETER =" not in text and "H1 COUNT =" not in text and "SURFACE ROUGHNESS = 3.20 um" in text, "sparse-control visible content differs")
    for name in ("mutations.json", "suite.json", "authoring-export-check.json"):
        backup = dest / "private" / ("initial-144-" + name)
        require(not backup.exists(), "history backup already exists")
        shutil.copyfile(dest / "private" / name, backup)
    checks["rows"].append({"case_id": packet["case_id"], "packet_sha256": sha256(folder / "packet.json"), "solid_count": len(part.solids()), "is_valid": part.is_valid,
                          "actual_envelope_mm": list(part.bounding_box().size), "actual_volume_mm3": part.volume, "actual_pdf_pages": len(pdf.pages), "actual_pdf_text": text,
                          "actual_hashes": {a["path"]: a["sha256"] for a in packet["artifacts"]}})
    summary = suite_summary(specs, 42)
    checks["summary"] = dict(summary, output=str(dest))
    write_json(dest / "private" / "mutations.json", {"schema_version": "1.0", "warning": "Generator intent is not ground truth", "mutations": specs})
    write_json(dest / "private" / "suite.json", summary)
    write_json(dest / "private" / "authoring-export-check.json", checks)
    print(f"Added sparse CAD-authoritative clean control {row['case_id']}; {len(specs)} actual presentations, original 144-case manifest and export evidence retained.")
    print(summary)


if __name__ == "__main__":
    main(sys.argv[1])
