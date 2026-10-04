# Implementation plan

This is a plan for a useful, bounded engineering test tool. All milestone outputs below are future work. The primary unknown is whether controlled exported artifacts and independent oracles can remain trustworthy while the tool produces useful reviewer regressions.

## Feasibility assessment

| Capability | Assessment | Scope decision |
|---|---|---|
| Local CLI, schemas, task graph, replay, deterministic matching | High confidence; ordinary software engineering with important semantics | Must |
| Parametric simple solids and STEP export/re-import | High confidence for bounded families using mature kernels | Must; reject unsupported topology |
| Controlled PDF annotations and PNG rendering | Feasible with existing drafting tools; export fidelity needs a spike | Must only after M0 proof |
| Independent visible-content and cross-artifact oracle | Hardest core problem; partial automation plus curated verification | Must; stop if circular or ambiguous |
| Reviewer regression with honest coverage and false-alert metrics | Feasible with explicit output contracts and adjudication | Must |
| Fully autonomous arbitrary drawing interpretation | Insufficiently reliable and already competitively occupied | Excluded |
| Native SolidWorks import | Licensing, platform and file-format burden | Excluded; use exported STEP/PDF |
| Exact manufacturing approval across shops | Not inferable from geometry/drawing alone | Excluded |
| User-authored external packet cases | Feasible with manual feature associations and declared intent | Should, and a gate for broad usefulness claims |

## Milestones and evidence

Estimates are planning judgments for focused engineering effort, including verification and rework, not promises of agent wall-clock speed. Target roughly **100–180 engineering hours** for a credible first release; stop after a **12–20 hour M0 budget** if the key proof fails. This is substantially larger than a weekend upload demo. Agent parallelism can shorten independent work, not eliminate engineering judgment.

| Milestone | Work and dependencies | Exit evidence | Indicative effort |
|---|---|---|---|
| M0 — Prove the gap and first case | T00–T03. Recheck prior art; pin a compatible stack; define minimal public/private contract; export a plate with defect, repair and valid alternative; use an external reviewer. | Source/license decision; verified artifact triplet; independent measurement and rendered evidence; two review paths including external; actionable comparison; explicit go/no-go. | 12–20 h |
| M1 — Stabilize contracts and profiles | T04–T05 after M0. Freeze schemas, rule-card format, authority semantics, IDs and profile counterfactual behavior. | Versioned schemas; error/unknown cases; exact boundary examples; migration policy; oracle/finding fixtures. | 10–16 h |
| M2 — Build validated generators and mutations | T06–T08. Three geometry families; six objective operators; advisory/profile track; independent artifact validator and quarantine. Generator and validator can progress separately after contracts. | Every operator has defective/repaired/valid controls; STEP measurements and visible drawing evidence; all invalid cases retained; no unsupported assumptions hidden. | 25–45 h |
| M3 — Integrate reviewers and scoring | T09–T10. Public packet export; structured/manual and local-process adapters; coverage/status; deterministic matching, adjudication and paired comparison. | External reviewer consumes ordinary artifacts; expected always-clear/always-flag/always-abstain failures; evidence localization; no answer-key leakage. | 18–30 h |
| M4 — Challenge the harness | T11–T12. Corpus splits, semantic reproducibility, evaluator mutants, layout/units controls, timeouts/partial runs, limits and safe reports. | Independent review report; detected evaluator faults; clean-control errors exposed; all unsupported/error cases accounted for. | 15–28 h |
| M5 — Consumer and portfolio evidence | T13–T14. Clean install on Windows/Linux; independent consumer walkthrough; useful regression example; separately authored packet; docs and factual blog draft. | Install/run evidence, HTML report, raw results, limits, dependency/license inventory, final traceability matrix and unpublished article. | 20–40 h |

The total range is approximate; individual rows overlap in integration effort. Trim Should/Could items before weakening any oracle, coverage or honesty requirement.

## M0 must be concrete

Build one ordinary single-part packet using a plate with a scoped hole group. Export a nominal drawing, one intentionally wrong diameter and one legitimate alternative with clearly declared process-stage context. The reviewer must infer the conclusion from the public files/context, not from test-specific labels.

The independent validator must re-import STEP, measure the bore, extract and inspect the visible annotation, check the stage/authority contract and demonstrate that other controlled obligations did not change. A saved generator JSON containing the correct diameter does not satisfy this gate.

Use two review paths: a small hand-coded/reference path for protocol testing and a genuine independent reviewer. The latter must actually inspect the O01 drawing, STEP geometry and process-stage context. It can be an existing tool with those capabilities or an independent Codex reviewer session given only the public packet and a neutral output schema. Manual JSON import is sufficient; do not pretend the Codex desktop app has a callable API. Label same-machine blinding as procedural, not secure isolation. A STEP-only tool is useful later for its declared geometry track, but cannot satisfy this M0 cross-artifact gate.

Show how the report helps explain one reviewer-version change, including a false alert or a miss. A deliberately perturbed reviewer/prompt is allowed to establish report behavior; label it as injected, preserve unmodified external results, and do not claim it is a naturally discovered external failure. The purpose is to establish diagnosability, not to demonstrate a high reviewer score. If no external interface works without leaking the oracle or hidden premises, revise or stop.

## Corpus release plan

Initial target: 36 objective groups (six operators × six parameter/context variants), each with a defective/repaired/valid triplet; 12 advisory/profile groups with paired outcomes; and at least 12 genuinely underdetermined cases. That gives a planned minimum of 144 packet presentations before additional controls. These are suite design choices, not existing data or a claim of statistical power.

Do not force every operator onto every part family. Group variants by source geometry, layout and ancestry before splitting, so repaired twins and near-duplicate parts cannot leak across development and holdout partitions. Reserve an entire independently authored family/layout for transfer testing. Report actual denominators after fixture quarantine. Requiring an exact count must never encourage accepting invalid examples.

Include sparse CAD-authoritative drawings, equivalent units, legitimate material aliases, explicit defaults, independent document revisions and partial evidence. Keep defect type concealed in filenames and neutral review instructions. A public regression corpus is not secret forever; future leaderboard claims would need separately governed evaluation data, which is outside v1.

## Proposed package structure

```text
src/rfqfuzz/
  contracts/       # versioned public/private schemas and migration
  generation/      # bounded geometry and drawing backends
  mutations/       # prerequisites, controlled edits, invariant lists
  validation/      # independent artifact readers and oracle checks
  profiles/        # conditional engineering rules and provenance
  adapters/        # export/import, local process protocol
  scoring/         # matching, adjudication, metrics, paired comparison
  reporting/       # offline escaped HTML with source evidence
  cli.py
tests/
  contracts/
  geometry/
  artifact_validation/
  scoring/
  metamorphic/
  consumer/
corpus/             # small licensed curated fixtures/manifests
evidence/           # reproducible validation and milestone summaries
```

Proposed CLI flow, to be finalized with contracts:

```text
rfqfuzz generate --suite core --seed 42 --out work/suite
rfqfuzz validate work/suite --out work/validation
rfqfuzz export-review work/suite --out work/public
rfqfuzz import-results work/reviewer-a.json --suite work/suite --out runs/a
rfqfuzz compare runs/a runs/b --out work/report
```

These commands are specification examples, not executable features today. Add a stable `demo` command only once this flow is implemented end to end.

## Release acceptance

- Every Must requirement has retained acceptance evidence and no unresolved failure. Should omissions are documented; no quiet promotions to claimed features.
- An independent consumer can install and evaluate supplied results without an API key, then feed in an actual external reviewer response.
- The report explains a real changed result and exposes misses, false alerts, uncertainty, failures and corpus limitations.
- The suite passes its independent artifact checks. At least one intentionally broken implementation for each critical evaluator category is caught: units, inequality, conclusion class, matching/deduplication, answer leakage and unknown handling.
- Windows and Linux supported paths are exercised with pinned dependencies. Rendering/kernel differences have explicit semantic tolerances.
- Broad industrial usefulness is not claimed without a separately authored packet and engineering review. Otherwise the release explicitly remains a synthetic regression toolkit.
- Documentation includes source/license provenance, setup, unsupported scope, reproducible examples and truthful results. The blog remains a draft until the user changes the no-publication instruction.

## Main risks and responses

| Risk | Response |
|---|---|
| Oracle repeats the generator's bug | Re-import final artifacts; analytic checks; independent validator owner; deliberately broken implementations; disclose common kernel. |
| Plausible but illegible drawing | Render inspection, annotation-region checks and rejection. Do not count hidden text as successful visible annotation. |
| “Missing” information exists elsewhere | Evaluate authority/precedence and all supported public representations. Exclude ambiguous correspondence. |
| Benchmark only recognizes its own template | Hold out ancestry/layout; independent packet; avoid generator-specific reviewer inputs. |
| Excess warnings look successful | Valid lookalikes, explicit coverage and false-alert metrics; always-flag negative baseline. |
| Real reviewer is closed, paid or unavailable | Manual structured-result adapter and existing Codex review session; keep product independent of that service. Never fabricate integration results. |
| Dependency churn or copyleft mismatch | Pin versions, test exports, record a compatible license; limit custom rendering fallback to bounded templates. |
| Growing scope becomes another generic DFM app | Keep review-testing workflow and separate tracks. Do not add machining certification, broad CAD import or a hosted service. |

## Autonomous work and human judgment

An agent can implement the contracts, generators, validator, adapters, scoring, CLI, report and tests with minimal guidance once M0 resolves the stack. It can propose explicit synthetic manufacturing profiles and produce a factual article draft. It cannot invent evidence of shop-floor validation or infer the user's personal experiences. Representative drawing review and practical feedback would strengthen the result, but no new account or permission is necessary to begin the local proof.
