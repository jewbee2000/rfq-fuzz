"""Actual public-only template reference, clearly separate from independent review."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from rfqfuzz.v1.reference import review_public,injected_regression
from rfqfuzz.v1.contracts import write_json,validate_review
r=review_public("evidence/M2/core-suite/public","evidence/M3/reference-core")
validate_review(r)
write_json("evidence/M3/reference-injected.json",injected_regression(r))
print({"cases":len(r["results"]),"states":{state:sum(row["status"]==state for row in r["results"]) for state in {row["status"] for row in r["results"]}}})
