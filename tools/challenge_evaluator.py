"""Run fixed acceptance tests against real isolated production-source mutants.

Never edits the checkout's implementation. Work copies live under ignored work/;
the exact diff, source hashes, command, process output and semantic failure are
retained in the requested new evidence directory. No hosted reviewer is used.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = "tests/metamorphic/test_evaluator_challenge.py"
MUTANTS = [
    {"id": "unit-conversion", "category": "unit conversion", "file": "src/rfqfuzz/v1/validation.py",
     "before": 'scale = 25.4 if match[3] == "in" else 1', "after": 'scale = 1  # DELIBERATE MUTANT: fail inch normalization',
     "test": "test_equivalent_inches_preserve_package_conclusions"},
    {"id": "comparison-boundary", "category": "comparison boundary", "file": "src/rfqfuzz/v1/validation.py",
     "before": 'geometry["wall_mm"] < threshold[m["material_class"]]', "after": 'geometry["wall_mm"] <= threshold[m["material_class"]]',
     "test": "test_wall_boundary_uses_strict_public_comparator"},
    {"id": "severity-conflation", "category": "severity", "file": "src/rfqfuzz/v1/validation.py",
     "before": 'return "advisory" if geometry["wall_mm"] < threshold[m["material_class"]] else "supported_clear"',
     "after": 'return "profile_exclusion" if geometry["wall_mm"] < threshold[m["material_class"]] else "supported_clear"',
     "test": "test_thin_wall_advisory_keeps_its_conclusion_class"},
    {"id": "duplicate-credit", "category": "deduplication", "file": "src/rfqfuzz/v1/scoring.py",
     "before": 'row["outcome"]="detected";n["detected"]+=1;op["detected"]+=1',
     "after": 'row["outcome"]="detected";n["detected"]+=len(hits);op["detected"]+=len(hits)',
     "test": "test_duplicate_root_findings_cannot_multiply_detection"},
    {"id": "private-leakage", "category": "leakage", "file": "src/rfqfuzz/v1/contracts.py",
     "before": 'for item in value.values():\n            private_scan(item)',
     "after": 'for item in value.values():\n            pass  # DELIBERATE MUTANT: stop scanning nested private keys',
     "test": "test_nested_private_answer_key_is_rejected"},
    {"id": "unknown-as-clear", "category": "unknown handling", "file": "src/rfqfuzz/v1/validation.py",
     "before": 'return "supported_clear" if m["tolerance_stage"] is not None or threshold.get("default_tolerance_stage") is not None else "missing_information"',
     "after": 'return "supported_clear" if m["tolerance_stage"] is not None or threshold.get("default_tolerance_stage") is not None else "supported_clear"',
     "test": "test_unresolved_finish_stage_cannot_become_clear"},
]


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_lineage(mutations):
    """Treat all twins/source families/layouts as indivisible split units."""
    groups = {"ancestry": defaultdict(set), "source_family": defaultdict(set), "layout_ancestry": defaultdict(set)}
    cases, failures = set(), []
    for row in mutations:
        if row["case_id"] in cases:
            failures.append(f"duplicate case ID: {row['case_id']}")
        cases.add(row["case_id"])
        source = row["source_parameters"]
        groups["ancestry"][row["ancestry"]].add(row["partition"])
        groups["source_family"][source.get("source_family", source["family"])].add(row["partition"])
        groups["layout_ancestry"][source["layout_ancestry"]].add(row["partition"])
    for kind, by_group in groups.items():
        for name, partitions in by_group.items():
            if len(partitions) != 1:
                failures.append(f"{kind} overlap: {name} appears in {sorted(partitions)}")
    return {"status": "passed" if not failures else "failed", "case_count": len(cases), "failures": failures,
            "groups": {kind: {name: sorted(values) for name, values in sorted(by_group.items())} for kind, by_group in groups.items()},
            "limitation": "A single development partition proves no cross-partition leakage; it provides no held-out transfer result"}


def run_pytest(cwd, node, basetemp, timeout=180):
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(Path(cwd) / "src")
    command = [sys.executable, "-m", "pytest", node, "-q", "--basetemp", str(basetemp)]
    process = subprocess.run(command, cwd=cwd, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return command, process.returncode, process.stdout + process.stderr


def challenge(out):
    out = Path(out).resolve()
    if out.exists():
        raise ValueError("challenge evidence exists; select a new output to preserve history")
    out.mkdir(parents=True)
    work = ROOT / "work" / "evaluator-mutants" / out.name
    if work.exists():
        raise ValueError("mutant work copies exist; select a new output name")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    command, rc, output = run_pytest(ROOT, TEST_FILE, out / "baseline-artifacts")
    (out / "baseline.txt").write_text(output, encoding="utf-8")
    write_json(out / "baseline-command.json", {"cwd": str(ROOT), "command": command, "returncode": rc})
    if rc != 0:
        raise ValueError("fixed baseline acceptance failed; no mutant result is valid")
    results = []
    for mutation in MUTANTS:
        case = out / mutation["id"]
        case.mkdir()
        clone = work / mutation["id"]
        clone.mkdir(parents=True)
        shutil.copytree(ROOT / "src", clone / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree(ROOT / "tests/metamorphic", clone / "tests/metamorphic", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copyfile(ROOT / "pyproject.toml", clone / "pyproject.toml")
        path = clone / mutation["file"]
        before = path.read_text(encoding="utf-8")
        if before.count(mutation["before"]) != 1:
            raise ValueError(f"{mutation['id']}: source anchor must identify exactly one actual implementation statement")
        after = before.replace(mutation["before"], mutation["after"], 1)
        path.write_text(after, encoding="utf-8")
        difference = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="a/" + mutation["file"], tofile="b/" + mutation["file"]))
        (case / "source.diff").write_text(difference, encoding="utf-8")
        # Compile before testing: syntax/import failures are not evaluator kills.
        compile(after, str(path), "exec")
        node = TEST_FILE + "::" + mutation["test"]
        command, rc, output = run_pytest(clone, node, case / "artifacts")
        (case / "pytest.txt").write_text(output, encoding="utf-8")
        killed = rc == 1 and ("FAILED " + node) in output and ("AssertionError" in output or "E       assert" in output or "DID NOT RAISE" in output)
        result = {"id": mutation["id"], "category": mutation["category"], "source_file": mutation["file"],
                  "original_source_sha256": sha256(ROOT / mutation["file"]), "mutated_source_sha256": sha256(path),
                  "patch_sha256": sha256(case / "source.diff"), "test": node, "command": command, "cwd": str(clone),
                  "returncode": rc, "status": "killed" if killed else "survived_or_invalid_failure",
                  "mechanism": "actual production-source replacement in an isolated ignored work copy; fixed acceptance test unchanged"}
        write_json(case / "result.json", result)
        results.append(result)
    summary = {"base_commit": commit, "python": sys.version, "baseline": "passed", "results": results,
               "killed": sum(r["status"] == "killed" for r in results), "total": len(results),
               "status": "passed" if all(r["status"] == "killed" for r in results) else "release_blocked",
               "limitations": ["Six relevant finite conceptual mutants, not exhaustive mutation coverage", "Synthetic authored obligations", "No industrial-competence inference", "No hosted reviewer or network needed"]}
    write_json(out / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="evidence/M4/challenge-tests")
    parser.add_argument("--audit-lineage", type=Path)
    args = parser.parse_args()
    if args.audit_lineage:
        data = json.loads(args.audit_lineage.read_text(encoding="utf-8"))
        result = audit_lineage(data["mutations"])
        write_json(args.out, result)
        print(result["status"], result["case_count"])
    else:
        result = challenge(args.out)
        print(result["status"], f"{result['killed']}/{result['total']} source mutants killed")
        if result["status"] != "passed":
            raise SystemExit(1)


if __name__ == "__main__":
    main()
