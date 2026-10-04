# T01: native export-stack proof

Requirement R22 (M0 subset; Linux release acceptance remains open). Host: Windows 11 x64, Python 3.12.2, repository-local `.venv`. Selected Draftwright 0.4.35 + build123d 0.10.0; exact transitive pins and license metadata retained in the lock and environment inventory. License direction: AGPL-3.0-only; see `docs/LICENSES.md`.

Actual acceptance commands:

```powershell
./.venv/Scripts/python.exe -m pip check
./.venv/Scripts/python.exe tools/smoke.py
./.venv/Scripts/python.exe tools/record_environment.py
```

Results: pip reports **No broken requirements found**. Smoke reopens an actual STEP containing one solid, volume **9373.805328941526 mm3** (40 x 30 x 8 minus a diameter-6 through-hole). Drawing PDF contains one page. Poppler-rendered PNG is **1754 x 1241** at 150 DPI. Coordinator visually inspected the actual PNG: diameter-6 THRU callout, envelope 40/30/8, views and title are visible and unclipped. This is an export smoke test, not the independent T02 oracle.

Evidence: `smoke/part.step`, `smoke/drawing.pdf`, `smoke/drawing.png`, `smoke/result.json`, `environment.json`, `install-report.json`, root lock, setup instructions and notices. One routine API mismatch failed before the passing run and is retained in `failures.json`; no acceptance criterion was relaxed.

Assessment: stack reuse is viable for the first controlled plate. Proceed to T02; no bounded fallback renderer is needed. Source-text extraction alone remains insufficient because Draftwright embeds invisible search text. Completion commit is recorded in tasks.json after this task commit.
