"""Coordinator-only fallback task ledger and handoff recorder."""
import argparse
import json
import subprocess
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("task")
p.add_argument("state",choices=["in_progress","completed"])
p.add_argument("--command")
p.add_argument("--evidence")
p.add_argument("--commit")
a=p.parse_args()
path=Path("tasks.json")
ledger=json.loads(path.read_text())
tasks={t["id"]:t for t in ledger["tasks"]}
t=tasks[a.task]
assert all(tasks[d]["status"]=="completed" for d in t["depends_on"]), "dependency not complete"
t["status"]=a.state
if a.state=="completed":
    assert a.command and a.evidence and a.commit
    assert Path(a.evidence).is_file()
    subprocess.run(["git","cat-file","-e",a.commit+"^{commit}"],check=True)
    t.update(verification=a.command,verification_is_proposed=False,evidence=a.evidence,completion_commit=a.commit)
path.write_text(json.dumps(ledger,indent=2)+"\n")
status=json.loads(Path("STATUS.json").read_text())
status.update(phase="M1-M5_execution",current_task=a.task,task_state=a.state,next_task=[x["id"] for x in ledger["tasks"] if x["status"]=="not_started" and all(tasks[d]["status"]=="completed" for d in x["depends_on"])])
Path("STATUS.json").write_text(json.dumps(status,indent=2)+"\n")
