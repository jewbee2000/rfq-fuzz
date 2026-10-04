# T08 integrated final-artifact acceptance

Requirements R04/R05/R06/R08. Independent implementation integrated at bd93538
(worker044dc175). Actual root command `.venv/Scripts/python.exe -m pytest
tests/artifact_validation -q`:49passed,4upstreamwarnings; retained
`T08-root-integration.txt`. No checks inferred from generation metadata.

Coordinator inspected all145 exported annotation regions in25 actual PNG sheets
and seven full pages, listed in `evidence/M4/visual-review/attestation.json`.
This is AI visual review of the finite shared layout, supplemented by per-file
native glyph/raster and correspondence checks. No human engineer or general OCR
accuracy claim. PDF/PNG hashes bind the review to the exact exported bytes.

Actual final command `.venv/Scripts/python.exe tools/validate_core.py` reopens
all145STEP/PDF/PNG/publiccontracts and checks observed mutation deltas with frozen
validator code:145valid,0quarantined,0unsupported,0timeouts. Full measurements,
visibility evidence, crops, native parser logs and expectations are retained at
`evidence/M4/core-validated`; stdout at `evidence/M4/core-validation-final.txt`.
The previous worker core observation is retained as a superseded diagnostic;
the final code treats unresolved equal-authority material premises as unknown
for conditional CNC rules.

The initial direct Python invocation failed because the package had not been
installed and no source path was supplied (`evidence/M4/core-validation.txt`).
The repository entry point records its explicit source path; installation is now
also available. No fixture was scored from that failed invocation.

M2 decision: continue to evaluator challenge and independent consumption.
These fixtures establish finite regression infrastructure feasibility. They share
OCCT and one drawing layout; all145core presentations remain development cases.
They establish no manufactured-part or held-out industrial performance evidence.
