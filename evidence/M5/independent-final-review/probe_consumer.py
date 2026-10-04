"""Read-only consumer review: writes only this ignored evidence directory."""
from pathlib import Path
import copy
import json
import shutil
import subprocess
import sys

from rfqfuzz.v1.contracts import load_json, write_json, sha256
from rfqfuzz.v1.reporting import make_report, audit_report

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DEMO = ROOT / "evidence/M5/coordinator-demo-v2"
results = {"source_sha256": {p: sha256(ROOT / p) for p in ["src/rfqfuzz/v1/reporting.py", "src/rfqfuzz/v1/cli.py", "src/rfqfuzz/v1/reference.py"]}}

oracle = load_json(DEMO / "validation/oracle.json", limit=32_000_000)
oracle["oracle_version"] = "independent-probe-unscored-version"
write_json(OUT / "edited-oracle.json", oracle)
try:
    make_report([DEMO / "before/run.json"], OUT / "edited-oracle.json", DEMO / "inputs/suite/public", OUT / "changed-oracle-report")
    results["revised_oracle"] = {"rejected": False}
except (ValueError, KeyError, TypeError, OSError) as error:
    results["revised_oracle"] = {"rejected": True, "reason": str(error), "output_created": (OUT / "changed-oracle-report").exists()}

run = load_json(DEMO / "before/run.json")
track = next(iter(run["score"]["tracks"]))
run["score"]["tracks"][track]["rates"]["recall"]["numerator"] = '<script>window.__rfqfuzz_probe=1</script>'
write_json(OUT / "malformed-rate/run.json", run)
shutil.copyfile(DEMO / "before/raw-review.json", OUT / "malformed-rate/raw-review.json")
try:
    make_report([OUT / "malformed-rate/run.json"], DEMO / "validation/oracle.json", DEMO / "inputs/suite/public", OUT / "malformed-rate-report")
    html = (OUT / "malformed-rate-report/index.html").read_text(encoding="utf-8")
    results["malformed_rate_html"] = {"report_written": True, "literal_script_written": '<script>window.__rfqfuzz_probe=1</script>' in html}
    try:
        results["malformed_rate_html"]["audit"] = audit_report(OUT / "malformed-rate-report/index.html")
    except ValueError as error:
        results["malformed_rate_html"]["audit_error"] = str(error)
except (ValueError, KeyError, TypeError, OSError) as error:
    results["malformed_rate_html"] = {"report_written": False, "rejected": True, "reason": str(error)}

public = OUT / "corrupt-reference-public"
source = next((DEMO / "inputs/suite/public").iterdir())
shutil.copytree(source, public / source.name)
folder = public / source.name
pdf = folder / "drawing.pdf"
pdf.write_bytes(b"%PDF-1.4\nInvalid probe PDF, no objects or EOF\n")
packet = load_json(folder / "packet.json")
for artifact in packet["artifacts"]:
    if artifact["path"] == "drawing.pdf":
        artifact["sha256"] = sha256(pdf)
write_json(folder / "packet.json", packet)
command = [sys.executable, "-m", "rfqfuzz.v1", "reference", str(public), str(OUT / "corrupt-reference-output")]
proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
(OUT / "reference-cli-stdout.txt").write_text(proc.stdout, encoding="utf-8")
(OUT / "reference-cli-stderr.txt").write_text(proc.stderr, encoding="utf-8")
response = load_json(OUT / "corrupt-reference-output/review.json") if (OUT / "corrupt-reference-output/review.json").is_file() else None
results["reference_error_summary"] = {"command": command, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "statuses": [r["status"] for r in response["results"]] if response else None, "reasons": [r["reason"] for r in response["results"]] if response else None}
write_json(OUT / "probe-results.json", results)
print(json.dumps(results, indent=2))
