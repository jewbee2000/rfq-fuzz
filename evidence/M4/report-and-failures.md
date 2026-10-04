# T12 acceptance — offline report and recovery

Requirements: R12, R18, R19. Actual acceptance:
`./.venv/Scripts/python.exe -m pytest tests/reporting tests/adapters --basetemp evidence/M4/report-test-data -q`

Result: **7 passed in 2.14 s**, `evidence/M4-report-tests.txt`. A missing basetemp
parent caused the first collection/setup failure; it is retained separately in
`M4-report-basetemp-failure.txt`. The test data directory now retains malformed
responses, interrupted/partial/complete attempts and the actual escaped HTML.
Recovery plans show pending cases and retain previous attempts rather than
overwriting their raw bytes. Native document auditing and process-tree timeouts
are exercised with the adapter tests.

The actual report probe was opened in a headless installed Microsoft Edge using
`tools/render_report.cjs`. `report-browser-probe/browser-audit.json` and
`report-top.png` retain the rendered outcome: no page errors, remote requests or
horizontal overflow. Coordinator visually inspected that screenshot. It shows
both tracks/counts, labels injected changes clearly and provides exact source
links. Probe has identical runs (zero changed anchors); final changed-case
navigation must also be exercised in the consumer demo.

Initial browser launch requested a missing bundled headless shell; using the
already installed Edge worked. No browser security setting was disabled and no
server/network was required. Arbitrary reviewer text is escaped, including a
literal script payload; audit checks real local links/anchors and rejects script,
event-handler, embedded object and executable/remote URL elements. HTML contains
actual rendered drawings, STEP measurements, expected/actual conclusions,
coverage, provenance and compatible-run comparison.

Assessment: report and resilient attempts are usable for T11/T13 integration.
The preserved M0 browser limitation remains historical; it is not retroactively
rewritten by the v1 probe. Final corpus and consumer rendering remain next checks.
