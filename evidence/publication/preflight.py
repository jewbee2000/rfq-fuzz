"""Read-only history scan and portable demo-byte check before public source push.

Run with the repository's Python from any working directory. The retained JSON
identifies the reviewed commit. Pattern checks are bounded and are not a claim
that all possible confidential information can be recognized automatically.
"""
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

root = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=root)


commit = git("rev-parse", "HEAD").decode().strip()
objects = git("rev-list", "--objects", commit).decode("utf-8").splitlines()
paths = {}
for line in objects:
    sha, _, path = line.partition(" ")
    paths[sha] = path
checks = subprocess.check_output(
    ["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
    input="".join(sha + "\n" for sha in paths).encode(), cwd=root,
).decode().splitlines()
blobs = [(sha, int(size)) for sha, kind, size in
         (line.split() for line in checks) if kind == "blob"]
patterns = {
    "private_key_header": rb"-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----",
    "github_token": rb"(?:github_pat_[A-Za-z0-9_]{25,}|gh[pousr]_[A-Za-z0-9]{30,})",
    "aws_access_key_id": rb"AKIA[A-Z0-9]{16}",
    "api_key_shape": rb"sk-[A-Za-z0-9_-]{30,}",
}
compiled = {name: re.compile(pattern) for name, pattern in patterns.items()}
hits = []
with subprocess.Popen(["git", "cat-file", "--batch"], cwd=root,
                      stdin=subprocess.PIPE, stdout=subprocess.PIPE) as reader:
    for sha, size in blobs:
        reader.stdin.write((sha + "\n").encode())
        reader.stdin.flush()
        header = reader.stdout.readline().decode().strip().split()
        assert header == [sha, "blob", str(size)]
        data = reader.stdout.read(size)
        assert len(data) == size and reader.stdout.read(1) == b"\n"
        for name, pattern in compiled.items():
            if pattern.search(data):
                hits.append({"pattern": name, "blob": sha, "path": paths[sha]})
    reader.stdin.close()
    assert reader.wait() == 0
oversized = [{"blob": sha, "bytes": size, "path": paths[sha]}
             for sha, size in blobs if size >= 100_000_000]

archives = {}
for policy in ("false", "true"):
    archive = git("-c", "core.autocrlf=" + policy, "archive", "--format=tar",
                  commit, "examples/v1-demo")
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        archives[policy] = {m.name: tar.extractfile(m).read()
                            for m in tar.getmembers() if m.isfile()}
assert archives["false"] == archives["true"]
files = archives["false"]
prefix = "examples/v1-demo/"
manifest = json.loads(files[prefix + "replay-manifest.json"])
assert set(files) == {prefix + path for path in manifest["files"]} | {
    prefix + "replay-manifest.json"}
assert len(files) == 65 and len(manifest["files"]) == 64
for path, expected in manifest["files"].items():
    data = files[prefix + path]
    assert hashlib.sha256(data).hexdigest() == expected, path
    assert data == (root / prefix / path).read_bytes(), path
result = {
    "status": "passed" if not hits and not oversized else "failed",
    "reviewed_commit": commit,
    "reachable_commits": int(git("rev-list", "--count", commit)),
    "unique_reachable_blobs_scanned": len(blobs),
    "largest_history_blob_bytes": max(size for _, size in blobs),
    "credential_patterns": list(patterns), "credential_pattern_hits": hits,
    "blobs_at_least_100MB": oversized,
    "portable_demo_files": len(files), "manifest_assets_hash_checked": 64,
    "git_autocrlf_true_false_inputs_identical": True,
    "limitations": "Bounded credential pattern scan; not an exhaustive confidentiality audit. "
                   "Synthetic provenance, licenses and consumer acceptance are retained separately. "
                   "No product tests were rerun for this documentation-only publication follow-on.",
}
destination = root / "evidence/publication/preflight.json"
destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
assert result["status"] == "passed", "Inspect flagged blob paths privately before public push"
