# Current handoff

Publication follow-on, 2026-10-04: the user authorized pushing this project and
selected a public GitHub repository. Target:
`https://github.com/jewbee2000/rfq-fuzz`; source, retained evidence, full history
and the labeled article draft are included. The article is not posted to the blog.
Current task: public source publication and an actionable owner checklist, completed.
Initial pushed/verified commit: `2d8feebd8e00b43f54f7b683f82c3aa72bfc2e81`;
this handoff metadata follows that commit. `git rev-parse HEAD` gives the current
checkout; `git ls-remote origin refs/heads/main` must match it after the final push.
Unauthenticated GitHub reads confirm public visibility and main's commit.
No active failing command. Publication evidence:
[history and portable-byte preflight](../evidence/publication/preflight.json),
[document audit](../evidence/publication/document-audit.json),
[repository creation](../evidence/publication/repository-created.json) and
[initial push verification](../evidence/publication/initial-push-verification.json).
The completed M0–M5 task graph is unchanged. Proposed follow-on dependencies and
owner inputs are in [NEXT_STEPS.md](NEXT_STEPS.md).
Environment and remaining assumptions are unchanged from the milestone record
below. Next dependency-ready engineering proposal: native Windows/Linux continuous
checks. External transfer work needs an owner-permitted packet, an engineer's
adjudication and a named reviewer; none has been newly supplied. Bounded source
publication is complete, while stronger transfer claims remain unproven.

## Completed milestone handoff (before GitHub publication)

2026-10-04, America/Los_Angeles. Current completed evidence commit:
`d76b4c29eb0f3620aec6e62a3bfd84b69642bded` (T14 content), following T13 evidence
`7f72883523776a66c710683bb0d493d4602798ec`. Implementation freeze `55b288a`,
portable audited-input correction `348c5f1`. All task completion commits are
immutable and recorded in `tasks.json`;22/22Must requirements are verified.
Metadata commits follow content commits; `git rev-parse HEAD` gives the current
checkout. Coordinator alone owns the fallback ledger; Beads was not adopted.

Environment: coordinator Windows11/Python3.12.2/.venv, Poppler26.07, integrated
tests270passed/4upstream warnings. Independent Windows consumer uses its own
Python3.12.2 environment; Ubuntu24.04.5/Python3.12.3/Poppler24.02 software QEMU TCG
consumer uses300/120second parser/audit bounds. Both complete15case replays,
three-family own-reader/PDF/PNG checks and report data/hash/link audits pass.
The actual v1 Edge rendering has no errors/remotes/overflow. M0's original browser
rejection remains unverified while its bytes/33tests remain preserved.

Task: complete; T00–T14 completed in dependency order,
with actual commands, evidence and local commits. Failing command: none active.
Retained failures include Linux60second native timeouts, Docker setup, initial
consumer command misuse, evaluator mutants, artifact corruption and original
Git-normalized hashes. None is relabeled a pass. Task-owned QEMU/server/launcher
are stopped, with no task-port listeners; actual ownership/powerdown record is
`evidence/M5/consumer-environments/helper-shutdown.json`.

Evidence: `evidence/M5/consumer.md`, full independent `consumer-environments`
handoff, `consumer-handoff-audit.json` (1699final manifest files), native core/visual
records under M2/M4, genuine external-v1 observations, separate transfer-v2,
`evidence/M5-final-release-tests.txt`, and final requirements/document audits.
`docs/REQUIREMENTS.md`/`REQUIREMENTS_EVIDENCE.md` are generated from the source JSON.

Unresolved assumptions: shared OCCT; finite grammar/aliases and one core layout;
all145corecases development, zero core holdout; one genuine units assertion
unadjudicated for missing envelope evidence; no second kernel, human engineer,
manufactured part or industrial accuracy evidence. Should portions and reasons
are in `docs/SHOULD_DEFERRALS.md`. Broader template invariance is deferred.

Next dependency-ready task: none in the completed authorized M0–M5 graph.
Assessment: bounded local regression scope remains worthwhile. Further engineering
claims need separately governed engineer-owned packets and oracle review; no
additional milestone is started. All changes remain local: no push, PR, deployment,
publication, outside message or manufacturing order at that milestone handoff.
