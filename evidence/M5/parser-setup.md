# Named consumer resource limits

Source freeze `55b288a` exposes explicit bounded parser settings through CLI/API.
Defaults remain native60seconds/documentaudit20seconds; overrides are greater
than0and at most300seconds. Invalid/nonfinite/bool/out-of-range settings reject
before demo output. Chosen limits are recorded in oracle isolation and demo result.
The existing timeout test still terminates native work and retains timeout without
expectations. Longer runtime never overrides geometry, glyph/raster, artifact
hash, mutation isolation or required visual attestation.

The software-emulated single-CPU Linux TCG attempt reached the60second limit;
its partial native outputs and timeout records remain retained by the independent
environment verifier. No incomplete native record was promoted to valid.
The named4CPUnoapic TCG setup's300second one-case probe completed63.1793seconds,
measured one solid68x44x39mm envelope and passed actual drawing checks. Without
attestation it correctly reports unverified/exit2, rather than timeout or pass.

Actual root relevant acceptance:75artifact-validation/adapter/consumer/report
checks passed with4upstreamwarnings (`evidence/M5-parser-bound-tests.txt`). All
product acceptance after this resource-only change is separately recorded at
`evidence/M5-final-release-tests.txt`. Consumer complete-workflow acceptance,
chosen platform bounds and failed attempts are recorded in `consumer.md` after
actual independent completion.
