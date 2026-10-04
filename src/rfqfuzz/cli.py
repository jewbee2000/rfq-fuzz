import argparse
import json
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="RFQFuzz M0 feasibility commands only")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--out", default="evidence/M0/bundle")
    val = sub.add_parser("validate")
    val.add_argument("public", nargs="?", default="evidence/M0/bundle/public")
    val.add_argument("--out", default="evidence/M0/validation")
    val.add_argument("--attestation", default="evidence/M0/visual-attestation.json")
    ref = sub.add_parser("reference")
    ref.add_argument("public", nargs="?", default="evidence/M0/bundle/public")
    ref.add_argument("--out", default="evidence/M0/runs/reference")
    imp = sub.add_parser("import-results")
    imp.add_argument("response")
    imp.add_argument("--public", default="evidence/M0/bundle/public")
    imp.add_argument("--oracle", default="evidence/M0/validation/oracle.json")
    imp.add_argument("--out", required=True)
    imp.add_argument("--adjudication")
    report = sub.add_parser("report")
    report.add_argument("runs", nargs='+')
    report.add_argument("--oracle", default="evidence/M0/validation/oracle.json")
    report.add_argument("--public", default="evidence/M0/bundle/public")
    report.add_argument("--out", default="evidence/M0/report")
    args = parser.parse_args()
    if args.command == "generate":
        from .generation import generate
        result = generate(args.out)
    elif args.command == "validate":
        from .validation import validate_suite
        result = validate_suite(Path(args.public), Path(args.out), Path(args.attestation))
    elif args.command == "reference":
        from .reference import review_public
        result = review_public(args.public, args.out)
    elif args.command == "import-results":
        from .scoring import import_result
        result = import_result(args.response, args.public, args.oracle, args.out, args.adjudication)
    elif args.command == "report":
        from .reporting import make_report
        result = make_report(args.runs, args.oracle, args.public, args.out)
    print(json.dumps(result, indent=2))
    if args.command == "validate" and result.get("status") != "valid":
        sys.exit(2)
