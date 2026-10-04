"""Create an explicitly labeled reference regression in a new output path."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from rfqfuzz.contracts import write_json
from rfqfuzz.scoring import injected_regression
p=argparse.ArgumentParser();p.add_argument('reference');p.add_argument('--out',required=True);a=p.parse_args()
if Path(a.out).exists():raise ValueError('output exists; preserve previous run')
write_json(a.out,injected_regression(json.loads(Path(a.reference).read_text(encoding='utf-8'))))
print('Created DELIBERATELY INJECTED reference regression; external observations unchanged.')
