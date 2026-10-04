# T05 — sourced conditional synthetic profiles

Date: 2026-10-04. Requirements: **R06** (conditional A01–A04 policies) and
**R09** (versioned provenance). This task implements the policy layer only;
T07/T08 must establish its controlled fixtures and independent final-artifact
witnesses. A profile result is not certification of an actual manufactured part.

## Implemented boundary

`src/rfqfuzz/v1/profiles.py` provides `profile(name="standard")`,
`default_profile()` and
`evaluate(profile, rule_id, measurements, manufacturing, setup)`.
Both built-ins validate under the frozen `CapabilityProfile` contract and are
fresh JSON-serializable public records. Profile and rule versions are **1.0.0**;
all cards state `synthetic_value: true`. The result contains only `conclusion`,
`reason` and `rule_id`; reasons identify the selected profile/rule versions.

The evaluator consumes measurements provided by a separate reader. It reads no
generator objects, private expectations, packet text, files or network services.
It is not itself independent artifact verification.

| Rule | Standard synthetic value | Relaxed synthetic value | Decision boundary |
| --- | --- | --- | --- |
| A01 wall | metal 0.8 mm; plastic 1.5 mm | metal 0.5 mm; plastic 1.0 mm | Strictly less yields `advisory`; equality is clear for A01 only. |
| A02 cylindrical bore depth/diameter | metal/plastic 4 | metal 8; plastic 6 | Strictly greater yields `advisory`; equality is clear for A02 only. No universal maximum. |
| A03 named XYZ setup | `synthetic-standard-XYZ`: 120 × 80 × 50 mm | `synthetic-relaxed-XYZ`: 240 × 160 × 100 mm | Any occupied axis strictly greater yields `profile_exclusion`; equality is included. |
| A04 tolerance-stage context | Project-owned `before_finish` default | No default | Explicit `before_finish`/`after_finish` overrides default; unresolved stage yields `missing_information`. |

A03 occupied extent is part envelope + stock allowance + fixture allowance in
each declared XYZ axis. Each allowance is the **total added occupied extent**,
not a per-side value; it is added once. Missing allowances never mean zero.
Axis permutation is unsupported. Exclusion names this synthetic setup only.

Material applicability is a finite project policy vocabulary, including 6061-T6,
304, 316, steel 1018, ABS, acetal/POM and Nylon 6/6, with a declared material
class. Unknown material/profile combinations yield `missing_information`, even
when measured dimensions would otherwise be clear. A known material paired with
a conflicting class yields `unsupported`. This vocabulary is not a cutting-data
database or material/finish compatibility chart.

Absent required measurements yield `missing_information`. Supplied nonpositive,
nonfinite or wrong-type geometry, negative allowances, unsupported orientations,
unsupported card units/comparators/severity and invalid explicit stages yield
`unsupported`. Neither state becomes clear. Invalid profile records fail the
frozen contract. A04 does not calculate coating compensation, infer finish
compatibility or reconcile different geometry stages.

## Provenance retained

Primary-source retrieval: **2026-10-04**, read-only website research. The short
paraphrases below retain the meaning required for policy design without copying
source pages or proprietary tables. All executable values are **RFQFuzz project
selections**, including numbers near vendor recommendations. Neither built-in is
a representation of an actual vendor's complete service capabilities.

| Source | Retrieved observation | Use and limitation |
| --- | --- | --- |
| [Xometry: CNC design tips](https://www.xometry.com/resources/machining/10-tips-improve-cad-cnc-design/) | The wall section discusses reduced stiffness and machining vibration, and gives different metal/plastic recommendations. | A01 conditional advisory rationale. The project selects its boundary and equality semantics. |
| [Protolabs: CNC milling design guidelines](https://www.protolabs.com/services/cnc-machining/cnc-milling/design-guidelines/) | Thin-feature guidance and published extents depend on the service/material/setup. | A01 alternate-policy motivation and A03 setup-specific scope. The project invents both named capacities and allowance arithmetic; vendor capacities are not imported. |
| [Protolabs Network: CNC design guide](https://www.hubs.com/knowledge-base/how-design-parts-cnc-machining/) | Hole guidance distinguishes recommended, typical and special-tooling depths. Flat-bottom milling and drilling have different context. | A02 advisory motivation. RFQFuzz measures the declared cylindrical bore depth; no process feasibility or largest-depth universal limit is inferred. |
| [Xometry: Manufacturing Standards](https://www.xometry.com/manufacturing-standards/) | The retrieved CNC section defines service defaults but does not establish a finish/tolerance-stage default. Explicit before-secondary-finishing statements occur in additive sections. | A04 explicit/default precedence motivation only. The standard built-in `before_finish` stage is project-selected, not a quoted or inferred Xometry CNC default. |

The architecture's supplementary
[Xometry post-processing link](https://xometry.pro/en-eu/articles/impact-post-processing-dimensional-accuracy/)
returned an internal retrieval error and its exact-title primary-domain search
returned no result. It was not used to assert a stage or compensation rule.
The current standards inspection therefore qualifies the earlier architecture
description rather than borrowing a default from another process.

## Acceptance evidence

Worker checkout: `.workers/profiles`; frozen starting commit
`159824975d08714a821417c64d6b26db454dbcf5`. Host: Windows x64, Python **3.12.2**,
root `.venv/Scripts/python.exe`; this policy layer adds no dependency.

Exact final acceptance command, run in the worker checkout:

```powershell
& 'C:/Users/Walt/Documents/Codex/2026-10-03/g/outputs/projects/rfq-fuzz/.venv/Scripts/python.exe' -m pytest tests/contracts tests/profiles -q
```

Full retained output, exit code **0**:

```text
........................................................................ [ 75%]
........................                                                 [100%]
96 passed in 0.10s
```

The tests include hand-calculated counterfactuals: a 0.6 mm metal wall is advisory
under standard and clear under relaxed; a 6D bore likewise changes conclusion;
each setup axis is tested immediately below/on/above its capacity. A 100 × 60 ×
30 mm part with 10 mm total stock and 10 mm total fixture allowances occupies
exactly the standard boundary; increasing either X allowance produces exclusion.
Explicit after-finish stage overrides standard's before-finish default, while
relaxed with an absent stage remains unknown. Unknown materials, missing
measurements, missing finish context and malformed/overflow values cannot produce
a false clear. Contract tests remain unchanged and pass in the same invocation.

The independent coordinator inspected the policy implementation before commit,
agreed with the provenance qualification and strict boundaries/precedence, and
reported no blocking issue. This is organizational code review, not independent
manufacturing evidence. Integration and combined-checkout reruns are the
coordinator's next checks. Boundary measurements from OCCT remain the separate
validator's responsibility; this evaluator introduces no implicit epsilon.

Additional executed smoke command (exit **0**) verifies keyword API compatibility
and canonical profile hashes:

```powershell
& 'C:/Users/Walt/Documents/Codex/2026-10-03/g/outputs/projects/rfq-fuzz/.venv/Scripts/python.exe' -c "import sys; sys.path.insert(0,'src'); from rfqfuzz.v1.profiles import profile,evaluate; from rfqfuzz.v1.contracts import digest; print(sys.version); print(sys.executable); print('standard_profile_sha256',digest(profile())); print('relaxed_profile_sha256',digest(profile('relaxed'))); print(evaluate(profile=profile(), rule_id='A01', measurements={'wall_mm':0.6}, manufacturing={'material':'6061-T6','material_class':'metal','finish':'none','tolerance_stage':None}, setup={'orientation':'XYZ','stock_allowance_mm':[0,0,0],'fixture_allowance_mm':[0,0,0]}))"
```

```text
3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
C:\Users\Walt\Documents\Codex\2026-10-03\g\outputs\projects\rfq-fuzz\.venv\Scripts\python.exe
standard_profile_sha256 656b690680dac79513e53970a58ff7013d54039796922dbb1319dc3a9460cab0
relaxed_profile_sha256 7a7ea735480584bea176b2aaf67f1e8e50a73abcf77e8382d7d506270094b4de
{'conclusion': 'advisory', 'reason': 'synthetic-standard@1.0.0 / A01@1.0.0: wall thickness 0.6 is below the project-selected metal advisory threshold 0.8; no general feasibility conclusion', 'rule_id': 'A01'}
```

An earlier direct smoke command without `src` on the import path failed with
`ModuleNotFoundError: No module named 'rfqfuzz'`. The corrected command above
retains the explicit source path; no consumer installation claim is made here.
`git diff --check` was also run successfully. No acceptance test failed.

## Handoff and next milestone assessment

Completion is a local commit with this evidence and the policy/tests; its SHA is
reported to the coordinator for the authoritative T05 ledger. Only the
coordinator updates task status. No shared schema, M0 artifact or task ledger was
edited by this worker. No active failing command remains. Unresolved assumption:
these synthetic thresholds can test reviewer policy reasoning but establish no
industrial transfer or demand.

Next dependency-ready work is T07/T08 once T06 is integrated. M2 remains
worthwhile: conditional conclusions and uncertainty now have reproducible
boundaries and public provenance. Continued value depends on independently
measuring and visibly verifying actual exported cases, and quarantining any
ambiguous or collateral defect before scoring.
