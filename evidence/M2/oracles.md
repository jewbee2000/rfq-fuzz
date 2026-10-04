# T08 independent final-artifact oracle

Date: 2026-10-04 (America/Los_Angeles). Requirements: R03, R04, R05, R06,
R08, R09, R19; conclusion semantics from R10. Dependency T06 was integrated
at worker commit `94a2ac0` (coordinator `1fd4803`); T07 at `9835a1f`
(coordinator `c255905`). M0 modules, artifacts and attestation were unchanged.

`src/rfqfuzz/v1/validation.py` imports no generator, reference reviewer or
profile evaluator. Direct OCP STEP re-import measures one solid, envelope,
orthogonal planes and complete cylindrical faces. Independent measured-face
closed-form volume checks cover through-hole plates, stepped blind bores and
top-open rectangular pockets. Public centers map actual H1/P1 features;
counterbore depth and H1 total top-origin depth are kept distinct. Tolerances
are 1e-6 mm and 1e-4 mm3. Rounding to six decimal mm suppresses only documented
kernel noise at synthetic profile boundaries. OCCT remains a shared dependency
and a disclosed common-mode limitation, not a second geometry kernel.

The drawing reader extracts actual complete lines and positions with pypdf,
independently renders the PDF using PDFium, and checks every non-whitespace
character's tight PDFium box for visible raster ink. It also compares that
render with the shipped Poppler PNG, allowing anti-aliasing differences up to
the recorded 0.015 unmatched-ink ratio. Hidden searchable digits, clipped glyphs
and PNG disagreement are rejected. Per-line crops, full rerenders, parser logs
and failure reasons are retained. Ink is a visibility signal, not infallible OCR;
hash-bound independent visual review remains a prerequisite for scoring.

`inspect_case(folder, outdir)` returns an unverified OracleRecord with empty
scorable expectations, or an explicit invalid/unsupported/timeout state. Native
STEP/PDF readers run in a bounded child process, terminated on timeout. File
hashes/signatures, allowed paths, bytes, page count, text/glyph count, pixels and
solids are checked. `validate_suite(suite_root, out, attestation=None)` retains
every case, checks observed objective twins' geometry, actual nonallowed drawing
lines and public context, and quarantines collateral or absent intended defects.
Private operator/ancestry/variant fields select allowable deltas; private source
parameter numbers never establish measurements or expected answers.

O01–O06 and A01–A04 conclusions are independently derived from final artifacts
and public authority, release, stage and profile premises. Each expected duty
uses a public obligation/category/feature, exact visible line witnesses, measured
STEP witnesses and canonical JSON of public context. O03 is one unit root cause;
its dependent diameter obligation is suppressed and recorded, rather than
counted as another issue or falsely claimed clean. Supporting blind-depth,
counterbore, pocket, wall and bore-type labels are also independently checked for
collateral errors. REF/STEP authority, explicit later reaming, scoped groups,
reviewed material aliases/precedence, absent finite requirements and independently
approved document revisions have clean controls. Missing stage/material premises
remain missing information; advisory values remain scoped to the public profile.
An independent coordinator challenge also established that equal-authority O04
material contradictions leave material-conditioned CNC rules unresolved. Those
rules now abstain rather than silently privileging the contract material. Explicit
contract precedence resolves the choice; drawing precedence selects one resolved
visible material and uses the selected public rule's material/class applicability.
The three precedence outcomes have separate actual-artifact tests.

## Acceptance actually run

`../../.venv/Scripts/python.exe -m pytest tests/artifact_validation -q --basetemp evidence/M2/validator-release-tests`

Result on the frozen final implementation: **49 passed**, four inherited build123d
deprecation warnings, 68.42s. Log: `evidence/M2/T08-tests-release.txt`.
Tests use actual exported artifacts,
cover all families/operators/conditional controls, retain stale-hash and corrupt
STEP/unit inputs, hide one numeric glyph while preserving PDF search text, clip
a real page, white out a PNG, terminate a parser, alter topology with a separately
authored extra bore, quarantine apparently clean collateral public-context edits,
reject a declared defect that was accidentally clear and test legitimate scoped
public-context differences. Synthetic test attestations are explicitly marked as
such and are not release visual evidence.

The final feature-correspondence strengthening was followed by:

`../../.venv/Scripts/python.exe -m pytest tests/artifact_validation -q -k 'independent_measured or explicit_stage' --basetemp evidence/M2/validator-final-correspondence`

Result: **6 passed**, 40 deselected, four inherited warnings, 7.48s. Log:
`evidence/M2/T08-final-correspondence.txt`. A final combined coordinator acceptance
run is still required after integration; unrun checks are not claimed here.

All six final T06 shipped PNGs were individually viewed in this chat; independent
PDFium full-page rerenders of the three families were also viewed. Every numeric
annotation was readable and unclipped, with explicit H1/C1 blind steps, P1 open
pocket/W1 correspondence, the 0.60 mm thin-wall example, the two-member H1/OTHER
scope control and the converted inch callouts. Their exact current hashes and
visually checked lines are in `representative-visual-attestation.json`.
`representative-validation/oracle.json`: **6 valid**. These are agent visual
inspections, not separately obtained human engineering reviews.

The first whole-core diagnostic observed **145 unverified, zero quarantined**
fixtures. Direct-reader geometry, glyph/raster and isolation checks passed.
`core-validation-unverified/` retains all native records/crops/logs;
`core-observation-summary.json` records conclusions and exclusions. The oracle
is 7,442,717 bytes, so whole-suite consumers need a bounded 32 MB oracle reader;
ordinary packet JSON remains bounded to 4 MB. Because supporting geometry checks
were strengthened during this diagnostic, it is explicitly not a frozen-code
release validation. It also predates the independent material-authority challenge
above: its O04 CNC clear conclusions are superseded by explicit uncertainty in
the final implementation. No old attestation was transplanted. The coordinator must
visually audit all actual core annotation sheets plus representative complete
views, then revalidate the frozen implementation with current hash-bound review.

## Current handoff and milestone assessment

Environment: repository-root isolated Python 3.12.2 environment and pinned M0 CAD,
PDF and raster stack. Current task T08: independent implementation and negative
acceptance implemented; final combined frozen-code core validation and visual
attestation are next. No failing acceptance command. Evidence paths are listed
above. Unresolved assumption: the finite ASCII annotation layout and same-kernel
geometry boundary remain deliberate v1 limits; arbitrary drawings, PMI and general
manufacturability are unsupported. Next dependency-ready work after the validated
core is T09/T10 integration and T11 challenge/partition audit. Continued work is
worthwhile for this finite reviewer-regression contract: independent actual-artifact
checks found no ambiguity in the representatives and catch meaningful corruptions.
It does not establish manufactured-part accuracy or general industrial competence.

Local implementation commit is supplied with this handoff and recorded by the
coordinator in the task ledger after integration. No push, PR, hosted transmission
or publication was performed.
