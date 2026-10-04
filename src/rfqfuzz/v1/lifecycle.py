"""Append-only attempts and a recovery plan; incomplete attempts are observable."""
from pathlib import Path
from .contracts import load_json,read_packet,sha256,require,write_json
from .adapters import check_binding

def resume_plan(public_root, attempt_paths):
    packets={p.name:read_packet(p) for p in Path(public_root).iterdir()}
    latest={};attempts=[]
    for path in attempt_paths:
        path=Path(path)
        if not path.is_file():
            attempts.append({"path":str(path),"status":"interrupted","reason":"attempt record absent; raw files may be retained"});continue
        record=load_json(path)
        attempts.append({"path":str(path),"status":record["status"],"reason":record.get("reason")})
        if "response" in record:
            check_binding(record["response"],public_root)
            latest.update({row["case_id"]:row for row in record["response"]["results"]})
    pending=[]
    for cid,p in packets.items():
        row=latest.get(cid)
        required=set().union(*(set(o["required_modalities"]) for o in p["obligations"]))
        if row is None or row["status"]!="completed" or not required<=set(row["reviewed_modalities"]) or not {o["id"] for o in p["obligations"]}<=set(row["reviewed_obligations"]):pending.append(cid)
    return {"pending_cases":pending,"latest_results":list(latest.values()),"attempts":attempts,"policy":"New attempt directories; no prior raw output overwritten"}
