"""Escaped offline evidence report with per-track counts and exact sources."""
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
from .contracts import load_json, require, write_json,sha256,digest,read_packet
from .scoring import compare

def make_report(run_paths, oracle_path, public_root, out):
    out=Path(out)
    require(not out.exists(), "report exists; preserve prior evidence")
    runs=[load_json(p) for p in run_paths]
    require(bool(runs), "at least one run required")
    # Reports must display the exact scored artifacts/oracle, even for one run.
    public_root=Path(public_root)
    paths=sorted(public_root.glob("*/packet.json"))
    require(bool(paths),"report public suite is empty")
    packets=[read_packet(p.parent) for p in paths]
    bindings={"oracle_sha256":sha256(oracle_path),"suite_sha256":digest([(p.parent.name,sha256(p)) for p in paths]),"profile_sha256":digest([packet["profile"] for packet in packets])}
    for run,path in zip(runs,run_paths):
        for key,value in bindings.items():
            require(run["manifest"][key]==value,"report source binding mismatch: "+key)
        raw=Path(path).parent/"raw-review.json"
        require(raw.is_file() and sha256(raw)==run["manifest"]["raw_sha256"],"report source binding mismatch: raw_sha256")
    changes=[{"before_reviewer":runs[0]["reviewer"],"after_reviewer":run["reviewer"],"changes":compare(runs[0],run)} for run in runs[1:]]
    oracle=load_json(oracle_path,limit=32_000_000)
    out.mkdir(parents=True)
    esc=lambda value:escape(str(value),quote=True)
    link=lambda path:esc(Path(os.path.relpath(Path(path).resolve(),out.resolve())).as_posix())
    chunks=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>RFQFuzz review regression</title><style>body{margin:0;background:#f4f6f8;color:#203044;font:16px/1.5 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:30px}h1{font-size:36px}h2{margin-top:32px}section,article{background:white;border:1px solid #cbd4df;border-radius:8px;padding:24px;margin:24px 0}a{color:#125c87}table{border-collapse:collapse;width:100%}th,td{border:1px solid #cbd4df;padding:10px;text-align:left;vertical-align:top}pre{background:#eef2f6;padding:16px;overflow:auto;font-size:13px}img{max-width:100%;height:auto}.notice{background:#fff0d2;padding:20px;border-left:5px solid #b77219}.change{font-size:18px}.muted{color:#5b6876}summary{cursor:pointer;padding:10px}</style></head><body><main><h1>RFQFuzz · review regression</h1><p>Finite CNC RFQ obligations, independently checked exported artifacts and explicit review coverage.</p><p class="notice">This is a synthetic regression toolkit. It does not approve a part for manufacture or establish general industrial competence. Deliberately injected reviewer changes are labeled in their reviewer configuration; genuine external observations remain separate.</p>']
    chunks.append('<h2>What changed</h2>')
    for group in changes:
        chunks.append(f'<article><h3>{esc(group["before_reviewer"]["name"])} → {esc(group["after_reviewer"]["name"])}</h3><p>{esc(group["after_reviewer"]["configuration"])}</p><ul>')
        for change in group["changes"]:
            anchor=f'{change["case_id"]}-{change["obligation_id"]}'
            chunks.append(f'<li class="change"><a href="#{esc(anchor)}">{esc(change["case_id"])} · {esc(change["obligation_id"])}</a>: {esc(change["before"])} → {esc(change["after"])}</li>')
        chunks.append('</ul></article>')
    chunks.append('<h2>Separate tracks and denominators</h2>')
    for run,path in zip(runs,run_paths):
        chunks.append(f'<article><h3>{esc(run["reviewer"]["name"])} · {esc(run["reviewer"]["version"])}</h3><p>{esc(run["reviewer"]["configuration"])}</p><table><tr><th>Track</th><th>Detection</th><th>Named clean alerts</th><th>Explicit false clears</th><th>Coverage</th><th>Appropriate abstention</th><th>Failures / unsupported</th></tr>')
        for track,n in run["score"]["tracks"].items():
            ratio=lambda name:esc(f'{n["rates"][name]["numerator"]}/{n["rates"][name]["denominator"]}')
            chunks.append(f'<tr><th>{esc(track)}</th><td>{ratio("recall")}</td><td>{ratio("named_clean_false_alert")}</td><td>{ratio("explicit_false_clear")}</td><td>{ratio("coverage")}</td><td>{ratio("appropriate_abstention")}</td><td>{esc(n["execution_failures"])} / {esc(n["unsupported"])}</td></tr>')
        chunks.append(f'</table><p>Unadjudicated findings: {len(run["score"]["unadjudicated"])}. Invalid fixtures: {esc(run["score"]["invalid_rate"])}. Precision finalized for finite matching: {esc(run["score"]["precision_finalized"])}. No composite score.</p><p><a href="{link(path)}">Run manifest and full counts</a> · <a href="{link(Path(path).parent/"raw-review.json")}">Original raw response</a></p></article>')
    chunks.append('<h2>Inspect expected and actual evidence</h2>')
    for case in oracle["cases"]:
        cid=case["case_id"]
        folder=Path(public_root)/cid
        if case["status"]!="valid":
            chunks.append(f'<section><h3>{esc(cid)} · {esc(case["status"])}</h3><p>Excluded: {esc(case["reasons"])}</p></section>');continue
        packet=read_packet(folder)
        chunks.append(f'<section><h3>{esc(cid)} · {esc(packet["part_id"])}</h3><p><a href="{link(folder/"drawing.pdf")}">Actual PDF page</a> · <a href="{link(folder/"drawing.png")}">Supplied rendered PNG</a> · <a href="{link(folder/"part.step")}">Exported STEP</a> · <a href="{link(folder/"packet.json")}">Public engineering contract</a></p><details><summary>Drawing, reimported geometry and public premises</summary><img src="{link(folder/"drawing.png")}" alt="Supplied complete engineering drawing"><pre>{esc(json.dumps(case["measurements"],indent=2))}</pre><pre>{esc(json.dumps(packet["authority"],indent=2))}</pre><pre>{esc(json.dumps(packet["manufacturing"],indent=2))}</pre></details>')
        for expected in case["expectations"]:
            oid=expected["obligation_id"]
            chunks.append(f'<article id="{esc(cid+"-"+oid)}"><h4>{esc(oid)} · {esc(expected["track"])}</h4><p>Validated expected conclusion: <b>{esc(expected["conclusion"])}</b>; location {esc(expected["feature_id"])}. Root cause {esc(expected["root_cause"])}.</p><pre>{esc(json.dumps(expected["evidence"],indent=2))}</pre>')
            if expected["rule_id"]:
                cards=[r for r in packet["profile"]["rules"] if r["id"]==expected["rule_id"]]
                chunks.append(f'<details><summary>Selected profile and rule provenance</summary><pre>{esc(json.dumps(cards,indent=2))}</pre></details>')
            else:
                chunks.append('<p class="muted">Package rule: finite public authority/release contract, schema 1.0; project-selected obligation. This is not an industry standard completeness assessment.</p>')
            for run in runs:
                actual=next((r for r in run["score"]["rows"] if r["case_id"]==cid and r["obligation_id"]==oid),None)
                chunks.append(f'<p><b>{esc(run["reviewer"]["name"])}</b>: {esc(actual["outcome"] if actual else "missing")} · actual {esc(actual["actual"] if actual else None)} · execution {esc(actual["status"] if actual else "missing")}</p><details><summary>Original grounded finding</summary><pre>{esc(json.dumps(actual,indent=2))}</pre></details>')
            chunks.append('</article>')
        chunks.append('</section>')
    chunks.append(f'<h2>Limits and replay</h2><p>Same-user blinding is procedural. Independent modules share OCCT; analytic checks and corruption controls supplement it. Canonical quotation matching is conservative; free prose requires explicit adjudication. Only named finite obligations are scored. Expected answers and operators shown here are private evaluation outputs, never reviewer inputs.</p><p><a href="{link(oracle_path)}">Complete independent oracle and retained exclusions</a></p><pre>{esc(json.dumps(runs[0]["manifest"],indent=2))}</pre></main></body></html>')
    (out/"index.html").write_text("".join(chunks),encoding="utf-8")
    record={"schema_version":"1.0","comparisons":changes,"manifest":runs[0]["manifest"],"scope":"Finite synthetic obligations; no industrial competence or manufacturing approval"}
    write_json(out/"comparison.json",record)
    write_json(out/"source-audit.json",audit_report(out/"index.html"))
    return record

def audit_report(path):
    path=Path(path).resolve()
    class Reader(HTMLParser):
        def __init__(self):super().__init__();self.links=[];self.unsafe=[];self.ids=set()
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag in {"script","iframe","object","embed"}:self.unsafe.append(tag)
            if any(k.lower().startswith("on") for k in attrs):self.unsafe.append("event handler")
            if "id" in attrs:self.ids.add(attrs["id"])
            for key in ("href","src"):
                if key in attrs:self.links.append(attrs[key])
    reader=Reader();reader.feed(path.read_text(encoding="utf-8"))
    require(not reader.unsafe,"unsafe HTML element")
    for url in reader.links:
        if url.startswith("#"):require(url[1:] in reader.ids,"missing report anchor")
        else:
            require(not re_remote(url),"report remote or executable URL")
            require((path.parent/url).is_file(),f"missing report source: {url}")
    return {"status":"passed","local_links":len(reader.links),"unsafe_elements":0}

def re_remote(url):
    return ":" in url or url.startswith("//")
