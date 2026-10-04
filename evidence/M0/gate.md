# M0 feasibility gate — PASS, bounded scope

Date: 2026-10-04, America/Los_Angeles. Decision: **PASS the first synthetic package-consistency feasibility gate**. This permits considering M1; the user's instruction stops this run here. T04 and later remain not started. No production certification, industrial competence, manufactured part, independent engineer validation, or broad release acceptance is claimed.

## Evidence behind the decision

| Gate | Actual result and retained evidence |
|---|---|
| Differentiation | Bounded primary-source recheck found no equivalent combined public workflow in inspected projects. Substantial adjacent work acknowledged. `decision.md` records revisions, limits and first consumer question. |
| Native stack | Python 3.12.2 repository-local `.venv`; Draftwright 0.4.35/build123d 0.10.0/OCCT 7.8.1, PDF renderer/exporter stack pinned. Actual STEP/PDF/Poppler PNG smoke passed; `environment.md`, lock, inventory and download hashes. AGPL-3.0-only project direction with retained dependency notices. |
| Exported oracle | All **3/3 final presentations valid**, six suite invariants true, one contradiction/two supported-clear obligations. Actual STEP single valid solid, four Ø6 mm through-bores, 80 x 50 x 8 mm envelope. Volume error **-1.82e-11 mm3**. Final PDF search values, independent PDFium renders, shipped Poppler PNGs and hash-bound visual inspection agree. `artifact-proof.md`, `validation/oracle.json` and source/crop records. |
| Corruption resistance | T02 combined checks: **15 passed**. Hidden callout/stage note whiteouts preserving search text, actual metre-unit STEP, truncated STEP, independent three-bore geometry, PNG/hash corruption, unsupported schema and missing/stale attestation are rejected or remain unscorable. `negative-tests/` retains actual inputs/results. |
| Public context/blinding | Exported neutral filenames and sufficient stage/authority/group/view premises. Reference gets public files only. Independent reviewer dispatched with `fork_turns=none`, no implementation history or answers; writes its own reader. Exact prompt/schema/public files are in `review-handoff/`; input hashes preserved. Procedural same-machine isolation only. |
| Independent review | Independently reopened every actual STEP, visually inspected all shipped PNGs and actual PDF renders, read manufacturing contract. Raw observations: pk-7a1c contradiction; pk-b8e2 and pk-4d90 supported clear for H1 only. CNC advisory unsupported. `review-handoff/review-output/` retains independent script, measurements, raw/schema JSON, renders and failed/corrected probe. Exact served model version and runtime unavailable (runtime null), not invented. |
| Actionable regression | Reference detects **1/1** defective obligation and clears **2/2** controls. A **DELIBERATELY INJECTED** reference regression creates pk-7a1c detected→explicit-false-clear and pk-4d90 correct-clear→false-alert. Independent raw decisions are unchanged and agree with reference. `report/index.html` and `report/comparison.json` link each changed case to visible callout, actual geometry and stage contract. |

The external response schema permits free category names. The first import retained three unmatched names as **unadjudicated**; its provisional count is a harness mapping limitation, not a reviewer miss. `category-adjudication.json` binds mappings to original raw, finding and oracle hashes; only category vocabulary changes. Conclusions, public feature/obligation, quoted witnesses and expected answers are unchanged. Both first import and adjudicated import are retained. Final external finite counts: detected **1/1**, false alerts **0/2**, correct clears **2/2**, coverage **3/3**, execution failures **0**, unsupported CNC obligations **0 scored**. No finalized precision or statistical claim.

Focused scoring checks passed **17 tests** before the final supported/unsupported reference classification check. They cover hand counts, always-flag/always-clear/always-abstain, duplicate/wrong-feature/wrong-witness findings, partial/error/timeout/unsupported/missing results, unknown class rejection, incompatible manifests, inconsistent assertions, stale adjudication and escaped HTML. Final integrated result: **33 passed in 14.42s**, four upstream build123d import-time deprecation warnings, no failures (`final-tests.txt`). No warnings were suppressed.

After correcting report links to work from arbitrary output directories, the relevant focused checks passed **18/18 in 2.17s**, with the same four upstream warnings (`report-checks.txt`). An actual offline replay performed **8/8 commands successfully** into `work/replay`, reproduced reference/injected/independent counts and resolved **34/34 report links** (`replay-result.json`). The final source audit also checked **34/34 links**, no script elements, no remote assets, immutable reviewer inputs and a clean public leakage scan (`final-audit.json`). This source audit does not establish browser rendering.

## Reproducible commands

Run in the repository root. Setup is `docs/SETUP_M0.md`; complete pinned packages are `requirements-m0.lock`. The frozen artifacts, independent raw review and visual attestation are committed, so offline replay needs no reviewer account/API key. A fresh non-existing output directory preserves prior evidence:

The retained replay above used `./.venv/Scripts/python.exe tools/replay_m0.py`, which runs the workflow below into a fresh `work/replay`. That directory now exists on this host; use another directory in the manual commands for another replay. The script intentionally refuses to overwrite it.

```powershell
New-Item -ItemType Directory -Force work/replay | Out-Null
./.venv/Scripts/python.exe -m pip check
./.venv/Scripts/python.exe tools/m0.py validate --out work/replay/validation
./.venv/Scripts/python.exe tools/m0.py reference --out work/replay/reference
./.venv/Scripts/python.exe tools/inject_m0.py work/replay/reference/review.json --out work/replay/injected/review.json
./.venv/Scripts/python.exe tools/m0.py import-results work/replay/reference/review.json --out work/replay/imported-reference
./.venv/Scripts/python.exe tools/m0.py import-results work/replay/injected/review.json --out work/replay/imported-injected
./.venv/Scripts/python.exe tools/m0.py import-results evidence/M0/review-handoff/review-output/review.json --adjudication evidence/M0/category-adjudication.json --out work/replay/imported-independent
./.venv/Scripts/python.exe tools/m0.py report work/replay/imported-reference/run.json work/replay/imported-injected/run.json work/replay/imported-independent/run.json --out work/replay/report
./.venv/Scripts/python.exe -m pytest tests/m0 --basetemp work/checks
./.venv/Scripts/python.exe tools/audit_m0.py
./.venv/Scripts/python.exe tools/check_ledger.py
```

The default oracle stays the committed `evidence/M0/validation/oracle.json` so run manifests and the retained adjudication bind to the frozen original. A new validation directory can independently confirm the same evidence but is not silently substituted as a new oracle. Use a new directory for a second replay; commands refuse to overwrite run/report outputs. Pytest owns its named test-only basetemp; keep it inside the workspace.

Regeneration is `./.venv/Scripts/python.exe tools/m0.py generate --out work/new-bundle`. CAD/PDF timestamps may vary; semantic equivalence is the target. New bytes require fresh visual inspection and a new hash-bound attestation before validation can score them. Do not copy old attestations or expected answers to make regenerated files pass. To repeat the independent review, give a fresh context only `review-handoff/PROMPT.txt`, schema and neutral public files; the raw review shown here is one actual retained observation, not a fabricated reproducible model call.

## Failures and risks that remain

- Initial exports had insufficiently explicit view-stage context. All three first-attempt presentations are retained/excluded as an authoring group (`attempt-01/`); final note and public authority remove the ambiguity. Final 0/3 invalidity does not hide the initial 3/3 quarantine.
- One smoke convenience-API mismatch was repaired. Validator development corrected centered-Z, hidden-note placement and console-encoding assumptions using final artifacts. The independent reviewer corrected its initial Z probe from actual bounds and retained both outputs. One scorer test command lacked its basetemp parent; failed output is retained. See `failures.json` and `validator-design.md`.
- Browser security policy blocked `file:` report preview. No server, alternate browser surface or bypass was attempted. Saved HTML is audited for actual local evidence links, no remote dependencies, and escaped content; **browser rendering is unverified**. The report is inspectable as an offline artifact and has source-linked JSON. M4 should include an authorized rendering check.
- Generator, validator and reviewer readers share OCCT; closed-form topology/volume checks help but do not eliminate common-mode kernel errors. Raster ink and manual vision establish these layouts, not arbitrary drawing validity. M0 numeric-token matching does not independently prove a reviewer's reasoning; original external witnesses were manually inspected. Full scorer/rule/adapter hardening remains T04 onward.
- Windows is exercised; Linux, arbitrary inputs, bounded parser subprocesses, another drawing family, an engineer-authored packet and industrial transfer remain unverified. Only O01/H1 is implemented. No advisory thresholds or physical reaming feasibility are assessed. Always-abstain cannot detect the determined defect; no underdetermined corpus is claimed.
- No Beads/Gas Town installation, paid model API, remote creation, push, PR, deployment, publication, outside message or manufacturing order occurred.

Assessment: the finite first case supports further contract/profile work because independent artifact validation, public-only review and localized comparison succeeded. The source-category mismatch is useful evidence that manual adapter normalization needs a stable contract in M1/M3. Next dependency-ready task is T04; this run stops at M0 as requested. Task acceptance and local completion commits are in tasks.json; checkpoint/handoff is in `checkpoint.json`.
