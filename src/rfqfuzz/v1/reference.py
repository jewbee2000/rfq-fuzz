"""Public-only template reference reviewer; not an independent competence result.

It shares observed STEP/PDF readers with validation but has its own conclusions
and never receives expected answers, mutation records or suite-private paths.
"""
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from .contracts import read_packet,sha256,write_json,load_json,require
from .profiles import evaluate
from .adapters import terminate_tree

def num(value):return f"{round(value,6):.6f}".rstrip("0").rstrip(".")
def context(p,*keys):
    values={}
    for key in keys:
        value=p
        for child in key.split("."):value=value[child]
        values[key]=value
    return {"artifact":"packet.json","quote":json.dumps(values,sort_keys=True,separators=(",",":"),ensure_ascii=False)}
def ev(artifact,quote):return {"artifact":artifact,"quote":quote}
def first(d,key):return next(iter(d["annotations"].get(key,[])),None)
def val(d,key):
    text=first(d,key)
    return text.split(" = ",1)[1] if text else None
def geo(g,feature,*pairs):return ev("part.step",feature+" "+"; ".join(name+"="+num(g[key]) for name,key in pairs))
def envelope(g):return ev("part.step","document envelope_mm=["+", ".join(num(x) for x in g["envelope_mm"])+"]")

def decisions(p,g,d):
    """Read the finite public obligations; no private operator/variant inputs."""
    result=[];unit=val(d,"UNITS");scale=25.4 if unit=="in" else 1
    env=val(d,"ENVELOPE")
    unit_bad=False
    if env:
        values=re.fullmatch(r"([0-9.]+) x ([0-9.]+) x ([0-9.]+) (mm|in)",env)
        require(values is not None,"reference cannot parse envelope")
        unit_bad=any(abs(float(values[i+1])*scale-g["envelope_mm"][i])>(.001301 if unit=="in" else .005011) for i in range(3))
    m=p["manufacturing"];a=p["authority"]
    aliases={"6061-T6":"6061-T6","AL6061-T6":"6061-T6","AL 6061-T6":"6061-T6","7075-T6":"7075-T6","304 STAINLESS":"304 stainless","ABS":"ABS","DELRIN":"Delrin","POM":"Delrin"}
    declared=[aliases.get(text.split(" = ",1)[1].upper()) for text in d["annotations"].get("MATERIAL",[])]
    candidates=[aliases.get(m["material"].upper())]+declared
    unresolved=(None in candidates or len(set(candidates))!=1) if a["material_precedence"]=="equal" else (None in declared or len(set(declared))!=1) if a["material_precedence"]=="drawing" else False
    for obligation in p["obligations"]:
        category=obligation["category"];conclusion="supported_clear";evidence=[]
        if category=="unit_consistency":
            conclusion="contradiction" if unit_bad else "supported_clear" if env or a["dimensions"]=="step" else "missing_information"
            evidence=[ev("drawing.pdf",first(d,"UNITS")),context(p,"units")]
            if env:evidence += [ev("drawing.pdf",first(d,"ENVELOPE")),envelope(g)]
        elif category=="diameter_consistency":
            if unit_bad:continue # one unit declaration root cause, not duplicate symptoms
            evidence=[geo(g,"H1",("diameter_mm","bore_diameter_mm"),("count","h1_count")),context(p,"authority.dimensions","manufacturing.model_stage","manufacturing.drawing_stage","manufacturing.transition")]
            text=val(d,"H1 DIAMETER")
            if text:
                evidence.append(ev("drawing.pdf",first(d,"H1 DIAMETER")))
                parts=re.fullmatch(r"([0-9.]+) \+/- ([0-9.]+) (mm|in)( REF)?",text)
                require(parts is not None,"reference cannot parse bore interval")
                nominal=float(parts[1])*scale;tolerance=float(parts[2])*scale
            if a["dimensions"]=="step" or text and parts[4]:pass
            elif not text:conclusion="missing_information"
            elif m["model_stage"]!=m["drawing_stage"]:
                transition=m["transition"]
                if transition is None:conclusion="missing_information"
                elif m["model_stage"]=="intermediate" and m["drawing_stage"]=="finished" and transition.get("operation")=="ream" and transition.get("feature_id")=="H1" and transition.get("from_stage")=="intermediate" and transition.get("to_stage")=="finished" and transition.get("target") in {"drawing bore callout","drawing H1 diameter callout"} and first(d,"TRANSITION"):
                    evidence.append(ev("drawing.pdf",first(d,"TRANSITION")))
                    conclusion="supported_clear" if nominal-tolerance>g["bore_diameter_mm"] else "contradiction"
                else:conclusion="unsupported"
            else:conclusion="supported_clear" if nominal-tolerance-1e-6<=g["bore_diameter_mm"]<=nominal+tolerance+1e-6 else "contradiction"
        elif category=="count_consistency":
            evidence=[geo(g,"H1",("count","h1_count")),context(p,"features","authority.dimensions")]
            count=val(d,"H1 COUNT")
            if count:
                evidence.append(ev("drawing.pdf",first(d,"H1 COUNT")))
                conclusion="supported_clear" if int(count)==g["h1_count"] else "contradiction"
            elif a["dimensions"]!="step":conclusion="missing_information"
        elif category=="material_consistency":
            declarations=d["annotations"].get("MATERIAL",[])
            evidence=[ev("drawing.pdf",text) for text in declarations]+[context(p,"manufacturing.material","authority.material_precedence")]
            values=[aliases.get(text.split(" = ",1)[1].upper()) for text in declarations]
            if a["material_precedence"]=="equal":
                values.append(aliases.get(m["material"].upper()))
                conclusion="missing_information" if None in values else "contradiction" if len(set(values))>1 else "supported_clear"
            elif a["material_precedence"]=="drawing" and len(set(values))>1:conclusion="contradiction"
        elif category=="required_representation":
            evidence=[context(p,"requirements")]
            for required in p["requirements"]:
                if required["representation"] in {"step","either"} and "geometry" in required["description"].lower():
                    evidence.append(ev("part.step",f"document solid_count={g['solid_count']}"));continue
                text=first(d,"SURFACE ROUGHNESS")
                if not text and "SURFACE FINISH" in required["description"]:text=first(d,"SURFACE FINISH")
                if text:evidence.append(ev("drawing.pdf",text))
                else:conclusion="contradiction"
        elif category=="release_association":
            release=p["release_association"]
            evidence=[ev("drawing.pdf",first(d,"DRAWING ID")),ev("drawing.pdf",first(d,"DRAWING REV")),ev("part.step",g["product_identity"]),context(p,"release_association")]
            conclusion="supported_clear" if val(d,"DRAWING ID")==release["drawing_id"]==release["model_id"] and [release["model_revision"],val(d,"DRAWING REV")] in release["permitted_pairs"] else "contradiction"
        else:
            rule={"wall_thickness":"A01","bore_ratio":"A02","setup_envelope":"A03","finish_stage":"A04"}[category]
            measures={key:round(g[key],6) if type(g[key]) in (float,int) else [round(x,6) for x in g[key]] for key in ("wall_mm","bore_depth_mm","bore_diameter_mm","envelope_mm") if key in g}
            effective=m
            if a["material_precedence"]=="drawing" and not unresolved:
                material=declared[0];card=next(card for card in p["profile"]["rules"] if card["id"]==rule)
                effective=dict(m,material=material,material_class=card["applicability"].get("materials",{}).get(material))
            conclusion="missing_information" if unresolved else evaluate(p["profile"],rule,measures,effective,p["setup"])["conclusion"]
            evidence=[context(p,"profile","manufacturing","setup")]
            if rule=="A01":evidence.append(geo(g,"W1",("wall_mm","wall_mm")))
            elif rule=="A02":evidence.append(geo(g,"H1",("depth_mm","bore_depth_mm"),("diameter_mm","bore_diameter_mm")))
            elif rule=="A03":evidence.append(envelope(g))
            else:evidence += [ev("drawing.pdf",first(d,"FINISH")),ev("drawing.pdf",first(d,"TOLERANCE STAGE"))]
        result.append({"id":obligation["id"],"obligation_id":obligation["id"],"category":category,"feature_id":obligation["feature_id"],"conclusion":conclusion,"evidence":evidence,"rationale":"Finite public-authority rule applied to observed final artifacts; template reference only, no general manufacturing conclusion."})
    return result

def review_public(public_root,out,timeout=20):
    out=Path(out).resolve();require(not out.exists(),"reference output exists")
    out.mkdir(parents=True);rows=[]
    for folder in sorted(Path(public_root).resolve().iterdir()):
        p=read_packet(folder);cid=p["case_id"];target=out/cid;target.mkdir()
        start=time.monotonic()
        stdout=stderr=b""
        env=os.environ.copy();env["PYTHONPATH"]=str(Path(__file__).resolve().parents[2])+os.pathsep+env.get("PYTHONPATH","")
        proc=subprocess.Popen([sys.executable,"-m","rfqfuzz.v1.reference","--probe",str(folder),str(target)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
        try:
            stdout,stderr=proc.communicate(timeout=timeout)
            require(proc.returncode==0,"reference artifact reader failed")
            observed=load_json(target/"observed.json")
            items=decisions(p,observed["geometry"],observed["drawing"])
            row={"case_id":cid,"packet_sha256":sha256(folder/"packet.json"),"status":"completed","reviewed_modalities":["step","pdf","context"],"reviewed_obligations":[o["id"] for o in p["obligations"]],"findings":[i for i in items if i["conclusion"] in {"contradiction","advisory","profile_exclusion"}],"assertions":[i for i in items if i["conclusion"] not in {"contradiction","advisory","profile_exclusion"}],"runtime_seconds":time.monotonic()-start,"raw_ref":str(target/"observed.json"),"reason":None}
        except subprocess.TimeoutExpired:
            terminate_tree(proc);stdout,stderr=proc.communicate();row={"case_id":cid,"packet_sha256":sha256(folder/"packet.json"),"status":"timeout","reviewed_modalities":[],"reviewed_obligations":[],"findings":[],"assertions":[],"runtime_seconds":time.monotonic()-start,"raw_ref":None,"reason":"reference parser timeout"}
        except (ValueError,KeyError,TypeError,OSError) as error:
            row={"case_id":cid,"packet_sha256":sha256(folder/"packet.json"),"status":"error","reviewed_modalities":[],"reviewed_obligations":[],"findings":[],"assertions":[],"runtime_seconds":time.monotonic()-start,"raw_ref":None,"reason":str(error)}
        (target/"reader-stdout.bin").write_bytes(stdout);(target/"reader-stderr.bin").write_bytes(stderr)
        write_json(target/"review-row.json",row);rows.append(row)
    response={"schema_version":"1.0","reviewer":{"name":"RFQFuzz public-only template reference","version":"1.0","configuration":"Shares observed readers/OCCT with validator; own public rule logic; not independent reviewer performance"},"results":rows}
    write_json(out/"review.json",response);return response

def injected_regression(response):
    value=copy.deepcopy(response)
    value["reviewer"].update(name="DELIBERATELY INJECTED reference regression",version="1.0-injected",configuration="Deliberately injected one detected-to-silent-miss and one correct-clear-to-false-alert. Not a naturally discovered external failure.")
    missed=alerted=False
    for row in value["results"]:
        if not missed and any(item["conclusion"]=="contradiction" for item in row["findings"]):
            item=next(item for item in row["findings"] if item["conclusion"]=="contradiction");row["findings"].remove(item);missed=True
        elif not alerted and any(item["conclusion"]=="supported_clear" and item["category"]=="diameter_consistency" for item in row["assertions"]):
            item=next(item for item in row["assertions"] if item["conclusion"]=="supported_clear" and item["category"]=="diameter_consistency");row["assertions"].remove(item);item["conclusion"]="contradiction";item["rationale"]="DELIBERATE INJECTION: ignore public stage/authority.";row["findings"].append(item);alerted=True
        if missed and alerted:break
    require(missed and alerted,"suite lacks appropriate injected regression controls")
    return value

if __name__=="__main__":
    require(len(sys.argv)==4 and sys.argv[1]=="--probe","internal observed-reader invocation")
    from .validation import measure_step,inspect_drawing
    folder=Path(sys.argv[2]);target=Path(sys.argv[3]);p=read_packet(folder)
    write_json(target/"observed.json",{"geometry":measure_step(folder/"part.step",p["family"],p["features"]),"drawing":inspect_drawing(folder/"drawing.pdf",folder/"drawing.png",target/"drawing")})
