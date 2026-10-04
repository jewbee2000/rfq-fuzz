import json
from pathlib import Path
import shutil
import pytest
from rfqfuzz.contracts import read_packet
from rfqfuzz.public_export import audit_public

PUBLIC = Path("evidence/M0/bundle/public")

def test_neutral_export():
    assert len(audit_public(PUBLIC)["cases"]) == 3

def test_missing_authority_and_units(tmp_path):
    dst = tmp_path / "case"
    shutil.copytree(PUBLIC / "pk-b8e2", dst)
    p = json.loads((dst / "packet.json").read_text())
    del p["authority"]
    (dst / "packet.json").write_text(json.dumps(p))
    with pytest.raises(ValueError, match="authority"):
        read_packet(dst)
    p["authority"] = {"nominal_geometry": "STEP"}
    p["units"] = {"model": "inch", "drawing": "mm"}
    (dst / "packet.json").write_text(json.dumps(p))
    with pytest.raises(ValueError, match="units"):
        read_packet(dst)

def test_private_answer_or_sidecar_is_rejected(tmp_path):
    root = tmp_path / "public"
    shutil.copytree(PUBLIC, root)
    (root / "pk-b8e2" / "oracle.json").write_text('{}')
    with pytest.raises(ValueError, match="sidecar"):
        audit_public(root)

def test_traversal_rejected(tmp_path):
    dst = tmp_path / "case"
    shutil.copytree(PUBLIC / "pk-b8e2", dst)
    p = json.loads((dst / "packet.json").read_text())
    p['artifacts'][0]['path'] = '../part.step'
    (dst / "packet.json").write_text(json.dumps(p))
    with pytest.raises(ValueError, match="paths"):
        read_packet(dst)
