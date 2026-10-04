"""Offline M0 frozen-input, evidence-link and ledger audit. No browser execution."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from rfqfuzz.contracts import sha256, write_json
from rfqfuzz.public_export import audit_public

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.paths=[]
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        for key in ('src','href'):
            if key in values and not values[key].startswith('#'):
                self.paths.append(values[key])

handoff=Path('evidence/M0/review-handoff')
hashes=json.loads((handoff/'PUBLIC_FILE_HASHES.json').read_text(encoding='utf-8'))
unchanged=all(sha256(handoff/name)==digest for name,digest in hashes.items())
assert unchanged, 'reviewer changed public input'
assert all(sha256(p)==sha256(handoff/'public'/p.relative_to('evidence/M0/bundle/public')) for p in Path('evidence/M0/bundle/public').rglob('*') if p.is_file())
report=Path('evidence/M0/report/index.html')
reader=Links();reader.feed(report.read_text(encoding='utf-8'))
assert '<script' not in report.read_text(encoding='utf-8').lower(), 'script in report'
assert all('://' not in p for p in reader.paths), 'remote report dependency'
missing=[p for p in reader.paths if not (report.parent/p).is_file()]
assert not missing, f'missing report evidence link: {missing}'
result={'public_inputs_unchanged':unchanged,'root_handoff_bytes_identical':True,
        'public_leakage_audit':audit_public('evidence/M0/bundle/public')['status'],
        'report_local_links_checked':len(reader.paths),'report_missing_links':missing,
        'report_script_elements':0,'remote_assets':0,
        'browser_rendering':'unverified: browser policy rejected local-file URL; no workaround attempted'}
write_json('evidence/M0/final-audit.json',result)
print(json.dumps(result,indent=2))
