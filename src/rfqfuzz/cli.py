import argparse
import json
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
    args = parser.parse_args()
    if args.command == "generate":
        from .generation import generate
        result = generate(args.out)
    elif args.command == "validate":
        from .validation import validate_suite
        result = validate_suite(Path(args.public), Path(args.out), Path(args.attestation))
    print(json.dumps(result, indent=2))
