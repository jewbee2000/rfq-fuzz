# Implement RFQFuzz

Open this folder as a local project in Codex. Start one implementation chat with the prompt below. Do not launch several implementation chats before the shared contracts and first fixture are working.

> Implement RFQFuzz from the repository plan. Read AGENTS.md, README.md, docs/RESEARCH_AND_GO_NO_GO.md, requirements.json, docs/ARCHITECTURE_AND_RULES.md and IMPLEMENTATION_PLAN.md. Begin with tasks T00 through T03 and the M0 feasibility gate. Recheck the closest competing repositories, select and pin a working CAD/drawing stack, create one defective/corrected/valid challenge bundle, independently validate its exported STEP and visible drawing, and exercise an external reviewer through the public packet interface. Produce an actionable regression report and record the gate decision in evidence/M0/. Do not expand the corpus or build a UI until this gate passes. Continue through ready tasks when the evidence supports the plan. Keep unknowns and unsupported cases explicit. Commit locally; do not push, create remote repositories, deploy, contact others, or publish website content. Use independent reviewers and isolated workers when they improve verification. If a core assumption fails, record the evidence and revise or stop that part of the plan instead of manufacturing a successful result.

## Setup

The first agent can handle environment creation, dependency resolution, lockfiles and local tests. Proposed baseline: Python 3.12, Git, a separate virtual environment, an OCCT-backed CAD library and a drawing/PDF renderer. The exact compatible versions are an M0 deliverable; they have not been installed or validated for this project. A working stack on Windows and Linux is a release requirement. Investigate WSL only if a native dependency actually blocks the Windows path.

No SolidWorks license, CNC machine, GPU, cloud database or new paid API account is required for the core. Existing Codex access can supply an independent reviewer session: export only the public packet plus review instructions, then import its structured response. This is a manual adapter workflow until an actual automation interface is implemented. Do not assume the desktop app exposes an API.

An optional paid model adapter needs credentials and an explicit cost budget later. It must not block offline generation, validation, imported-result scoring or reports. Beads is an optional development aid, not a product prerequisite. Full Gas Town is excluded from initial setup.

The proposed default drawing backend is Draftwright, subject to the M0 artifact tests. It is AGPL-3.0; plan a compatible open-source distribution if it is used, and record the dependency/license decision before adding a release license. Do not automatically label the project MIT. A small bounded renderer is a fallback only if reuse cannot meet the acceptance criteria; implementing a general drafting engine is outside scope.

## Where your input helps

There is no required permission or additional account needed to start the local proof. The most valuable later contribution is reviewing a few representative packets for engineering plausibility and choosing one real question the report should answer. That is a validation opportunity, not a reason to block the initial agent.

Before claiming relevance beyond synthetic examples, use a separately authored packet and, if available, a drawing you own and can legally share. Without that evidence, label the release a synthetic regression toolkit. No employer drawing or private file should enter a public corpus by assumption.

The current instruction permits local commits and forbids pushes. A GitHub repository and website article remain later publication steps requiring a changed instruction. The article should be finished only after there are real screenshots, measurements, failures and decisions to discuss.
