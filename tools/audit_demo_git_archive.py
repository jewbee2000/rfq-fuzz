"""Check actual Git archive bytes against the audited demo replay manifest."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

root = Path(__file__).resolve().parents[1]
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
archive = subprocess.check_output(["git", "-c", "core.autocrlf=false", "archive", "--format=tar", commit, "examples/v1-demo"], cwd=root)
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
    files = {m.name: tar.extractfile(m).read() for m in tar.getmembers() if m.isfile()}
prefix = "examples/v1-demo/"
manifest = json.loads(files[prefix + "replay-manifest.json"])
assert set(files) == {prefix + path for path in manifest["files"]} | {prefix + "replay-manifest.json"}
assert len(manifest["files"]) == 64
for relative, expected in manifest["files"].items():
    actual = files[prefix + relative]
    assert hashlib.sha256(actual).hexdigest() == expected, relative
    assert actual == (root / prefix / relative).read_bytes(), relative
windows_archive = subprocess.check_output(["git", "-c", "core.autocrlf=true", "archive", "--format=tar", commit, "examples/v1-demo"], cwd=root)
with tarfile.open(fileobj=io.BytesIO(windows_archive)) as tar:
    windows_files = {m.name: tar.extractfile(m).read() for m in tar.getmembers() if m.isfile()}
assert files == windows_files, "protected inputs changed under Git text policy"
result = {"status": "passed", "method": "git -c core.autocrlf=false/true archive --format=tar COMMIT examples/v1-demo",
          "commit": commit, "archive_sha256": hashlib.sha256(archive).hexdigest(),
          "manifest_assets": 64, "archived_regular_files": len(files),
          "git_text_policies_checked": [False, True], "protected_input_bytes_equal_under_both": True,
          "hash_mismatches": [], "working_copy_byte_mismatches": [],
          "limitation": "Portable input-byte check; consumer workflows and native checks are separate evidence."}
(root / "evidence/M5/git-archive-input-audit.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
