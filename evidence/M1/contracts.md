# T04 acceptance — versioned contracts

Requirements: R02, R10. Shared semantic contract is
`src/rfqfuzz/v1/contracts.py`; six generated transport schemas are in `schemas/v1`.
`docs/V1_CONTRACT.md` freezes meanings before parallel implementation. The
read-only independent design review confirmed the separate M0 namespace, per
obligation coverage/evidence and immutable hashes as essential boundaries.

Actual acceptance command on 2026-10-04:
`./.venv/Scripts/python.exe -m pytest tests/contracts tests/m0 -q`

Result: **64 passed**, four pre-existing build123d deprecation warnings, 12.68 s.
All 33 M0 tests are preserved. Positive/negative v1 cases cover all conclusion
classes, missing premises, private labels, traversal, invalid-oracle exclusion,
conflicting assertions, timeout decisions, malformed JSON and refused implicit
M0 migration. `tools/schema_v1.py` ran successfully to create the six transport
schemas. Semantic nested checks are required in addition to these schemas.

Assessment: T05/T06/T09 may proceed. Contract tests establish interface semantics;
they do not yet establish exported-artifact correctness or release acceptance.
