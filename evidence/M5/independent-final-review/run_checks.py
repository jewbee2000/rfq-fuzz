"""Retain final review checks without changing tracked implementation."""
from pathlib import Path
import json
import subprocess
import sys
from rfqfuzz.v1.contracts import sha256,write_json
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
files=['src/rfqfuzz/v1/cli.py','src/rfqfuzz/v1/api.py','src/rfqfuzz/v1/adapters.py','src/rfqfuzz/v1/reference.py','src/rfqfuzz/v1/reporting.py','docs/DEMO.md','docs/REVIEWER_PROTOCOL.md']
command=[sys.executable,'-m','pytest','tests/adapters','tests/consumer','tests/reporting','-q']
proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
(OUT/'pytest-stdout.txt').write_text(proc.stdout,encoding='utf-8')
(OUT/'pytest-stderr.txt').write_text(proc.stderr,encoding='utf-8')
record={'command':command,'returncode':proc.returncode,'source_sha256':{p:sha256(ROOT/p) for p in files}}
write_json(OUT/'check-results.json',record)
print(json.dumps(record,indent=2))
print(proc.stdout)
raise SystemExit(proc.returncode)
