"""Reopen the complete frozen development corpus using final validator code."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from rfqfuzz.v1.validation import validate_suite
r=validate_suite("evidence/M2/core-suite","evidence/M4/core-validated","evidence/M4/visual-review/attestation.json")
print(json.dumps({"status":r["status"],"counts":r["counts"]}))
if r["status"]!="valid":raise SystemExit(1)
