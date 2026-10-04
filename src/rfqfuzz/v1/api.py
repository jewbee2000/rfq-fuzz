"""Stable local workflow entry points; heavy native imports remain lazy."""
def generate(destination,seed=42):
    from .mutations import generate_suite
    return generate_suite(destination,seed)

def validate(suite,destination,attestation=None,parser_timeout=60):
    from .validation import validate_suite
    return validate_suite(suite,destination,attestation,parser_timeout)

def export(public,destination,parser_timeout=20):
    from .adapters import export_review
    return export_review(public,destination,parser_timeout)

def import_results(response,public,oracle,destination,adjudication=None):
    from .scoring import import_results as implementation
    return implementation(response,public,oracle,destination,adjudication)

def compare(before,after):
    from .scoring import compare as implementation
    return implementation(before,after)

def report(runs,oracle,public,destination):
    from .reporting import make_report
    return make_report(runs,oracle,public,destination)

def demo(assets,destination,parser_timeout=60,audit_timeout=20):
    """Reopen frozen audited bytes, import retained responses, compare offline.

    Responses are actual public-template-reference output and an explicit
    injected regression. Replay is infrastructure evidence, not a fresh review.
    """
    from pathlib import Path
    import shutil
    from .contracts import load_json,sha256,require,write_json
    from .scoring import compare as compare_runs
    assets=Path(assets).resolve();destination=Path(destination).resolve()
    require(not destination.exists(),"demo destination exists; choose a fresh directory")
    for value in (parser_timeout,audit_timeout):require(type(value) in (int,float) and 0 < value <=300,"parser timeout outside configured bounds (0,300]")
    manifest=load_json(assets/"replay-manifest.json")
    for relative,want in manifest["files"].items():
        source=(assets/relative).resolve()
        require(source.is_relative_to(assets),"unsafe replay asset path")
        require(source.is_file() and sha256(source)==want,"replay asset hash mismatch: "+relative)
    shutil.copytree(assets,destination/"inputs")
    inputs=destination/"inputs";suite=inputs/"suite";public=suite/"public"
    observed=validate(suite,destination/"validation",inputs/"attestation.json",parser_timeout)
    require(observed["status"]=="valid","consumer final-artifact validation failed")
    oracle=destination/"validation/oracle.json"
    export(public,destination/"review-bundle",audit_timeout)
    before=import_results(inputs/"reference.json",public,oracle,destination/"before")
    after=import_results(inputs/"injected.json",public,oracle,destination/"after")
    require("score" in before and "score" in after,"consumer response import failed")
    changed=compare_runs(before,after)
    require(sorted((c["before"],c["after"]) for c in changed)==sorted([("detected","silent_miss"),("correct_clear","false_alert")]),"consumer changed-outcome diagnosis differs")
    report([destination/"before/run.json",destination/"after/run.json"],oracle,public,destination/"report")
    result={"status":"passed","cases":len(observed["cases"]),"changes":changed,"report":str(destination/"report/index.html"),"tracks":after["score"]["tracks"],"provenance":manifest["provenance"],"limitations":manifest["limitations"],"resource_limits":{"native_parser_seconds":parser_timeout,"document_audit_seconds":audit_timeout}}
    write_json(destination/"demo-result.json",result)
    return result
