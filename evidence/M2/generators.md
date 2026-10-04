# T06 — bounded CAD and exported drawings

Requirements: R03, R04. Dependencies: frozen T04 interfaces and T05 public profile.
M0 source/artifacts are unchanged. This authoring implementation describes intent;
T08 separately reads final exported bytes before any fixture becomes scorable.

## Supported geometry and refusal boundary

All dimensions are millimetres. Every family is one valid solid centered about
the origin, with planar faces and Z-aligned cylindrical bores only. Width is X,
length Y, height Z; top is +Z. Parameters omitted by a caller take the defaults
in `src/rfqfuzz/v1/generation.py`. Unknown keys and nonfinite values are refused.

| Family | Bounds and defaults |
|---|---|
| All envelopes | X 20–240, Y 20–160, Z 3–80. |
| Plate | Default 80 x 50 x 8, diameter 6, count 4. Diameter 2–16 and strictly below one third of the smaller plan dimension; count exactly 1, 2 or 4. One hole is centered; other members occupy (+/-0.3125 X, +/-0.3 Y). Holes go through. |
| Blind/counterbore block | Default 60 x 40 x 35, H1 diameter 6/depth 24; C1 diameter 12/depth 4. H1 diameter 2–16; C1 at least H1+1 and at most the smaller plan dimension minus 4; C1 depth >=1 and <H1 depth; H1 depth <=height-1. One coaxial central group. |
| Open pocket block | Default 60 x 40 x 20; pocket 50 x 30 x 12; +X wall W1=5. Pocket plan dimensions >=8 and <=outer dimension-0.4; W1>=0.2 and leaves opposite wall>=0.2; depth >=1 and <=height-1. Pocket centered on Y and positioned on X from W1. |

Interacting bores, fillets, threads, enclosed cavities, freeform surfaces,
additional solids, arbitrary orientations and additions outside these keys fail
explicitly. These are topology bounds, not claims of manufacturing feasibility.
Some supported dimensions are outside a selected setup or trigger an advisory.

## Drawing implementation and public contract

build123d 0.10.0/OCCT 7.8.1 produces ordinary STEP. ReportLab 5.0.1 produces a
one-page A4 landscape vector PDF with explicitly authored schematic plan and
X-Z section A-A. Poppler `pdftoppm` 26.07.0 renders that PDF at 200 dpi into the
shipped 2339 x 1653 PNG. The packet records the renderer/version and dpi, units,
SHA-256 of all actual artifact bytes, public feature/view correspondences and
public STEP product identity. Dependency notices are already retained in
`docs/licenses/` and the project remains AGPL-3.0-only.

The finite fixed template was selected rather than adding automatic dimension
placement for these bounded families. It declares schematic views, numeric
annotation authority, model/drawing stages and top-origin depths on the actual
page. The blind-bore section shows both depth steps and blind floor. The pocket
section shows open entry, floor and W1 side wall. The plate section explains when
the off-axis pattern does not intersect Y=0. Numeric dimensions never come from
image scale. This choice narrows layout coverage; it is not an arbitrary-drawing
engine or a replacement for the preserved Draftwright M0 rendering.

Canonical visible line vocabulary for the independent reader:

- DRAWING ID / DRAWING REV, UNITS, MATERIAL, MODEL STAGE / DRAWING STAGE,
  FINISH / TOLERANCE STAGE, ENVELOPE and SURFACE ROUGHNESS.
- H1 DIAMETER with explicit +/- tolerance, H1 COUNT, H1 TYPE and blind H1 DEPTH.
- C1 DIAMETER / C1 DEPTH; P1 WIDTH / P1 LENGTH / P1 DEPTH; W1 THICKNESS.
- REF has explicit visible suffix. Approved intermediate-to-finished transitions
  are public in `manufacturing.transition` and visibly noted.

Scoped H1 controls label excluded equal-diameter bores OTHER in the actual plan
and expose only H1 member centers in the packet. The declared critical release
requirement RQ1 is the visible SURFACE ROUGHNESS = 3.20 um note; dropping it does
not remove a dimension needed by other obligations. CAD-authoritative sparse
drawings can deliberately omit dimensional callouts while exposing the geometry
authority and the finite requirements. Override text has finite line count,
width and ASCII limits; clipping is refused before PDF export.

## Acceptance evidence

Initial actual STEP round-trip acceptance on Windows/Python 3.12.2:

`C:/Users/Walt/Documents/Codex/2026-10-03/g/outputs/projects/rfq-fuzz/.venv/Scripts/python.exe -m pytest tests/geometry -q`

Result: **18 passed**, four inherited build123d import deprecation warnings, no
suppressed warnings. Nine independent closed-form envelope/volume examples
include all three defaults and lower/upper supported bounds. Re-imported STEP
has one valid solid, only PLANE/CYLINDER faces, and agrees within 1e-6 mm/mm3.
Nine refusal examples cover topology, invalid geometry and nonfinite values.

Final combined command added `tests/generation` and `--import-mode=importlib`:
**24 passed**, same four warnings. Retained logs: `T06-tests.txt` and
`T06-tests-final.txt`. Artifact checks actually reimport STEP, parse one vector
PDF page, inspect required canonical lines and read the shipped PNG dimensions
and ink. They cover equivalent inch conversion, REF, sparse CAD authority,
scoped H1 exclusion, unsupported edits and bounded annotation overflow refusal.

Representative final triplets are `generator-artifacts-v2/pk-000000000001` through
`pk-000000000006`: default plate/bore/pocket, 0.6 mm W1, H1 scoped subset and
correct inch conversion. `exported-measurements.json` retains actual reimported
volumes/envelopes/faces, PDF text and actual file hashes. Reproduce into a fresh
directory using `PYTHONPATH=src` and
`python tests/generation/retain_examples.py <fresh-destination>`; retained command
output is `T06-artifacts-v2.txt`.

The generation worker visually inspected all six first renders. The pocket plan
W1 label was too close to section marker A, so the entire first six-presentation
batch is retained at `generator-artifacts/` as an authoring attempt, not scoring
evidence. W1 was moved up 25 PDF points. The default bore and both pocket final
renders were then visually reopened; the unchanged plate/subset/inch content
remains readable. Final section steps, floor and W1 are distinct; all numeric
labels are visible at 200 dpi. This is an authoring inspection and does not grant
independent oracle validity. T08 owns final visible-content/isolation validation.

Environment: Windows 11, Python 3.12.2 in the coordinator's root `.venv`;
profile dependency commit 53eae8c (locally cherry-picked as e58196e). No failing
acceptance command remains. An early shell probe without PYTHONPATH failed to
import the source package, was corrected by setting PYTHONPATH=src, and supplied
no accepted evidence. The early drawing probe used a schema test profile and is
not scored. Local task commit is reported to the coordinator after this file is
committed; the coordinator owns the completion ledger.

Assessment: the three bounded exports and visible sections support proceeding
to T07/T08. Independent oracle validity, arbitrary CAD/drawing interpretation,
Linux execution and manufacturing competence remain unestablished. Next ready
tasks: T07 controlled variants and T08 independent final-artifact validation.
