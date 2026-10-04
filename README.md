# RFQFuzz

A proposed open-source test bench for CNC drawing-review tools. Create controlled mistakes in matched STEP models, drawings and manufacturing instructions; test a reviewer; inspect what it missed, invented or incorrectly declared acceptable.

**Status: M0 feasibility prototype passed, 4 October 2026; stopped at the requested checkpoint.** T00–T03 are complete. The repository is local; nothing has been pushed or published. This is a synthetic regression toolkit, not a production manufacturability certifier.

Inspect the [M0 gate and reproduction commands](evidence/M0/gate.md), [offline comparison report](evidence/M0/report/index.html), [actual public STEP/PDF/PNG packets](evidence/M0/bundle/public), and [independent review observations](evidence/M0/review-handoff/review-output/observations.md). The report's two reviewer regressions are deliberately injected into the reference path; the independent review's original decisions are retained separately. Browser HTML preview was blocked by local-file policy; source links/content were audited, but browser rendering is unverified.

The implemented spike handles one plate ancestry and the O01/H1 bore-group obligation: exported artifacts, independent validator with retained corruption controls, neutral public export, public-only reference review, structured manual import/adjudication and source-linked comparison. [Pinned Python 3.12 setup](docs/SETUP_M0.md) and [dependency licenses](docs/LICENSES.md) are retained. Other part families/operators, general adapters/scoring, advisory rules, Linux release checks and independent industrial transfer remain planned.

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

## Planned scope

| In the first release | Deferred or excluded |
|---|---|
| Local CLI and Python library; inspectable HTML report | Hosted upload service |
| Generated single-solid plates and prismatic blocks | Arbitrary imported CAD mutation |
| STEP, vector PDF and rendered PNG packets | Native SolidWorks drawing import |
| Six objective package-defect operators | Full GD&T or functional design approval |
| Conditional rules for size, walls, holes, material and finish context | Universal machinability predictions |
| Controlled defects, repairs, valid lookalikes and missing evidence | Five-axis process planning, CAM, molding or stamping |
| Reviewer adapters, replay and version comparisons | A new production DFM reviewer |

This table is the planned first-release boundary; it is not a claim that M1–M5 are implemented. See the requirements and M0 gate for actual completed scope.
