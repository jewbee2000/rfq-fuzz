"""Trace the two replay changes to own STEP readings, visible text and raw claims."""
import json
from pathlib import Path
import sys

demo=Path(sys.argv[1]);measurements=Path(sys.argv[2]);out=Path(sys.argv[3])
before=json.loads((demo/'before/raw-review.json').read_text())
after=json.loads((demo/'after/raw-review.json').read_text())
def response(run,case_id):
    return next(item for item in run['results'] if item['case_id']==case_id)
material_id='pk-0236ce4290c1';diameter_id='pk-0972292025ad'
material_packet=json.loads((demo/'inputs/suite/public'/material_id/'packet.json').read_text())
diameter_packet=json.loads((demo/'inputs/suite/public'/diameter_id/'packet.json').read_text())
material_m=json.loads((measurements/material_id/'measurements.json').read_text())
diameter_m=json.loads((measurements/diameter_id/'measurements.json').read_text())
assert 'MATERIAL = 7075-T6' in material_m['pdf_text'].splitlines()
assert material_packet['manufacturing']['material']=='6061-T6'
assert material_packet['authority']['material_precedence']=='equal'
assert any(x['obligation_id']=='obj-material' and x['conclusion']=='contradiction' for x in response(before,material_id)['findings'])
assert not any(x['obligation_id']=='obj-material' for x in response(after,material_id)['findings'])
diameters=sorted(2*face['radius_mm'] for face in diameter_m['faces'] if 'radius_mm' in face)
assert diameters==[6.2,12.2]
assert 'H1 DIAMETER = 6.20 +/- 0.05 mm' in diameter_m['pdf_text'].splitlines()
assert diameter_packet['manufacturing']['model_stage']==diameter_packet['manufacturing']['drawing_stage']=='finished'
assert diameter_packet['manufacturing']['transition'] is None and diameter_packet['manufacturing']['finish']=='none'
assert any(x['obligation_id']=='obj-diameter' and x['conclusion']=='supported_clear' for x in response(before,diameter_id)['assertions'])
assert any(x['obligation_id']=='obj-diameter' and x['conclusion']=='contradiction' for x in response(after,diameter_id)['findings'])
assert any(x['obligation_id']=='obj-release' for x in response(before,diameter_id)['findings'])
assert any(x['obligation_id']=='obj-release' for x in response(after,diameter_id)['findings'])
record={'result':'engineering_meanings_confirmed','source':'Own direct OCP measurements, actual PDF extraction, public context and immutable before/after raw claims; no private mutation/expected-answer/source conclusion logic',
 'material':{'case_id':material_id,'visible_drawing_material':'7075-T6','public_contract_material':'6061-T6','precedence':'equal','meaning':'The two material premises contradict; removal of its finding is a silent miss of a package obligation.'},
 'diameter':{'case_id':diameter_id,'measured_h1_diameter_mm':6.2,'actual_counterbore_diameter_mm':12.2,'visible_h1_annotation':'H1 DIAMETER = 6.20 +/- 0.05 mm','same_stage':'finished','transition':None,'meaning':'Measured H1 diameter equals drawing nominal at the same stage, inside the stated tolerance; the injected contradiction is a false alert for that obligation. A separate release-association contradiction persists in both responses, so the whole packet is not claimed clear.'},
 'limits':['Explicitly injected replay demonstrates example diagnosis infrastructure, not natural reviewer failure or industrial performance.','Direct geometry reader shares OCCT with generation.','Only the two changed obligations were independently traced here.']}
out.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
