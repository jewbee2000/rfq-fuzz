"""Provisional shared constants and ordinary public-packet file checks."""
import hashlib
import json
from pathlib import Path

VERSION = "m0.1"
CONCLUSIONS = {"contradiction", "profile_exclusion", "advisory", "missing_information", "supported_clear", "unsupported"}
STATES = {"completed", "partial", "unsupported", "timeout", "error"}
OBLIGATION = "bore_group_consistency"

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def read_packet(folder):
    folder = Path(folder)
    p = json.loads((folder / "packet.json").read_text(encoding="utf-8"))
    if p.get("schema_version") != VERSION:
        raise ValueError("unsupported PacketSpec version")
    for key in ("case_id", "part_id", "release_association", "units", "authority", "manufacturing", "profile", "setup", "features", "obligations", "artifacts"):
        if key not in p:
            raise ValueError(f"missing public premise: {key}")
    if p["units"] != {"model": "mm", "drawing": "mm"}:
        raise ValueError("unsupported M0 units")
    if not p["authority"] or not p["manufacturing"].get("model_stage") or not p["manufacturing"].get("drawing_stage"):
        raise ValueError("missing authority/stage")
    paths = {a["path"] for a in p["artifacts"]}
    if paths != {"part.step", "drawing.pdf", "drawing.png"} or len(p["artifacts"]) != 3:
        raise ValueError("unexpected artifact paths")
    for a in p["artifacts"]:
        f = folder / a["path"]
        if f.stat().st_size > 16_000_000:
            raise ValueError("artifact size limit exceeded")
        if sha256(f) != a["sha256"]:
            raise ValueError(f"artifact hash mismatch: {a['path']}")
    return p
