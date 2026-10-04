"""Read-only runtime/license capture; never rewrites M0 evidence or locks."""
import importlib.metadata as md
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from rfqfuzz.v1.contracts import write_json,sha256,require

destination=Path(sys.argv[1]);require(not destination.exists(),"environment record exists")
packages=[]
for distribution in sorted(md.distributions(),key=lambda d:d.metadata["Name"].lower()):
    meta=distribution.metadata
    packages.append({"name":meta["Name"],"version":distribution.version,"license_metadata":meta.get("License-Expression") or meta.get("License") or "unavailable","license_classifiers":[s for s in meta.get_all("Classifier",[]) if s.startswith("License ::")],"notice_files":[str(p) for p in (distribution.files or []) if any(s in str(p).lower() for s in ("license","notice","copying"))]})
renderer=shutil.which("pdftoppm")
poppler=subprocess.run([renderer,"-v"],capture_output=True,text=True,timeout=10).stderr.strip() if renderer else None
write_json(destination,{"python":sys.version,"platform":platform.platform(),"machine":platform.machine(),"packages":packages,"poppler":poppler,"lock_sha256":{p:sha256(p) for p in ("requirements-m0.lock","requirements-v1.lock","requirements-build.lock")},"limits":["Metadata is retained as supplied; ambiguous licenses are not invented","Principal notices at docs/licenses; installed wheels include bundled OCCT/PDFium/font notices"]})
print(f"Recorded{len(packages)} distributions")
