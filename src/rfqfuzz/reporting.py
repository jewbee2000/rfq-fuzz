"""Offline, escaped, source-linked M0 comparison; no server or remote assets."""
from pathlib import Path
import html
import json
import os
from .contracts import write_json
from .scoring import compare

def make_report(run_paths, oracle_path, public_root, out):
    out = Path(out)
    if out.exists():
        raise ValueError('report output exists; preserve previous comparison')
    runs = [json.loads(Path(p).read_text(encoding='utf-8')) for p in run_paths]
    oracle = json.loads(Path(oracle_path).read_text(encoding='utf-8'))
    out.mkdir(parents=True)
    esc = lambda s: html.escape(str(s), quote=True)
    link = lambda p: Path(os.path.relpath(Path(p).resolve(), out.resolve())).as_posix()
    evidence_link = lambda name: esc(link(Path('evidence/M0') / name))
    headers = ''.join(f'<th>{esc(r["reviewer"]["name"])}<small>{esc(r["reviewer"]["version"])}</small></th>' for r in runs)
    body = []
    for case in oracle['cases']:
        cid = case['case_id']
        source = Path(public_root) / cid
        crop = Path(oracle_path).parent / cid / 'callout.png'
        geometry = case['geometry']
        drawing = case['drawing']['callout']
        cells = []
        for r in runs:
            row = next(x for x in r['score']['rows'] if x['case_id'] == cid)
            cells.append(f'<td class="{esc(row["outcome"])}"><b>{esc(row["outcome"])}</b><br>{esc(row["actual"])}<br><small>Status: {esc(row["status"])}; modalities: {esc(row.get("reviewed_modalities", []))}</small></td>')
        body.append(f'<tr><th><a href="#case-{esc(cid)}">{esc(cid)}</a></th><td>{esc(case["expected_conclusion"])}</td>{"".join(cells)}</tr>')
    summary = []
    for r,p in zip(runs,run_paths):
        n = r['score']['counts']
        summary.append(f'<article><h3>{esc(r["reviewer"]["name"])}</h3><p>{esc(r["reviewer"]["configuration"])}</p><p>Detected {n["detected"]}/{n["defects"]}; false alerts {n["false_alerts"]}/{n["clean"]}; explicit false clears {n["explicit_false_clears"]}/{n["defects"]}; correct named clears {n["correct_clear"]}/{n["clean"]}; coverage {n["covered"]}/{len(oracle["cases"])}; missing information {n["missing_information"]}; failures {n["execution_failures"]}; unsupported {n["unsupported"]}; unadjudicated {len(r["score"]["unadjudicated"])}.</p><p><a href="{esc(link(p))}">Imported run manifest and score</a> · <a href="{esc(link(Path(p).parent / "raw-review.json"))}">Preserved raw review</a></p></article>')
    changes = compare(runs[0], runs[1])
    external_changes = compare(runs[0], runs[2]) if len(runs) > 2 else []
    change_list = ''.join(f'<li><a href="#case-{esc(c["case_id"])}">{esc(c["case_id"])}</a>: {esc(c["before"])} → {esc(c["after"])}</li>' for c in changes)
    sections = []
    for case in oracle['cases']:
        cid = case['case_id']; source = Path(public_root) / cid
        crop = Path(oracle_path).parent / cid / 'callout.png'
        g = case['geometry']; d = case['drawing']['callout']
        observations = []
        for run, path in zip(runs, run_paths):
            raw_path = Path(path).parent / 'raw-review.json'
            if raw_path.is_file():
                raw = json.loads(raw_path.read_text(encoding='utf-8'))
                items = [row for row in raw['results'] if row['case_id'] == cid]
                observations.append(f'<h3>{esc(run["reviewer"]["name"])}</h3><pre>{esc(json.dumps(items,ensure_ascii=False,indent=2))}</pre>')
        sections.append(f'<section id="case-{esc(cid)}"><h2>{esc(cid)} — {esc(case["expected_conclusion"])}</h2><img class="crop" src="{esc(link(crop))}" alt="Verified H1 bore callout"><p>Exported STEP: four Ø{g["cylinders"][0]["diameter_mm"]:g} mm bores, depth 8 mm; volume {g["volume_mm3"]:.11f} mm³. Visible callout Ø{d["diameter_mm"]:g} ±{d["symmetric_tolerance_mm"]:g} mm THRU. Contract: {esc(case["manufacturing"])}.</p><p>Private rule O01, m0.1: compare same-stage drawing interval with reimported nominal; honor explicitly declared intermediate-to-finished reaming. Project-selected release contract, 2026-10-04. Supported clear applies only to H1 package consistency.</p><p><a href="{esc(link(source / "drawing.pdf"))}">PDF page1</a> · <a href="{esc(link(source / "drawing.png"))}">Full rendered drawing</a> · <a href="{esc(link(source / "part.step"))}">Actual STEP</a> · <a href="{esc(link(source / "packet.json"))}">Public contract</a> · <a href="{esc(link(Path(oracle_path).parent / cid / "inspection.json"))}">Independent measurement/region evidence</a></p><details><summary>View full drawing and geometric witnesses</summary><img class="drawing" src="{esc(link(source / "drawing.png"))}" alt="Complete supplied drawing"><pre>{esc(json.dumps(g,indent=2))}</pre></details><details><summary>Original reviewer findings, assertions and witnesses</summary>{"".join(observations)}</details></section>')
    document = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>RFQFuzz M0 evidence comparison</title>
<style>body{{margin:0;background:#f5f6f8;color:#172332;font:16px/1.5 system-ui,sans-serif}}main{{max-width:1380px;margin:auto;padding:32px}}h1{{font-size:34px;margin:0}}h2{{font-size:23px}}small{{display:block}}table{{border-collapse:collapse;width:100%;background:white}}th,td{{text-align:left;vertical-align:top;padding:16px;border:1px solid #cdd5df}}a{{color:#0e537e}}article,section{{background:white;padding:24px;margin:24px 0;border:1px solid #d5dde5;border-radius:6px}}.banner{{background:#fff0d0;border-left:6px solid #a65900;padding:18px}}.explicit_false_clear,.false_alert{{background:#fff0df}}.detected,.correct_clear{{background:#eaf4ef}}.crop{{max-width:100%;image-rendering:auto;border:1px solid #ddd;padding:12px}}.drawing{{max-width:100%}}pre{{overflow:auto;background:#f0f3f6;padding:18px;font-size:13px}}</style>
<main><h1>RFQFuzz · M0 evidence comparison</h1><p>Three presentations of one synthetic plate. One named bore-group obligation per case. This benchmark does not certify manufacture or general industrial competence.</p>
<p class="banner"><b>DELIBERATELY INJECTED REVIEWER REGRESSIONS</b><br>The second column of reviewer results intentionally clears a contradiction and ignores the declared reaming stage. These are reference-code perturbations, not naturally discovered failures of the independent reviewer. Its original observations are retained separately.</p>
<h2>What changed</h2><p>Reference → deliberately injected reference:</p><ul>{change_list}</ul><p>Reference → independent reviewer: {esc(external_changes)} (no changed decisions when empty).</p>
<table><tr><th>Case / source evidence</th><th>Validated expectation</th>{headers}</tr>{''.join(body)}</table>
<h2>Separate tracks and denominators</h2><p>Package consistency is the only scored track. CNC advisory/profile review is <b>unsupported, 0 scored obligations</b>. Frozen fixture invalidity: 0/3. Initial authoring attempt: 3/3 excluded as a group for ambiguous view-stage context; not hidden in the final denominator. Corruption controls are intentionally invalid and unscored. No finalized precision, composite score, significance claim or independent industrial transfer evidence.</p><p>The public response schema allows free category names. The external findings use different names for the same H1 obligation. <a href="{evidence_link('category-adjudication.json')}">Evidence-bound manual mappings</a> normalize those names without changing conclusions, witnesses or oracle. <a href="{evidence_link('runs/imported-independent/run.json')}">Initial unadjudicated import</a> is retained as a harness limitation; it is not an observed reviewer miss.</p>{''.join(summary)}
<h2>Inspect the exact evidence</h2>{''.join(sections)}
<h2>Limits and replay</h2><p>Generator/validator share OCCT. Raster ink does not prove text semantics; hash-bound visual inspection is required. Same-machine reviewer blinding is procedural. The reference parses this known PDF template and does not visually interpret PNG. Windows Python3.12 was exercised; Linux and a separately authored drawing remain unverified.</p><p><a href="{evidence_link('gate.md')}">M0 gate</a> · <a href="{evidence_link('artifact-proof.md')}">Artifact acceptance</a> · <a href="{evidence_link('review-handoff/PROMPT.txt')}">Exact neutral reviewer prompt</a> · <a href="{evidence_link('review-handoff/review-output/observations.md')}">Independent raw observations</a> · <a href="{evidence_link('validation/oracle.json')}">Private validated oracle</a></p></main></html>'''
    (out / 'index.html').write_text(document, encoding='utf-8')
    record = {'schema_version':'m0.1', 'injected_changes': changes, 'external_changes': external_changes,
              'runs': [{ 'reviewer':r['reviewer'], 'counts':r['score']['counts']} for r in runs],
              'manifest':runs[0]['manifest'], 'scope':'one synthetic ancestry; CNC advisory unsupported; no industrial claim'}
    write_json(out / 'comparison.json', record)
    return record
