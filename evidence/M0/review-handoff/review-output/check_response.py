"""Validate the response against the supplied schema subset and retained hashes."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent.parent
schema = json.loads((ROOT / "review-result.schema.json").read_text(encoding="utf-8"))
response = json.loads((ROOT / "review-output/review.json").read_text(encoding="utf-8"))
measurements = json.loads((ROOT / "review-output/measurements.json").read_text(encoding="utf-8"))

supported_keywords = {"$schema", "title", "$defs", "$ref", "type", "required",
                      "additionalProperties", "properties", "const", "items", "enum",
                      "uniqueItems", "pattern", "minimum"}

def check(node, value, location):
    assert set(node) <= supported_keywords, f"Unhandled schema keyword: {set(node)-supported_keywords}"
    if "$ref" in node:
        target = schema
        for key in node["$ref"].removeprefix("#/").split("/"):
            target = target[key]
        return check(target, value, location)
    if "const" in node:
        assert value == node["const"], f"{location}: const mismatch"
    if "enum" in node:
        assert value in node["enum"], f"{location}: enum mismatch"
    types = node.get("type", [])
    types = types if isinstance(types, list) else [types]
    matches = {"object": isinstance(value, dict), "array": isinstance(value, list),
               "string": isinstance(value, str), "number": isinstance(value, (int,float)) and not isinstance(value,bool),
               "null": value is None}
    if types:
        assert any(matches.get(t,False) for t in types), f"{location}: type mismatch"
    if isinstance(value, dict):
        assert set(node.get("required", [])) <= set(value), f"{location}: required key missing"
        properties = node.get("properties", {})
        if node.get("additionalProperties") is False:
            assert set(value) <= set(properties), f"{location}: extra properties"
        for key, content in value.items():
            if key in properties:
                check(properties[key], content, f"{location}.{key}")
    if isinstance(value, list):
        if node.get("uniqueItems"):
            assert len(value) == len({json.dumps(v,sort_keys=True) for v in value}), f"{location}: duplicates"
        if "items" in node:
            for index, content in enumerate(value):
                check(node["items"], content, f"{location}[{index}]")
    if isinstance(value, str) and "pattern" in node:
        assert re.search(node["pattern"], value), f"{location}: pattern mismatch"
    if isinstance(value, (int,float)) and not isinstance(value,bool) and "minimum" in node:
        assert value >= node["minimum"], f"{location}: below minimum"

check(schema, response, "response")
expected_cases = {folder.name for folder in (ROOT / "public").iterdir() if folder.is_dir()}
actual_cases = [result["case_id"] for result in response["results"]]
assert len(actual_cases) == len(expected_cases) and set(actual_cases) == expected_cases
for result in response["results"]:
    path = ROOT / "public" / result["case_id"] / "packet.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == result["packet_sha256"]
    assert result["reviewed_obligations"] == ["bore_group_consistency"]
    assert set(result["reviewed_modalities"]) == {"step","pdf","png","context"}
    raw_file = result["raw_output_reference"].split("#")[0]
    assert (ROOT / raw_file).is_file()
    for finding in result["findings"] + result["assertions"]:
        assert finding["obligation"] == "bore_group_consistency" and finding["feature_id"] == "H1"
for case in measurements["cases"]:
    for name, observed_hash in case["actual_file_sha256"].items():
        assert hashlib.sha256((ROOT / "public" / case["case_id"] / name).read_bytes()).hexdigest() == observed_hash
report = {"schema_compliant": True,
          "schema_method": "Local stdlib recursive checker implements every validation keyword used by the supplied schema; no project validator imported",
          "one_result_per_public_case": True, "actual_packet_hashes_match_response": True,
          "public_bytes_match_initial_measurement_hashes": True,
          "all_required_modalities_and_only_named_obligation": True,
          "evidence_references_exist": True, "case_ids": actual_cases}
(ROOT / "review-output/response-check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
