# Publication code review, 2026-10-04

These repairs were made after the original 270-test implementation and GitHub
publication. They are a separate review pass for Walter's combined experiment
article. Original fixtures, oracle answers, external-review responses and replay
reports remain unchanged.

## Local dimension units

The finite validator read a bore dimension's explicit `mm` or `in` unit, but the
template reference reviewer used the drawing's default unit. A correctly labeled
inch dimension on a millimetre drawing could become a false contradiction. The
reference also required a tolerance even though the finite grammar permits a
nominal-only dimension. Five added regressions cover conversions in both
directions, true contradictions and a nominal-only value. Three failed before
repair (`reference-units-before.txt`). The reference now interprets the explicit
local unit and optional tolerance independently of the validator.

## Process output limit

The configured local adapter checked its 4,000,000-byte output limit only while
the child was alive. A fast child could exit between polls and leave oversized
stdout accepted as completed. A real-process probe reproduced this in one of
three trials with 4,100,000 output bytes. Three deterministic regressions cover
already completed processes with oversized stdout, stderr and response files;
all failed before repair (`output-bound-before.txt`). A final file-size check now
runs before accepting completion. This is a polling resource control for trusted
local processes, not a security sandbox or kernel-enforced quota.

## Verification

The targeted adapter/consumer/scoring selection passed all 16 cases. The final
full pytest log and JUnit are retained here, with commands and source/log hashes in
`checks.json`. The full suite includes `test_consumer_frozen_demo`: it executes the
real 15-case offline replay, requires both result tracks and exactly two injected
changes, and checks the generated HTML for unsafe elements. The eight added
regression cases are publication-audit coverage, not evidence of the original
agent getting these edges right without review.
