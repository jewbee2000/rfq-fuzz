"""Inspect retained consumer demo artifacts without importing repository logic.

Usage: python check_consumer_report.py DEMO_ROOT OUTPUT_JSON [provenance options]
Requires pypdf and Pillow. Performs no network requests and does not revalidate
geometry, rendering, engineering rules, or oracle correctness.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image
from pypdf import PdfReader


LINUX_PREFIX = "/home/consumer/linux-final-workflow/demo"
DECLARED_COMMIT = "4c98b5f158c5b563ad256184303165e60231c088"
EXPECTED_ARCHIVE_SHA256 = (
    "815297d886c9e2be3a784cd8544efed1b904d750bc2b03caec864b09db0bc3cc"
)
EXPECTED_CHANGES = [
    {
        "case_id": "pk-0236ce4290c1",
        "obligation_id": "obj-material",
        "track": "package_consistency",
        "before": "detected",
        "after": "silent_miss",
    },
    {
        "case_id": "pk-0972292025ad",
        "obligation_id": "obj-diameter",
        "track": "package_consistency",
        "before": "correct_clear",
        "after": "false_alert",
    },
]
FORBIDDEN_KEYS = {
    "expected", "expected_answer", "answer_key", "mutation", "mutation_id",
    "mutation_spec", "operator", "operator_id", "seed", "oracle",
    "oracle_record", "root_cause", "outcome",
}
PRIVATE_MARKER = re.compile(
    r"\b(?:O\d\d|mutation(?:_id)?|oracle|answer[_ -]?key|expected[_ -]?answer|seed)\b",
    re.IGNORECASE,
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = []
        self.unsafe = []
        self.pre = []
        self.buffer = None

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag in {"script", "iframe", "object", "embed", "form", "base"}:
            self.unsafe.append({"tag": tag})
        for name, value in attributes.items():
            if name == "id":
                self.ids.append(value)
            if name in {"href", "src"}:
                self.links.append({"tag": tag, "attr": name, "target": value})
            if name.lower().startswith("on") or name == "srcdoc":
                self.unsafe.append({"attribute": name})
        if tag == "pre":
            self.buffer = []

    def handle_endtag(self, tag):
        if tag == "pre" and self.buffer is not None:
            self.pre.append("".join(self.buffer))
            self.buffer = None

    def handle_data(self, data):
        if self.buffer is not None:
            self.buffer.append(data)


def inspect(root, output, archive_path=None,
            archive_sha256=EXPECTED_ARCHIVE_SHA256,
            declared_commit=DECLARED_COMMIT, linux_prefix=LINUX_PREFIX):
    root = root.resolve()
    output = output.resolve()
    report = root / "report/index.html"
    checks = {}
    failures = []

    def read(relative):
        return json.loads((root / relative).read_text(encoding="utf-8"))

    def check(name, condition, detail):
        checks[name] = {"observed_ok": bool(condition), "detail": detail}
        if not condition:
            failures.append(name)

    before, after = read("before/run.json"), read("after/run.json")
    comparison, demo = read("report/comparison.json"), read("demo-result.json")
    oracle = read("validation/oracle.json")
    key = lambda row: (row["case_id"], row["obligation_id"], row["track"])
    before_rows = {key(row): row for row in before["score"]["rows"]}
    after_rows = {key(row): row for row in after["score"]["rows"]}
    changes = [
        {
            "case_id": item[0], "obligation_id": item[1], "track": item[2],
            "before": before_rows[item]["outcome"],
            "after": after_rows[item]["outcome"],
        }
        for item in before_rows.keys() & after_rows.keys()
        if before_rows[item]["outcome"] != after_rows[item]["outcome"]
    ]
    changes.sort(key=lambda item: (item["case_id"], item["obligation_id"]))
    check(
        "exactly_two_diagnosis_changes",
        changes == EXPECTED_CHANGES
        and changes == comparison["comparisons"][0]["changes"]
        and changes == demo["changes"]
        and before_rows.keys() == after_rows.keys(),
        {"changes": changes, "before_rows": len(before_rows),
         "after_rows": len(after_rows)},
    )
    case_ids = sorted({row["case_id"] for row in before["score"]["rows"]})
    valid_cases = sorted(
        case["case_id"] for case in oracle["cases"] if case["status"] == "valid"
    )
    check(
        "fifteen_case_denominator",
        len(case_ids) == 15 and case_ids == valid_cases
        and oracle["status"] == "valid"
        and all(
            run["score"]["invalid_rate"] == {"numerator": 0, "denominator": 15}
            and not run["score"]["invalid_fixtures"]
            for run in (before, after)
        ),
        {
            "cases": len(case_ids), "oracle_recorded_counts": oracle["counts"],
            "oracle_case_status_counts": dict(Counter(
                case["status"] for case in oracle["cases"])),
            "before_invalid_rate": before["score"]["invalid_rate"],
            "after_invalid_rate": after["score"]["invalid_rate"],
            "scope": "Observed artifact statuses, not geometry revalidation.",
        },
    )
    bindings = []
    for name, run, source in (
        ("before", before, "reference"), ("after", after, "injected")
    ):
        imported = read(name + "/import.json")
        raw = read(name + "/raw-review.json")
        raw_hash = sha256(root / name / "raw-review.json")
        packet_mismatches = [
            result["case_id"] for result in raw["results"]
            if result["packet_sha256"] != sha256(
                root / "inputs/suite/public" / result["case_id"] / "packet.json")
        ]
        bindings.append({
            "run": name, "raw_sha256": raw_hash,
            "raw_matches_import_and_run_hash":
                raw_hash == imported["raw_sha256"] == run["manifest"]["raw_sha256"],
            "raw_matches_retained_input_bytes":
                raw_hash == sha256(root / "inputs" / (source + ".json")),
            "import_response_matches_raw_object": imported["response"] == raw,
            "packet_hash_mismatches": packet_mismatches,
            "results": len(raw["results"]),
            "result_statuses": dict(Counter(
                result["status"] for result in raw["results"])),
            "oracle_sha256_matches_file":
                run["manifest"]["oracle_sha256"] == sha256(root / "validation/oracle.json"),
        })
    check(
        "retained_response_source_binding",
        all(
            binding["raw_matches_import_and_run_hash"]
            and binding["raw_matches_retained_input_bytes"]
            and binding["import_response_matches_raw_object"]
            and not binding["packet_hash_mismatches"]
            and binding["results"] == 15
            and binding["oracle_sha256_matches_file"]
            for binding in bindings
        ), bindings,
    )
    premise_keys = ["suite_sha256", "oracle_sha256", "profile_sha256", "seed", "adapter_version"]
    check(
        "shared_run_premise_bindings",
        all(before["manifest"][name] == after["manifest"][name]
            == comparison["manifest"][name] for name in premise_keys),
        {name: before["manifest"][name] for name in premise_keys},
    )

    recorded_report = demo["report"]
    normalized_recorded = recorded_report.replace("\\", "/")
    linux_prefix = linux_prefix.replace("\\", "/").rstrip("/")
    mapping = {"recorded_prefix": linux_prefix, "local_prefix": str(root)}
    mapping_applied = normalized_recorded == linux_prefix or normalized_recorded.startswith(linux_prefix + "/")
    if mapping_applied:
        suffix = normalized_recorded[len(linux_prefix):].lstrip("/")
        resolved_recorded = (root / suffix).resolve()
    else:
        resolved_recorded = Path(recorded_report).resolve()
    check(
        "recorded_report_path_binding",
        resolved_recorded == report.resolve() and resolved_recorded.is_file(),
        {
            "recorded_report_path": recorded_report,
            "inspected_report_path": str(report),
            "resolved_recorded_path": str(resolved_recorded),
            "supported_export_mapping": mapping,
            "mapping_applied": mapping_applied,
            "observed_path_limitation": (
                "The recorded Linux absolute path is checked through its explicit "
                "export-prefix mapping to this local copy. The original Linux path "
                "is not accessed or established as reachable from this checker."
                if mapping_applied else
                "The recorded absolute report path resolves directly in this environment. "
                "Linux export-prefix mapping is supported but was not used."
            ),
        },
    )
    page = Page()
    page.feed(report.read_text(encoding="utf-8"))
    local_links, anchors, invalid_links = [], [], []
    for link in page.links:
        url = urlsplit(link["target"])
        if url.scheme or url.netloc:
            invalid_links.append(link)
            continue
        if url.path:
            path = (report.parent / unquote(url.path)).resolve()
            entry = {**link, "resolved_path": str(path), "exists": path.is_file(),
                     "within_demo_root": path.is_relative_to(root)}
            local_links.append(entry)
            if not entry["exists"] or not entry["within_demo_root"]:
                invalid_links.append(entry)
        elif url.fragment:
            entry = {**link, "exists": unquote(url.fragment) in page.ids}
            anchors.append(entry)
            if not entry["exists"]:
                invalid_links.append(entry)
    check(
        "offline_html_links_and_inert_content",
        not invalid_links and not page.unsafe,
        {"local_file_links": len(local_links), "fragment_links": len(anchors),
         "unique_local_files": len({link["resolved_path"] for link in local_links}),
         "missing_external_or_outside_demo_links": invalid_links,
         "unsafe_elements_or_attributes": page.unsafe,
         "producer_audit": read("report/source-audit.json")},
    )
    embedded = []
    for text in page.pre:
        try:
            obj = json.loads(text)
        except (ValueError, TypeError):
            continue
        if isinstance(obj, dict) and all(
            name in obj for name in ("case_id", "obligation_id", "track", "outcome")
        ):
            embedded.append(obj)
    retained_rows = before["score"]["rows"] + after["score"]["rows"]
    check(
        "html_displayed_rows_bind_to_run_rows",
        Counter(map(canonical, embedded)) == Counter(map(canonical, retained_rows)),
        {"embedded_rows": len(embedded), "retained_run_rows": len(retained_rows)},
    )
    check(
        "track_counts_visible_and_consistent",
        before["score"]["tracks"]["package_consistency"]["rates"]["recall"]
            == {"numerator": 8, "denominator": 8}
        and after["score"]["tracks"] == demo["tracks"]
        and after["score"]["tracks"]["package_consistency"]["rates"]["recall"]
            == {"numerator": 7, "denominator": 8}
        and after["score"]["tracks"]["package_consistency"]["rates"]["named_clean_false_alert"]
            == {"numerator": 1, "denominator": 79}
        and before["score"]["tracks"]["cnc_advisory"] == after["score"]["tracks"]["cnc_advisory"],
        {"before_tracks": before["score"]["tracks"],
         "after_tracks": after["score"]["tracks"]},
    )

    bundle = root / "review-bundle"
    files = sorted(path.relative_to(bundle).as_posix()
                   for path in bundle.rglob("*") if path.is_file())
    private_keys, byte_mismatches, bad_case_files, metadata, markers = [], [], [], [], []

    def walk(obj, location):
        if isinstance(obj, dict):
            for name, value in obj.items():
                if name.lower() in FORBIDDEN_KEYS:
                    private_keys.append(location + "." + name)
                walk(value, location + "." + name)
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                walk(value, location + "[" + str(index) + "]")

    for case_id in case_ids:
        folder = bundle / "public" / case_id
        names = sorted(path.name for path in folder.iterdir() if path.is_file())
        if names != ["drawing.pdf", "drawing.png", "packet.json", "part.step"]:
            bad_case_files.append({"case_id": case_id, "files": names})
        packet = json.loads((folder / "packet.json").read_text(encoding="utf-8"))
        walk(packet, case_id)
        for name in names:
            if sha256(folder / name) != sha256(root / "inputs/suite/public" / case_id / name):
                byte_mismatches.append(case_id + "/" + name)
        pdf = PdfReader(folder / "drawing.pdf")
        pdf_metadata = {str(name): str(value) for name, value in (pdf.metadata or {}).items()}
        texts = [
            " ".join(page.extract_text() or "" for page in pdf.pages),
            json.dumps(pdf_metadata),
            (folder / "part.step").read_text(encoding="utf-8", errors="replace"),
            json.dumps(packet),
        ]
        with Image.open(folder / "drawing.png") as image:
            png_info = dict(image.info)
        texts.append(json.dumps(png_info, default=str))
        metadata.append({"case_id": case_id, "pdf_pages": len(pdf.pages),
                         "pdf_metadata": pdf_metadata, "png_metadata_keys": list(png_info)})
        for kind, text in zip(
            ("pdf_text", "pdf_metadata", "step_text", "packet_json", "png_metadata"), texts
        ):
            matches = sorted(set(PRIVATE_MARKER.findall(text)))
            if matches:
                markers.append({"case_id": case_id, "content": kind, "markers": matches})
    allowed_top = {"INSTRUCTIONS.txt", "REVIEWER_PROTOCOL.md", "export-audit.json"}
    unexpected = [name for name in files
                  if not name.startswith("public/") and name not in allowed_top]
    check(
        "public_export_privacy_observations",
        len(files) == 63 and not unexpected and not private_keys
        and not bad_case_files and not byte_mismatches and not markers
        and not (bundle / "private").exists(),
        {"total_files": len(files), "case_count": len(case_ids), "files_per_case": 4,
         "top_level_files": sorted(name for name in files if "/" not in name),
         "unexpected_files": unexpected, "forbidden_json_keys": private_keys,
         "bad_case_file_sets": bad_case_files, "public_input_byte_mismatches": byte_mismatches,
         "private_marker_hits": markers, "pdf_and_png_metadata": metadata,
         "limits": "Finite key/token and exported-byte observations; not a proof "
                   "of all semantic leakage or a security sandbox."},
    )
    archive = (archive_path.resolve() if archive_path is not None else next(
        (parent / "frozen-consumer-final.tar.gz" for parent in root.parents
         if (parent / "frozen-consumer-final.tar.gz").is_file()), None))
    archive_observation = {
        "declared_source_commit": declared_commit,
        "expected_archive_sha256": archive_sha256.lower(),
        "scope": "Declared commit supplied by coordinator; no source or archive internals inspected.",
        "status": ("not_available_at_local_ancestors" if archive is None else
                   "observed" if archive.is_file() else "supplied_archive_missing"),
        "archive_argument_supplied": archive_path is not None,
    }
    if archive is not None and archive.is_file():
        archive_observation.update({"archive": str(archive), "actual_sha256": sha256(archive)})
        check("supplied_frozen_archive_hash",
              archive_observation["actual_sha256"] == archive_sha256.lower(),
              archive_observation)
    elif archive_path is not None:
        archive_observation["archive"] = str(archive)
        check("supplied_frozen_archive_hash", False, archive_observation)
    evidence_names = [
        "demo-result.json", "before/run.json", "after/run.json",
        "before/raw-review.json", "after/raw-review.json",
        "before/import.json", "after/import.json", "report/index.html",
        "report/comparison.json", "report/source-audit.json",
        "validation/oracle.json", "inputs/replay-manifest.json",
        "review-bundle/export-audit.json",
    ]
    result = {
        "inspection_kind": "Independent consumer artifact inspection",
        "status": "observations_passed" if not failures else "observations_failed",
        "requirements": ["R01", "R02", "R14", "R15", "R16", "R18"],
        "artifact_root": str(root),
        "environment": {"python": sys.version, "platform": sys.platform,
                        "source_logic_used": False, "network_or_packet_transmission": False},
        "checks": checks, "failures": failures,
        "inspected_artifact_sha256": {name: sha256(root / name) for name in evidence_names},
        "checker_sha256": sha256(Path(__file__).resolve()),
        "archive_observation": archive_observation,
        "retained_evidence": str(output),
        "invocation": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
        "invocation_working_directory": str(Path.cwd()),
        "inspection_configuration": {
            "declared_commit": declared_commit,
            "archive_sha256": archive_sha256.lower(),
            "linux_prefix": linux_prefix,
        },
        "limitations": [
            "Artifact agreement is not independent geometry/oracle revalidation.",
            "Retained demonstration replays audited reviewer bytes and explicitly injected "
            "changes; no new external reviewer measurement.",
            "No visual browser-render assessment performed.",
            "No industrial competence or manufacturing approval claim.",
            "Recorded Linux paths are accessed only through the explicitly recorded "
            "export-prefix mapping; original Linux filesystem availability is unverified.",
            "No source/status files edited; output is only the requested findings JSON.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "failures": failures, "evidence": str(output),
        "evidence_sha256": sha256(output), "checker_sha256": result["checker_sha256"],
        "changes": changes,
        "counts": {"cases": len(case_ids), "before_rows": len(before_rows),
                   "after_rows": len(after_rows), "html_embedded_rows": len(embedded),
                   "local_file_links": len(local_links), "fragment_links": len(anchors),
                   "public_export_files": len(files)},
        "report_path_mapping": checks["recorded_report_path_binding"],
    }, indent=2))
    return 0 if not failures else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_root", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--archive", type=Path,
                        help="Frozen archive to hash; otherwise locate the prior default archive at an ancestor.")
    parser.add_argument("--archive-sha256", default=EXPECTED_ARCHIVE_SHA256,
                        help="Expected archive SHA-256 (defaults to the prior frozen source).")
    parser.add_argument("--declared-commit", default=DECLARED_COMMIT,
                        help="Coordinator-declared source commit; source contents are not inspected.")
    parser.add_argument("--linux-prefix", default=LINUX_PREFIX,
                        help="Recorded Linux demo prefix mapped to the exported local demo_root.")
    arguments = parser.parse_args()
    return inspect(arguments.demo_root, arguments.output_json,
                   archive_path=arguments.archive,
                   archive_sha256=arguments.archive_sha256,
                   declared_commit=arguments.declared_commit,
                   linux_prefix=arguments.linux_prefix)


if __name__ == "__main__":
    raise SystemExit(main())
