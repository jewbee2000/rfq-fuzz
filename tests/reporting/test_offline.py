import copy
import importlib.util
from pathlib import Path
import shutil
from rfqfuzz.v1.contracts import write_json
from rfqfuzz.v1.reporting import make_report,audit_report
from rfqfuzz.v1.scoring import score

spec=importlib.util.spec_from_file_location("score_cases",Path(__file__).parents[1]/"scoring/test_v1.py")
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def test_escaped_source_navigation(tmp_path):
    r,o=h.setup();c=o["cases"][0];cid=c["case_id"]
    folder=tmp_path/"public"/cid;shutil.copytree("evidence/M0/bundle/public/pk-b8e2",folder)
    # Report presentation test only, not a new scored geometry fixture.
    r["reviewer"]["configuration"]='<script>alert(1)</script>'
    run={"reviewer":r["reviewer"],"manifest":{"suite_sha256":"a","oracle_sha256":"b","profile_sha256":"c"},"score":score(r,o)}
    runs=[]
    for name in ("a","b"):
        target=tmp_path/name;write_json(target/"run.json",run);write_json(target/"raw-review.json",r);runs.append(target/"run.json")
    oracle=tmp_path/"oracle.json";write_json(oracle,o)
    make_report(runs,oracle,folder.parent,tmp_path/"report")
    path=tmp_path/"report/index.html"
    assert audit_report(path)["local_links"]>5
    assert '&lt;script&gt;' in path.read_text() and '<script>' not in path.read_text()
    assert "package_consistency" in path.read_text() and "cnc_advisory" in path.read_text()
