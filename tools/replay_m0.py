"""Run the documented frozen-suite workflow offline into fresh local directories."""
import json
from pathlib import Path
import subprocess
import sys
from html.parser import HTMLParser

out=Path('work/replay')
if out.exists():raise ValueError('work/replay already exists; preserve prior replay')
out.mkdir(parents=True)
python=sys.executable
commands=[
    [python,'-m','pip','check'],
    [python,'tools/m0.py','validate','--out',str(out/'validation')],
    [python,'tools/m0.py','reference','--out',str(out/'reference')],
    [python,'tools/inject_m0.py',str(out/'reference/review.json'),'--out',str(out/'injected/review.json')],
    [python,'tools/m0.py','import-results',str(out/'reference/review.json'),'--out',str(out/'imported-reference')],
    [python,'tools/m0.py','import-results',str(out/'injected/review.json'),'--out',str(out/'imported-injected')],
    [python,'tools/m0.py','import-results','evidence/M0/review-handoff/review-output/review.json','--adjudication','evidence/M0/category-adjudication.json','--out',str(out/'imported-independent')],
    [python,'tools/m0.py','report',str(out/'imported-reference/run.json'),str(out/'imported-injected/run.json'),str(out/'imported-independent/run.json'),'--out',str(out/'report')],
]
results=[]
for i,command in enumerate(commands):
    result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
    (out/f'command-{i}.stdout.txt').write_text(result.stdout,encoding='utf-8')
    (out/f'command-{i}.stderr.txt').write_text(result.stderr,encoding='utf-8')
    results.append({'command':command,'returncode':result.returncode,'stderr':result.stderr})
    if result.returncode:raise RuntimeError(f'replay failed, retained {out}/command-{i}.stderr.txt')
class Links(HTMLParser):
    def __init__(self):super().__init__();self.paths=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('src','href') and not value.startswith('#'):self.paths.append(value)
parser=Links();parser.feed((out/'report/index.html').read_text(encoding='utf-8'))
assert all((out/'report'/p).is_file() for p in parser.paths)
counts={name:json.loads((out/name/'run.json').read_text(encoding='utf-8'))['score']['counts'] for name in ('imported-reference','imported-injected','imported-independent')}
record={'status':'passed','commands':results,'counts':counts,'report_links_checked':len(parser.paths),
        'limits':'offline replay of frozen suite and actual saved reviewer response; not a second independent live review or another platform; browser rendering not tested'}
Path('evidence/M0/replay-result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','commands':len(commands),'counts':counts,'links':len(parser.paths)},indent=2))
