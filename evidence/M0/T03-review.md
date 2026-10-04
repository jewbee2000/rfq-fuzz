# T03: public review, import and comparison acceptance

Requirements: R11/R15, finite M0 subset; contributes R12/R13/R14/R18 semantics without claiming the full later tasks. Prerequisite T02 completed at c038a99 before the independent reviewer dispatch.

Reference path reads only public packets and actual STEP/PDF content using build123d reimport and a known-template pypdf parser. It explicitly lacks PNG visual interpretation; prior independent corpus validation establishes drawing visibility. Raw public reads/runtime values are retained under `runs/reference/`. Reference detects one same-stage contradiction and clears two named controls. General unsupported templates/units are classified separately from errors; unknown, partial, timeout, error and unsupported outputs are never credited as clear.

Independent reviewer dispatch used existing Codex access with `fork_turns=none`, no implementation conversation, private answer, mutation label or reference code. It received only the standalone neutral folder, output schema, prompt and available interpreter. Its own `measure.py` independently reads OCP STEP geometry, checks circular boundaries and material point classification; it inspected all original PNGs and independent actual PDF renders. Exact model version is unavailable and runtime unmeasured; neither is invented. Same-machine restriction is procedural, not enforced adversarial sandboxing. It did not modify public inputs; all hashes were audited. `independent-provenance.json` and `review-handoff/review-output/observations.md` retain the method/limits and first failed/corrected geometry probe.

The public schema allowed free category strings. The initial importer recognized a smaller category vocabulary and retained three unadjudicated findings. Manual hash-bound mappings changed category strings only. They do not alter conclusions/evidence, expected answers or physical assertions. The first import/report remains inspectable as an explicitly annotated harness failure; final external counters are 1/1 detected, 0/2 false alerts, 2/2 correct clears, coverage 3/3. No natural external reviewer regression was observed.

Two changes in `runs/injected/` are **DELIBERATELY INJECTED REFERENCE REVIEWER REGRESSIONS**: ignore the same-stage diameter mismatch (pk-7a1c explicit false clear) and ignore later reaming (pk-4d90 false alert). Original independent raw responses remain untouched. The report has per-case verified callout crops, model volume/cylinder witnesses, actual/expected decisions, raw reviewer findings, manufacturing contract, version/manifest/hash provenance and ordinary local artifact links. CNC advisory remains unsupported, zero obligations scored. No overall manufacturing score or finalized precision.

Performed acceptance commands (logs retained):

```powershell
./.venv/Scripts/python.exe tools/m0.py reference
./.venv/Scripts/python.exe tools/m0.py import-results evidence/M0/runs/reference/review.json --out evidence/M0/runs/imported-reference
./.venv/Scripts/python.exe tools/m0.py import-results evidence/M0/runs/injected/review.json --out evidence/M0/runs/imported-injected
./.venv/Scripts/python.exe tools/m0.py import-results evidence/M0/review-handoff/review-output/review.json --out evidence/M0/runs/imported-independent
./.venv/Scripts/python.exe tools/m0.py import-results evidence/M0/review-handoff/review-output/review.json --adjudication evidence/M0/category-adjudication.json --out evidence/M0/runs/imported-independent-adjudicated
./.venv/Scripts/python.exe tools/m0.py report evidence/M0/runs/imported-reference/run.json evidence/M0/runs/imported-injected/run.json evidence/M0/runs/imported-independent-adjudicated/run.json
./.venv/Scripts/python.exe -m pytest tests/m0 --basetemp evidence/M0/final-tests -q
./.venv/Scripts/python.exe tools/replay_m0.py
./.venv/Scripts/python.exe tools/audit_m0.py
```

Results: integrated 33 passed, four dependency deprecation warnings (14.42s). Relevant post-link portability checks: 18 passed, same four warnings (2.17s). Eight-command offline replay passed, identical finite counts, 34 local links resolved. Current public inputs unchanged and identical to root public bytes. Browser local-file preview was security-policy rejected; no workaround. Saved HTML source/links and escaped content were audited, browser rendering unverified. Original STEP/PDF/PNG visual/geometry inspection is verified separately.

Independent development reviewer inspected scoring/adjudication/report, recomputed counts and hashes, and found no blocker for these three manually inspected M0 responses. Numeric token matching is not semantic evaluation of arbitrary reviewer reasoning. General adversarial inputs, Linux, industrial transfer and broader part/operator coverage are later gates. Completion commit is recorded in tasks.json. Assessment: PASS finite feasibility; next contract work remains worthwhile, but this run stops at the user's M0 checkpoint.
