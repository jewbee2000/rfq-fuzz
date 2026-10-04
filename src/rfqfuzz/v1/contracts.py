"""Strict, dependency-free v1 boundaries for finite review obligations.

These checks are intentionally separate from the frozen M0 readers. JSON schemas
in schemas/v1 document the transport; these functions enforce semantic invariants.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
from pathlib import Path
from . import VERSION

CONCLUSIONS = frozenset({"contradiction", "profile_exclusion", "advisory", "missing_information", "supported_clear", "unsupported"})
STATES = frozenset({"completed", "partial", "unsupported", "timeout", "error"})
VALIDATION_STATES = frozenset({"valid", "invalid_fixture", "unsupported_input", "unverified", "timeout"})
TRACKS = frozenset({"package_consistency", "cnc_advisory"})
MODALITIES = frozenset({"step", "pdf", "png", "context"})
FAMILIES = frozenset({"plate", "bore_block", "pocket_block"})
PRIVATE_KEYS = frozenset({"expected", "expectations", "expected_conclusion", "operator", "mutation", "variant", "oracle", "answer", "partition", "ancestry", "source_parameters"})
MAX_JSON_BYTES = 4_000_000

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

def load_json(path, limit=MAX_JSON_BYTES):
    path = Path(path)
    require(path.stat().st_size <= limit, "JSON size limit exceeded")
    def unique(items):
        value = {}
        for key, item in items:
            require(key not in value, f"duplicate JSON key: {key}")
            value[key] = item
        return value
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))

def fields(value, required, optional=(), label="record"):
    require(isinstance(value, dict), f"{label} must be an object")
    require(set(required) <= value.keys(), f"{label} missing: {sorted(set(required) - value.keys())}")
    require(value.keys() <= set(required) | set(optional), f"{label} unknown fields: {sorted(value.keys() - set(required) - set(optional))}")

def version(value):
    require(value.get("schema_version") == VERSION, "unsupported schema version; explicit migration required")

def nonempty(value, label):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= 8192, f"invalid {label}")

def finite(value, label, positive=False):
    require(type(value) in (int, float) and math.isfinite(value) and (not positive or value > 0), f"invalid {label}")

def vector(value, label):
    require(isinstance(value, list) and len(value) == 3, f"invalid {label}")
    for item in value:
        finite(item, label)

def private_scan(value):
    if isinstance(value, dict):
        require(not (value.keys() & PRIVATE_KEYS), "private answer or mutation metadata in public packet")
        for item in value.values():
            private_scan(item)
    elif isinstance(value, list):
        for item in value:
            private_scan(item)

def validate_profile(p):
    fields(p, ("schema_version", "id", "version", "synthetic", "rules", "scope", "unsupported_operations"), label="CapabilityProfile")
    version(p)
    nonempty(p["id"], "profile ID")
    nonempty(p["version"], "profile version")
    require(p["synthetic"] is True, "v1 accepts explicitly synthetic profiles only")
    require(isinstance(p["rules"], list) and len(p["rules"]) == 4, "profile needs A01–A04 rule cards")
    require({r["id"] for r in p["rules"]} == {"A01", "A02", "A03", "A04"}, "rule IDs must be unique")
    for r in p["rules"]:
        fields(r, ("id", "version", "source", "retrieved", "paraphrase", "applicability", "units", "threshold", "comparison", "severity", "precedence", "limits", "synthetic_value"), label="rule card")
        require(r["severity"] in {"advisory", "profile_exclusion", "missing_information"}, "invalid rule severity")
        require(r["synthetic_value"] is True, "threshold ownership must be explicit")
        for key in ("version", "source", "retrieved", "paraphrase", "comparison", "precedence", "limits"):
            nonempty(r[key], key)
    return p

def validate_packet(p):
    fields(p, ("schema_version", "case_id", "part_id", "family", "units", "release_association", "authority", "manufacturing", "setup", "profile", "features", "requirements", "obligations", "artifacts", "render"), label="PacketSpec")
    version(p)
    private_scan(p)
    require(isinstance(p["case_id"], str) and re.fullmatch(r"pk-[0-9a-f]{12}", p["case_id"]), "case ID must be opaque")
    nonempty(p["part_id"], "part ID")
    require(p["family"] in FAMILIES, "unsupported family")
    fields(p["units"], ("model", "drawing"), label="units")
    require(p["units"]["model"] == "mm" and p["units"]["drawing"] in {"mm", "in"}, "unsupported declared units")
    release = p["release_association"]
    fields(release, ("model_id", "model_revision", "drawing_id", "drawing_revision", "permitted_pairs"), label="release association")
    for key in ("model_id", "model_revision", "drawing_id", "drawing_revision"):
        nonempty(release[key], key)
    require(isinstance(release["permitted_pairs"], list) and bool(release["permitted_pairs"]), "missing approved release association")
    require(all(isinstance(pair, list) and len(pair) == 2 and all(isinstance(x, str) for x in pair) for pair in release["permitted_pairs"]), "invalid revision pairs")
    fields(p["authority"], ("geometry", "dimensions", "material_precedence", "process", "release"), label="authority")
    require(p["authority"]["geometry"] == "step", "geometry authority must be STEP")
    require(p["authority"]["dimensions"] in {"drawing", "step"}, "missing dimension authority")
    require(p["authority"]["material_precedence"] in {"equal", "drawing", "contract"}, "invalid material precedence")
    for key in ("process", "release"):
        nonempty(p["authority"][key], key)
    fields(p["manufacturing"], ("model_stage", "drawing_stage", "transition", "material", "material_class", "finish", "tolerance_stage"), label="manufacturing")
    for key in ("model_stage", "drawing_stage", "material", "material_class", "finish"):
        nonempty(p["manufacturing"][key], key)
    require(p["manufacturing"]["tolerance_stage"] in {None, "before_finish", "after_finish"}, "invalid tolerance stage")
    require(p["manufacturing"]["transition"] is None or isinstance(p["manufacturing"]["transition"], dict), "invalid transition")
    fields(p["setup"], ("orientation", "stock_allowance_mm", "fixture_allowance_mm"), label="setup")
    require(p["setup"]["orientation"] == "XYZ", "unsupported setup orientation")
    for key in ("stock_allowance_mm", "fixture_allowance_mm"):
        vector(p["setup"][key], key)
        require(all(x >= 0 for x in p["setup"][key]), "negative allowance")
    validate_profile(p["profile"])
    require(isinstance(p["features"], list) and bool(p["features"]), "missing feature mappings")
    feature_ids = set()
    for f in p["features"]:
        fields(f, ("id", "type", "drawing_association"), ("centers_mm",), label="feature")
        nonempty(f["id"], "feature ID")
        require(f["id"] not in feature_ids, "duplicate feature ID")
        feature_ids.add(f["id"])
        nonempty(f["drawing_association"], "drawing association")
        if "centers_mm" in f:
            for center in f["centers_mm"]:
                vector(center, "feature center")
    require(isinstance(p["requirements"], list), "invalid finite requirements")
    for r in p["requirements"]:
        fields(r, ("id", "representation", "description"), label="critical requirement")
        require(r["representation"] in {"drawing", "step", "either"}, "unsupported requirement representation")
        nonempty(r["description"], "required public engineering context")
    require(isinstance(p["obligations"], list) and bool(p["obligations"]), "missing finite obligations")
    ids = set()
    for o in p["obligations"]:
        fields(o, ("id", "track", "category", "feature_id", "required_modalities"), label="obligation")
        require(o["id"] not in ids, "duplicate obligation")
        ids.add(o["id"])
        require(o["track"] in TRACKS and o["feature_id"] in feature_ids | {"document"}, "invalid track or mapping")
        require(bool(o["required_modalities"]) and set(o["required_modalities"]) <= MODALITIES, "invalid modality premise")
    require(isinstance(p["artifacts"], list) and len(p["artifacts"]) == 3, "three artifacts required")
    require({a["path"] for a in p["artifacts"]} == {"part.step", "drawing.pdf", "drawing.png"}, "invalid artifact paths")
    for a in p["artifacts"]:
        fields(a, ("path", "sha256", "media_type"), label="artifact")
        require(re.fullmatch(r"[0-9a-f]{64}", a["sha256"]), "invalid artifact hash")
    fields(p["render"], ("renderer", "dpi"), label="render provenance")
    finite(p["render"]["dpi"], "render DPI", positive=True)
    return p

def read_packet(folder):
    folder = Path(folder).resolve()
    p = validate_packet(load_json(folder / "packet.json"))
    for a in p["artifacts"]:
        path = folder / a["path"]
        require(path.resolve().parent == folder, "artifact escape or symlink")
        require(0 < path.stat().st_size <= 16_000_000, "artifact size limit exceeded")
        require(sha256(path) == a["sha256"], f"artifact hash mismatch: {a['path']}")
    return p

def validate_mutation(m):
    fields(m, ("schema_version", "case_id", "operator", "variant", "ancestry", "partition", "seed", "prerequisites", "allowed_deltas", "invariants", "source_parameters"), label="MutationSpec")
    version(m)
    require(m["operator"] in {f"O{i:02}" for i in range(1, 7)} | {f"A{i:02}" for i in range(1, 5)}, "unsupported mutation")
    require(m["variant"] in {"defective", "repaired", "valid_alternative", "underdetermined", "boundary", "profile_alternative"}, "invalid variant")
    require(m["partition"] in {"development", "holdout", "transfer"}, "invalid partition")
    require(bool(m["prerequisites"]) and bool(m["invariants"]), "mutation contract needs prerequisites and invariants")
    return m

def validate_oracle(o):
    fields(o, ("schema_version", "oracle_version", "case_id", "packet_sha256", "status", "reasons", "measurements", "drawing", "expectations", "isolation"), label="OracleRecord")
    version(o)
    require(o["status"] in VALIDATION_STATES, "invalid fixture state")
    if o["status"] != "valid":
        require(not o["expectations"] and bool(o["reasons"]), "invalid fixtures must not be scorable")
    for e in o["expectations"]:
        fields(e, ("obligation_id", "track", "category", "feature_id", "conclusion", "rule_id", "evidence", "root_cause", "operator"), label="expected obligation")
        require(e["conclusion"] in CONCLUSIONS and e["track"] in TRACKS, "invalid expected semantics")
        require(bool(e["evidence"]), "expectation lacks independent artifact evidence")
    return o

def validate_review(r):
    fields(r, ("schema_version", "reviewer", "results"), label="ReviewResult")
    version(r)
    fields(r["reviewer"], ("name", "version", "configuration"), label="reviewer provenance")
    for value in r["reviewer"].values():
        nonempty(value, "reviewer provenance")
    require(isinstance(r["results"], list), "results must be a list")
    ids = set()
    for row in r["results"]:
        fields(row, ("case_id", "packet_sha256", "status", "reviewed_modalities", "reviewed_obligations", "findings", "assertions", "runtime_seconds", "raw_ref", "reason"), label="review row")
        require(row["case_id"] not in ids, "duplicate review case")
        ids.add(row["case_id"])
        require(row["status"] in STATES, "unknown execution state")
        require(set(row["reviewed_modalities"]) <= MODALITIES, "invalid reviewed modality")
        if row["runtime_seconds"] is not None:
            finite(row["runtime_seconds"], "runtime")
            require(row["runtime_seconds"] >= 0, "negative runtime")
        require(isinstance(row["findings"], list) and isinstance(row["assertions"], list), "invalid findings")
        for item in row["findings"] + row["assertions"]:
            fields(item, ("id", "obligation_id", "category", "conclusion", "feature_id", "evidence", "rationale"), label="Finding")
            require(item["conclusion"] in CONCLUSIONS, "unknown conclusion")
            require(isinstance(item["evidence"], list) and bool(item["evidence"]), "finding needs evidence")
            for witness in item["evidence"]:
                fields(witness, ("artifact", "quote"), ("region",), label="evidence")
                require(witness["artifact"] in {"part.step", "drawing.pdf", "drawing.png", "packet.json"}, "invalid evidence path")
                nonempty(witness["quote"], "evidence witness")
            nonempty(item["rationale"], "finding rationale")
        conclusions = {}
        for item in row["findings"] + row["assertions"]:
            conclusions.setdefault(item["obligation_id"], set()).add(item["conclusion"])
        require(all(len(value) == 1 for value in conclusions.values()), "conflicting assertions for same obligation")
        if row["status"] in {"error", "timeout", "unsupported"}:
            require(not row["findings"] and not row["assertions"], "failed execution cannot assert a decision")
    return r

def validate_manifest(m):
    fields(m, ("schema_version", "suite_sha256", "oracle_sha256", "profile_sha256", "adapter_version", "seed", "environment", "raw_sha256", "limitations", "failures"), label="RunManifest")
    version(m)
    for key in ("suite_sha256", "oracle_sha256", "profile_sha256", "raw_sha256"):
        require(isinstance(m[key], str) and re.fullmatch(r"[0-9a-f]{64}", m[key]), f"invalid {key}")
    return m

def migrate_m0(_value):
    raise ValueError("M0 evidence is immutable; use tools/m0.py replay, not an inferred v1 migration")
