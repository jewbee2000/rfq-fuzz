# Research and build decision

Research date: 4 October 2026. Sources are primary vendor documentation, repository documentation/source, standards-body material and research papers. Product capabilities below are advertised unless source inspection is explicitly identified. No commercial product was trialed and no performance claim was independently reproduced.

## Decision

**Do not build the proposed general upload-and-review product.** Existing tools already advertise PDF drawing checking, missing callouts, dimensional/GD&T checks and CNC DFM. Open-source geometry analysis also exists. A new upload form, LLM prompt or supplier-profile database is not a defensible gap by itself.

**Proceed conditionally with RFQFuzz:** a local, reusable fault-injection and regression kit for reviewers of CNC RFQ packages. It creates matched STEP/drawing/context packets, verifies controlled defects in the exported artifacts, includes repaired and legitimately different examples, and compares localized reviewer findings across versions. Package-consistency and manufacturing-advisory results remain separate.

Bounded conclusion: no publicly runnable kit with this combined workflow was found in the sources examined. This is not proof that no private system, unindexed project or future release implements it. The concrete audience and demand remain hypotheses to test at M0 and the consumer milestone.

## The original idea already exists

| Product/project | Evidence and overlap | Effect on the proposal |
|---|---|---|
| [CoLab AutoReview](https://www.colabsoftware.com/product/autoreview) | Advertises drawing completeness, dimension/tolerance checks, hole/thread callouts, material conflicts, 2D/3D discrepancies and CNC geometry checks. | Closely matches the original feature bundle. Do not recreate it as the portfolio claim. |
| [Axial](https://www.getaxial.com/) | Advertises drawing review and redlines for dimensions, GD&T and manufacturability. | PDF review alone is occupied. Accuracy claims are not validation for our project. |
| [ClearHandoff AI Review](https://www.clearhandoff.com/en/help/ai-review/) | Documents dimensional, tolerance, material, finish and process-aware review. | Custom rules and manufacturing context are not unique. |
| [HCL DFMPro](https://dfmpro.com/about-dfmpro/) | Describes CAD-integrated DFM and customizable manufacturing rules. | Generic rules-based DFM is mature prior art. |
| [Oscillation Design](https://www.oscillation.design/) | Describes STEP analysis and shop capability/tool/material profiles. | A supplier-specific checker would also overlap. |
| [Palmetto](https://github.com/connorkapoor/Palmetto) | Public MIT repository; source includes a STEP/C++ geometry engine and CNC feature/DFM analysis. Inspected, not executed. | Open-source STEP DFM already exists; consider a partial reviewer adapter. |
| [DFM Studio](https://www.dfmanalysis.com/) | Advertises STEP/IGES CNC analysis and open-source availability. Its linked GitHub repository returned 404 during research. | Checker overlap is advertised; availability as reusable open source is unverified. |
| [DraftGuard](https://genaisys.ai/draftguard.html) | Advertises drawing extraction, deterministic/AI checks and cross-document analysis; reports internal seeded-defect tests. | Neither cross-document review nor seeded defects are new concepts. |

Commercial availability and source availability are separate questions. The user's original go/no-go condition concerns whether the tool exists, not merely whether a free implementation exists.

## Closest alternatives to the pivot

| Prior art | What is already solved or attempted | Remaining distinction to prove |
|---|---|---|
| [MechVQA](https://github.com/xiaofengShi/MechVQA) | Mechanical drawing QA, including anomaly and consistency questions, with a generation pipeline. | An executable paired-artifact mutation kit, valid counterexamples and reviewer regression, rather than another fixed drawing QA collection. |
| [CADGenBench](https://github.com/huggingface/cadgenbench) | CAD generation/editing evaluation with geometric comparisons. | Evaluate review decisions about supplied RFQ evidence, rather than whether an agent generated the correct shape. |
| [MakerBench-HWE](https://github.com/tonykoop/makerbench-hwe) | Parametric hardware tasks, deterministic grading and deliverable-packet checks. | Its CNC track reads declared manifest fields; its packet checker checks disclosure/completeness. It does not implement this paired drawing-defect/reviewer-response loop. |
| [MakerBench CNC source](https://github.com/tonykoop/makerbench-hwe/blob/main/makerbench/tvo_cnc_track.py) and [packet contract](https://github.com/tonykoop/makerbench-hwe/blob/main/docs/DELIVERABLE_PACKET.md) | Source inspected: orientation/tool/reachability/collision declarations and optional drawing/model deliverables. | RFQFuzz must inspect exported evidence independently, not simply grade self-declared metadata. |
| [Draftwright](https://github.com/pzfreo/draftwright) | STEP/build123d drawing generation, authored annotations, suppressed-requirement tracking and linting. | Reuse generation if feasible. Controlled artifact mutations, independent export validation and third-party reviewer scoring are the contribution. Its own lint cannot be the independent oracle. |
| [DraftGuard](https://genaisys.ai/draftguard.html) | Vendor reports internal seeded mechanical/electrical drawing benchmarks. | No publicly reusable generator or vendor-neutral review adapter was identified in the inspected material. Do not claim inventing fault injection. |
| [NIST PMI validation](https://www.nist.gov/ctl/smart-connected-systems-division/smart-connected-manufacturing-systems-group/mbe-pmi-validation) | CAD/PMI and derivative-format validation. | CNC RFQ review behavior under controlled documentation and capability changes. CAD conformance testing is established prior art. |
| [OmniMech paper](https://arxiv.org/abs/2608.05539) | Large paired CAD/STEP/drawing dataset and reasoning/generation tasks; release status was not verified. | Paired CAD and drawings are not novel. Runtime controllable mutations and reviewer regression must add value. |
| [BenDFM](https://arxiv.org/abs/2603.13102) | Synthetic feasible/infeasible sheet-metal bending examples. | Different process and evaluation target; useful precedent for conditional manufacturing labels. |
| [RedlineBench](https://redlinebench.benfeicht.com/) | Known-issue architectural drawing review benchmark. | Different engineering domain; precedent for seeded review errors, not a CNC oracle. |
| [2D–3D annotation-mapping research](https://arxiv.org/abs/2602.18296) | Combines deterministic association, language-model assistance and human resolution. | Do not claim arbitrary drawing-to-CAD correspondence is solved; author explicit associations in v1. |

The narrower novelty claim depends on the combination of **controlled mutations, independently checked final artifacts, sufficient public engineering context, valid alternatives, profile-sensitive expected behavior and reproducible review regression**. Removing those elements would leave an ordinary benchmark or drawing generator.

## Why an engineer might use it

This is a reasoned product hypothesis, not an interview finding. Teams adopting AI drawing review need a way to detect regressions when changing a prompt/model or rule. A warning count cannot distinguish better detection from indiscriminate flagging. A controlled challenge kit can give them small reproducible failures to debug and regression cases to retain. Open-source DFM maintainers can use the geometric subset without claiming PDF support.

The target user is an engineer responsible for evaluating or maintaining review automation. A hardware engineer who simply needs a single part reviewed should use an existing reviewer. The initial tool is not a substitute for that workflow.

The portfolio value comes from solving a test-engineering problem: defining observable requirements, generating controlled faults, proving the fault is present, excluding confounders, and measuring a system's response. It fits manufacturing/test engineering even though the product under test may be an AI system.

## Research limits and search coverage

Search themes included CNC DFM drawing review PDF/STEP, open-source CNC geometry checkers, drawing completeness/annotation tools, manufacturing review regression, seeded drawing defects, CAD mutation benchmarks, mechanical VQA, supplier capability rules and CAD/PMI validation. Repository source was inspected for MakerBench's CNC and packet checks; repository documentation was read for Palmetto, Draftwright, MechVQA and CADGenBench. Official CNC design guides and the requested Beads/Gas Town sources were read.

This is a market and technical feasibility review, not a patent search, exhaustive code audit or independent test of vendor accuracy. Source URLs are mutable. The implementation agent should capture pinned dependency commits, rule retrieval dates and concise factual summaries when creating fixtures; avoid redistributing copyrighted source pages or standards tables.

## Gates that can stop the project

1. **Equivalent public workflow:** if the kickoff recheck finds the proposed workflow already available, prefer a concrete contribution or discontinue this proposal. Do not rename an existing feature and call it new.
2. **Artifact/oracle integrity:** export and independently verify one challenge bundle. If the only ground truth is the generator's metadata, or unintended defects cannot be detected, do not scale the corpus.
3. **Practical review interface:** run the same ordinary public packet through two independent review paths, at least one a real external reviewer/agent that examines the drawing, STEP and process-stage context in the first diameter case. A STEP-only tool does not satisfy this gate. If only the project's reference checker can consume it, the tool has not proved usefulness.
4. **Actionable regression:** demonstrate a version-to-version change with source-localized evidence and a comprehensible cause. A score without a diagnosable case is insufficient. A clearly labeled deliberately perturbed reviewer can prove report behavior; preserve genuine external results separately and do not market the injected regression as a discovered external failure.
5. **False-positive resistance:** an always-flag reviewer and an always-clear reviewer must both perform poorly. Required context must be visible to reviewers; hidden intent is an invalid test.
6. **Transfer:** before claiming industry usefulness, test a separately authored drawing family and an engineer-authored packet. Without this, ship only with explicit synthetic-corpus limitations, or defer broader release claims.

Proceeding means funding a bounded proof first. It does not mean promising that every proposed feature or an industry-ready benchmark is already feasible.
