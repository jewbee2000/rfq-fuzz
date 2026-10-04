import json
from pathlib import Path
import subprocess
import sys
import pytest
from rfqfuzz.v1.cli import main
from rfqfuzz.v1.contracts import sha256

ROOT=Path(__file__).resolve().parents[2]

def test_help_outside_repository(tmp_path):
    # The package is installed for fresh-consumer acceptance; repo tests also
    # set an explicit source path for the subprocess instead of relying on cwd.
    import os
    env=os.environ.copy();env["PYTHONPATH"]=str(ROOT/"src")
    r=subprocess.run([sys.executable,"-m","rfqfuzz.v1","--help"],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert r.returncode==0 and "export-review" in r.stdout

def test_cli_failed_input_is_explicit(tmp_path,capsys):
    code=main(["validate",str(tmp_path/"absent"),str(tmp_path/"result")])
    assert code==2
    assert json.loads(capsys.readouterr().err)["status"]=="error"

def test_frozen_replay_rejects_changed_asset(tmp_path):
    from rfqfuzz.v1.api import demo
    from rfqfuzz.v1.contracts import write_json
    assets=tmp_path/"assets";assets.mkdir();(assets/"part.step").write_text("changed")
    write_json(assets/"replay-manifest.json",{"files":{"part.step":"0"*64}})
    with pytest.raises(ValueError,match="hash mismatch"):demo(assets,tmp_path/"out")
    assert not (tmp_path/"out").exists()

@pytest.mark.parametrize("value",[0,-1,301,float("inf"),float("nan"),True])
def test_demo_parser_bounds_reject_before_creating_outputs(tmp_path,value):
    from rfqfuzz.v1.api import demo
    with pytest.raises(ValueError,match="timeout outside"):
        demo(ROOT/"examples/v1-demo",tmp_path/"demo",parser_timeout=value)
    assert not (tmp_path/"demo").exists()

def test_consumer_frozen_demo(tmp_path):
    from rfqfuzz.v1.api import demo
    from rfqfuzz.v1.reporting import audit_report
    result=demo(ROOT/"examples/v1-demo",tmp_path/"demo")
    assert result["status"]=="passed"
    assert len(result["changes"])==2
    assert set(result["tracks"])=={"package_consistency","cnc_advisory"}
    assert audit_report(result["report"])["unsafe_elements"]==0
