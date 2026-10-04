"""Fixed black-box witnesses for six deliberate production-source faults."""
from copy import deepcopy
from pathlib import Path

import pytest

from rfqfuzz.v1.contracts import validate_packet
from rfqfuzz.v1.generation import generate_case
from rfqfuzz.v1.profiles import profile
from rfqfuzz.v1.scoring import score
from rfqfuzz.v1.validation import _native


def observe(tmp_path, family="plate", **kwargs):
    folder = tmp_path / "pk-0123456789ab"
    packet = generate_case(folder, folder.name, family, **kwargs)
    observation = _native(folder, tmp_path / "observed")
    return packet, observation


def conclusion(observation, obligation):
    return next(e["conclusion"] for e in observation["expectations"] if e["obligation_id"] == obligation)


def test_equivalent_inches_preserve_package_conclusions(tmp_path):
    _, observed = observe(tmp_path, drawing_overrides={"drawing_units": "in"})
    assert observed["measurements"]["bore_diameter_mm"] == 6
    assert conclusion(observed, "obj-units") == "supported_clear"
    assert conclusion(observed, "obj-diameter") == "supported_clear"
    assert "H1 DIAMETER = 0.2362 +/- 0.0020 in" in observed["drawing"]["text"]


def test_wall_boundary_uses_strict_public_comparator(tmp_path):
    _, observed = observe(tmp_path, "pocket_block", parameters={"wall": .8})
    assert observed["measurements"]["wall_mm"] == .8
    assert conclusion(observed, "cnc-wall") == "supported_clear"


def test_thin_wall_advisory_keeps_its_conclusion_class(tmp_path):
    _, observed = observe(tmp_path, "pocket_block", parameters={"wall": .6})
    assert conclusion(observed, "cnc-wall") == "advisory"
    assert conclusion(observed, "cnc-envelope") == "supported_clear"


def duplicate_control():
    evidence = [{"artifact": "drawing.pdf", "quote": "UNITS = in"},
                {"artifact": "part.step", "quote": "document envelope_mm=[80, 50, 8]"}]
    expected = {"obligation_id": "obj-units", "track": "package_consistency", "category": "unit_consistency",
                "feature_id": "document", "conclusion": "contradiction", "rule_id": None, "evidence": evidence,
                "root_cause": "unit-root", "operator": "O03"}
    case = {"schema_version": "1.0", "oracle_version": "challenge-hand-count-1", "case_id": "pk-0123456789ab",
            "packet_sha256": "a" * 64, "status": "valid", "reasons": [], "measurements": {}, "drawing": {},
            "expectations": [expected], "isolation": {"scope": "hand-authored scorer arithmetic control; no part claim"}}
    findings = [{"id": f"duplicate-{i}", "obligation_id": "obj-units", "category": "unit_consistency", "feature_id": "document",
                 "conclusion": "contradiction", "evidence": deepcopy(evidence), "rationale": "One globally governed units discrepancy"} for i in range(3)]
    response = {"schema_version": "1.0", "reviewer": {"name": "hand-count control", "version": "1", "configuration": "three duplicate grounded findings"},
                "results": [{"case_id": case["case_id"], "packet_sha256": case["packet_sha256"], "status": "completed",
                             "reviewed_modalities": ["step", "pdf", "context"], "reviewed_obligations": ["obj-units"],
                             "findings": findings, "assertions": [], "runtime_seconds": None, "raw_ref": "hand-count.json", "reason": "scorer arithmetic witness"}]}
    return response, {"cases": [case]}


def test_duplicate_root_findings_cannot_multiply_detection():
    response, oracle = duplicate_control()
    result = score(response, oracle)
    counts = result["tracks"]["package_consistency"]
    assert counts["detected"] == counts["issues"] == 1
    assert result["operators"]["O03"] == {"issues": 1, "detected": 1}
    assert len(result["suppressed_duplicates"]) == 2
    assert result["unadjudicated"] == []


def test_nested_private_answer_key_is_rejected(tmp_path):
    packet, _ = observe(tmp_path)
    leaked = deepcopy(packet)
    leaked["profile"]["rules"][0]["threshold"]["oracle"] = {"expected_conclusion": "advisory"}
    with pytest.raises(ValueError, match="private"):
        validate_packet(leaked)


def test_unresolved_finish_stage_cannot_become_clear(tmp_path):
    _, observed = observe(tmp_path, context_overrides={"manufacturing": {"finish": "anodize", "tolerance_stage": None}}, profile=profile("relaxed"))
    assert conclusion(observed, "cnc-stage") == "missing_information"


def test_relaxation_changes_only_conditional_conclusions(tmp_path):
    standard, a = observe(tmp_path / "standard", "pocket_block", parameters={"wall": .6})
    relaxed, b = observe(tmp_path / "relaxed", "pocket_block", parameters={"wall": .6}, profile=profile("relaxed"))
    assert a["measurements"] == b["measurements"]
    assert a["drawing"]["annotations"] == b["drawing"]["annotations"]
    assert conclusion(a, "cnc-wall") == "advisory" and conclusion(b, "cnc-wall") == "supported_clear"
    assert {e["obligation_id"]: e["conclusion"] for e in a["expectations"] if e["track"] == "package_consistency"} == {
        e["obligation_id"]: e["conclusion"] for e in b["expectations"] if e["track"] == "package_consistency"}
    assert standard["profile"]["id"] != relaxed["profile"]["id"]


def test_global_units_fault_is_one_observed_root_cause(tmp_path):
    _, observed = observe(tmp_path, drawing_overrides={"drawing_units": "in", "convert_dimensions": False})
    contradictions = [e for e in observed["expectations"] if e["conclusion"] == "contradiction"]
    assert len(contradictions) == 1
    assert contradictions[0]["operator"] == "O03" and contradictions[0]["obligation_id"] == "obj-units"
    assert observed["suppressed_unit_dependents"] == ["obj-diameter"]


def test_same_config_replays_artifact_semantics_and_bound_hashes(tmp_path):
    from rfqfuzz.v1.contracts import sha256, read_packet
    _, a = observe(tmp_path / "first")
    _, b = observe(tmp_path / "second")
    assert a["measurements"] == b["measurements"]
    assert a["drawing"]["annotations"] == b["drawing"]["annotations"]
    assert [(e["obligation_id"], e["conclusion"]) for e in a["expectations"]] == [(e["obligation_id"], e["conclusion"]) for e in b["expectations"]]
    # Do not demand cross-platform byte-identical STEP exporter timestamps.
    for name in ("first", "second"):
        folder = tmp_path / name / "pk-0123456789ab"
        packet = read_packet(folder)
        assert all(sha256(folder / artifact["path"]) == artifact["sha256"] for artifact in packet["artifacts"])
    assert sha256(tmp_path / "first/pk-0123456789ab/drawing.pdf") == sha256(tmp_path / "second/pk-0123456789ab/drawing.pdf")
    assert sha256(tmp_path / "first/pk-0123456789ab/drawing.png") == sha256(tmp_path / "second/pk-0123456789ab/drawing.png")
