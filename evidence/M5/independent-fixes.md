# Independent consumer/code audit corrections

An independent read-only reviewer used actual frozen demo artifacts to expose
three report/CLI gaps and a material scorer grounding bug. Its scripts, deliberately
corrupted input copies, source hashes and before/after observations are retained
in `independent-final-review/`. They are diagnostic controls, not normal packets.

1. Reports compared run manifests to each other but did not bind the supplied
oracle/public sources to those scored versions. Reports now verify exact oracle,
packet-suite/profile and actual artifact hashes, plus original raw-response hashes,
before writing even a single-run report. Revised source inputs fail explicitly.
2. Metric fields were interpolated without escaping. Every displayed field is now
escaped; actual report source/unsafe-element auditing runs before returning.
3. Reference parsing errors were retained but CLI summary exited0. It now reports
per-state counts and returns2 for contains_failures; the original error row/raw
observations remain retained.
4. Scorer substring matching credited observed `H1 count=40`/`H1 COUNT = 30` against
required `4`/`3`. Exact complete canonical witness equality after benign
case/whitespace/plus-minus normalization now rejects the altered numbers. An actual
O02corecase regression test preserves this failure. Narrative evidence remains
conservatively unadjudicated rather than inferred into a match.

Actual acceptance logs: `evidence/M5-independent-fixes-tests.txt` (6checks),
`M5-report-audit-final-tests.txt` (5reportchecks), `M5-numeric-fix-tests.txt`
(33scorer/metamorphic/report checks). Final integrated verification follows this
correction. No original M0 source/evidence or genuine external conclusion changed.

Standalone public exports now include the full transport/witness protocol so a
reviewer need not read private evaluator or contract implementation code.
