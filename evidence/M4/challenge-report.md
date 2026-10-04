# T11 evaluator challenge and replay/lineage evidence

Date: 2026-10-04 (America/Los_Angeles). Requirements: R07, R16, R17. Should
requirement S05 is explicitly deferred below. Worker base:
`bd93538847dcae3ff141db56bec153533a54bae1`; isolated worktree
`.workers/challenge-v1`, root isolated Python 3.12.2 environment.

The fixed acceptance tests detect **all six deliberately broken implementations**.
These are actual edits to the production validator/scorer/contracts source in
ignored work copies. They are not fabricated reviewer answers or manually assigned
"mutant" labels. The production checkout's source was never edited. Each copy is
compiled before testing; a syntax/import failure is not counted as detection.
The named unchanged acceptance test must fail with a semantic assertion, not an
execution error. Original/mutated source hashes, exact diffs, commands, outputs,
actual artifact inputs and result records are retained under `challenge-tests/`.

| Conceptual fault | Actual source change | Observed failing assertion |
|---|---|---|
| Unit conversion | Disable inch-to-mm normalization in numeric drawing parser | Correct converted drawing becomes `contradiction` instead of `supported_clear` |
| Boundary comparison | Replace W1 `<` with `<=` | 0.80 mm equality becomes `advisory` instead of `supported_clear` |
| Severity | Return setup `profile_exclusion` for a thin-wall advisory | 0.60 mm W1 returns the wrong conclusion class |
| Deduplication | Award detection credit for every matching duplicate | Three grounded warnings produce detected count 3 instead of 1 |
| Leakage | Stop recursive private-key scanning inside dictionaries | A nested `oracle`/`expected_conclusion` field is accepted rather than rejected |
| Unknown handling | Change unresolved stage fallback to clear | No explicit/default finish stage becomes `supported_clear` instead of `missing_information` |

`challenge-tests/summary.json`: **6 of 6 killed**, no surviving selected mutants.
Each directory contains `source.diff`, `pytest.txt` and `result.json`. Exact
source-file and patch hashes bind the result to the implementation exercised.
This is a small relevant challenge set, not exhaustive mutation coverage or proof
that every evaluator error is detectable. OCCT and the finite annotation reader
remain shared dependencies; none of these tests establishes industrial competence.

## Actual acceptance commands

`../../.venv/Scripts/python.exe -m pytest tests/metamorphic -q --basetemp evidence/M4/metamorphic-tests`

Result: **12 passed**, four inherited build123d deprecation warnings, 21.07s.
Log: `metamorphic-acceptance.txt`. The tests inspect actual STEP/PDF/PNG exports for
converted inches, exact boundaries, profile relaxation, unresolved finish stage,
one-root O03 grouping and repeated semantics. Repeated exports preserve measured
geometry, visible annotations and finite conclusions; actual artifact hashes are
checked against each PacketSpec. In this same environment the deterministic PDF
and PNG bytes also matched. Cross-platform STEP byte identity is deliberately not
claimed, because exporter timestamps/identifiers may vary.

`../../.venv/Scripts/python.exe tools/challenge_evaluator.py --out evidence/M4/challenge-tests`

Result: **passed, 6/6 source mutants killed**. The clean fixed-test baseline passed
before any mutated copy ran. Its output and command are `challenge-tests/baseline.txt`
and `baseline-command.json`; each selected mutated command returned pytest exit 1
for the expected semantic assertion. No mutant changed the acceptance test.

`../../.venv/Scripts/python.exe tools/challenge_evaluator.py --audit-lineage evidence/M2/core-suite/private/mutations.json --out evidence/M4/challenge-tests/lineage-audit.json`

Result: **passed, 145 cases**. Source-family, layout-ancestry and twin/source-ancestry
groups each occur in only one partition. All current generated cases are in
`development`: this proves no cross-partition leakage in the released configuration,
and provides no held-out transfer score. A deliberate partition reassignment fails
all three relevant overlap checks. The immutable public corpus has exactly its four
allowlisted files per case, valid opaque identities and bound actual hashes.

## Should deferral and remaining milestone evidence

**S05 deferred:** arbitrary font/layout/view-order/PNG-resolution transformations
are not implemented in the single bounded, visually audited v1 template. The
converted-unit and profile-counterfactual tests preserve meaning within this
template; they are not evidence of broad presentation invariance. Future presentation
variants need documented legibility bounds, actual artifact and feature-association
verification, independent visual review and separate transfer/error accounting.

The coordinator owns final whole-corpus visual attestation, frozen-code validation,
always-clear/always-flag/always-abstain corpus baselines and exact final counts.
Those results are not substituted with the earlier unverified diagnostic corpus.
The final artifact expected at `evidence/M4/core-validated/oracle.json` must remain
bound to its public packet/profile/oracle versions before reviewer comparison.

## Handoff and milestone assessment

Current task: T11 implementation complete in its permitted files; local commit is
provided with the handoff and recorded by the coordinator after integration. No
failing acceptance command; selected mutant failures are intentional retained
evidence. Environment and base commit are above. Evidence paths: `challenge-tests/`,
`metamorphic-tests/`, `metamorphic-acceptance.txt`, and this report. Unresolved limits:
six finite chosen faults, one drawing layout, one development partition, synthetic
geometry and shared OCCT. Next dependency-ready work: integrate these tests, finish
the coordinator's frozen-corpus/count audit, then T13 consumer replay and T14 release
traceability. The next milestone remains worthwhile: concrete faulty evaluators are
detected and the regression obligations replay. The evidence supports this bounded
workflow, not general drawing-review or manufacturing-approval claims.

No M0 edits, remote publication, hosted packet transfer or outside messages occurred.
