# RFQFuzz

A proposed open-source test bench for CNC drawing-review tools. Create controlled mistakes in matched STEP models, drawings and manufacturing instructions; test a reviewer; inspect what it missed, invented or incorrectly declared acceptable.

**Status: researched implementation plan, 4 October 2026. No application has been implemented or benchmark results produced.** This repository is local. Nothing has been pushed or published.

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

These are proposed features. See the requirements for the exact release boundary and evidence required before making claims about usefulness.
