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
