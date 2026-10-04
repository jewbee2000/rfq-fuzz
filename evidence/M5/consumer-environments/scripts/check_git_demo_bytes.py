"""Check committed replay bytes against the committed replay's hash manifest."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

commit=sys.argv[1];output=Path(sys.argv[2]);prefix='examples/v1-demo/'
def read(path):
    return subprocess.run(['git','show',commit+':'+path],capture_output=True,check=True).stdout
manifest=json.loads(read(prefix+'replay-manifest.json'))
files=[]
for path,expected in manifest['files'].items():
    actual=hashlib.sha256(read(prefix+path)).hexdigest()
    files.append({'path':path,'expected_sha256':expected,'committed_bytes_sha256':actual,'matches':actual==expected})
failures=[item for item in files if not item['matches']]
record={'source_commit':commit,'scope':'Git object bytes, independent of host checkout EOL settings; no source logic or private conclusions read','status':'passed' if not failures else 'failed','files_checked':len(files),'mismatch_count':len(failures),'files':files}
output.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({key:value for key,value in record.items() if key!='files'},indent=2))
sys.exit(0 if not failures else 2)
