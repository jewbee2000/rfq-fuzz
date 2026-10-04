"""Public-only known-template reference reviewer; not independent ground truth."""
from pathlib import Path
import re
import time
from build123d import import_step, GeomType
from pypdf import PdfReader
from .contracts import VERSION, OBLIGATION, read_packet, sha256, write_json

class UnsupportedInput(ValueError):
    pass

def review_public(public_root, out):
    out = Path(out)
    if out.exists():
        raise ValueError("reference output exists; preserve prior run")
    results, raw = [], []
    for folder in sorted(Path(public_root).iterdir()):
        start = time.perf_counter()
        row = {"case_id": folder.name, "packet_sha256": sha256(folder / "packet.json"), "status": "error",
               "reviewed_modalities": [], "reviewed_obligations": [], "findings": [], "assertions": [],
               "cnc_advisory": "unsupported", "runtime_seconds": None, "raw_output_reference": "public-read.json"}
        try:
            packet = read_packet(folder)
            text = "\n".join(p.extract_text() for p in PdfReader(folder / "drawing.pdf").pages)
            model = import_step(folder / "part.step")
            cylinders = model.faces().filter_by(GeomType.CYLINDER)
            diameters = sorted(2 * f.radius for f in cylinders)
            match = re.search(r"(\d+)[×x]\s*[øØ⌀]\s*(\d+(?:\.\d+)?)\s*±\s*(\d+(?:\.\d+)?)\s*THRU", text)
            if match is None or len(model.solids()) != 1 or len(diameters) != 4:
                raise UnsupportedInput("unsupported reference template/topology")
            count, diameter, tolerance = int(match[1]), float(match[2]), float(match[3])
            model_stage = re.search(r"MODEL STAGE: ([A-Z]+)", text)[1].lower()
            drawing_stage = re.search(r"DRAWING STAGE: ([A-Z]+)", text)[1].lower()
            if model_stage != packet['manufacturing']['model_stage'] or drawing_stage != packet['manufacturing']['drawing_stage']:
                raise ValueError("drawing/context stage conflict")
            if model_stage == drawing_stage:
                conclusion = "supported_clear" if count == len(diameters) and all(diameter-tolerance <= d <= diameter+tolerance for d in diameters) else "contradiction"
                reason = "At the same stage, the drawing interval must contain the STEP nominal bore."
            else:
                transition = packet['manufacturing']['transition']
                if not transition or transition.get('operation') != 'ream' or transition.get('feature_id') != 'H1' or "REAM AFTER MODEL STAGE TO DRAWING SIZE" not in text:
                    conclusion, reason = "missing_information", "No explicit operation resolves the stage difference."
                else:
                    conclusion = "supported_clear" if count == len(diameters) and all(d < diameter-tolerance for d in diameters) else "contradiction"
                    reason = "Declared later reaming explains the larger final bore; process feasibility is outside scope."
            item = {"obligation": OBLIGATION, "feature_id": "H1", "category": "diameter_consistency", "conclusion": conclusion,
                    "drawing_evidence": f"drawing.pdf page1 H1: {count}x diameter {diameter:g} +/-{tolerance:g} mm THRU",
                    "geometry_evidence": f"part.step: {len(diameters)} cylindrical bore walls; diameters {diameters} mm",
                    "context_evidence": f"model_stage={model_stage}; drawing_stage={drawing_stage}; transition={packet['manufacturing']['transition']}",
                    "rationale": reason}
            row['findings' if conclusion == 'contradiction' else 'assertions'].append(item)
            row.update(status="completed", reviewed_modalities=["step", "pdf", "context"], reviewed_obligations=[OBLIGATION])
            raw.append({"case_id": folder.name, "packet_sha256": row['packet_sha256'], "extracted_pdf_text": text,
                        "measured_diameters_mm": diameters, "geometry_volume_mm3": model.volume})
        except UnsupportedInput as exc:
            row['status'] = 'unsupported'
            raw.append({"case_id": folder.name, "unsupported": str(exc)})
        except (ValueError, KeyError, OSError, TypeError, IndexError) as exc:
            if isinstance(exc, ValueError) and str(exc).startswith('unsupported'):
                row['status'] = 'unsupported'
            raw.append({"case_id": folder.name, "error": f"{type(exc).__name__}: {exc}"})
        row['runtime_seconds'] = time.perf_counter() - start
        results.append(row)
    response = {"schema_version": VERSION, "reviewer": {"name": "RFQFuzz reference", "version": "m0-template-1",
                "configuration": "Public-only STEP reimport/build123d and pypdf template parser. PNG interpretation unsupported; drawing visibility established only by prior independent corpus validation.",
                "provenance": "Local hand-coded protocol reference, not a general reviewer or oracle"}, "results": results}
    write_json(out / 'public-read.json', raw)
    write_json(out / 'review.json', response)
    return response
