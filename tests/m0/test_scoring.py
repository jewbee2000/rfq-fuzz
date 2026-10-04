import copy
import json
import shutil
from pathlib import Path
import pytest
from rfqfuzz.scoring import score, read_review, compare, injected_regression, apply_adjudications, import_result
from rfqfuzz.reporting import make_report
from rfqfuzz.reference import review_public

ORACLE = json.loads(Path('evidence/M0/validation/oracle.json').read_text(encoding='utf-8'))
BASE = json.loads(Path('evidence/M0/runs/reference/review.json').read_text(encoding='utf-8'))

def altered(conclusion):
    value = copy.deepcopy(BASE)
    for row in value['results']:
        item = (row['findings'] + row['assertions'])[0]
        item['conclusion'] = conclusion
        row['findings'] = [item] if conclusion == 'contradiction' else []
        row['assertions'] = [] if conclusion == 'contradiction' else [item]
    return value

def defective(response):
    return next(r for r in response['results'] if r['case_id'] == 'pk-7a1c')

def test_reference_and_injected_regression_hand_counts():
    assert read_review('evidence/M0/runs/reference/review.json') == BASE
    n = score(BASE, ORACLE)['counts']
    assert (n['detected'],n['defects'],n['false_alerts'],n['clean'],n['correct_clear']) == (1,1,0,2,2)
    n = score(injected_regression(BASE), ORACLE)['counts']
    assert (n['detected'],n['false_alerts'],n['explicit_false_clears'],n['correct_clear']) == (0,1,1,1)

@pytest.mark.parametrize('conclusion,expected', [
    ('contradiction', {'detected':1,'false_alerts':2,'correct_clear':0}),
    ('supported_clear', {'detected':0,'explicit_false_clears':1,'correct_clear':2}),
    ('missing_information', {'detected':0,'correct_clear':0,'missing_information':3}),
    ('unsupported', {'detected':0,'correct_clear':0,'unsupported':3}),
])
def test_trivial_baselines_do_not_pass(conclusion, expected):
    counts = score(altered(conclusion), ORACLE)['counts']
    for key,value in expected.items(): assert counts[key] == value

def test_duplicates_do_not_multiply_credit():
    value = copy.deepcopy(BASE)
    defective(value)['findings'] *= 3
    assert score(value, ORACLE)['counts']['detected'] == 1

@pytest.mark.parametrize('key,value', [('feature_id','H99'),('geometry_evidence','Diameter42 mm at an unrelated feature'),('category','check_everything')])
def test_wrong_witness_does_not_match(key, value):
    review = copy.deepcopy(BASE)
    defective(review)['findings'][0][key] = value
    scored = score(review, ORACLE)
    assert scored['counts']['detected'] == 0
    assert scored['counts']['silent_misses'] == 1
    assert len(scored['unadjudicated']) == 1
    assert not scored['precision_finalized']

def test_missing_results_errors_partial_and_unsupported_are_distinct():
    missing = copy.deepcopy(BASE); missing['results'] = []
    assert score(missing,ORACLE)['counts']['execution_failures'] == 3
    for state,outcome in [('error','reviewer_failure'),('timeout','reviewer_failure'),('partial','partial_or_uncovered'),('unsupported','unsupported')]:
        review = copy.deepcopy(BASE); defective(review)['status'] = state
        result = score(review,ORACLE)
        assert result['counts']['detected'] == 0
        assert next(r for r in result['rows'] if r['case_id']=='pk-7a1c')['outcome'] == outcome

def test_inconsistent_assertions_get_no_detection_credit():
    review = copy.deepcopy(BASE)
    clear = copy.deepcopy(defective(review)['findings'][0]);clear['conclusion']='supported_clear'
    defective(review)['assertions']=[clear]
    assert score(review,ORACLE)['counts']['detected'] == 0

def test_invalid_oracle_and_stale_packets_cannot_score():
    oracle=copy.deepcopy(ORACLE);oracle['status']='invalid_fixture'
    with pytest.raises(ValueError,match='cannot be scored'):score(BASE,oracle)
    review=copy.deepcopy(BASE);defective(review)['packet_sha256']='0'*64
    with pytest.raises(ValueError,match='different packet'):score(review,ORACLE)

def test_unknown_class_and_malformed_response_rejected(tmp_path):
    for mutation in ('status','schema','fields','runtime'):
        review=copy.deepcopy(BASE)
        if mutation=='status':defective(review)['status']='unknown'
        if mutation=='schema':review['schema_version']='future'
        if mutation=='fields':del defective(review)['reviewed_modalities']
        if mutation=='runtime':defective(review)['runtime_seconds']=float('nan')
        path=tmp_path/f'{mutation}.json';path.write_text(json.dumps(review),encoding='utf-8')
        with pytest.raises(ValueError):read_review(path)

def test_mismatched_run_comparison_rejected():
    a=json.loads(Path('evidence/M0/runs/imported-reference/run.json').read_text())
    for key in ('suite_sha256','oracle_sha256','profile_sha256'):
        b=copy.deepcopy(a);b['manifest'][key]='bad'
        with pytest.raises(ValueError,match=key):compare(a,b)

def test_manual_category_adjudication_preserves_conclusions_and_evidence():
    raw=read_review('evidence/M0/review-handoff/review-output/review.json')
    decisions=json.loads(Path('evidence/M0/category-adjudication.json').read_text())
    normalized=apply_adjudications(raw,decisions['decisions'])
    for before,after in zip(raw['results'],normalized['results']):
        for a,b in zip(before['findings']+before['assertions'],after['findings']+after['assertions']):
            assert {k:v for k,v in a.items() if k!='category'} == {k:v for k,v in b.items() if k!='category'}
    assert score(normalized,ORACLE)['counts']['detected']==1
    bad=copy.deepcopy(decisions['decisions']);bad[0]['finding_sha256']='0'*64
    with pytest.raises(ValueError,match='exactly one'):apply_adjudications(raw,bad)

def test_stale_adjudication_is_rejected(tmp_path):
    d=json.loads(Path('evidence/M0/category-adjudication.json').read_text());d['oracle_sha256']='0'*64
    p=tmp_path/'stale.json';p.write_text(json.dumps(d))
    with pytest.raises(ValueError,match='stale adjudication'):
        import_result('evidence/M0/review-handoff/review-output/review.json','evidence/M0/bundle/public','evidence/M0/validation/oracle.json',tmp_path/'out',p)

def test_reference_unsupported_input_is_distinct_from_error(tmp_path):
    public=tmp_path/'public';folder=public/'pk-b8e2'
    shutil.copytree('evidence/M0/bundle/public/pk-b8e2',folder)
    p=folder/'packet.json';data=json.loads(p.read_text());data['units']['drawing']='inch';p.write_text(json.dumps(data))
    result=review_public(public,tmp_path/'review')
    assert result['results'][0]['status']=='unsupported'
    assert result['results'][0]['findings']==[] and result['results'][0]['assertions']==[]

def test_report_escapes_untrusted_text(tmp_path):
    paths=[]
    for name in ('imported-reference','imported-injected'):
        run=json.loads(Path(f'evidence/M0/runs/{name}/run.json').read_text(encoding='utf-8'))
        run['reviewer']['name']='<script>alert(1)</script>'
        folder=tmp_path/name;folder.mkdir();p=folder/'run.json';p.write_text(json.dumps(run),encoding='utf-8');paths.append(p)
    make_report(paths,'evidence/M0/validation/oracle.json','evidence/M0/bundle/public',tmp_path/'report')
    html=(tmp_path/'report/index.html').read_text(encoding='utf-8')
    assert '<script>' not in html and '&lt;script&gt;' in html
