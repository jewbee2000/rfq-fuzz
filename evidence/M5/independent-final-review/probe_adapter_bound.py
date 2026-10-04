"""An explicitly configured fast local process, only ignored outputs."""
from pathlib import Path
import json
import sys
import shutil
from rfqfuzz.v1.contracts import load_json, write_json, sha256
from rfqfuzz.v1.adapters import run_local

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
DEMO=ROOT/'evidence/M5/coordinator-demo-v2'
source=next((DEMO/'inputs/suite/public').iterdir())
shutil.copytree(source,OUT/'adapter-public'/source.name)
response=load_json(DEMO/'before/raw-review.json')
response['results']=[r for r in response['results'] if r['case_id']==source.name]
write_json(OUT/'burst-response.json',response)
program="import sys,json,os; q=json.loads(sys.stdin.read()); data=json.load(open(sys.argv[1],encoding='utf-8')); json.dump(data,open(q['response_path'],'w',encoding='utf-8')); os.write(1,b'x'*5000001); os._exit(0)"
command=[sys.executable,'-c',program,str(OUT/'burst-response.json')]
result=run_local(command,OUT/'adapter-public',OUT/'adapter-burst-output',timeout=5)
record={'source_sha256':sha256(ROOT/'src/rfqfuzz/v1/adapters.py'),'status':result['status'],'reason':result['reason'],'stdout_bytes':(OUT/'adapter-burst-output/stdout.bin').stat().st_size,'configured_output_limit':4_000_000,'command':command,'response_rows':len(result.get('response',{}).get('results',[]))}
write_json(OUT/'adapter-probe-results.json',record)
print(json.dumps(record,indent=2))
