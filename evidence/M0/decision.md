# T00: bounded recheck and first consumer question

Date: 2026-10-04 (user's America/Los_Angeles date). Requirement: R21.

Decision: **conditional GO for the first feasibility challenge only**. The original general drawing/DFM reviewer remains a no-go. No equivalent publicly runnable combined workflow was identified in this bounded source recheck; this is neither an exhaustive novelty search nor evidence of market demand.

| Primary source inspected | Source revision | Observed scope |
|---|---|---|
| [Draftwright](https://github.com/pzfreo/draftwright) | `8b844121aaf7b9f68e9c7a643cf7bba3deff4d72` | Technical drawing generation and lint/repair. Reuse candidate, not an independent oracle or vendor-neutral reviewer regression suite. |
| [MakerBench-HWE](https://github.com/tonykoop/makerbench-hwe), [CNC grader](https://github.com/tonykoop/makerbench-hwe/blob/2b3ea9be56033f944edc99a377e0a37139f3c9ad/makerbench/tvo_cnc_track.py) | `2b3ea9be56033f944edc99a377e0a37139f3c9ad` | Hardware generation tasks and manifest/disclosure grading, rather than independently measured drawing/STEP reviewer decisions. |
| [MechVQA](https://github.com/xiaofengShi/MechVQA) | `c8d61513aef05b4f5d117bb0c6d1a055451d6f33` | Drawing VQA generation and QC. No combined executable STEP/context mutation-review-regression loop found in inspected documentation. |
| [CADGenBench](https://github.com/huggingface/cadgenbench) | `33304cf771fc5639144b1df9611e347251052cf8` | Evaluation of generated/edited CAD shapes, a different target from supplied RFQ review decisions. |
| [Palmetto](https://github.com/connorkapoor/Palmetto) | `7141d6fbe02ad7b3720aa92da9ef00d576477007` | STEP geometry feature/DFM review. Useful adjacent work; drawing/stage review regression not established. |

Source inspection was read-only; no product was trialed, repository executed, or vendor contacted. A separate research worker challenged the differentiation. The researched distinction remains the combination of controlled artifact mutations, independent final-artifact measurements, public engineering premises, valid alternatives, and localized reviewer-version comparison. Do not claim invention of seeded defects, paired CAD/drawings, or DFM review.

The recheck also found [FreeCAD Automation](https://github.com/dooosp/freecad-automation/tree/659405b3e36d01d21027f0c75db3f7e36ded159b) and [CAD Guardian evaluation kit](https://github.com/tsmithcode/cadguardian-inventor-automation-proof/tree/77f6e35d3633b9d8e41ff18e08fdb6c6221c9741). Their inspected contracts provide CAD/drawing/readiness artifacts, clean/blocker fixtures or revision comparisons, but did not establish the independent reviewer-version regression loop proposed here. These increase the overlap boundary; neither was executed.

## Frozen consumer question and acceptance boundary

Can a reviewer detect a four-bore drawing/STEP diameter disagreement for the same manufacturing stage, then correctly clear a corrected twin and a legitimate later-stage diameter requirement? Can a report explain a deliberately injected missed contradiction and false alert by linking to the visible bore callout, exported cylinder measurements, and stage contract?

One synthetic plate: 80 x 50 x 8 mm, four through-bores, nominal STEP diameter 6.00 mm, centers (+/-25, +/-15) in the XY plane. Same-stage drawing values: 6.80 +/-0.05 (defect), 6.00 +/-0.05 (repair). Valid alternative: explicit later reaming to 6.80 +/-0.05 after the supplied intermediate 6.00 mm model; no physical manufacturing claim or inferred compensation. This is a package consistency obligation, not certification of the process.

T01 will first test pinned Draftwright on native Windows Python 3.12. If reuse cannot produce an unambiguous controlled drawing, retain the failure before selecting a bounded single-template fallback. No general drawing engine, additional family, Beads, Gas Town, UI, hosted API, or publication is authorized by this milestone.

Acceptance performed: repository plan/requirement/task inspection and read-only primary-source recheck. Evidence: this document, source revisions above. Next dependency-ready task: T01. Completion commit is recorded in `tasks.json` after the local research commit.
