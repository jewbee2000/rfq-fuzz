# Reproduce the M0 prototype

Native Windows was exercised on Python 3.12.2 x64. Linux has not been exercised at M0; R22's two-platform release acceptance remains open. No SolidWorks, GPU, Beads, Gas Town, cloud account, or paid model API is needed.

From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install pip==26.2.1
./.venv/Scripts/python.exe -m pip install -r requirements-m0.lock
./.venv/Scripts/python.exe -m pip check
./.venv/Scripts/python.exe tools/smoke.py
```

`requirements-m0.in` records the four deliberate selections; the lock pins every resolved transitive dependency. `evidence/M0/install-report.json` retains downloaded artifact URLs/hashes and package metadata. `evidence/M0/environment.json` records platform, interpreter, distribution versions and installed license-notice paths. The environment is repository-local and excluded from Git. This lock is a tested Windows resolution, not a claimed universal platform lock.

The smoke command needs Poppler's `pdftoppm` on PATH. This host uses the Codex bundled Poppler runtime (version recorded in environment.json); the product code never assumes its absolute path. On a clean Windows consumer host install a compatible Poppler build and put its `Library/bin` on PATH. On Debian/Ubuntu the anticipated command is `sudo apt-get install poppler-utils`; Python setup uses `python3.12 -m venv .venv` and `.venv/bin/python`. These other-host instructions are unverified until M5. Record any changed renderer version; compare semantics and numeric tolerances rather than byte-identical kernel exports.

Draftwright 0.4.35 requires build123d <0.11 on Python 3.12. Do not replace build123d 0.10.0 with the incompatible current 0.13 line. The selected OCCT binding is cadquery-ocp 7.8.1.1.post1. Draftwright renders vector drawing geometry through svglib/ReportLab; RFQFuzz uses an independent Poppler process for PNG rendering. PDFium is installed as a Draftwright dependency and is available for independent cross-render checks.

See `evidence/M0/environment.md` for actual checks and `docs/LICENSES.md` for license direction. Later M0 commands are documented in the gate; later milestones are not implemented by this setup.

