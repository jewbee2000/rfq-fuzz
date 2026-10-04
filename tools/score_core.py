"""Score actual template output, injected changes and degenerate diagnostics."""
import copy
from collections import Counter
from pathlib import Path
from rfqfuzz.v1.contracts import load_json,read_packet,sha256,write_json
from rfqfuzz.v1.scoring import import_results,score,compare
from rfqfuzz.v1.reporting import make_report,audit_report

public=Path("evidence/M2/core-suite/public");oraclepath=Path("evidence/M4/core-validated/oracle.json")
oracle=load_json(oraclepath,limit=32_000_000)
before=import_results("evidence/M3/reference-core/review.json",public,oraclepath,"evidence/M4/core-reference-run")
after=import_results("evidence/M3/reference-injected.json",public,oraclepath,"evidence/M4/core-injected-run")
changes=compare(before,after)
write_json("evidence/M4/core-comparison.json",changes)
packets={p.name:read_packet(p) for p in public.iterdir()}
baselines={}
for label,conclusion in [("always_flag","contradiction"),("always_clear","supported_clear"),("always_abstain","missing_information")]:
    response={"schema_version":"1.0","reviewer":{"name":label,"version":"1.0-diagnostic","configuration":"Degenerate scorer diagnostic using oracle witnesses to isolate policy failure; not independent reviewer performance"},"results":[]}
    for case in oracle["cases"]:
        if case["status"]!="valid":continue
        items=[{"id":e["obligation_id"],"obligation_id":e["obligation_id"],"category":e["category"],"conclusion":conclusion,"feature_id":e["feature_id"],"evidence":copy.deepcopy(e["evidence"]),"rationale":"Intentionally degenerate diagnostic constant conclusion"} for e in case["expectations"]]
        packet=packets[case["case_id"]]
        response["results"].append({"case_id":case["case_id"],"packet_sha256":case["packet_sha256"],"status":"completed","reviewed_modalities":["context","step","pdf"],"reviewed_obligations":[o["id"] for o in packet["obligations"]],"findings":items if conclusion=="contradiction" else [],"assertions":[] if conclusion=="contradiction" else items,"runtime_seconds":None,"raw_ref":None,"reason":None})
    result=score(response,oracle,packets)
    write_json(f"evidence/M4/baselines/{label}-response.json",response)
    write_json(f"evidence/M4/baselines/{label}-score.json",result)
    baselines[label]=result["tracks"]
summary={"oracle_sha256":sha256(oraclepath),"valid_cases":oracle["counts"],"case_family_counts":dict(Counter(p["family"] for p in packets.values())),"expectations":dict(Counter((e["track"]+":"+e["conclusion"]) for c in oracle["cases"] for e in c["expectations"])),"reference_tracks":before["score"]["tracks"],"reference_unadjudicated":len(before["score"]["unadjudicated"]),"injected_changes":changes,"baselines":baselines,"partitions":{"development":145,"heldout":0,"transfer_pending_separate":1},"limits":["Allcorelayoutsdevelopment","Publicreference sharesartifactreaders withvalidator; notexternalcompetence","Baselinesuseoraclewitnesses only as evaluator diagnostics","Seededdefectsnotphysicalindustrialproof"]}
write_json("evidence/M4/corpus-summary.json",summary)
make_report(["evidence/M4/core-reference-run/run.json","evidence/M4/core-injected-run/run.json"],oraclepath,public,"evidence/M4/core-report")
write_json("evidence/M4/core-report-audit.json",audit_report("evidence/M4/core-report/index.html"))
print(summary)
