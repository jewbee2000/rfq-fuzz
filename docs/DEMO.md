# Local v1 consumer demo

Python3.12 is the tested interpreter family. Install in an isolated environment:

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-v1.lock -r requirements-build.lock
.venv/Scripts/python.exe -m pip install --no-deps --no-build-isolation -e .
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m rfqfuzz.v1 demo examples/v1-demo work/my-demo
```

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-v1.lock -r requirements-build.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m pip check
.venv/bin/python -m rfqfuzz.v1 demo examples/v1-demo work/my-demo
```

Generation additionally requires Poppler `pdftoppm` on PATH (Windows verified
26.07; Linux environment record supplies its actual version). On Ubuntu, install
`python3.12-venv poppler-utils libgl1 libglib2.0-0` before the isolated environment.
Installation needs package downloads or a prepared wheel cache; the complete
consumer replay needs no internet, API key, paid model, GPU or proprietary CAD.
The installed `rfqfuzz` entry point works outside the repository when paths are
absolute. `tools/rfq_v1.py` is an optional repository-local entry point.

Open `work/my-demo/report/index.html`. The15case replay reopens the exact audited
STEP/PDF/PNG bytes, validates their hash-bound visual attestations, exports a
public-only bundle, imports two retained raw responses and compares separate
package-consistency/CNC-advisory tracks. It writes `demo-result.json`, immutable
raw imports, native observations, per-track counts and the local HTML report.

The baseline response is an actual public-only template reference that shares
artifact readers with the validator. The second response deliberately removes a
material contradiction and falsely flags a valid diameter control. Expect exactly
`detected -> silent_miss` and `correct_clear -> false_alert`. This is a replay
diagnosis, not a fresh external review or an industrial performance result.
Genuine external observations are retained separately at M0 and M5.

The replay manifest hashes every supplied input. Regenerated exports may differ
in timestamps or rendering bytes; they require fresh actual visual review. Never
reuse an old attestation on regenerated files. Without it, validation reports
`unverified` and exits2; no case becomes a pass automatically.

Every workflow step is also independently available:

```sh
rfqfuzz generate work/new-suite --seed 42
rfqfuzz validate work/new-suite work/new-observations
rfqfuzz export-review work/new-suite/public work/reviewer-bundle
rfqfuzz import-results YOUR_RESPONSE.json work/new-suite/public YOUR_VALIDATED_ORACLE.json work/run
rfqfuzz compare BEFORE_RUN.json AFTER_RUN.json work/changes.json
rfqfuzz report YOUR_VALIDATED_ORACLE.json work/new-suite/public work/report BEFORE_RUN.json AFTER_RUN.json
```

Use a new output directory for each attempt. Structured errors, timeouts,
unsupported inputs, invalid fixtures, uncovered duties and missing information
remain distinct. Local process adapters accept an explicitly configured argv;
packet text never selects a command. No hosted adapter is implemented.
The public response format is in `REVIEWER_PROTOCOL.md`.

Python API has the same entry points:

```python
from rfqfuzz.v1 import api
result = api.demo("/absolute/path/examples/v1-demo", "/absolute/path/new-demo")
# api.generate, api.validate, api.export, api.import_results, api.compare, api.report
```

M0 is a frozen independent regression path: `tools/replay_m0.py`,
`tools/audit_m0.py`, and `pytest tests/m0`. It is not silently migrated to v1.
