# Independent final consumer audit

Read-only audit of coordinator checkout `src/rfqfuzz/v1/{cli,api,adapters,reference,reporting}.py`, `docs/DEMO.md`, and `docs/REVIEWER_PROTOCOL.md`. Additional scorer review followed an actual grounding challenge. Final targeted verification used coordinator commit `4c98b5f158c5b563ad256184303165e60231c088`. The reviewer edited only ignored `work/final-review` evidence files, with no production, task-state or M0 edits. All tests/probes used the repository's Python 3.12 environment and local frozen exported artifacts; no hosted service or outside message was used.

## Commands and retained evidence

1. `.venv/Scripts/python.exe work/final-review/run_checks.py`: **18 passed in 40.07s** across adapters, consumer and reporting tests. Exact pytest invocation, exit code and seven reviewed source/document SHA256 values are in `check-results.json`; stdout/stderr are retained separately. This includes actual 15-case consumer replay and offline report auditing.
2. `.venv/Scripts/python.exe work/final-review/probe_consumer.py`: copied/edited oracle rejected before report output; deliberately malformed score display text safely escaped; rehashed malformed PDF retained as a reference error. `probe-results.json` binds the examined source hashes and details. No browser executed the HTML payload; the audit inspected generated markup.
3. `.venv/Scripts/python.exe work/final-review/probe_adapter_bound.py`: explicitly configured fast local process emitted 5,000,001 bytes to stdout and was rejected with `status=error`, `reason=adapter output size limit`; record and exact argv are in `adapter-probe-results.json`.
4. Repeating the corrupt-PDF CLI call into a fresh output directory after coordinator repair returned **exit 2**, `status=contains_failures`, `states={error:1}`, and retained the failed review record. Exact invocation/output/source hash are in `reference-fixed-results.json`.
5. `.venv/Scripts/python.exe work/final-review/probe_numeric_prefix.py`: changed two grounded numeric claims in the actual retained response for `pk-d0f406e22f58:obj-count`; source/data/result records are retained in `numeric-prefix-results.json` and `numeric-prefix-review.json`.
6. `.venv/Scripts/python.exe work/final-review/probe_numeric_prefix.py -fixed`: unchanged numeric challenge independently rerun against corrected scoring source SHA256 `a8fca4cd8b5ce4b569711ca89c3b814eb9c23a8780be0964a50afc84ab1fb8d2`. Original witnesses match; false numeric claims do not match, receive `silent_miss`, and remain unadjudicated. `numeric-prefix-results-fixed.json` and the altered response are retained.

## Findings and dispositions

| Finding | Actual evidence | Disposition |
| --- | --- | --- |
| Report could display a different oracle/public source from the scored runs | Inspection found report compared runs to each other but omitted supplied source binding, including the single-run path | Coordinator added oracle/suite/profile/raw hashes and reads actual artifact hashes. Revised-oracle probe now rejects before report creation; source-binding acceptance tests passed. |
| Report count/rate fields could emit unescaped HTML | Inspection found direct interpolation of rate/count fields from loaded run JSON | Coordinator escaped those fields. Actual copied valid bound run with a script-like numerator now writes escaped text; offline audit passes with 78 local links and zero unsafe elements. |
| Reference CLI obscured failed rows with successful command status | Actual rehashed corrupt PDF created `status=error` review row while CLI returned exit 0 and no failure summary | Coordinator added aggregate execution states and failure exit. Same artifact now returns exit 2 and explicit error count; raw/native errors remain retained. |
| Numeric prefix accepted as grounded evidence | Actual count mismatch has STEP `H1 count=4` and PDF `H1 COUNT = 3`; altered claims `H1 count=40` and `H1 COUNT = 30` still matched and scored `detected` under source hash `d0dcd14b0b66693253dc8751fffba35acf5a4f8b022a9a76f46ecb67737c6ad4` | Coordinator commit `4c98b5f` uses complete canonical normalized equality. Independent rerun rejects both false claims, records a silent miss and retains the unmatched finding as unadjudicated, while accepting original quotes. **Resolved.** |

The numeric prefix issue is a concrete R13 evidence-credit defect (challenged under R17), even though the chosen conclusion remains a real contradiction. Unsupported numeric claims must not count as an independently grounded finding. Existing positive replay/tests alone did not detect it. Requirement ID corrected by the coordinator at the independent reviewer's request; raw probes and their results are unchanged.

## Consumer behavior otherwise supported by the review

- Frozen replay verifies listed asset hashes before copying, independently reopens actual STEP/PDF/PNG, requires the exact artifact-bound visual attestation, then exports public packets and imports retained responses. Fresh generation does not inherit old attestations.
- Public export rejects sidecars, private keys/labels and bad signatures; same-user blinding remains explicitly procedural. Local adapters use explicit argv and `shell=False`; packet text does not select commands.
- Scoring keeps engineering classes, execution failures, unsupported cases, missing coverage, invalid fixtures and unadjudicated findings separate. Partial coverage can credit a covered individual duty but does not make the attempt complete for resume.
- The two changed demo outcomes are explicitly injected into actual reference results; shared native readers/kernel are disclosed. The demo/documents make no fresh external-review, manufacture or general industrial-competence claim.
- Report hyperlinks remain local and point to retained raw response, oracle and actual artifact sources. Source binding is now checked before output creation.

Small usability recommendation: include `docs/REVIEWER_PROTOCOL.md` or its equivalent complete response template/canonical witness instructions in the exported bundle. Current `INSTRUCTIONS.txt` gives broad record fields and correct engineering/public scope but omits the exact canonical quote vocabulary/path sets documented in the repository. This is a recommendation, not an additional unseen engineering premise.

No remaining material issue was found in the assigned consumer scope after targeted correction verification. This audit does not independently repeat all 145-case visual inspection, Linux installation or external-review experiments; those remain separate coordinator/verifier evidence. The 18-test run preceded the final exact-match scorer change; the only repeated check after that change was the independently retained numeric grounding challenge. Broader final integration tests remain the coordinator's responsibility.
