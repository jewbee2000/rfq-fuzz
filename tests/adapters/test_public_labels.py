import pytest
from rfqfuzz.v1.adapters import PRIVATE_LABEL,audit_public
from pathlib import Path

def test_private_labels_are_complete_words():
    assert PRIVATE_LABEL.search("axis permutation is not assumed") is None
    assert PRIVATE_LABEL.search("capability determination") is None
    for label in ["mutation","defective","valid_alternative","oracle","expected_conclusion"]:
        assert PRIVATE_LABEL.search("label="+label) is not None

def test_actual_demo_profile_exports_without_false_leakage_alarm():
    public=Path(__file__).resolve().parents[2]/"examples/v1-demo/suite/public"
    assert len(audit_public(public)["cases"])==15

def test_standalone_export_contains_public_transport_and_witness_protocol(tmp_path):
    from rfqfuzz.v1.adapters import export_review
    public=Path(__file__).resolve().parents[2]/"examples/v1-demo/suite/public"
    export_review(public,tmp_path/"bundle")
    protocol=(tmp_path/"bundle/REVIEWER_PROTOCOL.md").read_text()
    assert "packet_sha256" in protocol and "H1 diameter_mm=" in protocol
    assert "runtime_seconds" in protocol and "YOUR CONCLUSION" in protocol
