"""Finite, deterministic M0 import/matching/comparison; no industrial score."""
from pathlib import Path
import copy
import hashlib
import json
import math
import re
from .contracts import VERSION, OBLIGATION, sha256, write_json

def check_schema(value, schema, root=None, path='$'):
    """Validate precisely the JSON Schema keywords used by the frozen M0 schema."""
    root = root or schema
    if '$ref' in schema:
        target = root
        for part in schema['$ref'].split('/')[1:]:
            target = target[part]
        return check_schema(value, target, root, path)
    if 'const' in schema and value != schema['const']:
        raise ValueError(f'{path}: const mismatch')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path}: unsupported enum')
    kinds = schema.get('type', [])
    kinds = [kinds] if isinstance(kinds, str) else kinds
    types = {'object': lambda x: isinstance(x, dict), 'array': lambda x: isinstance(x, list),
             'string': lambda x: isinstance(x, str), 'number': lambda x: type(x) in (int,float) and math.isfinite(x),
             'null': lambda x: x is None}
    if kinds and not any(types[k](value) for k in kinds):
        raise ValueError(f'{path}: wrong type')
    if isinstance(value, dict):
        missing = set(schema.get('required', [])) - value.keys()
        extra = value.keys() - schema.get('properties', {}).keys()
        if missing or (schema.get('additionalProperties') is False and extra):
            raise ValueError(f'{path}: missing {sorted(missing)} / extra {sorted(extra)}')
        for key, child in schema.get('properties', {}).items():
            if key in value:
                check_schema(value[key], child, root, f'{path}.{key}')
    if isinstance(value, list):
        if schema.get('uniqueItems') and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            raise ValueError(f'{path}: duplicate items')
        for i, item in enumerate(value):
            check_schema(item, schema.get('items', {}), root, f'{path}[{i}]')
    if isinstance(value, str) and 'pattern' in schema and re.search(schema['pattern'], value) is None:
        raise ValueError(f'{path}: pattern mismatch')
    if type(value) in (int,float) and value < schema.get('minimum', -math.inf):
        raise ValueError(f'{path}: below minimum')

def read_review(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    schema = json.loads(Path('schemas/m0-review-result.schema.json').read_text(encoding='utf-8'))
    check_schema(data, schema)
    ids = [r['case_id'] for r in data['results']]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate case response')
    return data

def manifest(public_root, oracle_path):
    packets = [(p.parent.name, sha256(p)) for p in sorted(Path(public_root).glob('*/packet.json'))]
    profiles = [json.loads(p.read_text(encoding='utf-8'))['profile'] for p in sorted(Path(public_root).glob('*/packet.json'))]
    digest = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()
    return {'schema_version': VERSION, 'suite_sha256': digest(packets), 'oracle_sha256': sha256(oracle_path),
            'profile_sha256': digest(profiles), 'adapter_version': 'manual-m0.1', 'environment_sha256': sha256('evidence/M0/environment.json'),
            'limits': 'three synthetic presentations, one H1 obligation each; CNC advisories unsupported'}

def supported_witness(finding, case):
    if finding['obligation'] != OBLIGATION or finding['feature_id'] != 'H1' or finding['category'] not in {'diameter_consistency','bore_diameter_consistency','dimensional_consistency','model_drawing_mismatch'}:
        return False
    if not all(finding[k].strip() for k in ('drawing_evidence','geometry_evidence','context_evidence','rationale')):
        return False
    numbers = lambda text: [float(v) for v in re.findall(r'(?<![\d.])[+-]?\d+(?:\.\d+)?(?![\d.])', text)]
    close = lambda target, text: any(abs(target - n) <= 1e-6 for n in numbers(text))
    radius = case['geometry']['cylinders'][0]['radius_mm']
    geometry_ok = close(radius * 2, finding['geometry_evidence']) or ('radius' in finding['geometry_evidence'].lower() and close(radius, finding['geometry_evidence']))
    return close(case['drawing']['callout']['diameter_mm'], finding['drawing_evidence']) and geometry_ok

def score(response, oracle):
    if oracle['status'] != 'valid':
        raise ValueError('invalid/unverified oracle cannot be scored')
    lookup = {r['case_id']: r for r in response['results']}
    if set(lookup) - {c['case_id'] for c in oracle['cases']}:
        raise ValueError('response has cases outside frozen suite')
    rows, unmatched = [], []
    totals = {k: 0 for k in ('defects','detected','clean','false_alerts','explicit_false_clears','silent_misses','correct_clear','missing_information','execution_failures','unsupported','covered')}
    for case in oracle['cases']:
        expected = case['expected_conclusion']
        totals['defects' if expected == 'contradiction' else 'clean'] += 1
        row = {'case_id': case['case_id'], 'expected': expected, 'status': 'missing', 'actual': [], 'outcome': 'reviewer_failure', 'unadjudicated': []}
        actual = lookup.get(case['case_id'])
        if actual is None:
            totals['execution_failures'] += 1
            rows.append(row)
            continue
        if actual['packet_sha256'] != case['packet_sha256']:
            raise ValueError('review response bound to different packet bytes')
        row['status'] = actual['status']
        if actual['status'] in ('error','timeout'):
            totals['execution_failures'] += 1
        elif actual['status'] == 'unsupported':
            totals['unsupported'] += 1
            row['outcome'] = 'unsupported'
        elif actual['status'] != 'completed' or not {'step','pdf','context'} <= set(actual['reviewed_modalities']) or OBLIGATION not in actual['reviewed_obligations']:
            row['outcome'] = 'partial_or_uncovered'
        else:
            totals['covered'] += 1
            accepted = []
            for f in actual['findings'] + actual['assertions']:
                if supported_witness(f, case):
                    accepted.append(f)
                else:
                    row['unadjudicated'].append(f)
                    unmatched.append({'case_id': case['case_id'], 'finding': f, 'status': 'unadjudicated'})
            conclusions = {f['conclusion'] for f in accepted}
            row['actual'] = sorted(conclusions)
            if {'contradiction','supported_clear'} <= conclusions:
                row['outcome'] = 'inconsistent_reviewer_assertions'
            elif 'contradiction' in conclusions:
                if expected == 'contradiction':
                    row['outcome'] = 'detected'; totals['detected'] += 1
                else:
                    row['outcome'] = 'false_alert'; totals['false_alerts'] += 1
            elif 'supported_clear' in conclusions:
                if expected == 'contradiction':
                    row['outcome'] = 'explicit_false_clear'; totals['explicit_false_clears'] += 1
                else:
                    row['outcome'] = 'correct_clear'; totals['correct_clear'] += 1
            elif 'missing_information' in conclusions:
                row['outcome'] = 'missing_information'; totals['missing_information'] += 1
            elif 'unsupported' in conclusions:
                row['outcome'] = 'unsupported'; totals['unsupported'] += 1
            elif conclusions:
                row['outcome'] = 'unadjudicated_conclusion'
            else:
                row['outcome'] = 'silent_miss' if expected == 'contradiction' else 'unasserted_clean'
                if expected == 'contradiction': totals['silent_misses'] += 1
            if conclusions - {'contradiction','supported_clear','missing_information','unsupported'}:
                row['unadjudicated'].extend(f for f in accepted if f['conclusion'] not in {'contradiction','supported_clear','missing_information','unsupported'})
                unmatched.extend({'case_id': case['case_id'], 'finding': f, 'status': 'unadjudicated'} for f in row['unadjudicated'] if f in accepted)
        row['reviewed_modalities'] = actual['reviewed_modalities']
        rows.append(row)
    return {'track': 'package_consistency', 'counts': totals, 'rows': rows, 'unadjudicated': unmatched,
            'precision_finalized': False, 'precision_note': 'No precision claim: M0 scores one named finite obligation per case; unmatched findings require adjudication.',
            'cnc_advisory': {'status': 'unsupported', 'scored_obligations': 0}}

def apply_adjudications(response, decisions):
    """Map free reviewer categories after inspecting evidence; preserve raw findings."""
    value = copy.deepcopy(response)
    applied = 0
    for decision in decisions:
        hits = []
        for row in value['results']:
            for finding in row['findings'] + row['assertions']:
                digest = hashlib.sha256(json.dumps(finding,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest()
                if row['case_id'] == decision['case_id'] and digest == decision['finding_sha256']:
                    hits.append(finding)
        if len(hits) != 1 or not decision['reason'].strip() or hits[0]['category'] != decision['original_category']:
            raise ValueError('adjudication does not identify exactly one evidence-bound finding')
        hits[0]['category'] = decision['mapped_category']
        applied += 1
    if applied != len(decisions):
        raise ValueError('incomplete adjudication application')
    return value

def import_result(path, public_root, oracle_path, out, adjudication_path=None):
    out = Path(out)
    if out.exists():
        raise ValueError('import output exists; preserve raw run')
    response = read_review(path)
    oracle = json.loads(Path(oracle_path).read_text(encoding='utf-8'))
    adjudication = None
    if adjudication_path:
        adjudication = json.loads(Path(adjudication_path).read_text(encoding='utf-8'))
        if adjudication['raw_sha256'] != sha256(path) or adjudication['oracle_sha256'] != sha256(oracle_path):
            raise ValueError('stale adjudication raw/oracle binding')
        response = apply_adjudications(response, adjudication['decisions'])
    result = score(response, oracle)
    record = {'manifest': manifest(public_root, oracle_path), 'reviewer': response['reviewer'], 'score': result,
              'raw_sha256': sha256(path), 'raw_source': str(path), 'adjudication': adjudication}
    out.mkdir(parents=True)
    (out / 'raw-review.json').write_bytes(Path(path).read_bytes())
    write_json(out / 'run.json', record)
    return record

def compare(a, b):
    for key in ('suite_sha256','oracle_sha256','profile_sha256'):
        if a['manifest'][key] != b['manifest'][key]:
            raise ValueError(f'incompatible comparison: {key}')
    before = {r['case_id']: r for r in a['score']['rows']}
    changes = []
    for row in b['score']['rows']:
        old = before[row['case_id']]
        if old['outcome'] != row['outcome']:
            changes.append({'case_id': row['case_id'], 'before': old['outcome'], 'after': row['outcome']})
    return changes

def injected_regression(response):
    """Deliberate reference mutations only; external observations remain untouched."""
    result = copy.deepcopy(response)
    result['reviewer'].update(name='RFQFuzz reference — DELIBERATELY INJECTED REGRESSION', version='m0-template-injected-2',
                             configuration='Injected: clear same-stage contradiction; ignore declared ream transition and flag later-stage target. Not a naturally observed external failure.')
    for row in result['results']:
        if row['findings']:
            item = row['findings'][0]
            item.update(conclusion='supported_clear', rationale='DELIBERATE INJECTION: ignore same-stage nominal mismatch.')
            row['assertions'], row['findings'] = [item], []
        elif any('intermediate' in f['context_evidence'].lower() for f in row['assertions']):
            item = row['assertions'][0]
            item.update(conclusion='contradiction', rationale='DELIBERATE INJECTION: ignore the explicit later reaming operation.')
            row['findings'], row['assertions'] = [item], []
    return result
