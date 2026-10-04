"""Project-selected, public synthetic policies for finite CNC review obligations.

This module evaluates supplied measurements and premises, not CAD topology or
manufacturing feasibility. The independent validator must derive measurements
from the final artifacts before using it. Every clear result is scoped to one
rule in the selected profile; it is never a general manufacturability approval.
"""
from __future__ import annotations

import math
from typing import Any

from . import VERSION
from .contracts import validate_profile

CapabilityProfile = dict[str, Any]
RETRIEVED = "2026-10-04"
PROFILE_VERSION = "1.0.0"
WALL_SOURCE = "Xometry, CNC design tips; https://www.xometry.com/resources/machining/10-tips-improve-cad-cnc-design/ ; Protolabs, CNC milling guidelines; https://www.protolabs.com/services/cnc-machining/cnc-milling/design-guidelines/"
BORE_SOURCE = "Protolabs Network, How to design parts for CNC machining; https://www.hubs.com/knowledge-base/how-design-parts-cnc-machining/"
ENVELOPE_SOURCE = "Protolabs, CNC milling design guidelines; https://www.protolabs.com/services/cnc-machining/cnc-milling/design-guidelines/"
STAGE_SOURCE = "Xometry, Manufacturing Standards; https://www.xometry.com/manufacturing-standards/ ; RFQFuzz project-selected synthetic stage policy (not a sourced vendor CNC default)"

# A finite project policy vocabulary, not a material database or finish chart.
MATERIALS = {
    "6061-T6": "metal", "aluminum 6061-T6": "metal", "304": "metal",
    "stainless steel 304": "metal", "316": "metal", "steel 1018": "metal",
    "ABS": "plastic", "acetal": "plastic", "POM": "plastic",
    "Nylon 6/6": "plastic",
}
UNKNOWN = frozenset({"unknown", "unspecified", "not specified", "tbd", "?"})
COMPARISONS = {
    "A01": "wall_mm < class threshold; equality is clear for this rule",
    "A02": "bore_depth_mm / bore_diameter_mm > class threshold; equality is clear for this rule",
    "A03": "any envelope_mm + stock_allowance_mm + fixture_allowance_mm axis > capacity; equality is included",
    "A04": "explicit before_finish/after_finish first; otherwise public profile default; otherwise missing_information",
}
RULE_UNITS = {"A01": "mm", "A02": "dimensionless depth/diameter", "A03": "mm XYZ total occupied extent", "A04": "manufacturing stage"}
SEVERITIES = {"A01": "advisory", "A02": "advisory", "A03": "profile_exclusion", "A04": "missing_information"}


def profile(name: str = "standard") -> CapabilityProfile:
    """Return a fresh complete public CapabilityProfile, or refuse an unknown name.

    Allowances in the public setup are *total additional occupied extents* in
    X/Y/Z, not per-side offsets. A03 adds each allowance exactly once. The
    named synthetic envelope describes only the fixed XYZ setup in this card.
    """
    if name not in {"standard", "relaxed"}:
        raise ValueError(f"unknown synthetic capability profile: {name!r}")
    relaxed = name == "relaxed"
    applicability = {"materials": dict(MATERIALS), "material_classes": ["metal", "plastic"]}

    def card(rule_id, source, paraphrase, units, threshold, comparison, severity,
             precedence, limits):
        return {
            "id": rule_id, "version": PROFILE_VERSION, "source": source,
            "retrieved": RETRIEVED, "paraphrase": paraphrase,
            "applicability": {"materials": dict(applicability["materials"]),
                              "material_classes": list(applicability["material_classes"])},
            "units": units, "threshold": threshold, "comparison": comparison,
            "severity": severity, "precedence": precedence, "limits": limits,
            "synthetic_value": True,
        }

    result = {
        "schema_version": VERSION, "id": f"synthetic-{name}",
        "version": PROFILE_VERSION, "synthetic": True,
        "scope": "RFQFuzz project-selected regression policy for one-solid plate, bore-block and open-pocket fixtures; fixed XYZ setup; no production certification",
        "unsupported_operations": ["CAM", "toolpath collision", "workholding synthesis", "turning", "five-axis machining", "finish compatibility or thickness prediction"],
        "rules": [
            card("A01", WALL_SOURCE,
                 "Published thin-feature recommendations differ; reduced stiffness can increase machining risk. RFQFuzz selects its own metal/plastic advisory values.",
                 "mm", {"metal": 0.5 if relaxed else 0.8, "plastic": 1.0 if relaxed else 1.5},
                 COMPARISONS["A01"], "advisory",
                 "Selected public synthetic profile governs this advisory; an advisory never overrides an explicit engineering requirement.",
                 "Requires an independently measured minimum wall for the declared feature and known material/class. No tool, vibration or actual part feasibility proof."),
            card("A02", BORE_SOURCE,
                 "The guide separates recommended, typical and special-tooling hole depths. RFQFuzz chooses a depth/diameter advisory without imposing a universal maximum.",
                 "dimensionless depth/diameter", {"metal": 8.0 if relaxed else 4.0, "plastic": 6.0 if relaxed else 4.0},
                 COMPARISONS["A02"], "advisory",
                 "Selected public synthetic profile governs; depth means the declared cylindrical bore depth, not drill-tip depth or counterbore depth.",
                 "Requires independent bore diameter and cylindrical depth. Non-standard tooling, drill-tip shape, machining process and chip evacuation are not solved."),
            card("A03", ENVELOPE_SOURCE,
                 "Published service envelopes vary with setup and material. RFQFuzz selects a named synthetic XYZ capacity, with explicit stock and fixture occupied extents.",
                 "mm XYZ total occupied extent",
                 {"setup_name": f"synthetic-{name}-XYZ", "orientation": "XYZ",
                  "envelope_mm": [240.0, 160.0, 100.0] if relaxed else [120.0, 80.0, 50.0],
                  "allowance_convention": "total_added_extent_per_axis"},
                 COMPARISONS["A03"], "profile_exclusion",
                 "Only the named selected profile and declared XYZ orientation govern; no automatic axis permutation or assumed zero allowance.",
                 "Exclusion is solely from this named setup. It does not exclude another machine, orientation, tool or fixture. Allowances are total additions, not per-side values."),
            card("A04", STAGE_SOURCE,
                 "Service defaults and explicit requirements can differ. The retrieved CNC standards section does not establish a finish-stage default; RFQFuzz owns the synthetic default here.",
                 "manufacturing stage", {"default_tolerance_stage": None if relaxed else "before_finish"},
                 COMPARISONS["A04"], "missing_information",
                 "Explicit manufacturing.tolerance_stage overrides the selected public synthetic default. An invalid explicit stage never falls back to a default.",
                 "Establishes inspection-stage context only. It does not establish finish/material compatibility, compensate coating thickness or reconcile contradictory geometry stages."),
        ],
    }
    return validate_profile(result)


def default_profile() -> CapabilityProfile:
    """Convenience alias for the standard project-selected profile."""
    return profile()


def _number(value, *, positive=False):
    try:
        return type(value) in (int, float) and math.isfinite(value) and (value > 0 if positive else value >= 0)
    except OverflowError:
        return False


def _vector(value, *, positive=False):
    return isinstance(value, (list, tuple)) and len(value) == 3 and all(_number(x, positive=positive) for x in value)


def evaluate(profile: CapabilityProfile, rule_id: str, measurements: dict,
             manufacturing: dict, setup: dict) -> dict[str, str]:
    """Evaluate one rule on public premises and independently supplied measures.

    Missing premises return missing_information; supplied unsupported/invalid
    values return unsupported. Neither becomes clear. Malformed profile records
    fail the frozen contract with ValueError. No packet parsing or network I/O is
    performed here. The caller records actual artifact witnesses separately.
    """
    selected = validate_profile(profile)

    def result(conclusion, reason):
        return {"conclusion": conclusion,
                "reason": f"{selected['id']}@{selected['version']} / {rule_id}@{rule['version'] if rule else 'unknown'}: {reason}",
                "rule_id": rule_id}

    rule = next((r for r in selected["rules"] if r["id"] == rule_id), None)
    if rule is None:
        return result("unsupported", "rule is outside A01-A04")
    if rule["comparison"] != COMPARISONS[rule_id] or rule["units"] != RULE_UNITS[rule_id] or rule["severity"] != SEVERITIES[rule_id]:
        return result("unsupported", "rule comparator, units or severity is unsupported by this evaluator")
    if not all(isinstance(x, dict) for x in (measurements, manufacturing, setup)):
        return result("unsupported", "measurements, manufacturing and setup must be objects")
    application = rule["applicability"]
    if not isinstance(application, dict) or not isinstance(application.get("materials"), dict):
        return result("unsupported", "this evaluator requires a finite public material/class mapping")
    material = manufacturing.get("material")
    material_class = manufacturing.get("material_class")
    if any(x is not None and not isinstance(x, str) for x in (material, material_class)):
        return result("unsupported", "material and material_class must be declared strings")
    if material not in application["materials"] or material_class not in application.get("material_classes", []):
        return result("missing_information", "no declared applicability for this material/profile combination")
    if application["materials"][material] != material_class:
        return result("unsupported", "material and material_class disagree with the declared profile mapping")
    threshold = rule["threshold"]
    if not isinstance(threshold, dict):
        return result("unsupported", "unsupported threshold representation")

    if rule_id in {"A01", "A02"}:
        limit = threshold.get(material_class)
        if not _number(limit, positive=True):
            return result("unsupported", "missing or invalid class threshold")
        keys = ("wall_mm",) if rule_id == "A01" else ("bore_depth_mm", "bore_diameter_mm")
        if any(measurements.get(key) is None for key in keys):
            return result("missing_information", f"required independent measurements: {', '.join(keys)}")
        if any(not _number(measurements[key], positive=True) for key in keys):
            return result("unsupported", "measurements must be positive finite values in declared mm units")
        value = measurements["wall_mm"] if rule_id == "A01" else measurements["bore_depth_mm"] / measurements["bore_diameter_mm"]
        if not math.isfinite(value):
            return result("unsupported", "depth/diameter is not finite")
        alert = value < limit if rule_id == "A01" else value > limit
        relation = "below" if rule_id == "A01" else "above"
        detail = "wall thickness" if rule_id == "A01" else "cylindrical bore depth/diameter"
        return result("advisory" if alert else "supported_clear",
                      f"{detail} {value:.12g} {'is ' + relation if alert else 'does not cross'} the project-selected {material_class} advisory threshold {limit:.12g}; no general feasibility conclusion")

    if rule_id == "A03":
        if setup.get("orientation") is None:
            return result("missing_information", "declared setup orientation is required")
        if setup["orientation"] != "XYZ" or threshold.get("orientation") != "XYZ":
            return result("unsupported", "only the declared XYZ setup is supported")
        if threshold.get("allowance_convention") != "total_added_extent_per_axis":
            return result("unsupported", "unsupported allowance convention")
        capacity = threshold.get("envelope_mm")
        if not _vector(capacity, positive=True) or not isinstance(threshold.get("setup_name"), str) or not threshold["setup_name"].strip():
            return result("unsupported", "named setup needs a positive XYZ capacity")
        envelope = measurements.get("envelope_mm")
        stock = setup.get("stock_allowance_mm")
        fixture = setup.get("fixture_allowance_mm")
        if any(x is None for x in (envelope, stock, fixture)):
            return result("missing_information", "independent envelope, stock allowance and fixture allowance must all be explicit")
        if not _vector(envelope, positive=True) or not _vector(stock) or not _vector(fixture):
            return result("unsupported", "envelope must be positive and allowances nonnegative finite XYZ vectors")
        occupied = [envelope[i] + stock[i] + fixture[i] for i in range(3)]
        if not all(math.isfinite(x) for x in occupied):
            return result("unsupported", "total occupied extent is not finite")
        axes = ["XYZ"[i] for i in range(3) if occupied[i] > capacity[i]]
        return result("profile_exclusion" if axes else "supported_clear",
                      f"named setup {threshold['setup_name']}: total occupied XYZ {occupied} mm (part + total stock + total fixture) versus {capacity} mm; "
                      + (f"outside on {', '.join(axes)} only in this setup" if axes else "inside or on this setup boundary only"))

    stage = manufacturing.get("tolerance_stage")
    if stage is not None and (not isinstance(stage, str) or stage not in {"before_finish", "after_finish"}):
        return result("unsupported", "invalid explicit tolerance stage; no default applied")
    finish = manufacturing.get("finish")
    if not isinstance(finish, str) or not finish.strip() or finish.casefold().strip() in UNKNOWN:
        return result("missing_information", "finish context is unspecified")
    if stage is not None:
        return result("supported_clear", f"explicit public tolerance stage {stage} governs finish {finish}; profile default is subordinate; finish compatibility is unevaluated")
    default = threshold.get("default_tolerance_stage")
    if default is not None and (not isinstance(default, str) or default not in {"before_finish", "after_finish"}):
        return result("unsupported", "invalid public synthetic stage default")
    if default is None:
        return result("missing_information", "no explicit tolerance stage and no selected public profile default")
    return result("supported_clear", f"selected public project-owned default establishes {default} for finish {finish}; no coating compensation or vendor CNC default inferred")
