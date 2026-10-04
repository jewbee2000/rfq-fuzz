"""Lightweight final traceability and document integrity acceptance."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

parser = argparse.ArgumentParser()
parser.add_argument("--pending-finalization", action="store_true",
                    help="check final content before coordinator closes T14 metadata")
arguments = parser.parse_args()
root = Path(__file__).resolve().parents[1]
requirements = json.loads((root / "requirements.json").read_text())
ledger = json.loads((root / "tasks.json").read_text())
must = [r for r in requirements["requirements"] if r["priority"] == "must"]
assert len(must) == 22
tasks = {t["id"]: t for t in ledger["tasks"]}
pending = [t["id"] for t in tasks.values() if t["status"] != "completed"]
assert pending == (["T14"] if arguments.pending_finalization else [])
for task in tasks.values():
    assert all(tasks[d]["status"] == "completed" for d in task["depends_on"])
    if arguments.pending_finalization and task["id"] == "T14":
        assert task["status"] == "in_progress"
        continue
    assert task["verification_is_proposed"] is False
    assert (root / task["evidence"]).is_file()
    assert task["completion_commit"] and task["completion_commit"] != "HEAD"
    subprocess.run(["git", "cat-file", "-e", task["completion_commit"] + "^{commit}"], cwd=root, check=True)
for requirement in must:
    ready = all(tasks[t]["status"] == "completed" for t in requirement["tasks"])
    assert requirement["status"] == ("verified" if ready else "in_progress")
    assert requirement["completion_evidence"] and requirement["acceptance_commands"]
    assert all((root / path).exists() for path in requirement["completion_evidence"])

documents = ["README.md", "docs/DEMO.md", "docs/REQUIREMENTS.md",
             "docs/REQUIREMENTS_EVIDENCE.md", "docs/SHOULD_DEFERRALS.md",
             "docs/BLOG_DRAFT.md", "docs/BLOG_EVIDENCE.md"]
links = []
for relative in documents:
    file = root / relative
    source = file.read_text(encoding="utf-8")
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", source):
        target = target.strip().strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or not parsed.path:
            continue
        path = (file.parent / unquote(parsed.path)).resolve()
        assert path.is_relative_to(root) and path.exists(), (relative, target)
        links.append({"document": relative, "target": target})

blog = (root / "docs/BLOG_DRAFT.md").read_text(encoding="utf-8")
prose = re.sub(r"<!--.*?-->", "", blog, flags=re.S)
prose = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", prose)
prose = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", prose)
words = len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", prose))
figures = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", blog)
assert 800 <= words <= 1200, words
assert len(figures) == 3, len(figures)
assert "editorial item" not in blog and "still being finalized" not in blog
result = {"status": "content_passed_pending_finalization" if arguments.pending_finalization else "passed",
          "Must_verified": sum(r["status"] == "verified" for r in must),
          "Must_evidence_checked": len(must),
          "completed_tasks": len(tasks) - len(pending), "pending_tasks": pending,
          "local_links_checked": len(links),
          "blog_prose_words": words, "actual_embedded_figures": len(figures),
          "documents": documents,
          "limitations": "File/traceability audit; actual visual and consumer acceptance are retained separately."}
destination = "document-content-audit.json" if arguments.pending_finalization else "document-audit.json"
(root / "evidence/M5" / destination).write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
