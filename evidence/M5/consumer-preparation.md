# T13 consumer implementation and initial acceptance

Local v1 CLI and Python API implement generate/validate/public export/structured
import/compare/report, with installable entry point, reference/local process modes,
resume planning and frozen offline replay. M0 is unchanged.15representative cases
are frozen with exact input hashes and actual public-template-reference raw output;
the second response is explicitly injected. No API or packet upload is used.

Actual commands: build dependencies installed from requirements-build.lock;
editable install `pip install --no-deps --no-build-isolation -e .` succeeded.
`pytest tests/adapters tests/consumer -q` after the export correction:13passed
(`evidence/M5-consumer-fixed-final-tests.txt`). Earlier failure traces retained:
the first corpus consumer rejected `permutation` as a mutation label; whole-word
label checks fix this while recursive forbidden-key checks remain. A failed patch
application caused one collection error, separately retained. CLI script naming
collision was corrected by `tools/rfq_v1.py`; installed module/entrypoint works.

`python -m rfqfuzz.v1 demo examples/v1-demo evidence/M5/coordinator-demo-v2`
is the actual accepted complete local workflow. Original failed attempt remains
`coordinator-demo`, with CLI stderr at `evidence/M5-demo.txt`. This acceptance
does not replace independent Windows/Linux clean environments.

Separately authored transferv2 is independently read and visually inspected:
one solid,70x44x18mm envelope,58x30x10mm pocket,W1=2.5mm,38040mm3volume,
occupied76x50x26mm under namedprofile. Seven conclusions supported_clear agree
with separately retained author intent, read only after independent validation.
Original `REV = A` label was rejected by finite importer vocabulary; compatible
`DRAWING REV = A` revision passes and preserves geometric/context meanings.
Both attempts/provenance/licenses retained at transfer-rejected/ and transfer-v2/.
This supports agent-authored importer/layout diagnostics, not human engineer or
manufactured-part evidence; second CAD kernel remains unavailable.

Task completion is pending clean consumer results, external raw review import,
offline browser/source navigation and final requirements audit. Linux pins add
observed pexpect4.9.0/ptyprocess0.7.0 without changing the frozen M0 lock.
