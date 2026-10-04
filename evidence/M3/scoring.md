# T10 acceptance — evidence matching and per-track accounting

Requirements: R10, R12–R15. Actual command:
`./.venv/Scripts/python.exe -m pytest tests/contracts tests/scoring tests/adapters -q`

Result: **51 passed in 2.20 s**. `evidence/M3-scoring-tests.txt` retains output.
An earlier combined collection failed on identical test module basenames; the
failure is retained in `M3-scoring-collection-failure.txt`. Pytest importlib mode
fixes collection without changing M0 source. `testpaths` now includes all tests.

Independent read-only review challenged the matcher before closure. Identity
(category, public obligation/feature, every required artifact witness) is matched
before conclusion correctness, so explicit false clears and advisory/exclusion
errors remain measurable. Whitespace/case and +/- presentation normalize;
units/metric names/numbers remain intact. Conservative canonical source quoting
is required; unsupported paraphrases remain unadjudicated. It is not an opaque
language-model judge. Duplicate grounded findings count once and are retained.
Private expected root causes must be unique, so one units fault cannot require
credit for multiple symptoms. Expected obligation records are also unique.

Hand cases cover all conclusion classes, per-track counts, always-flag/clear/
abstain behavior, wrong feature/region/unit/metric and missing artifact, partial
coverage, silent misses, invalid exclusion, actual packet binding, stale hashes
and raw/oracle-bound category adjudications. All three hashes must match before
comparison. Unmatched findings prevent finalized precision claims. Counts and
numerators/denominators are explicit; no composite intelligence score exists.

Assessment: T11 challenge work and T12 offline reporting may proceed. T10 is
software acceptance on hand examples; integrated corpus evidence remains T11.
