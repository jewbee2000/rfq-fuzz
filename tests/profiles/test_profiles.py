import json

import pytest

from rfqfuzz.v1.contracts import CONCLUSIONS, private_scan, validate_profile
from rfqfuzz.v1.profiles import default_profile, evaluate, profile


def manufacturing(**changes):
    return {"material": "6061-T6", "material_class": "metal", "finish": "anodize", "tolerance_stage": None, **changes}


def setup(**changes):
    return {"orientation": "XYZ", "stock_allowance_mm": [0, 0, 0], "fixture_allowance_mm": [0, 0, 0], **changes}


def decision(rule, measurements=None, name="standard", manufacturing_changes=None, setup_changes=None):
    return evaluate(profile(name), rule, measurements or {}, manufacturing(**(manufacturing_changes or {})), setup(**(setup_changes or {})))


@pytest.mark.parametrize("name", ["standard", "relaxed"])
def test_complete_public_synthetic_cards(name):
    selected = profile(name)
    assert validate_profile(selected) is selected
    private_scan(selected)
    assert json.loads(json.dumps(selected)) == selected
    assert selected["synthetic"] is True
    for rule in selected["rules"]:
        assert rule["synthetic_value"] is True
        assert rule["retrieved"] == "2026-10-04"
        assert "https://" in rule["source"]
        assert rule["version"] == selected["version"]
        assert rule["limits"]
        assert rule["precedence"]


def test_profiles_are_fresh_and_unknown_profile_refused():
    selected = profile()
    selected["rules"][0]["threshold"]["metal"] = 100
    selected["rules"][0]["applicability"]["materials"]["6061-T6"] = "plastic"
    assert profile()["rules"][0]["threshold"]["metal"] == 0.8
    assert profile()["rules"][1]["applicability"]["materials"]["6061-T6"] == "metal"
    assert default_profile() == profile()
    with pytest.raises(ValueError, match="unknown synthetic"):
        profile("a supplier with no contract")


@pytest.mark.parametrize("value,expected", [(0.799999, "advisory"), (0.8, "supported_clear"), (0.800001, "supported_clear")])
def test_wall_boundary(value, expected):
    assert decision("A01", {"wall_mm": value})["conclusion"] == expected


def test_wall_material_and_profile_counterfactuals():
    assert decision("A01", {"wall_mm": 0.6})["conclusion"] == "advisory"
    assert decision("A01", {"wall_mm": 0.6}, name="relaxed")["conclusion"] == "supported_clear"
    assert decision("A01", {"wall_mm": 1.0})["conclusion"] == "supported_clear"
    assert decision("A01", {"wall_mm": 1.0}, manufacturing_changes={"material": "ABS", "material_class": "plastic"})["conclusion"] == "advisory"
    assert decision("A01", {"wall_mm": 1.0}, name="relaxed", manufacturing_changes={"material": "ABS", "material_class": "plastic"})["conclusion"] == "supported_clear"


@pytest.mark.parametrize("depth,expected", [(23.999999, "supported_clear"), (24.0, "supported_clear"), (24.000001, "advisory")])
def test_bore_boundary(depth, expected):
    assert decision("A02", {"bore_depth_mm": depth, "bore_diameter_mm": 6})["conclusion"] == expected


def test_bore_alternate_and_large_ratio_remain_advisories():
    measurements = {"bore_depth_mm": 36, "bore_diameter_mm": 6}
    assert decision("A02", measurements)["conclusion"] == "advisory"
    assert decision("A02", measurements, name="relaxed")["conclusion"] == "supported_clear"
    assert decision("A02", {"bore_depth_mm": 1000, "bore_diameter_mm": 6})["conclusion"] == "advisory"


@pytest.mark.parametrize("axis", range(3))
def test_setup_axis_boundaries(axis):
    envelope = [120, 80, 50]
    assert decision("A03", {"envelope_mm": envelope})["conclusion"] == "supported_clear"
    envelope[axis] += 0.000001
    row = decision("A03", {"envelope_mm": envelope})
    assert row["conclusion"] == "profile_exclusion"
    assert "XYZ"[axis] in row["reason"]
    assert "synthetic-standard-XYZ" in row["reason"]
    assert decision("A03", {"envelope_mm": envelope}, name="relaxed")["conclusion"] == "supported_clear"


def test_allowances_are_total_extents_and_both_are_counted_once():
    measurements = {"envelope_mm": [100, 60, 30]}
    assert decision("A03", measurements, setup_changes={"stock_allowance_mm": [10, 10, 10], "fixture_allowance_mm": [10, 10, 10]})["conclusion"] == "supported_clear"
    assert decision("A03", measurements, setup_changes={"stock_allowance_mm": [10, 10, 10], "fixture_allowance_mm": [11, 10, 10]})["conclusion"] == "profile_exclusion"
    assert decision("A03", measurements, setup_changes={"stock_allowance_mm": [21, 0, 0]})["conclusion"] == "profile_exclusion"
    assert decision("A03", measurements, setup_changes={"fixture_allowance_mm": [21, 0, 0]})["conclusion"] == "profile_exclusion"


def test_missing_allowances_cannot_be_assumed_zero():
    for key in ["stock_allowance_mm", "fixture_allowance_mm", "orientation"]:
        context = setup()
        del context[key]
        row = evaluate(profile(), "A03", {"envelope_mm": [100, 60, 30]}, manufacturing(), context)
        assert row["conclusion"] == "missing_information"


def test_setup_does_not_permute_axes_or_imply_universal_exclusion():
    assert decision("A03", {"envelope_mm": [70, 100, 40]})["conclusion"] == "profile_exclusion"
    assert decision("A03", {"envelope_mm": [100, 70, 40]})["conclusion"] == "supported_clear"
    assert decision("A03", {"envelope_mm": [70, 100, 40]}, setup_changes={"orientation": "YXZ"})["conclusion"] == "unsupported"


def test_stage_explicit_precedence_default_and_no_default():
    assert decision("A04")["conclusion"] == "supported_clear"
    assert "before_finish" in decision("A04")["reason"]
    assert decision("A04", name="relaxed")["conclusion"] == "missing_information"
    for stage in ["before_finish", "after_finish"]:
        for name in ["standard", "relaxed"]:
            row = decision("A04", name=name, manufacturing_changes={"tolerance_stage": stage})
            assert row["conclusion"] == "supported_clear"
            assert f"explicit public tolerance stage {stage}" in row["reason"]
    assert decision("A04", manufacturing_changes={"tolerance_stage": "finished"})["conclusion"] == "unsupported"
    # Even no finish does not invent a stage when the selected policy has none.
    assert decision("A04", name="relaxed", manufacturing_changes={"finish": "none"})["conclusion"] == "missing_information"


@pytest.mark.parametrize("finish", [None, "", "unknown", "unspecified"])
def test_missing_finish_context_cannot_be_defaulted_clear(finish):
    assert decision("A04", manufacturing_changes={"finish": finish})["conclusion"] == "missing_information"


@pytest.mark.parametrize("rule,measurements", [("A01", {"wall_mm": 10}), ("A02", {"bore_depth_mm": 6, "bore_diameter_mm": 6}), ("A03", {"envelope_mm": [10, 10, 10]}), ("A04", {})])
@pytest.mark.parametrize("changes", [{"material": "unknown"}, {"material": "unmapped alloy", "material_class": "metal"}, {"material_class": "unknown"}])
def test_unknown_material_never_clear(rule, measurements, changes):
    assert decision(rule, measurements, manufacturing_changes=changes)["conclusion"] == "missing_information"


def test_material_class_conflict_is_unsupported():
    assert decision("A01", {"wall_mm": 10}, manufacturing_changes={"material_class": "plastic"})["conclusion"] == "unsupported"


@pytest.mark.parametrize("rule", ["A01", "A02", "A03"])
def test_missing_measurements_are_unknown(rule):
    assert decision(rule)["conclusion"] == "missing_information"


@pytest.mark.parametrize("value", [0, -1, True, "1", float("nan"), float("inf")])
def test_invalid_wall_is_unsupported(value):
    assert decision("A01", {"wall_mm": value})["conclusion"] == "unsupported"


@pytest.mark.parametrize("value", [0, -1, True, "1", float("nan"), float("inf")])
def test_invalid_diameter_is_unsupported(value):
    assert decision("A02", {"bore_depth_mm": 10, "bore_diameter_mm": value})["conclusion"] == "unsupported"


@pytest.mark.parametrize("vector", [[-1, 0, 0], [float("nan"), 0, 0], [0, 0], [True, 0, 0], "XYZ"])
def test_invalid_allowance_is_unsupported(vector):
    assert decision("A03", {"envelope_mm": [10, 10, 10]}, setup_changes={"stock_allowance_mm": vector})["conclusion"] == "unsupported"


def test_result_has_bounded_semantics_and_versioned_rule_reference():
    row = decision("A01", {"wall_mm": 0.6})
    assert set(row) == {"conclusion", "reason", "rule_id"}
    assert row["conclusion"] in CONCLUSIONS
    assert "synthetic-standard@1.0.0 / A01@1.0.0" in row["reason"]
    assert row["rule_id"] == "A01"
    assert decision("A05")["conclusion"] == "unsupported"


def test_invalid_profile_rejected_not_clear():
    selected = profile()
    selected["synthetic"] = False
    with pytest.raises(ValueError):
        evaluate(selected, "A01", {"wall_mm": 10}, manufacturing(), setup())


def test_unsupported_policy_representation_never_clear():
    selected = profile()
    selected["rules"][0]["applicability"] = ["metal"]
    assert evaluate(selected, "A01", {"wall_mm": 10}, manufacturing(), setup())["conclusion"] == "unsupported"
    selected = profile()
    selected["rules"][0]["threshold"] = 1
    assert evaluate(selected, "A01", {"wall_mm": 10}, manufacturing(), setup())["conclusion"] == "unsupported"


def test_numeric_overflow_is_unsupported():
    assert decision("A02", {"bore_depth_mm": 1e308, "bore_diameter_mm": 1e-308})["conclusion"] == "unsupported"
    assert decision("A03", {"envelope_mm": [1e308, 10, 10]}, setup_changes={"stock_allowance_mm": [1e308, 0, 0]})["conclusion"] == "unsupported"
    assert decision("A01", {"wall_mm": 10**1000})["conclusion"] == "unsupported"


@pytest.mark.parametrize("key,value", [("comparison", "less_than_or_equal"), ("units", "in"), ("severity", "profile_exclusion")])
def test_unsupported_rule_semantics_do_not_use_builtin_behavior(key, value):
    selected = profile()
    selected["rules"][0][key] = value
    assert evaluate(selected, "A01", {"wall_mm": 10}, manufacturing(), setup())["conclusion"] == "unsupported"


@pytest.mark.parametrize("changes", [{"material": []}, {"material_class": {}}, {"tolerance_stage": []}])
def test_malformed_premise_types_do_not_crash_or_default_clear(changes):
    assert decision("A04", manufacturing_changes=changes)["conclusion"] == "unsupported"
