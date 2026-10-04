"""Read-only consumer-environment inspection; no source or lock rewrite."""
import importlib
import importlib.metadata as md
import json
import platform
from pathlib import Path
import shutil
import subprocess
import sys

imports = {}
for name in ('build123d', 'draftwright', 'OCP', 'numpy', 'pypdf', 'PIL', 'pypdfium2', 'vtk', 'reportlab'):
    module = importlib.import_module(name)
    imports[name] = {'file': getattr(module, '__file__', None)}
packages = []
for dist in sorted(md.distributions(), key=lambda d: d.metadata['Name'].lower()):
    meta = dist.metadata
    notices = [str(f) for f in (dist.files or []) if any(term in str(f).lower() for term in ('license', 'copying', 'notice'))]
    packages.append({'name': meta['Name'], 'version': dist.version,
                     'license_metadata': meta.get('License-Expression') or meta.get('License') or '',
                     'notice_files': notices})
poppler = subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True, check=True)
record = {'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
          'machine': platform.machine(), 'prefix': sys.prefix, 'base_prefix': sys.base_prefix,
          'poppler': {'executable': shutil.which('pdftoppm'), 'version': poppler.stderr.strip()},
          'imports': imports, 'packages': packages}
Path(sys.argv[1]).write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: record[key] for key in ('python', 'executable', 'platform', 'machine', 'prefix', 'base_prefix', 'poppler')}))
print(f'Imported {len(imports)} modules; recorded {len(packages)} distributions')
