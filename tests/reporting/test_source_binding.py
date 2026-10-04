import copy
import json
from pathlib import Path
import shutil
import pytest
from rfqfuzz.v1.contracts import load_json,write_json
from rfqfuzz.v1.reporting import make_report

ROOT=Path(__file__).resolve().parents[2]
DEMO=ROOT/"evidence/M5/coordinator-demo-v2"

def test_single_run_report_rejects_revised_oracle(tmp_path):
    oracle=load_json(DEMO/"validation/oracle.json",limit=32_000_000)
    oracle["oracle_version"]="unscored-new-version"
    write_json(tmp_path/"oracle.json",oracle)
    with pytest.raises(ValueError,match="oracle_sha256"):
        make_report([DEMO/"before/run.json"],tmp_path/"oracle.json",DEMO/"inputs/suite/public",tmp_path/"report")
    assert not (tmp_path/"report").exists()

def test_report_rejects_changed_actual_step(tmp_path):
    shutil.copytree(DEMO/"inputs/suite/public",tmp_path/"public")
    step=next((tmp_path/"public").glob("*/part.step"))
    step.write_bytes(step.read_bytes()+b"\nCHANGED ACTUAL SOURCE\n")
    with pytest.raises(ValueError,match="hash"):
        make_report([DEMO/"before/run.json"],DEMO/"validation/oracle.json",tmp_path/"public",tmp_path/"report")
    assert not (tmp_path/"report").exists()

def test_report_rejects_changed_retained_response(tmp_path):
    shutil.copytree(DEMO/"before",tmp_path/"run")
    raw=tmp_path/"run/raw-review.json"
    raw.write_bytes(raw.read_bytes()+b" ")
    with pytest.raises(ValueError,match="raw_sha256"):
        make_report([tmp_path/"run/run.json"],DEMO/"validation/oracle.json",DEMO/"inputs/suite/public",tmp_path/"report")
    assert not (tmp_path/"report").exists()

def test_report_escapes_rate_fields(tmp_path):
    shutil.copytree(DEMO/"before",tmp_path/"run")
    run=load_json(tmp_path/"run/run.json")
    run["score"]["tracks"]["package_consistency"]["rates"]["recall"]["numerator"]="<script>alert(1)</script>"
    run["score"]["tracks"]["package_consistency"]["execution_failures"]="<img onerror=evil()>"
    write_json(tmp_path/"run/run.json",run)
    make_report([tmp_path/"run/run.json"],DEMO/"validation/oracle.json",DEMO/"inputs/suite/public",tmp_path/"report")
    text=(tmp_path/"report/index.html").read_text()
    assert "<script>" not in text and "<img onerror" not in text
    assert "&lt;script&gt;" in text
