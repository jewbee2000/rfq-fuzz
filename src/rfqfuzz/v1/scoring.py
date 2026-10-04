"""Finite, evidence-bound per-obligation scoring; no manufacturing approval score."""
from __future__ import annotations
import copy
import platform
from pathlib import Path
import re
from .contracts import digest, load_json, sha256, write_json, require, validate_oracle, validate_review, validate_manifest
from .adapters import import_response

ISSUES = {"contradiction", "advisory", "profile_exclusion"}

def normalized(text):
    return " ".join(str(text).lower().replace("±", "+/-").split())

def matches(item, expected):
    if any(item[k] != expected[k] for k in ("obligation_id", "category", "feature_id")):
        return False
    # A quoted canonical source line or measured witness must actually appear;
    # numbers alone are insufficient. This intentionally conservative structured
    # path does not infer semantic equivalence from arbitrary free prose.
    for witness in expected["evidence"]:
        hits = [w for w in item["evidence"] if w["artifact"] == witness["artifact"]
                and normalized(witness["quote"]) in normalized(w["quote"])
                and ("region" not in witness or w.get("region") == witness["region"])]
        if not hits:
            return False
    return True

def score(response, oracle, packets=None):
    validate_review(response)
    cases = oracle["cases"]
    for case in cases: validate_oracle(case)
    lookup = {row["case_id"]:row for row in response["results"]}
    require(not (lookup.keys() - {c["case_id"] for c in cases}), "response outside frozen suite")
    tracks = {track:{key:0 for key in ("applicable", "issues", "clean", "underdetermined", "detected", "false_alerts", "explicit_false_clears", "silent_misses", "correct_clear", "appropriate_abstentions", "abstentions", "covered", "execution_failures", "unsupported", "unasserted_clean", "reasoning_errors")} for track in ("package_consistency", "cnc_advisory")}
    rows, unadjudicated, operators, invalid, duplicates = [], [], {}, [], []
    for case in cases:
        if case["status"] != "valid":
            invalid.append({"case_id":case["case_id"],"status":case["status"],"reasons":case["reasons"]})
            continue
        actual = lookup.get(case["case_id"])
        if actual:
            require(actual["packet_sha256"] == case["packet_sha256"], "response bound to different packet bytes")
        consumed = set()
        items = (actual["findings"] + actual["assertions"]) if actual else []
        for expected in case["expectations"]:
            n = tracks[expected["track"]]
            want = expected["conclusion"]
            row = {"case_id":case["case_id"],"obligation_id":expected["obligation_id"],"track":expected["track"],"operator":expected["operator"],"expected":want,"actual":None,"status":actual["status"] if actual else "missing","outcome":"uncovered","matched_finding":None}
            n["applicable"] += 1
            if want in ISSUES: n["issues"] += 1
            elif want == "supported_clear": n["clean"] += 1
            elif want == "missing_information": n["underdetermined"] += 1
            op = operators.setdefault(expected["operator"], {"issues":0,"detected":0})
            if want in ISSUES: op["issues"] += 1
            required = {"context"}
            if packets:
                obligations = packets[case["case_id"]]["obligations"]
                required = set(next(o["required_modalities"] for o in obligations if o["id"] == expected["obligation_id"]))
            if actual is None or actual["status"] in {"error", "timeout"}:
                row["outcome"] = "reviewer_failure"; n["execution_failures"] += 1
            elif actual["status"] == "unsupported":
                row["outcome"] = "unsupported"; n["unsupported"] += 1
            elif expected["obligation_id"] not in actual["reviewed_obligations"] or not required <= set(actual["reviewed_modalities"]):
                row["outcome"] = "uncovered"
            else:
                n["covered"] += 1
                hits = [(i,item) for i,item in enumerate(items) if i not in consumed and matches(item,expected)]
                if hits:
                    i,item = hits[0]
                    # Consume all duplicates of the same grounded root obligation;
                    # the first counts once, no duplicate recall or false alert.
                    consumed.update(i for i,_ in hits)
                    duplicates.extend({"case_id":case["case_id"],"obligation_id":expected["obligation_id"],"finding":item} for _,item in hits[1:])
                    got = item["conclusion"]
                    row.update(actual=got,matched_finding=item)
                    if got == want:
                        if got in ISSUES:
                            row["outcome"]="detected";n["detected"]+=1;op["detected"]+=1
                        elif got == "supported_clear":
                            row["outcome"]="correct_clear";n["correct_clear"]+=1
                        elif got == "missing_information":
                            row["outcome"]="appropriate_abstention";n["appropriate_abstentions"]+=1;n["abstentions"]+=1
                        else:
                            row["outcome"]="unsupported";n["unsupported"]+=1
                    elif got in ISSUES and want == "supported_clear":
                        row["outcome"]="false_alert";n["false_alerts"]+=1
                    elif got == "supported_clear" and want in ISSUES:
                        row["outcome"]="explicit_false_clear";n["explicit_false_clears"]+=1
                    elif got == "missing_information":
                        row["outcome"]="inappropriate_abstention";n["abstentions"]+=1
                    elif got == "unsupported":
                        row["outcome"]="unsupported";n["unsupported"]+=1
                    else:
                        row["outcome"]="reasoning_error";n["reasoning_errors"]+=1
                else:
                    row["outcome"]="silent_miss" if want in ISSUES else "unasserted_clean" if want == "supported_clear" else "unasserted_unknown"
                    if want in ISSUES:n["silent_misses"]+=1
                    elif want == "supported_clear":n["unasserted_clean"]+=1
            rows.append(row)
        for i,item in enumerate(items):
            if i not in consumed:
                unadjudicated.append({"case_id":case["case_id"],"finding":item,"status":"unadjudicated"})
    for n in tracks.values():
        n["rates"] = {"recall":{"numerator":n["detected"],"denominator":n["issues"]},"named_clean_false_alert":{"numerator":n["false_alerts"],"denominator":n["clean"]},"explicit_false_clear":{"numerator":n["explicit_false_clears"],"denominator":n["issues"]},"coverage":{"numerator":n["covered"],"denominator":n["applicable"]},"appropriate_abstention":{"numerator":n["appropriate_abstentions"],"denominator":n["underdetermined"]}}
    return {"tracks":tracks,"operators":operators,"rows":rows,"invalid_fixtures":invalid,"invalid_rate":{"numerator":len(invalid),"denominator":len(cases)},"unadjudicated":unadjudicated,"suppressed_duplicates":duplicates,"precision_finalized":not unadjudicated,"precision_note":"Finite obligation matching only; no claim about all drawing content or industrial competence"}

def manifest(public_root, oracle_path, response_path, adapter_version="manual-1.0", seed=42):
    packet_paths = sorted(Path(public_root).glob("*/packet.json"))
    return validate_manifest({"schema_version":"1.0","suite_sha256":digest([(p.parent.name,sha256(p)) for p in packet_paths]),"oracle_sha256":sha256(oracle_path),"profile_sha256":digest([load_json(p)["profile"] for p in packet_paths]),"adapter_version":adapter_version,"seed":seed,"environment":{"python":platform.python_version(),"platform":platform.platform()},"raw_sha256":sha256(response_path),"limitations":["Finite synthetic obligations","Shared OCCT kernel","Conservative canonical source quotation matching"],"failures":[]})

def apply_adjudications(response, adjudication, raw_hash, oracle_hash):
    require(adjudication["raw_sha256"]==raw_hash and adjudication["oracle_sha256"]==oracle_hash, "stale adjudication")
    value=copy.deepcopy(response)
    for decision in adjudication["decisions"]:
        require(bool(decision["reason"].strip()), "adjudication requires reason")
        hits=[item for row in value["results"] if row["case_id"]==decision["case_id"] for item in row["findings"]+row["assertions"] if digest(item)==decision["finding_sha256"]]
        require(len(hits)==1, "adjudication must identify one raw finding")
        require(hits[0]["category"]==decision["original_category"], "category binding changed")
        hits[0]["category"]=decision["mapped_category"]
    return validate_review(value)

def import_results(response_path, public_root, oracle_path, out, adjudication_path=None):
    record=import_response(response_path, public_root, out)
    if record["status"] != "imported": return record
    from .contracts import read_packet
    oracle=load_json(oracle_path,limit=32_000_000)
    response=record["response"]
    adjudication=None
    if adjudication_path:
        adjudication=load_json(adjudication_path)
        response=apply_adjudications(response,adjudication,sha256(response_path),sha256(oracle_path))
    packets={p.name:read_packet(p) for p in Path(public_root).iterdir()}
    m=manifest(public_root,oracle_path,response_path)
    result={"schema_version":"1.0","manifest":m,"reviewer":response["reviewer"],"score":score(response,oracle,packets),"adjudication":adjudication}
    write_json(Path(out)/"run.json",result)
    return result

def compare(a,b):
    for key in ("suite_sha256","oracle_sha256","profile_sha256"):
        require(a["manifest"][key]==b["manifest"][key], f"incompatible comparison: {key}")
    key=lambda r:(r["case_id"],r["obligation_id"])
    old={key(row):row for row in a["score"]["rows"]};new={key(row):row for row in b["score"]["rows"]}
    require(old.keys()==new.keys(), "incompatible obligation coverage")
    return [{"case_id":k[0],"obligation_id":k[1],"track":new[k]["track"],"before":old[k]["outcome"],"after":new[k]["outcome"]} for k in old if old[k]["outcome"]!=new[k]["outcome"]]
