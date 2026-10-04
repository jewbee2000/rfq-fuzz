"""Finite semantic authoring operators. Private intent never supplies an oracle.

The suite intentionally includes repaired controls, valid lookalikes, profile
counterfactuals and uncertainty. Final artifact validation remains independent.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from pathlib import Path

from .contracts import VERSION, digest, require, validate_mutation, write_json
from .generation import generate_case, parameters_for
from .profiles import profile

SUITE_VERSION = "core-1.0"
POLICIES = {
    "O01": (["Explicit H1 bore mapping", "Same-stage diameter unless public transition or REF control"], ["drawing.H1 DIAMETER", "context.authority.dimensions", "context.manufacturing.model_stage", "context.manufacturing.transition", "drawing.TRANSITION"], ["STEP geometry unchanged", "Other annotations unchanged", "Counts, units, material, release and RQ1 unchanged"]),
    "O02": (["Plate H1 group has four actual members", "Scope is publicly mapped"], ["drawing.H1 COUNT", "drawing.plan.H1 versus OTHER labels", "context.features.H1 centers and scope"], ["STEP geometry unchanged", "Diameter, units, material, stages, RQ1 and release unchanged"]),
    "O03": (["Supported globally governed dimensions", "STEP unit declaration is millimetres"], ["drawing.UNITS", "drawing.governed numeric dimensions", "context.units.drawing"], ["STEP geometry unchanged", "One dimensional root cause", "Material, stages, RQ1, release and count unchanged"]),
    "O04": (["Two global material declarations", "Public material-precedence policy"], ["drawing.MATERIAL", "context.authority.material_precedence"], ["STEP geometry and dimensional callouts unchanged", "Units, stages, RQ1 and release unchanged"]),
    "O05": (["RQ1 explicitly names required visible surface roughness", "STEP alone cannot represent RQ1"], ["drawing.SURFACE ROUGHNESS", "drawing.SURFACE FINISH", "context.requirements", "valid_alternative_only.drawing model dimensions with public STEP authority"], ["STEP unchanged", "Units, material, stages, release and profile unchanged", "Required drawing-only surface specification remains required when public RQ1 says so"]),
    "O06": (["Visible drawing identity", "STEP product model identity", "Public permitted release pairs"], ["drawing.DRAWING REV", "context.release_association.drawing_revision", "context.release_association.permitted_pairs"], ["STEP geometry/model identity unchanged", "Dimensions, units, material, stages, RQ1 and profile unchanged"]),
    "A01": (["Top-open rectangular pocket", "W1 is mapped +X wall", "Material-dependent named profile"], ["geometry.W1 wall", "context.profile", "context.manufacturing.material and material_class"], ["Other topology remains one planar solid", "Drawing must faithfully represent changed geometry", "Package obligations remain clear"]),
    "A02": (["Central blind bore with visible top-origin depth", "Named advisory depth/diameter policy"], ["geometry.H1 depth", "context.profile", "context.manufacturing.material and material_class"], ["Blind floor remains", "Drawing faithfully represents changed geometry", "Package obligations remain clear"]),
    "A03": (["Explicit XYZ setup", "Public stock and fixture allowances", "Named finite envelope"], ["geometry.envelope", "context.setup allowances", "context.profile"], ["Supported one-solid topology", "Drawing faithfully represents changed geometry", "No universal machinability assertion"]),
    "A04": (["Public finish and tolerance-stage context", "Public profile default and precedence"], ["context.manufacturing.finish and tolerance_stage", "drawing.FINISH and TOLERANCE STAGE", "context.profile"], ["Geometry and package obligations remain clear", "Missing stage without default is uncertainty"]),
}


def _base_parameters(family, index):
    if family == "plate":
        return {"width": 80. + index * 2, "length": 50. + index, "height": 8. + index * .4, "diameter": 6. + index * .2}
    if family == "bore_block":
        diameter = 6. + index * .2
        return {"width": 60. + index * 2, "length": 40. + index, "height": 35. + index, "diameter": diameter, "depth": diameter * 4, "counterbore_diameter": diameter + 6, "counterbore_depth": 4.}
    return {"width": 60. + index * 2, "length": 40. + index, "height": 20. + index, "pocket_width": 50. + index * 2, "pocket_length": 30. + index, "pocket_depth": 12., "wall": 5.}


def _spec(operator, variant, ancestry, family, params, seed, drawing=None, context=None, profile_name="standard", index=0):
    require(operator in POLICIES, "unsupported operator")
    parameters_for(family, params)
    # A source family/layout is held in one partition. This avoids shipping twins
    # or this generator's identical drawing style across apparent holdouts. The
    # independent transfer authoring step adds its own reserved layout later.
    partition = "development"
    prerequisites, allowed, invariants = POLICIES[operator]
    value = {"schema_version": VERSION, "case_id": "pk-" + digest([SUITE_VERSION, seed, ancestry, variant, index])[:12],
             "operator": operator, "variant": variant, "ancestry": ancestry, "partition": partition, "seed": seed,
             "prerequisites": prerequisites, "allowed_deltas": allowed, "invariants": invariants,
             "source_parameters": {"family": family, "parameters": deepcopy(params), "drawing_overrides": deepcopy(drawing or {}), "context_overrides": deepcopy(context or {}), "profile_name": profile_name, "layout_ancestry": "bounded-vector-a4-v1"}}
    return validate_mutation(value)


def objective_group(operator, index=0, seed=42):
    """One supported defective/repaired/valid triplet, with finite refusal."""
    require(operator in {f"O{i:02}" for i in range(1, 7)}, "objective operator required")
    require(type(index) is int and 0 <= index < 6, "objective variant index outside bounds")
    family = "plate" if operator == "O02" else ("plate" if index % 2 == 0 else "bore_block") if operator == "O01" else ("plate", "bore_block", "pocket_block")[index % 3]
    params = _base_parameters(family, index)
    ancestry = f"source-{operator.lower()}-{index:02}"
    rows = []
    for variant in ("defective", "repaired", "valid_alternative"):
        drawing, context = {}, {}
        if operator == "O01":
            if variant != "repaired":
                drawing["h1_diameter"] = params["diameter"] + .8
            if variant == "valid_alternative":
                if index % 2:
                    drawing["diameter_ref"] = True
                    context["authority"] = {"dimensions": "step"}
                else:
                    context["manufacturing"] = {"model_stage": "intermediate", "transition": {"operation": "ream", "feature_id": "H1", "from_stage": "intermediate", "to_stage": "finished", "target": "drawing H1 diameter callout"}}
        elif operator == "O02":
            if variant == "defective":
                drawing["h1_count"] = 3
            elif variant == "valid_alternative":
                drawing.update(h1_count=2, h1_group_members=[0, 1])
        elif operator == "O03":
            if variant != "repaired":
                drawing.update(drawing_units="in", convert_dimensions=variant == "valid_alternative")
        elif operator == "O04":
            if variant == "defective":
                drawing["drawing_material"] = "7075-T6"
            elif variant == "valid_alternative":
                drawing["drawing_material"] = "AL6061-T6" if index % 2 == 0 else "7075-T6"
                if index % 2:
                    context["authority"] = {"material_precedence": "contract"}
        elif operator == "O05":
            if variant != "repaired":
                drawing["omit"] = ["SURFACE ROUGHNESS"]
            if variant == "valid_alternative":
                if index % 2:
                    drawing["extra_notes"] = ["SURFACE FINISH = Ra 3.20 um"]
                    context["requirements"] = [{"id": "RQ1", "representation": "drawing", "description": "A visible SURFACE ROUGHNESS = 3.20 um or SURFACE FINISH = Ra 3.20 um note is required for release. STEP alone does not represent it."}]
                else:
                    context["requirements"] = []
        else:
            if variant != "repaired":
                drawing["drawing_revision"] = "B"
            if variant == "valid_alternative":
                context["release_association"] = {"drawing_revision": "B", "permitted_pairs": [["A", "B"]]}
        rows.append(_spec(operator, variant, ancestry, family, params, seed, drawing, context))
    return rows


def _advisory_groups(seed):
    rows = []
    for i in range(3):
        # Counterfactual profiles are public; a synthetic recommendation is not
        # a process impossibility, and exact equality does not trigger '<'.
        for alternative in (False, True):
            variant = "profile_alternative" if alternative else "defective"
            material = {"manufacturing": {"material": "ABS", "material_class": "plastic"}} if i == 1 else {}
            wall = 1.2 if i == 1 else .6
            params = dict(_base_parameters("pocket_block", i), wall=wall)
            prof = "relaxed" if alternative else "standard"
            if i == 2:
                params["wall"] = .8 if alternative else .79
                prof, variant = "standard", "boundary" if alternative else "defective"
            rows.append(_spec("A01", variant, f"source-a01-{i:02}", "pocket_block", params, seed, context=material, profile_name=prof))
            params = dict(_base_parameters("bore_block", i), diameter=6., depth=30. if i else 26.)
            prof = "relaxed" if alternative else "standard"
            variant = "profile_alternative" if alternative else "defective"
            if i == 0 and alternative:
                params["depth"], prof, variant = 24., "standard", "boundary"
            rows.append(_spec("A02", variant, f"source-a02-{i:02}", "bore_block", params, seed, context=material, profile_name=prof))
            family = ("plate", "bore_block", "pocket_block")[i]
            params = dict(_base_parameters(family, i), width=125. if i == 0 else 120. if i == 1 else 118.)
            if family == "pocket_block":
                params["pocket_width"] = params["width"] - 10
            context = {} if i == 0 else {"setup": {"stock_allowance_mm": [2., 0., 0.], "fixture_allowance_mm": [0. if i == 1 else 1., 0., 0.]}}
            rows.append(_spec("A03", "profile_alternative" if alternative else "defective", f"source-a03-{i:02}", family, params, seed, context=context, profile_name="relaxed" if alternative else "standard"))
            context = {"manufacturing": {"finish": "anodize" if i != 1 else "paint", "tolerance_stage": None}}
            if i == 2 and alternative:
                context["manufacturing"]["tolerance_stage"] = "after_finish"
            rows.append(_spec("A04", "repaired" if alternative else "underdetermined", f"source-a04-{i:02}", family, _base_parameters(family, i), seed, context=context, profile_name="standard" if alternative and i < 2 else "relaxed"))
    return rows


def _underdetermined(seed):
    rows = []
    for i in range(12):
        case = i % 4
        family = "plate" if case < 2 else "pocket_block" if case == 2 else "bore_block"
        params = _base_parameters(family, i // 4)
        drawing, context, prof = {}, {}, "standard"
        if case == 0:
            operator = "O01"
            drawing["omit"] = ["H1 DIAMETER"]
        elif case == 1:
            operator = "O01"
            drawing["h1_diameter"] = params["diameter"] + .8
            context["manufacturing"] = {"model_stage": "intermediate", "transition": None}
        elif case == 2:
            operator = "A01"
            context["manufacturing"] = {"material": "Unspecified alloy", "material_class": "unknown"}
        else:
            operator = "A04"
            context["manufacturing"] = {"finish": "anodize", "tolerance_stage": None}
            prof = "relaxed"
        rows.append(_spec(operator, "underdetermined", f"source-uncertain-{i:02}", family, params, seed, drawing, context, prof))
    return rows


def specifications(seed=42):
    require(type(seed) is int and 0 <= seed < 2**32, "bounded integer seed required")
    rows = [row for op in (f"O{i:02}" for i in range(1, 7)) for index in range(6) for row in objective_group(op, index, seed)]
    rows.extend(_advisory_groups(seed))
    rows.extend(_underdetermined(seed))
    rows.append(_spec("O05", "valid_alternative", "source-sparse-00", "plate", _base_parameters("plate", 0), seed,
                      drawing={"sparse": True}, context={"authority": {"dimensions": "step"}}))
    require(len(rows) == 145 and len({row["case_id"] for row in rows}) == 145, "opaque ID collision or suite-count bug")
    return rows


def verify_spec(row):
    """Check applicability before applying an operator to caller-supplied intent."""
    validate_mutation(row)
    source = row["source_parameters"]
    require(isinstance(source, dict) and set(source) == {"family", "parameters", "drawing_overrides", "context_overrides", "profile_name", "layout_ancestry"}, "unsupported source intent fields")
    p = parameters_for(source["family"], source["parameters"])
    require(source["layout_ancestry"] == "bounded-vector-a4-v1", "unsupported authoring layout")
    require(source["profile_name"] in {"standard", "relaxed"}, "unsupported public profile")
    operator = row["operator"]
    if operator in {"O01", "O02", "A02"}:
        require(source["family"] in {"plate", "bore_block"}, "operator requires an actual H1 bore")
    if operator == "O02":
        require(source["family"] == "plate" and p["count"] == 4, "scoped-count operator requires four-member source pattern")
    if operator == "A01":
        require(source["family"] == "pocket_block", "wall operator requires a mapped pocket wall")
    if operator == "A02":
        require(source["family"] == "bore_block", "depth operator requires blind bore with explicit top-origin depth")
    return row


def suite_summary(rows, seed):
    return {"schema_version": VERSION, "suite_version": SUITE_VERSION, "seed": seed, "public_cases": len(rows), "configuration_sha256": digest(rows),
            "operator_counts": dict(sorted(Counter(row["operator"] for row in rows).items())),
            "partition_counts": dict(sorted(Counter(row["partition"] for row in rows).items())),
            "limitations": ["Synthetic authored finite obligations only", "All diagrams share one bounded layout; no independent layout transfer claimed", "Final fixtures must pass independent artifact/isolation validation"]}


def generate_suite(dest, seed=42, specs=None):
    dest = Path(dest)
    require(not dest.exists() or not any(dest.iterdir()), "suite destination is not empty; preserve prior evidence")
    rows = specifications(seed) if specs is None else deepcopy(specs)
    require(bool(rows), "empty suite")
    require(len({row["case_id"] for row in rows}) == len(rows), "duplicate case ID")
    for row in rows:
        verify_spec(row)
    for row in rows:
        source = row["source_parameters"]
        generate_case(dest / "public" / row["case_id"], row["case_id"], source["family"], source["parameters"], source["drawing_overrides"], source["context_overrides"], profile(source["profile_name"]))
    # Never place these files in public. Intent describes a planned edit, not
    # ground truth or an expected industrial judgment.
    write_json(dest / "private" / "mutations.json", {"schema_version": VERSION, "warning": "Generator intent is not ground truth", "mutations": rows})
    summary = suite_summary(rows, seed)
    write_json(dest / "private" / "suite.json", summary)
    return dict(summary, output=str(dest))
