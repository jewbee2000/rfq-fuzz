"""Copy installed package license notices for retained reproducibility evidence."""
import hashlib
import importlib.metadata as md
import json
from pathlib import Path
import re
import shutil
import sys

out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
manifest=[]
for dist in sorted(md.distributions(),key=lambda d:d.metadata['Name'].lower()):
    name=dist.metadata['Name']
    record={'name':name,'version':dist.version,'license_metadata':dist.metadata.get('License-Expression') or dist.metadata.get('License') or '', 'notices':[]}
    for i,entry in enumerate(dist.files or []):
        if not any(word in str(entry).lower() for word in ('license','copying','notice')):
            continue
        source=Path(dist.locate_file(entry))
        if not source.is_file():
            continue
        destination=out/re.sub(r'[^A-Za-z0-9._-]','_',name)/f'{i:04d}-{source.name}'
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,destination)
        record['notices'].append({'installed_relative_path':str(entry),'retained_relative_path':str(destination.relative_to(out)),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()})
    manifest.append(record)
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'distributions':len(manifest),'copied_notice_files':sum(len(item['notices']) for item in manifest)}))
