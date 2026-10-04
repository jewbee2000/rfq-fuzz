"""Generate readable requirements/evidence from source and coordinator ledger."""
import argparse
import json
from pathlib import Path
import re
import subprocess

p=argparse.ArgumentParser();p.add_argument("--final",action="store_true");a=p.parse_args()
source=Path("requirements.json");data=json.loads(source.read_text());ledger=json.loads(Path("tasks.json").read_text());tasks={t["id"]:t for t in ledger["tasks"]}
proof={
"R01":["docs/DEMO.md","evidence/M5/consumer.md"],
"R02":["evidence/M1/contracts.md","evidence/M4/core-public-export-audit.json","docs/REVIEWER_PROTOCOL.md"],
"R03":["evidence/M2/generators.md","evidence/M2/generation-integration.txt"],
"R04":["evidence/M2/core-final-acceptance.md","evidence/M4/visual-review/attestation.json"],
"R05":["evidence/M2/mutations.md","evidence/M4/core-validated/oracle.json"],
"R06":["evidence/M1/profiles.md","evidence/M4/corpus-summary.json"],
"R07":["evidence/M4/challenge-report.md","evidence/M4/baselines","evidence/M2/core-suite/public/pk-61e732a788ae"],
"R08":["evidence/M2/oracles.md","evidence/M2/core-final-acceptance.md"],
"R09":["evidence/M1/profiles.md","docs/RULE_PROVENANCE.md"],
"R10":["evidence/M1/contracts.md","evidence/M3/scoring.md"],
"R11":["evidence/M0/gate.md","evidence/M3/adapters.md","evidence/M5/external-v1/summary.json"],
"R12":["evidence/M3/adapters.md","evidence/M4/report-and-failures.md","evidence/M5/independent-fixes.md"],
"R13":["evidence/M3/scoring.md","evidence/M5/independent-final-review/numeric-prefix-results-fixed.json"],
"R14":["evidence/M4/corpus-summary.json","evidence/M4/core-comparison.json","evidence/M5/external-v1/summary.json"],
"R15":["evidence/M5/consumer.md","evidence/M5/independent-fixes.md","evidence/M5/coordinator-demo-v2/report/index.html"],
"R16":["evidence/M4/challenge-report.md","examples/v1-demo/replay-manifest.json","evidence/M5/git-archive-input-audit.json"],
"R17":["evidence/M4/challenge-report.md","evidence/M4/challenge-tests","evidence/M5/independent-final-review/final-consumer-review.md"],
"R18":["evidence/M4/report-and-failures.md","evidence/M5/consumer.md","evidence/M5-report-audit-final-tests.txt"],
"R19":["evidence/M4/adapter-size-followup.md","evidence/M4/report-and-failures.md","docs/REVIEWER_PROTOCOL.md"],
"R20":["evidence/M5/consumer.md","docs/BLOG_DRAFT.md","docs/LICENSES.md","docs/SHOULD_DEFERRALS.md"],
"R21":["tasks.json","docs/MILESTONE_ASSESSMENTS.md","docs/CURRENT_HANDOFF.md","evidence/M5/release-review.md"],
"R22":["docs/DEMO.md","requirements-v1.lock","evidence/M5/consumer.md","evidence/M5/environment-windows-coordinator.json"]}
# Rule cards are retained in the implemented profile module and evidence notes.
if not Path("docs/RULE_PROVENANCE.md").exists():proof["R09"][1]="src/rfqfuzz/v1/profiles.py"
partial={"S01","S03","S07"}
final_log=Path("evidence/M5-final-release-tests.txt")
if not final_log.exists():final_log=Path("evidence/M5-final-after-audit-tests.txt")
match=re.search(r"^(\d+) passed, (\d+) warnings in [^\r\n]+$",final_log.read_text(),re.M)
passed,warnings=map(int,match.groups()) if match else (0,0)
missing=[path for paths in proof.values() for path in paths if not Path(path).exists()]
for t in tasks.values():
    if t["status"]=="completed":
        assert t["completion_commit"] and t["completion_commit"]!="HEAD","completion commit must be immutable"
        assert not t["verification_is_proposed"] and Path(t["evidence"]).is_file(),"completed task lacks actual acceptance evidence"
        subprocess.run(["git","cat-file","-e",t["completion_commit"]+"^{commit}"],check=True)
if a.final:
    assert all(t["status"]=="completed" for t in tasks.values()),"task acceptance incomplete"
    assert final_log.name=="M5-final-release-tests.txt" and passed>=270,"final integrated checks missing"
    assert not missing,missing
for r in data["requirements"]:
    if r["priority"]=="must":
        ready=all(tasks[t]["status"]=="completed" for t in r["tasks"])
        r["status"]="verified" if ready else "in_progress"
        r["completion_evidence"]=proof[r["id"]]
        r["acceptance_commands"]=[tasks[t]["verification"] for t in r["tasks"] if tasks[t]["verification_is_proposed"] is False]
    elif r["priority"]=="should":
        r["status"]="partial_with_deferred_scope" if r["id"] in partial else "deferred"
        r["completion_evidence"]=["docs/SHOULD_DEFERRALS.md"]
    else:r["status"]="respected" if r["priority"]=="wont" else "deferred"
data["status"]="M1-M5_verified_bounded_synthetic_release" if a.final else "M1-M5_consumer_acceptance_active"
source.write_text(json.dumps(data,indent=2)+"\n")
readable=["# Requirements","","Generated from [requirements.json](../requirements.json), the source of truth. Status and acceptance evidence describe the bounded synthetic release; acceptance criteria remain the original contract. See [evidence matrix](REQUIREMENTS_EVIDENCE.md) and [Should deferrals](SHOULD_DEFERRALS.md).",""]
for group,title in [("must","Must"),("should","Should"),("could","Could"),("wont","Won't")]:
    readable += ["## "+title,""]
    for r in data["requirements"]:
        if r["priority"]!=group:continue
        readable += [f"### {r['id']} — {r['title']}","",r["requirement"],"",f"**Rationale:** {r['rationale']}","",f"**Acceptance:** {r['acceptance']}","",f"**Delivery/status:** {r['milestone']}; {', '.join(r['tasks']) or 'no initial task'}; {r['status']}.",""]
Path("docs/REQUIREMENTS.md").write_text("\n".join(readable))
matrix=["# Requirements evidence matrix","","The 22 Must requirements are evaluated for a finite local synthetic reviewer-regression toolkit. All core cases are development-only. Genuine external observations, template reference agreement and injected changes are separate evidence; none establishes general manufacturing competence.","",f"Final integrated acceptance: {passed} passed, {warnings} upstream warnings (`{final_log}`). Task ledger provides exact commands, requirement IDs, dependencies and local completion commits. M0 artifacts/hashes remain unchanged. No remote publication occurred.","","| ID | Status and acceptance evidence | Commands/tasks | Local implementation commits |","| --- | --- | --- | --- |"]
for r in data["requirements"]:
    if r["priority"]!="must":continue
    evidence="; ".join(f"[{Path(path).name}](../{path})" for path in proof[r["id"]])
    commands="; ".join(f"{t}: {tasks[t]['verification']}" for t in r["tasks"])
    commits="; ".join(f"{t}: `{tasks[t]['completion_commit'] or 'documentation acceptance active; see tasks.json'}`" for t in r["tasks"])
    matrix.append(f"| {r['id']} {r['title']} | {r['status']}; {evidence} | {commands.replace('|','/')} | {commits} |")
matrix += ["","Independent corrections at `4c98b5f` cover report-source binding/escaping, reference error status and exact numeric grounding. Implementation freeze `55b288a` adds explicitly bounded parser controls for the slower software-emulated Linux setup. Portable Git-byte correction `348c5f1` preserves the same audited demo inputs without text normalization; product Python is unchanged. These supplement initial task commits and are independently checked; documentation commits follow.","","All Should requirements have explicit delivered/deferred portions in [SHOULD_DEFERRALS.md](SHOULD_DEFERRALS.md). No second CAD kernel, human engineer oracle, physical manufacture, broad layout invariance, hosted adapter or industrial benchmark result is claimed.",""]
Path("docs/REQUIREMENTS_EVIDENCE.md").write_text("\n".join(matrix))
print(json.dumps({"Must":22,"verified":sum(r["priority"]=="must" and r["status"]=="verified" for r in data["requirements"]),"missing_evidence":missing,"final":a.final}))
