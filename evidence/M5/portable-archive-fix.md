# Independent consumer archive finding

Requirements R16/R20/R22; coordinator integration for T13. Local source fix
`348c5f1ea5a6e99bc0acdb4f0d0af52f3a8146e0`. No input was regenerated.

The independent consumer checked the Windows-byte source freeze against Git
blobs and found text normalization. In particular the committed demo packet JSON
did not match its replay-manifest hash on a canonical Linux Git export. Its
Windows checkout/archive had the actually audited CRLF bytes. A matching local
replay alone therefore had not proved Git checkout portability.

`.gitattributes` now protects **all** `examples/v1-demo/**` as `-text`, alongside
the existing evidence/artifact protection. The original audited working bytes
were re-added to Git. Product readers and all fixture meanings remain unchanged.
The commit's large apparent JSON diff is the preservation of literal CRLF bytes.

Executed `.venv/Scripts/python.exe tools/audit_demo_git_archive.py`. The actual
`git archive` of the commit contains65regular files: the manifest and64hashed
assets. Every asset matches both its manifest hash and the audited working file.
Initial commit/archive digest and zero mismatches are retained in
`git-archive-input-audit-348c5f1.json`. A follow-up at `b3f90a9` independently
exports under both `core.autocrlf=false` and `true`: all65protected files are
byte-identical under both policies and all64manifest hashes match.
`git-archive-input-audit.json` records that follow-up. Product Python and demo
inputs are unchanged between these commits. Independent consumer source/archive equivalence
and actual platform acceptance are retained separately when complete.

The earlier one-line `evidence/M5-archive-audit.txt` lacks a recorded commit/method
and did not establish canonical Git export portability. It is retained as an
insufficient diagnostic and superseded by the explicit Git-byte audit. Original
M0 source/artifacts are unaffected. No remote repository, push or release occurred.
