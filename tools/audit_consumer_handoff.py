"""Coordinator verifies the independently retained consumer handoff bytes."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence/M5/consumer-environments"
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
complete = read(evidence / "COMPLETE.json")
assert complete["status"] == "copy_complete"
entries = read(evidence / "retained-file-manifest.json")["files"]
for entry in entries:
    path = (evidence / entry["path"]).resolve()
    assert path.is_relative_to(evidence) and path.is_file()
    assert path.stat().st_size == entry["bytes"] and sha(path) == entry["sha256"], entry["path"]
visual = read(evidence / "visual-inspection.json")["platforms"]
platforms = {}
for platform in ("windows", "linux"):
    folder = evidence / platform
    demo = folder / "demo"
    result = read(demo / "demo-result.json")
    assert result["status"] == "passed" and result["cases"] == 15
    assert sorted((c["before"], c["after"]) for c in result["changes"]) == [
        ("correct_clear", "false_alert"), ("detected", "silent_miss")]
    oracle = read(demo / "validation/oracle.json")
    assert oracle["status"] == "valid" and oracle["counts"] == {"valid": 15}
    assert len(oracle["cases"]) == 15 and all(c["status"] == "valid" and c["expectations"] for c in oracle["cases"])
    inspection = read(folder / "report-inspection.json")
    assert inspection["status"] == "observations_passed" and not inspection["failures"]
    assert all(check["observed_ok"] for check in inspection["checks"].values())
    for relative, expected in inspection["inspected_artifact_sha256"].items():
        assert sha(demo / relative) == expected, (platform, relative)
    for run in ("before", "after"):
        observed = read(demo / run / "run.json")
        assert len(observed["score"]["rows"]) == 121
        assert observed["manifest"]["raw_sha256"] == sha(demo / run / "raw-review.json")
        assert observed["manifest"]["oracle_sha256"] == sha(demo / "validation/oracle.json")
    families = folder / "families"
    semantic = read(families / "independent-inspection/semantic-summary.json")["cases"]
    assert len(semantic) == 3 and all(c["result"] == "semantics_confirmed" and c["pdf_png_pixels_identical"] for c in semantic)
    generated = read(families / "workflow/generated-observations/oracle.json")
    assert generated["status"] == "unverified" and generated["counts"] == {"unverified": 3}
    assert all(not c["expectations"] for c in generated["cases"])
    for packet_file in (families / "workflow/generated-suite/public").glob("*/packet.json"):
        family = read(packet_file)["family"]
        assert sha(packet_file.parent / "drawing.png") == visual[platform.title()][family]["sha256"]
    platforms[platform] = {"valid_replay_cases": 15, "rows_per_response": 121,
                           "changed_duties": 2, "fresh_families_semantically_checked": 3,
                           "fresh_unattested_cases": 3, "report_inspection": "passed",
                           "recorded_resource_limits": result["resource_limits"]}
result = {"status": "passed", "retained_manifest_files_checked": len(entries),
          "platforms": platforms,
          "limitations": "Verifies handoff hashes/accounting and actual independent-check records; does not replace native readers or human engineering review."}
(root / "evidence/M5/consumer-handoff-audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
