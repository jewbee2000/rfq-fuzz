# Separate synthetic transfer-packet authorship

Created locally on 2026-10-04 by a separate Codex agent. This is an agent-authored
synthetic RFQ fixture, not a human-engineer-authored packet, a physical part,
manufacturing validation, or evidence of industrial generalization. The useful
diagnostic is distinct geometry-author and drawing-layout ancestry.

The public packet folder is `pk-48bd731ca9e2`. It contains only `packet.json`,
`part.step`, `drawing.pdf`, and `drawing.png`. The author script, analytic intent,
check results, logs, and inspection notes are outside that folder. Do not export
`PRIVATE_AUTHOR_EXPECTATIONS.json` to reviewers.

## Inputs and separation

The author read `AGENTS.md`, the research/requirements scope,
`docs/V1_CONTRACT.md`, and `src/rfqfuzz/v1/contracts.py`. The only fixture read was
the public `evidence/M2/generator-artifacts-v2/pk-000000000003/packet.json`;
only its complete public CapabilityProfile was copied. Its transport served as
the field-shape example. No project generator, validator, reference-reviewer,
private oracle, mutation label, or source parameters were read or imported.

Geometry was newly authored with low-level OCP boxes and a boolean cut. Drawing
paths/text were authored with a new ReportLab layout: release/process/dimension
rail at left, PLAN and XZ SECTION A-A stacked at right. No existing PDF, PNG,
STEP, or drawing-template bytes were reused. PNG was rendered from the actual
exported PDF by Poppler, not drawn independently.

Ordinary STEP export uses a supported writer-model edit to set the sole PRODUCT
ID/name to `TRP-217 REV A`; OCCT otherwise appends a shape number. Exported geometry
is one centered body with a single +Z opening. No material or tolerance PMI is
claimed in STEP; those premises are public context and visible drawing notes.

## Analytic choices and public context

- Body bounds: X [-35,35], Y [-22,22], Z [-9,9] mm.
- Pocket bounds: X [-25.5,32.5], Y [-15,15], Z [-1,9] mm.
- Envelope 70 x 44 x 18 mm; pocket 58 x 30 x 10 mm.
- +X wall 2.5 mm; -X wall 9.5 mm; Y walls 7 mm; floor 8 mm.
- Analytic solid volume: 70*44*18 - 58*30*10 = 38,040 mm3.
- Known material 6061-T6, no finish, both geometry stages finished,
  explicit tolerance stage after_finish, permitted release pair A/A.
- Fixed XYZ stock allowance [2,2,2] and fixture allowance [4,4,6] mm, each
  interpreted as total added axis extent. Occupied extent [76,50,26] mm.
- Public standard profile retained in full, including rule provenance and limits.
- Finite required visible roughness representation: SURFACE ROUGHNESS = 3.20 um.
- Finite obligations: obj-units, obj-material, obj-requirement, obj-release,
  cnc-wall, cnc-envelope, cnc-stage; explicit P1/W1 view associations.

Intended conclusions are private author intent, not ground truth. Coordinator
validation and independent registration/adjudication are still required.

## Actual acceptance work

From the repository root with its isolated Python environment:

```powershell
.venv/Scripts/python.exe work/transfer-author/author_transfer.py
.venv/Scripts/python.exe work/transfer-author/verify_export_ocp.py
```

The successful author invocation is retained in `AUTHOR_COMMAND_REPAIR2.log`.
Earlier logs retain the failed PRODUCT-name assumption and ReportLab dash API
call, both repaired before final export. `REIMPORT_COMMAND.log` records the
successful separate-file checks. No failed check is described as passing.

`verify_export_ocp.py` is a separate script, does not import the author script or
project readers, and never reads private expectation metadata. It reimports the
actual STEP, checks shape validity, one solid, exact bounding box/volume, eleven
planar faces, each pocket-wall/floor boundary, floor area, wall thickness, depth,
exported units and PRODUCT. It also reopens the actual PDF, verifies its sole page
and every canonical label, verifies no raster-image XObjects, and rehashes all
three final artifacts. Values and tolerance (1e-6 mm) are retained in
`STEP_PDF_REIMPORT_CHECKS.json`; extracted text is retained in `ACTUAL_PDF_TEXT.txt`.

This is independent code organization and final-file inspection by the author,
not an independent engineer/oracle. The OCP reader/writer share the OCCT kernel;
common-mode CAD-kernel error remains possible. Coordinator checks remain needed.

The author visually inspected the complete one-page actual PDF raster. The final
hash-bound record is `VISUAL_INSPECTION.json`. The PNG is 2500 x 1806 pixels at
200 DPI. Poppler logged unavailable display fonts for unrelated legacy font
families; all document Helvetica text and geometry were visibly rendered.

## Versions, licenses and provenance

`AUTHOR_ENVIRONMENT.json` records Python 3.12.2 on Windows 11, actual interpreter,
Poppler 26.07.0, and installed package versions. `DEPENDENCY_METADATA_LICENSES.json`
retains local package license metadata and project URLs. Used author/check stack:

- cadquery-ocp 7.8.1.1.post1: OCP bindings' upstream
  [Apache-2.0 license](https://raw.githubusercontent.com/CadQuery/OCP/master/LICENSE).
  Bundled OCCT is separately LGPL 2.1 with the OCCT additional exception;
  [official OCCT licensing statement](https://occt3d.com/open-cascade-technology/index.html).
  The installed OCP wheel's metadata did not declare a license; that omission is
  retained rather than silently overwritten.
- ReportLab 5.0.1: BSD license according to installed metadata; copied installed
  LICENSE is retained under `dependency-licenses`.
- pypdf 6.9.1: BSD-3-Clause; copied installed LICENSE retained.
- Poppler 26.07.0: bundled runtime renderer, version/copyright output retained.
  [Official project](https://poppler.freedesktop.org/); no Poppler binary is
  redistributed. This packet does not change the runtime's license inventory.
- build123d 0.10.0 is available in the same environment but not called by the
  author/check scripts; Apache-2.0 metadata and installed LICENSE/NOTICE retained.

License observations retrieved/read on 2026-10-04. Own scripts and newly authored
artifacts are offered under the MIT license in `LICENSE.txt`. No proprietary
standards tables were copied. Rule cards are the already-public project's concise
paraphrases and synthetic selected thresholds, not supplier manufacturing approval.

## Handoff

Task supports requirements R02/R03/R04/R08/R09/R16/R19/R20 and S01/S05/S07 only
within a synthetic-source diagnostic. At author start the repository commit was
`66a996bb9496021972bc381281fce76907762aaa`. No source, task state, requirement status,
or commits were changed by this subtask; its directory is ignored by Git. This
explicit coordinator instruction supersedes the working agreement's normal
completed-task commit requirement for this temporary evidence handoff.

Current failing command: none among the commands above after repair. Remaining
assumption: public family/feature correspondence and canonical drawing tokens
will be independently accepted by the coordinator's bounded validator. Next task:
coordinator validates actual artifact bytes, reviews this author intent separately,
registers if supported, and retains or quarantines any disagreement. A successful
registration would justify this small source/layout diagnostic, but would still
leave engineer-authored transfer and industrial-usefulness claims unestablished.
