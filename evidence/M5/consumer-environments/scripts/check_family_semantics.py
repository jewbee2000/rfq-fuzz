"""Analytic checks against visible drawing dimensions and own STEP readings."""
import json
import math
from pathlib import Path
import sys

root = Path(sys.argv[1])
records = []
expected = {
    'plate': ([80, 50, 8], 80*50*8-4*math.pi*3**2*8,
              ['ENVELOPE = 80.00 x 50.00 x 8.00 mm', 'H1 DIAMETER = 6.00 +/- 0.05 mm', 'H1 COUNT = 4', 'H1 TYPE = THROUGH']),
    'bore_block': ([60, 40, 35], 60*40*35-math.pi*6**2*4-math.pi*3**2*(24-4),
                   ['ENVELOPE = 60.00 x 40.00 x 35.00 mm', 'H1 DIAMETER = 6.00 +/- 0.05 mm', 'H1 TYPE = BLIND', 'H1 DEPTH = 24.00 mm', 'C1 DIAMETER = 12.00 mm', 'C1 DEPTH = 4.00 mm']),
    'pocket_block': ([60, 40, 20], 60*40*20-50*30*12,
                     ['ENVELOPE = 60.00 x 40.00 x 20.00 mm', 'P1 WIDTH = 50.00 mm', 'P1 LENGTH = 30.00 mm', 'P1 DEPTH = 12.00 mm', 'W1 THICKNESS = 5.00 mm']),
}

def near(a, b, tolerance=1e-6):
    assert abs(a-b) < tolerance, (a, b, tolerance)

for family, (envelope, analytic_volume, lines) in expected.items():
    m = json.loads((root/family/'measurements.json').read_text())
    assert m['solids'] == 1
    bbox = m['shape_bounds_mm']
    dimensions = [bbox[i+3]-bbox[i] for i in range(3)]
    for observed, target in zip(dimensions, envelope):
        near(observed, target)
    near(m['volume_mm3'], analytic_volume)
    assert m['pdf_pages'] == 1
    assert all(line in m['pdf_text'].splitlines() for line in lines)
    assert m['png_check']['pixel_delta_bounds'] is None
    assert any('SI_UNIT(.MILLI.,.METRE.)' in line for line in m['step_unit_lines'])
    cylinders = [face for face in m['faces'] if 'radius_mm' in face]
    if family == 'plate':
        assert len(cylinders) == 4
        assert sorted(tuple(face['axis_location_mm'][:2]) for face in cylinders) == [(-25,-15),(-25,15),(25,-15),(25,15)]
        for face in cylinders:
            near(face['radius_mm'], 3)
            near(face['bounds_mm'][2], -4)
            near(face['bounds_mm'][5], 4)
        details = {'through_hole_count':4, 'diameter_mm':6, 'through_depth_mm':8, 'centers_xy_mm':[[-25,-15],[-25,15],[25,-15],[25,15]]}
    elif family == 'bore_block':
        assert len(cylinders) == 2
        cylinders.sort(key=lambda face: face['radius_mm'])
        narrow, wide = cylinders
        near(narrow['radius_mm'],3); near(wide['radius_mm'],6)
        near(narrow['bounds_mm'][2], -6.5); near(narrow['bounds_mm'][5],13.5)
        near(wide['bounds_mm'][2],13.5); near(wide['bounds_mm'][5],17.5)
        for face in cylinders:
            near(face['axis_location_mm'][0],0); near(face['axis_location_mm'][1],0)
        details = {'blind_hole_total_depth_from_top_mm':24, 'narrow_cylinder_depth_mm':20, 'counterbore_depth_mm':4, 'diameters_mm':[6,12], 'blind_floor_z_mm':-6.5, 'remaining_bottom_mm':11}
    else:
        assert not cylinders
        floor = [face for face in m['faces'] if 'plane_location_mm' in face and abs(face['plane_location_mm'][2]+2)<1e-6 and abs(face['normal'][2])>0.99]
        assert len(floor)==1
        fb=floor[0]['bounds_mm']
        near(fb[0],-25);near(fb[1],-15);near(fb[3],25);near(fb[4],15)
        details={'pocket_width_mm':50,'pocket_length_mm':30,'pocket_depth_mm':12,'floor_z_mm':-2,'minimum_side_wall_mm':5}
    records.append({'family':family,'actual_export_dimensions_mm':dimensions,'actual_export_volume_mm3':m['volume_mm3'],'analytic_volume_mm3':analytic_volume,'geometry':details,'visible_pdf_quotes':lines,'pdf_png_pixels_identical':True,'result':'semantics_confirmed'})
record = {'reader':'Own direct STEPControl, actual PDF text and fresh Poppler rerender; no toolkit conclusion logic', 'cases':records, 'tolerance':{'length_mm':1e-6,'volume_mm3':1e-6},'limits':'Shares OCCT kernel with generator; named default synthetic fixtures only. Visual review recorded separately. Does not attest generated suite or certify manufacture.'}
(root/'semantic-summary.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
