"""Freeze a representative audited consumer replay, with actual raw provenance."""
import shutil
from pathlib import Path
from rfqfuzz.v1.contracts import load_json,write_json,sha256

destination=Path("examples/v1-demo");assert not destination.exists()
changes=load_json("evidence/M4/core-comparison.json")
mutations=load_json("evidence/M2/core-suite/private/mutations.json")["mutations"]
selected={c["case_id"] for c in changes}
for op in ("O01","O02","O03","O04","O05","O06","A01","A02","A03"):
    selected.add(next(m["case_id"] for m in mutations if m["operator"]==op and m["variant"]=="defective"))
for op,variant in [("O01","valid_alternative"),("O03","valid_alternative"),("A04","underdetermined")]:
    selected.add(next(m["case_id"] for m in mutations if m["operator"]==op and m["variant"]==variant))
selected.add("pk-61e732a788ae")
for cid in sorted(selected):shutil.copytree(Path("evidence/M2/core-suite/public")/cid,destination/"suite/public"/cid)
write_json(destination/"suite/private/mutations.json",{"schema_version":"1.0","warning":"private author intent is not ground truth","mutations":[m for m in mutations if m["case_id"] in selected]})
attestation=load_json("evidence/M4/visual-review/attestation.json")
attestation["cases"]=[c for c in attestation["cases"] if c["case_id"] in selected]
write_json(destination/"attestation.json",attestation)
for source,name in [("evidence/M3/reference-core/review.json","reference.json"),("evidence/M3/reference-injected.json","injected.json")]:
    response=load_json(source);response["results"]=[r for r in response["results"] if r["case_id"] in selected]
    for row in response["results"]:row["raw_ref"]=None # source provenance retained in manifest; no author absolute paths
    write_json(destination/name,response)
manifest={"schema_version":"1.0","cases":len(selected),"files":{p.relative_to(destination).as_posix():sha256(p) for p in sorted(destination.rglob("*")) if p.is_file()},"provenance":{"reference":"Actual public-only template reference observation evidence/M3/reference-core; shares observed readers with validator","injected":"Explicitly injected missingcontradiction+falsealert, evidence/M3/reference-injected.json","source_response_sha256":{"reference":sha256("evidence/M3/reference-core/review.json"),"injected":sha256("evidence/M3/reference-injected.json")}},"limitations":["Auditedbytes replay, notnewreviewermeasurement","No API/network needed after installation","Fresh regenerated artifacts require newvisualattestation","Allcases syntheticdevelopment, notmanufacturingapproval"]}
write_json(destination/"replay-manifest.json",manifest)
print({"cases":len(selected),"changes":changes})
