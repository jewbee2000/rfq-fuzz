# RFQFuzz

A local regression toolkit for CNC RFQ reviewers. Create controlled STEP/drawing
packages, validate the actual exported artifacts, import a review and inspect
changed behavior. Package consistency and conditional CNC advisories are separate.

**Status: M1–M5 accepted for the bounded local scope, 4 October2026.**
M0 remains a frozen regression.270integrated Windows tests pass;145corepackets pass final
artifact validation;6/6deliberate evaluator mutants are caught. All145corecases
are development-only. This is a synthetic regression toolkit; no part is approved
for manufacture. Source and retained evidence are available in the public
[`jewbee2000/rfq-fuzz`](https://github.com/jewbee2000/rfq-fuzz) repository;
the article draft has not been posted to the blog.

Independent Windows/Linux consumers pass the complete offline demo, three fresh
family checks and source-linked diagnosis. Linux software emulation uses the
documented explicit300/120second resource bounds; the earlier timeout is retained.
The [requirements evidence matrix](docs/REQUIREMENTS_EVIDENCE.md) records each
Must acceptance and local commit; all seven Should scopes are documented.

Start with the [reproducible15case demo](docs/DEMO.md),
[offline comparison report](evidence/M5/coordinator-bounded-demo/report/index.html),
[Should deferrals](docs/SHOULD_DEFERRALS.md), [article draft](docs/BLOG_DRAFT.md)
and [next steps and owner checklist](docs/NEXT_STEPS.md).
The report's two changes are deliberately injected into retained public-template
reference observations. Genuine [M5 external observations](evidence/M5/external-v1)
and the original [M0 external review](evidence/M0/review-handoff/review-output)
remain separate. Actual v1 browser rendering and changed-evidence navigation pass
without page errors, remote requests or horizontal overflow.

V1 supports three bounded families, six objective operators, four conditional
profile rules, uncertainty/valid controls, local/manual adapters, immutable raw
imports, per-track scoring and source-linked HTML. Read [artifact acceptance](evidence/M2/core-final-acceptance.md),
[challenge evidence](evidence/M4/challenge-report.md) and [licenses](docs/LICENSES.md).
The original [M0 gate](evidence/M0/gate.md), artifacts and reproduction remain
unchanged. Exact witness matching is intentionally conservative; human engineer,
second-kernel and physical/industrial evidence are unavailable.

The original upload-and-check idea is a **no-go**: existing products already combine CNC DFM with drawing checks. The qualified alternative is a reusable regression tool for the people adopting or developing those reviewers. A bounded search found no publicly runnable equivalent to the combined workflow proposed here. This is an opportunity hypothesis, not proof of universal novelty or customer demand.

## The useful outcome

An engineer changes an AI review prompt, a rule engine or a supplier capability profile. Before trusting the change, they run the same controlled challenge packets through both versions. RFQFuzz shows the exact drawing region, relevant geometry, expected conclusion, actual finding and changed behavior. Valid alternatives test whether the reviewer has learned to flag everything. Ambiguous cases test whether it can admit that information is missing.

Example: a four-hole plate has 6.00 mm bores in its STEP file. One drawing says 6.80 ±0.05 mm; a corrected twin says 6.00 ±0.05 mm. A third packet legitimately specifies different dimensions at a different process stage. A useful reviewer catches the first contradiction and understands why the other two are acceptable within their declared contracts.

The initial tool tests **RFQ package consistency**, with a separately reported **CNC advisory/profile track**. It does not certify that a part can be manufactured.

## Start here

- [Research and build decision](docs/RESEARCH_AND_GO_NO_GO.md): competitors, adjacent work, sources, uncertainty and stop conditions.
- [Requirements](docs/REQUIREMENTS.md): Must/Should/Could/Won't, rationale and acceptance criteria. [Structured source](requirements.json).
- [Architecture and engineering rules](docs/ARCHITECTURE_AND_RULES.md): supported geometry, mutations, independent oracles, data contracts and scoring.
- [Implementation plan](IMPLEMENTATION_PLAN.md): staged delivery, feasibility, risks and release gates.
- [Agent workflow](docs/AGENT_WORKFLOW.md): Beads-inspired task execution, independent verification and local-only integration.
- [Kickoff instructions](START_HERE.md): the exact first implementation prompt and setup requirements.
- [Blog brief](docs/BLOG_BRIEF.md): a first-person article outline grounded in work that will actually be done.

The decisive first milestone is one independently validated challenge bundle evaluated through an external review interface. If it cannot produce an actionable regression report, stop before building a larger corpus or UI.

## Implemented boundary

| In the first release | Deferred or excluded |
|---|---|
| Local CLI and Python library; inspectable HTML report | Hosted upload service |
| Generated single-solid plates and prismatic blocks | Arbitrary imported CAD mutation |
| STEP, vector PDF and rendered PNG packets | Native SolidWorks drawing import |
| Six objective package-defect operators | Full GD&T or functional design approval |
| Conditional rules for size, walls, holes, material and finish context | Universal machinability predictions |
| Controlled defects, repairs, valid lookalikes and missing evidence | Five-axis process planning, CAM, molding or stamping |
| Reviewer adapters, replay and version comparisons | A new production DFM reviewer |

See the requirements source/evidence matrix for acceptance and the Should record
for deferred portions. Extensibility is not implemented support for arbitrary
drawings, general tolerancing or manufacturing processes.
