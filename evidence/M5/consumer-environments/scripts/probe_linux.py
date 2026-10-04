"""Bounded one-case consumer probe before a full emulated Linux replay."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

root=Path('/home/consumer/linux-bounded-probe');root.mkdir()
source=Path('/home/consumer/frozen-bounded')
suite=root/'suite';(suite/'public').mkdir(parents=True)
case_id='pk-0236ce4290c1'
shutil.copytree(source/'examples/v1-demo/suite/public'/case_id,suite/'public'/case_id)
argv=[sys.executable,'-m','rfqfuzz.v1','validate',str(suite),str(root/'observations'),'--parser-timeout','300']
start=time.monotonic()
with (root/'command.log').open('w') as handle:
    result=subprocess.run(argv,cwd=source,stdout=handle,stderr=subprocess.STDOUT,timeout=420)
elapsed=time.monotonic()-start
oracle=json.loads((root/'observations/oracle.json').read_text())
case=oracle['cases'][0]
record={'utc':datetime.now(timezone.utc).isoformat(),'argv':argv,'seconds':elapsed,'exit_code':result.returncode,'status':case['status'],'reasons':case['reasons'],'measured_geometry':case['measurements'],'isolation':case['isolation'],'setup':'four-CPU QEMU TCG noapic; externally restricted user network','interpretation':'No visual attestation supplied: unverified is required, timeout/error would fail readiness.'}
(root/'probe-result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
assert result.returncode==2 and case['status']=='unverified' and case['measurements']['solid_count']==1
assert elapsed < 300
(root/'PROBE_READY').write_text(datetime.now(timezone.utc).isoformat()+'\n')
