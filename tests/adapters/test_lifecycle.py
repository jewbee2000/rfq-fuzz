import importlib.util
import json
from pathlib import Path
import shutil
import sys
import pytest
from rfqfuzz.v1 import adapters as a
from rfqfuzz.v1.contracts import sha256,write_json

spec=importlib.util.spec_from_file_location("contract_cases",Path(__file__).parents[1]/"contracts/test_v1.py")
helper=importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)

@pytest.fixture
def public(tmp_path):
    folder=tmp_path/"public"/"pk-012345abcdef"
    shutil.copytree("evidence/M0/bundle/public/pk-b8e2",folder)
    p=helper.packet()
    for artifact in p["artifacts"]:artifact["sha256"]=sha256(folder/artifact["path"])
    write_json(folder/"packet.json",p)
    return folder.parent

def test_export_audit_and_private_sidecar(public,tmp_path):
    assert a.export_review(public,tmp_path/"handoff")["status"]=="passed"
    (next(public.iterdir())/"oracle.json").write_text("{}")
    with pytest.raises(ValueError,match="sidecar"):a.audit_public(public)

def test_manual_partial_and_malformed_retained(public,tmp_path):
    r=helper.review(); r["results"][0]["packet_sha256"]=sha256(next(public.glob("*/packet.json")));r["results"][0]["status"]="partial"
    path=tmp_path/"raw.json";write_json(path,r)
    assert a.import_response(path,public,tmp_path/"import")["response"]["results"][0]["status"]=="partial"
    path.write_text("bad json")
    bad=a.import_response(path,public,tmp_path/"bad")
    assert bad["status"]=="error" and (tmp_path/"bad/raw-review.json").read_text()=="bad json"
    with pytest.raises(ValueError,match="immutable"):a.import_response(path,public,tmp_path/"bad")

def test_timeout_and_descendant_kill(public,tmp_path):
    script=tmp_path/"sleep.py"
    script.write_text("import subprocess,sys,time\nsubprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])\ntime.sleep(60)\n")
    assert a.run_local([sys.executable,str(script)],public,tmp_path/"timeout",timeout=.2)["status"]=="timeout"

def test_malformed_process_and_packet_text_never_executed(public,tmp_path):
    assert a.run_local([sys.executable,"-c","print('hello')"],public,tmp_path/"malformed")["status"]=="error"
    with pytest.raises(ValueError,match="argv"):a.run_local("echo hello",public,tmp_path/"x")

def test_signatures_and_hashes(public):
    folder=next(public.iterdir());p=json.loads((folder/"packet.json").read_text())
    (folder/"drawing.pdf").write_bytes(b"not PDF")
    p["artifacts"][1]["sha256"]=sha256(folder/"drawing.pdf");write_json(folder/"packet.json",p)
    with pytest.raises(ValueError,match="signature"):a.audit_public(public)

def test_oversized_import_and_process_output_retains_reason(public,tmp_path):
    source=tmp_path/"huge.json";source.write_bytes(b"x"*4_000_001)
    record=a.import_response(source,public,tmp_path/"oversized")
    assert record["status"]=="error" and 'size limit' in (tmp_path/"oversized/import.json").read_text()
    record=a.run_local([sys.executable,"-c","import sys,time;sys.stdout.write('x'*4_100_000);sys.stdout.flush();time.sleep(10)"],public,tmp_path/"output-limit")
    assert record["status"]=="error" and record["reason"]=="adapter output size limit"
