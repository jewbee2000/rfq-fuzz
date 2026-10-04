"""Capture the resolved environment and dependency notices, without network access."""
import importlib.metadata as md
import json
import platform
from pathlib import Path
import subprocess
import sys

out = Path("evidence/M0")
out.mkdir(parents=True, exist_ok=True)
packages = []
for dist in sorted(md.distributions(), key=lambda d: d.metadata['Name'].lower()):
    meta = dist.metadata
    license_value = meta.get('License-Expression') or meta.get('License') or ''
    classifiers = [x for x in meta.get_all('Classifier', []) if x.startswith('License ::')]
    notices = [str(f) for f in (dist.files or []) if 'license' in str(f).lower() or 'copying' in str(f).lower() or 'notice' in str(f).lower()]
    packages.append({'name': meta['Name'], 'version': dist.version, 'license_metadata': license_value,
                     'license_classifiers': classifiers, 'notice_files': notices})
lock = '\n'.join(f"{p['name']}=={p['version']}" for p in packages if p['name'].lower() not in ('pip', 'rfqfuzz')) + '\n'
Path('requirements-m0.lock').write_text(lock)
record = {'python': sys.version, 'platform': platform.platform(), 'machine': platform.machine(),
          'pip': md.version('pip'), 'packages': packages,
          'poppler': subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True, check=True).stderr.strip()}
(out / 'environment.json').write_text(json.dumps(record, indent=2) + '\n')
install = Path('work-install.json')
if install.exists():
    (out / 'install-report.json').write_bytes(install.read_bytes())
print(f"Recorded {len(packages)} distributions and pinned {len(lock.splitlines())} packages")
