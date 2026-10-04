import json
from pathlib import Path
import shutil
from rfqfuzz.v1.cli import main
from rfqfuzz.v1.contracts import load_json,write_json,sha256

def test_reference_corrupt_pdf_is_not_cli_success(tmp_path,capsys):
    root=Path(__file__).resolve().parents[2]
    folder=tmp_path/"public/pk-c6060a86b3df"
    shutil.copytree(root/"evidence/M2/core-suite/public"/folder.name,folder)
    (folder/"drawing.pdf").write_bytes(b"%PDF-BOGUS\n")
    packet=load_json(folder/"packet.json")
    for artifact in packet["artifacts"]:
        if artifact["path"]=="drawing.pdf":artifact["sha256"]=sha256(folder/"drawing.pdf")
    write_json(folder/"packet.json",packet)
    assert main(["reference",str(folder.parent),str(tmp_path/"observed")])==2
    summary=json.loads(capsys.readouterr().out)
    assert summary["states"]=={"error":1}
    result=load_json(tmp_path/"observed/review.json")
    assert result["results"][0]["status"]=="error"
    assert result["results"][0]["findings"]==[]
