import copy
import importlib.util
from pathlib import Path
import shutil
from rfqfuzz.v1.contracts import write_json,load_json,sha256
from rfqfuzz.v1.reporting import make_report,audit_report
from rfqfuzz.v1.scoring import score

spec=importlib.util.spec_from_file_location("score_cases",Path(__file__).parents[1]/"scoring/test_v1.py")
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def test_escaped_source_navigation(tmp_path):
    source=Path(__file__).resolve().parents[2]/"evidence/M5/coordinator-demo-v2"
    r=load_json(source/"before/raw-review.json")
    r["reviewer"]["configuration"]='<script>alert(1)</script>'
    run=load_json(source/"before/run.json")
    run["reviewer"]=r["reviewer"]
    runs=[]
    for name in ("a","b"):
        target=tmp_path/name;write_json(target/"raw-review.json",r)
        run["manifest"]["raw_sha256"]=sha256(target/"raw-review.json")
        write_json(target/"run.json",run);runs.append(target/"run.json")
    make_report(runs,source/"validation/oracle.json",source/"inputs/suite/public",tmp_path/"report")
    path=tmp_path/"report/index.html"
    assert audit_report(path)["local_links"]>5
    assert '&lt;script&gt;' in path.read_text() and '<script>' not in path.read_text()
    assert "package_consistency" in path.read_text() and "cnc_advisory" in path.read_text()
