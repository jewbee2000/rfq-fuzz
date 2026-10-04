# T07 — controlled public presentations and private authoring policy

Requirements: R05, R06, R07. Dependencies: T04 frozen contracts, T05 sourced
synthetic profiles, T06 exported CAD/vector drawing generator. Environment:
Windows 11/Python 3.12.2 root `.venv`; build123d 0.10.0, ReportLab 5.0.1 and
Poppler 26.07.0. M0 files remain unchanged. Independent T08 validation is required
before these authored presentations are scorable; generator intent is not truth.

## Finite operators and controls

`src/rfqfuzz/v1/mutations.py` implements `objective_group(operator,index,seed)`,
`specifications(seed)` and `generate_suite(dest,seed,specs=None)`. Fresh output
directories are required. `verify_spec` rejects missing H1/pocket prerequisites,
unsupported topology/profile/layout and non-four-member count source patterns
before export. Mutation contracts retain prerequisites, allowed deltas,
invariants, ancestry, partition, seed and source authoring values privately.

| Operator | Defect / repaired / legitimate alternative |
|---|---|
| O01 | H1 diameter +0.8 mm at the same stage / actual diameter / explicitly later-stage ream target, or visible REF plus public CAD dimension authority. Geometry stays unchanged. |
| O02 | Three declared members vs four scoped bores / four / two publicly scoped H1 members while two otherwise identical bores are visibly labeled OTHER. Geometry stays unchanged. |
| O03 | Global inch declaration with unconverted governed values / millimetres / correctly converted inch values/tolerances at four decimal places. Multiple dependent symptoms are one unit root cause. |
| O04 | Global 7075-T6 drawing vs 6061-T6 contract, equal authority / agreement / AL6061-T6 alias or explicit contract precedence. No proprietary alloy compatibility table. |
| O05 | Remove sole required drawing surface-roughness note while RQ1 stays public / restore note / public geometry-only release without RQ1, or explicitly permitted visible SURFACE FINISH = Ra 3.20 um alternate wording. |
| O06 | Visible revision B outside permitted model A/drawing A association / A/A / public approved A/B association, with actual STEP model identity still A. Revision inconsistency does not prove geometric incompatibility. |

Every objective group has unchanged exported geometry and separate named
ordinary obligations so collateral defects can be independently quarantined.
Descriptions of allowed changes are policies, not an oracle accepting any
artifact the generator happens to produce.

Conditional CNC presentations use only explicit named synthetic profiles:

- A01: 0.6 mm metal wall or 1.2 mm ABS wall under standard vs relaxed policy;
  0.79 vs exact 0.8 mm boundary under standard policy. These are advisories.
- A02: 26/6 vs exact 24/6 depth/diameter boundary; 30/6 under standard vs relaxed
  material policy. H1 depth is top-to-blind-floor, including counterbore entry.
- A03: width 125, width 120+stock 2, or width 118+stock 2+fixture 1 under standard
  vs relaxed XYZ setup capacities. Allowances add once per axis and the exclusion
  is scoped to the named setup.
- A04: anodize/paint with unspecified tolerance stage and no relaxed default,
  paired with an explicit stage or public standard before-finish default. A
  missing stage is uncertainty, never a clear result by silence.

Twelve additional uncertainty controls comprise three each of missing H1
diameter under drawing authority, differing stages without a defined transition,
unknown material applicability, and absent finish stage with no public default.
Unknown material is outside profile support; none of these is implicitly clear.

Supplemental sparse clean control `pk-61e732a788ae` uses explicit STEP dimension
authority and omits all model dimensions from its drawing. Its required visible
SURFACE ROUGHNESS note remains. It exposes the governing authority and RQ1 to the
reviewer and belongs to the same development layout lineage.

## Actual retained counts and reproducibility

The initial planned 144 presentations were actually generated and reopened:
108 objective presentations (36 defective/repaired/valid triplets), 24 advisory
paired presentations and 12 additional uncertainty controls. A supplemental
sparse control brings the final suite to **145**: plate 62, bore block 46, pocket
block 37. Final variant counts: defective 45, repaired 39, valid alternative 37,
underdetermined 15, profile alternative 7, exact-boundary 2. These are authoring
labels, not independently verified expected conclusions.

All 145 share the bounded-vector-a4-v1 layout and are **development only**.
Assigning this same layout to a purported holdout would give false independence.
Twins and all family/layout ancestors stay together. No core holdout accuracy,
independent layout transfer or industrial generality is claimed. T11 may add a
separately authored transfer lineage; it must not relabel this core template.

Final actual files are `evidence/M2/core-suite/public/<opaque-case-id>` with only
`packet.json`, `part.step`, `drawing.pdf`, `drawing.png`. Private mutation/suite
manifests and `authoring-export-check.json` record actual hashes, reimported
volumes/envelopes/one-solid validity and actual PDF text. All 145 exported STEP
models reopen as one valid solid; all PDFs are one page and hashes agree. The
final private configuration SHA-256 is
`95a8a730ead48e8098c0e8821d5c05288048d5bdf58ea28a1f30bcb8b501d5dc`.

Reproduce from the worktree/repository with root Python and `PYTHONPATH=src`:

```text
python -m pytest tests/mutations -q --import-mode=importlib
python tests/mutations/retain_suite.py <fresh-destination>
```

Actual focused acceptance: **14 passed**, four inherited build123d import
deprecation warnings, no suppressed warnings. `T07-tests-final.txt` retains the
exact output; `T07-tests.txt` is the earlier 13-test acceptance before adding the
sparse case. Tests verify final emitted defect/repair/valid visible text for all
six operators, explicit refusals, aliases/precedence/revisions/alternate note,
public leakage scan, replay/configuration and honest partition policy.

`T07-full-suite.txt` retains the actual first 144-case export/reopen command.
The new sparse case was then exported/reopened with the one-time
`tests/mutations/append_sparse_control.py` evidence extension, retaining all
original 144-case private manifests as `initial-144-*.json`. Existing public bytes
were hash-checked unchanged. `T07-sparse-extension-final.txt` records the final
145-case result. The first extension attempted exact full policy equality and
refused because the O05 policy was deliberately widened for a valid sparse
control; `T07-sparse-extension.txt` retains that refusal. The repaired guard
requires all original authoring values/IDs/ancestry/seed unchanged, checks the
actual original hashes, and preserves the prior policy manifests. No failed
export was treated as accepted.

The generation worker visually reopened final representative actual PNGs:
`pk-c6060a86b3df`, `pk-d0f406e22f58`, `pk-3f31a2dd3b69`,
`pk-34a1f03c9a26`, `pk-1c883f887ddb`, `pk-55e3e96a424c` and
`pk-61e732a788ae`. The changed values, alternate roughness wording and sparse
retained requirement are readable. This authoring inspection is distinct from
the independent hash-bound visibility/oracle acceptance in T08.

No acceptance command currently fails. Local task commit is reported to the
coordinator after commit, which owns the ledger. Assessment: the emitted finite
operators and controls justify T08 final-artifact validation. Final isolated
expected conclusions, fixture quarantine and M2 go/no-go remain T08 work; these
145 generated examples alone prove neither manufacturing correctness nor useful
reviewer accuracy. Next ready task: T08, then adapters/scoring after valid oracle.
