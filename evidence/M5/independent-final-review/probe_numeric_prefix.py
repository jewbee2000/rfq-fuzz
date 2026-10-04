"""Grounding challenge with the retained actual public demo response."""
from pathlib import Path
import copy
import json
import sys
from rfqfuzz.v1.contracts import load_json,write_json,sha256,read_packet
from rfqfuzz.v1.scoring import matches,score
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
tag=sys.argv[1] if len(sys.argv)>1 else ''
DEMO=ROOT/'evidence/M5/coordinator-demo-v2'
oracle=load_json(DEMO/'validation/oracle.json',limit=32_000_000)
response=load_json(DEMO/'before/raw-review.json')
choices=[(c,e) for c in oracle['cases'] for e in c['expectations'] if e['category']=='count_consistency']
case,expected=next(((c,e) for c,e in choices if e['conclusion']=='contradiction'),choices[0])
row=next(r for r in response['results'] if r['case_id']==case['case_id'])
item=next(i for i in row['findings']+row['assertions'] if i['obligation_id']==expected['obligation_id'])
before=copy.deepcopy(item)
changed=[]
for witness in item['evidence']:
    if witness['artifact'] in {'part.step','drawing.pdf'}:
        previous=witness['quote']
        witness['quote']+='0'
        changed.append({'artifact':witness['artifact'],'correct_quote':previous,'false_quote':witness['quote']})
packets={p.name:read_packet(p) for p in (DEMO/'inputs/suite/public').iterdir()}
scored=score(response,oracle,packets)
outcome=next(r for r in scored['rows'] if r['case_id']==case['case_id'] and r['obligation_id']==expected['obligation_id'])
record={'scoring_sha256':sha256(ROOT/'src/rfqfuzz/v1/scoring.py'),'case_id':case['case_id'],'obligation_id':expected['obligation_id'],'changes':changed,'matches_original':matches(before,expected),'matches_false_numeric_prefix':matches(item,expected),'scored_row':outcome}
write_json(OUT/f'numeric-prefix-review{tag}.json',response)
write_json(OUT/f'numeric-prefix-results{tag}.json',record)
print(json.dumps(record,indent=2))
