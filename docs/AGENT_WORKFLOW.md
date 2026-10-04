# Agent development workflow

This workflow applies to building RFQFuzz. It does not make an LLM a trusted manufacturing oracle. All setup commands below are optional future instructions; no Beads installation, initialization, integration setup or remote synchronization has been performed for this plan.

## Work from contracts and evidence

Read `AGENTS.md`, the research decision, `requirements.json`, `docs/ARCHITECTURE_AND_RULES.md` and `IMPLEMENTATION_PLAN.md` before claiming work. Finish the M0 go/no-go decision before expanding the corpus. The difficult contribution is trustworthy review regression evidence, not the number of agents used.

`requirements.json` owns requirements. `tasks.json` initially owns task dependencies and execution state. Each task must identify its requirement IDs, prerequisites, permitted edit scope, public/private interfaces, acceptance commands and retained evidence. Acceptance criteria are agreed before implementation; changing a criterion requires a documented engineering reason rather than a convenient way to pass.

Use one coordinator and at most two simultaneous implementation workers initially. Freeze shared schemas before parallel implementation. Give potentially conflicting editors separate worktrees. Integrate changes sequentially, then rerun relevant checks on the combined commit. An independent reviewer should challenge difficult oracle and scoring changes rather than rubber-stamp every small edit.

## Separate the roles

The fixture-generator worker implements bounded geometry, drawings and mutations. Its metadata describes intent; it cannot establish that exported artifacts contain that intent.

The validator worker independently reopens STEP and rendered PDF/PNG outputs, checks visible annotations, measures supported geometry, and verifies mutation invariants. Give it the contract and source evidence rather than only the generator's explanation. Shared CAD kernels remain a disclosed common failure mode; analytic checks and deliberately broken implementations supplement them.

The reviewer under test receives only the neutral public packet, declared engineering premises and output schema. It receives no expected finding, mutation label or diagnostic filename. Procedural blinding on the same machine is not secure isolation. External adapters require explicit configuration; installing an adapter never authorizes hosted API calls or packet transmission. Manual result import is valid. Do not invent a callable Codex desktop API.

The scorer checks the reviewer against validated expectations and declared coverage. A separate development reviewer challenges matching, deduplication, abstention and error handling. Neither a reviewer response nor another agent's confidence can validate an ambiguous fixture.

## Close tasks only with evidence

Use the dependency graph in `tasks.json`: M0 proof precedes schemas and profiles; stable contracts unlock generator and validator work; validated public packets unlock reviewer adapters and scoring; independent challenge tests precede the consumer demonstration.

Before closing a task, retain the exact acceptance command, result, artifact paths, requirement IDs and local commit. Keep failed examples. Invalid fixture, unsupported input, unknown, timeout and reviewer failure must remain distinguishable. Do not convert any into a pass.

Critical checks include equivalent-unit transformations, threshold boundaries, defective/repaired/valid controls, removed-evidence cases, evaluator mutants and always-clear/always-flag/always-abstain baselines. Split related geometry and layout ancestry together. Evaluate the actual exported files and running report, not just in-memory structures or screenshots of a successful command.

After three unsuccessful repairs of the same conceptual failure, reassess the assumption or scope. At each milestone record whether continued work remains justified. At handoff save the commit, environment versions, current task, failing command, evidence paths, unresolved assumption and next dependency-ready task.

## Optional Beads adoption

Beads supplies persistent tasks, dependencies, atomic claims and context recovery. A future basic loop is:

```text
bd prime
bd ready --json
bd show <id> --json
bd update <id> --claim
# Implement, validate, retain evidence, and commit locally.
bd close <id> --reason "Acceptance evidence: <path>; local commit: <sha>"
```

If adopted, record the pinned version and map each existing `Txx` task to its Beads ID. Beads then becomes the sole execution-state authority. Freeze the original seed graph and generate readable exports; do not independently edit task statuses in Beads, `tasks.json` and Markdown. Keep requirements authoritative in `requirements.json`. [Beads README](https://github.com/gastownhall/beads)

Current Beads uses Dolt. Default embedded storage is single-writer at `.beads/embeddeddolt/`; only the coordinator writes it. Workers return proposed updates. JSONL exports omit database history and non-issue tables, so use a genuine local backup with `bd backup init <local-path>` and `bd backup sync`. Do not commit raw database directories. [Dolt architecture and backup guide](https://github.com/gastownhall/beads/blob/main/docs/architecture/dolt.md)

Inspect changes from future `bd init` or `bd setup codex`, which can install instructions and hooks. Preserve the user's authority: local commits are allowed; pushes, remote Beads synchronization, publication and outside messages are prohibited. [Integration policies](https://github.com/gastownhall/beads/blob/main/docs/getting-started/ide-setup.md)

## Use the inspiration selectively

Gas Town's useful ideas are durable work, explicit dependencies and orderly integration. Its January article describes older Beads storage; current repository documentation governs setup. Full Gas Town services and orchestration are outside the initial project. [Requested article](https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04), [current Gas Town repository](https://github.com/gastownhall/gastown)

Independent evaluation and explicit completion contracts also follow contemporary harness research. That research reports evaluator leniency and orchestration overhead: inspect failures and keep only mechanisms that improve evidence quality. Agent-assisted development does not require a runtime AI feature. [Anthropic harness research](https://www.anthropic.com/engineering/harness-design-long-running-apps)
