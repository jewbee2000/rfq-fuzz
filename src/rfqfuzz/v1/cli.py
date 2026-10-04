"""Explicit local CLI. Packet text never selects or executes commands."""
import argparse
import json
from pathlib import Path
import sys
from . import api
from .contracts import load_json,write_json

def parser():
    p=argparse.ArgumentParser(prog="rfqfuzz",description="Finite local RFQ reviewer regression; no manufacturing certification")
    sub=p.add_subparsers(dest="action",required=True)
    q=sub.add_parser("generate");q.add_argument("destination");q.add_argument("--seed",type=int,default=42)
    q=sub.add_parser("generate-case");q.add_argument("destination");q.add_argument("--case-id",required=True);q.add_argument("--family",choices=["plate","bore_block","pocket_block"],required=True);q.add_argument("--parameters",help="JSON file with bounded family parameters")
    q=sub.add_parser("validate");q.add_argument("suite");q.add_argument("destination");q.add_argument("--attestation")
    q=sub.add_parser("export-review");q.add_argument("public");q.add_argument("destination")
    q=sub.add_parser("import-results");q.add_argument("response");q.add_argument("public");q.add_argument("oracle");q.add_argument("destination");q.add_argument("--adjudication")
    q=sub.add_parser("compare");q.add_argument("before");q.add_argument("after");q.add_argument("destination")
    q=sub.add_parser("report");q.add_argument("oracle");q.add_argument("public");q.add_argument("destination");q.add_argument("runs",nargs="+")
    q=sub.add_parser("reference");q.add_argument("public");q.add_argument("destination")
    q=sub.add_parser("run-local");q.add_argument("public");q.add_argument("destination");q.add_argument("--timeout",type=float,default=30);q.add_argument("command",nargs=argparse.REMAINDER)
    q=sub.add_parser("resume");q.add_argument("public");q.add_argument("attempts",nargs="*")
    q=sub.add_parser("demo");q.add_argument("assets");q.add_argument("destination")
    return p

def main(argv=None):
    a=parser().parse_args(argv)
    try:
        if a.action=="generate":result=api.generate(a.destination,a.seed)
        elif a.action=="generate-case":
            from .generation import generate_case
            result=generate_case(a.destination,a.case_id,a.family,load_json(a.parameters) if a.parameters else None)
        elif a.action=="validate":
            r=api.validate(a.suite,a.destination,a.attestation)
            result={"status":r["status"],"counts":r["counts"],"oracle":str(Path(a.destination)/"oracle.json")}
        elif a.action=="export-review":result=api.export(a.public,a.destination)
        elif a.action=="import-results":
            r=api.import_results(a.response,a.public,a.oracle,a.destination,a.adjudication)
            result={"status":"scored","tracks":r["score"]["tracks"]} if "score" in r else r
        elif a.action=="compare":
            result=api.compare(load_json(a.before,limit=32_000_000),load_json(a.after,limit=32_000_000));write_json(a.destination,result)
        elif a.action=="report":result=api.report(a.runs,a.oracle,a.public,a.destination)
        elif a.action=="reference":
            from .reference import review_public
            r=review_public(a.public,a.destination);result={"cases":len(r["results"]),"response":str(Path(a.destination)/"review.json"),"limitations":"Public-only template reference shares observed readers with validator; no independent competence claim"}
        elif a.action=="run-local":
            from .adapters import run_local
            command=a.command[1:] if a.command[:1]==["--"] else a.command
            result=run_local(command,a.public,a.destination,a.timeout)
        elif a.action=="resume":
            from .lifecycle import resume_plan
            result=resume_plan(a.public,a.attempts)
        else:result=api.demo(a.assets,a.destination)
        print(json.dumps(result,indent=2,default=str))
        if isinstance(result,dict) and result.get("status") in {"error","timeout","contains_quarantine","unverified"}:return 2
        return 0
    except (ValueError,KeyError,TypeError,OSError,RuntimeError) as error:
        print(json.dumps({"status":"error","reason":f"{type(error).__name__}: {error}"}),file=sys.stderr);return 2

if __name__=="__main__":raise SystemExit(main())
