"""One bounded synthetic challenge, generation owns intent only (AGPL-3.0-only)."""
from pathlib import Path
import subprocess
from build123d import Box, Cylinder, Pos, export_step
from draftwright import Sheet
from .contracts import VERSION, OBLIGATION, sha256, write_json

CASES = (
    ("pk-7a1c", 6.80, "finished", "finished", "defective"),
    ("pk-b8e2", 6.00, "finished", "finished", "repaired"),
    ("pk-4d90", 6.80, "intermediate", "finished", "valid_alternative"),
)
CENTERS = ((-25, -15, 0), (-25, 15, 0), (25, -15, 0), (25, 15, 0))

def generate(out):
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError("output exists: choose a new directory to preserve prior evidence")
    mutations = []
    part = Box(80, 50, 8)
    for xyz in CENTERS:
        part -= Pos(*xyz) * Cylinder(3, 12)
    for case_id, nominal, model_stage, drawing_stage, variant in CASES:
        dest = out / "public" / case_id
        dest.mkdir(parents=True)
        export_step(part, dest / "part.step")
        sheet = Sheet(part, title="Mounting plate", number="MP-001", revision="A", date="2026-10-04",
                      material="6061-T6", tolerance="SEE CALLOUT", drawn_by="RFQ author", page="A4", scale=1)
        env = sheet.envelope()
        group = sheet.hole(diameter=nominal, at=CENTERS[0], axis="z", through=True,
                           count=4, members=CENTERS).tolerance(0.05)
        sheet.authored_dimensions()
        for role in ("width.length", "height.length", "depth.length"):
            sheet.dimension(env, role)
        sheet.dimension(group, "bore.diameter")
        transition = None
        notes = ["ALL DIMENSIONS IN mm", "H1 = ALL FOUR Z THROUGH BORES",
                 f"MODEL STAGE: {model_stage.upper()}", f"DRAWING STAGE: {drawing_stage.upper()}", "FINISH: NONE",
                 "VIEWS SHOW SUPPLIED MODEL AT MODEL STAGE"]
        if model_stage != drawing_stage:
            transition = {"operation": "ream", "feature_id": "H1", "from_stage": "intermediate", "to_stage": "finished", "target": "drawing bore callout"}
            notes.append("H1: REAM AFTER MODEL STAGE TO DRAWING SIZE")
        else:
            notes.append("H1: DRAWING AND MODEL APPLY AT SAME STAGE")
        sheet.notes(notes, prefer="tr")
        sheet.export(str(dest / "drawing"), formats=("pdf",))
        subprocess.run(["pdftoppm", "-singlefile", "-r", "200", "-png", str(dest / "drawing.pdf"), str(dest / "drawing")], check=True, timeout=60)
        packet = {
            "schema_version": VERSION, "case_id": case_id, "part_id": "MP-001",
            "release_association": {"model_id": "MP-001", "model_revision": "A", "drawing_id": "MP-001", "drawing_revision": "A", "permitted_pairs": [["A", "A"]]},
            "units": {"model": "mm", "drawing": "mm"},
            "authority": {"nominal_geometry": "STEP at model_stage", "views": "drawing geometry views depict supplied STEP at model_stage; numeric bore callout governs drawing_stage", "tolerances": "visible drawing callouts at drawing_stage", "process": "public manufacturing contract and visible drawing notes", "consistency": "same-stage drawing intervals must contain STEP nominal; explicit later-stage operation governs its target stage"},
            "manufacturing": {"model_stage": model_stage, "drawing_stage": drawing_stage, "transition": transition, "material": "6061-T6", "finish": "none"},
            "profile": {"id": "m0-package-consistency", "version": VERSION, "synthetic": True, "scope": "Finite H1 package consistency only; CNC advisories and process feasibility unsupported", "rule_provenance": "project-selected release contract, 2026-10-04; no universal manufacturing threshold"},
            "setup": {"orientation": "bores parallel to Z; XY plate; no workholding/tooling determination"},
            "features": [{"id": "H1", "type": "through_bore_group", "drawing_association": "all four bores in plan view and the grouped 4x callout", "centers_mm": [list(c) for c in CENTERS]}],
            "obligations": [OBLIGATION],
            "artifacts": [{"path": f, "sha256": sha256(dest / f), "media_type": media} for f, media in (("part.step", "model/step"), ("drawing.pdf", "application/pdf"), ("drawing.png", "image/png"))],
        }
        write_json(dest / "packet.json", packet)
        mutations.append({"case_id": case_id, "variant": variant, "operator": "O01", "version": VERSION,
                          "seed": 42, "allowed_delta": "bore annotation numeric value only" if variant != "valid_alternative" else "model stage, explicit ream transition and visible stage notes",
                          "forbidden": ["STEP geometry", "units", "material", "identity", "envelope", "hole count/centers", "unrelated notes"],
                          "intended_drawing_nominal_mm": nominal})
    write_json(out / "private" / "mutations.json", {"schema_version": VERSION, "mutations": mutations, "warning": "Generator intent is not ground truth"})
    return {"output": str(out), "public_cases": len(CASES), "scope": "one synthetic plate ancestry"}
