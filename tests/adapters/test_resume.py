import importlib.util
from pathlib import Path
import shutil
from rfqfuzz.v1.contracts import write_json,sha256
from rfqfuzz.v1.lifecycle import resume_plan

spec=importlib.util.spec_from_file_location("contract_cases",Path(__file__).parents[1]/"contracts/test_v1.py")
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def test_interrupted_partial_complete_resume(tmp_path):
    folder=tmp_path/"public/pk-012345abcdef";shutil.copytree("evidence/M0/bundle/public/pk-b8e2",folder)
    packet=h.packet()
    for artifact in packet["artifacts"]:artifact["sha256"]=sha256(folder/artifact["path"])
    write_json(folder/"packet.json",packet)
    missing=tmp_path/"interrupted/adapter.json"
    assert resume_plan(folder.parent,[missing])["attempts"][0]["status"]=="interrupted"
    r=h.review();r["results"][0].update(packet_sha256=sha256(folder/"packet.json"),status="partial")
    path=tmp_path/"first/adapter.json";write_json(path,{"status":"completed","response":r})
    assert resume_plan(folder.parent,[missing,path])["pending_cases"]==[packet["case_id"]]
    r["results"][0]["status"]="completed";next_path=tmp_path/"second/adapter.json";write_json(next_path,{"status":"completed","response":r})
    assert resume_plan(folder.parent,[missing,path,next_path])["pending_cases"]==[]
    assert 'partial' in path.read_text()
