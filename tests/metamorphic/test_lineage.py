"""Audit the immutable source split; do not imply held-out performance."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("challenge_evaluator", ROOT / "tools/challenge_evaluator.py")
challenge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(challenge)


def mutations():
    return json.loads((ROOT / "evidence/M2/core-suite/private/mutations.json").read_text(encoding="utf-8"))["mutations"]


def test_all_core_twins_families_and_layouts_stay_in_one_partition():
    result = challenge.audit_lineage(mutations())
    assert result["status"] == "passed" and result["case_count"] == 145
    assert {p for partitions in result["groups"]["ancestry"].values() for p in partitions} == {"development"}
    assert {p for partitions in result["groups"]["source_family"].values() for p in partitions} == {"development"}
    assert {p for partitions in result["groups"]["layout_ancestry"].values() for p in partitions} == {"development"}


def test_ancestry_or_shared_layout_cross_partition_is_rejected():
    rows = deepcopy(mutations())
    rows[0]["partition"] = "holdout"
    result = challenge.audit_lineage(rows)
    assert result["status"] == "failed"
    assert any("ancestry overlap" in f for f in result["failures"])
    assert any("source_family overlap" in f for f in result["failures"])
    assert any("layout_ancestry overlap" in f for f in result["failures"])


def test_exact_frozen_artifact_hash_replay_has_no_public_private_keys():
    from rfqfuzz.v1.contracts import read_packet, sha256
    for folder in sorted((ROOT / "evidence/M2/core-suite/public").iterdir()):
        packet = read_packet(folder)
        assert packet["case_id"] == folder.name
        assert all(sha256(folder / a["path"]) == a["sha256"] for a in packet["artifacts"])
        assert {p.name for p in folder.iterdir()} == {"packet.json", "part.step", "drawing.pdf", "drawing.png"}
