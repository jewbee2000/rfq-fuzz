"""Retain independent raw observation and score only the requested two packets."""
import shutil
from pathlib import Path
from rfqfuzz.v1.contracts import load_json,write_json
from rfqfuzz.v1.scoring import import_results
from rfqfuzz.v1.reporting import make_report

source=Path("work/consumer-env/external-v1-review")
target=Path("evidence/M5/external-v1")
assert not target.exists()
shutil.copytree(source,target/"observations")
raw=load_json(source/"review-result.json")
ids={r["case_id"] for r in raw["results"]}
for cid in ids:shutil.copytree(Path("evidence/M2/core-suite/public")/cid,target/"suite/public"/cid)
oracle=load_json("evidence/M4/core-validated/oracle.json",limit=32_000_000)
oracle["cases"]=[case for case in oracle["cases"] if case["case_id"] in ids]
oracle["counts"]={"valid":len(ids)}
write_json(target/"oracle.json",oracle)
r=import_results(target/"observations/review-result.json",target/"suite/public",target/"oracle.json",target/"run")
make_report([target/"run/run.json"],target/"oracle.json",target/"suite/public",target/"report")
write_json(target/"summary.json",{"tracks":r["score"]["tracks"],"unadjudicated":r["score"]["unadjudicated"],"scope":"Exactly the2publiccases requested for genuineindependentobservation; full145suiteimport earlier is an integrationdiagnostic with unrequested coverage, not reviewer performance"})
print({"cases":len(ids),"rows":len(r["score"]["rows"]),"unadjudicated":len(r["score"]["unadjudicated"])})
