# T09 acceptance — public-only adapters

Requirements: R11, R12, R19. Actual command:
`./.venv/Scripts/python.exe -m pytest tests/adapters -q`

Result on 2026-10-04: **5 passed in 2.14 s**. Retained log:
`evidence/M3-adapters-tests.txt`. Inputs use the actual preserved M0 STEP/PDF/PNG
with a v1 transport wrapper for adapter-only tests; they are not new validated
geometry fixtures or corpus members.

`rfqfuzz.v1.adapters` exports only audited ordinary files, fixed public context
and neutral instructions. PDF/PNG signature/page/size/metadata auditing runs in
a bounded subprocess. Manual import retains original bytes even when malformed;
missing rows remain missing for scoring. Local processes receive an explicit
configured argv and public bundle request, never a command extracted from packet
text. Attempts preserve requests, input audit, stdout, stderr, response and
failure reasons. Timeout testing started a sleeping descendant and terminated
the process tree. Output directories cannot overwrite prior attempts.

The existing genuine M0 external reviewer/raw observations remain retained in
`evidence/M0/review-handoff`; T13 will exercise the expanded interface independently.
No hosted adapter or packet transmission exists. Local same-user execution is
procedural blinding, not adversarial containment or an enforced network sandbox.
Configured local processes are trusted code. Offline import/export needs no API.

Assessment: lifecycle is ready for T10 matching and T12 reporting/resume work.
The adapter tests establish error accounting, not review competence.
