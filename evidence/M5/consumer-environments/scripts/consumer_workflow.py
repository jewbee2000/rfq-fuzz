"""Independent consumer command runner. No validator or generator source imports."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--skip-demo', action='store_true')
parser.add_argument('--parser-timeout', type=float, default=60)
parser.add_argument('--audit-timeout', type=float, default=20)
args = parser.parse_args()
source = args.source.resolve()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
env = os.environ.copy()
env.pop('PYTHONPATH', None)
records = []

def run(label, arguments, expected_exit):
    command = [sys.executable, '-m', 'rfqfuzz.v1', *map(str, arguments)]
    start = time.monotonic()
    print(json.dumps({'start_utc': datetime.now(timezone.utc).isoformat(), 'label': label, 'cwd': str(source), 'argv': command}), flush=True)
    with (out / f'{label}.log').open('w', encoding='utf-8') as handle:
        result = subprocess.run(command, cwd=source, env=env, stdout=handle, stderr=subprocess.STDOUT, timeout=1800)
    record = {'label': label, 'argv': command, 'cwd': str(source), 'exit_code': result.returncode, 'expected_exit': expected_exit, 'seconds': time.monotonic()-start, 'log': f'{label}.log'}
    records.append(record)
    (out / 'commands.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(record), flush=True)
    if result.returncode != expected_exit:
        raise RuntimeError(f'{label}: expected {expected_exit}, got {result.returncode}; retained {out / (label + ".log")}')

if not args.skip_demo:
    demo_args = ['demo', source/'examples/v1-demo', out/'demo']
    if args.parser_timeout != 60:
        demo_args += ['--parser-timeout',str(args.parser_timeout)]
    if args.audit_timeout != 20:
        demo_args += ['--audit-timeout',str(args.audit_timeout)]
    run('demo', demo_args, 0)
suite = out/'generated-suite'
(suite/'public').mkdir(parents=True)
for family in ('plate', 'bore_block', 'pocket_block'):
    opaque_id = 'pk-' + hashlib.sha256(('fresh-consumer-' + family).encode()).hexdigest()[:12]
    run(f'generate-{family}', ['generate-case', suite/'public'/opaque_id, '--case-id', opaque_id, '--family', family], 0)
validation_args = ['validate', suite, out/'generated-observations']
if args.parser_timeout != 60:
    validation_args += ['--parser-timeout',str(args.parser_timeout)]
run('validate-generated-suite', validation_args, 2)
oracle = json.loads((out/'generated-observations'/'oracle.json').read_text())
(out/'validation-result-retained.json').write_text(json.dumps(oracle, indent=2)+'\n')
assert oracle['status']=='unverified' and len(oracle['cases'])==3
assert all(case['status']=='unverified' and not case['expectations'] for case in oracle['cases'])
(out / 'WORKFLOW_COMMANDS_READY').write_text(datetime.now(timezone.utc).isoformat()+'\n')
