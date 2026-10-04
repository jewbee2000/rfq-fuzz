import copy
import importlib.util
from pathlib import Path
import pytest
from rfqfuzz.v1.scoring import score,compare,apply_adjudications
from rfqfuzz.v1.contracts import digest

spec=importlib.util.spec_from_file_location("contract_cases",Path(__file__).parents[1]/"contracts/test_v1.py")
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def setup(want="contradiction",got="contradiction"):
    r=h.review(got);r["results"][0]["packet_sha256"]="b"*64
    e={"obligation_id":"bore_consistency","track":"package_consistency","category":"diameter","feature_id":"H1","conclusion":want,"rule_id":None,"evidence":[{"artifact":"drawing.pdf","quote":"H1 6.00"}],"root_cause":"units","operator":"O01"}
    c={"schema_version":"1.0","oracle_version":"1","case_id":"pk-012345abcdef","packet_sha256":"b"*64,"status":"valid","reasons":[],"measurements":{},"drawing":{},"expectations":[e],"isolation":{"passed":True}}
    return r,{"cases":[c]}

@pytest.mark.parametrize("want,got,outcome",[("contradiction","contradiction","detected"),("supported_clear","contradiction","false_alert"),("contradiction","supported_clear","explicit_false_clear"),("missing_information","missing_information","appropriate_abstention"),("advisory","profile_exclusion","reasoning_error"),("missing_information","supported_clear","reasoning_error"),("profile_exclusion","profile_exclusion","detected"),("unsupported","unsupported","unsupported")])
def test_semantics(want,got,outcome):
    r,o=setup(want,got);assert score(r,o)["rows"][0]["outcome"]==outcome

def test_wrong_feature_number_alone_wrong_region_and_duplicates():
    for key,value in [("feature_id","H2"),("evidence",[{"artifact":"drawing.pdf","quote":"6.00 somewhere"}])]:
        r,o=setup();r["results"][0]["findings"][0][key]=value
        s=score(r,o);assert s["rows"][0]["outcome"]=="silent_miss" and not s["precision_finalized"]
    r,o=setup();o["cases"][0]["expectations"][0]["evidence"][0]["region"]="page1:H1"
    assert score(r,o)["rows"][0]["outcome"]=="silent_miss"
    r,o=setup();r["results"][0]["findings"]*=3
    assert score(r,o)["tracks"]["package_consistency"]["detected"]==1

def test_hand_counts_tracks_baselines_missing_and_silent():
    r,o=setup(); second=copy.deepcopy(o["cases"][0]);second["case_id"]="pk-000000000001";second["expectations"][0]["conclusion"]="supported_clear";o["cases"].append(second)
    row=copy.deepcopy(r["results"][0]);row["case_id"]=second["case_id"];r["results"].append(row)
    n=score(r,o)["tracks"]["package_consistency"]
    assert (n["detected"],n["issues"],n["false_alerts"],n["clean"])==(1,1,1,1)
    for row in r["results"]:row["findings"][0]["conclusion"]="supported_clear"
    n=score(r,o)["tracks"]["package_consistency"];assert n["explicit_false_clears"]==1 and n["correct_clear"]==1
    for row in r["results"]:row["findings"][0]["conclusion"]="missing_information"
    n=score(r,o)["tracks"]["package_consistency"];assert n["detected"]==0 and n["abstentions"]==2
    r["results"]=[];assert score(r,o)["tracks"]["package_consistency"]["execution_failures"]==2
    r,o=setup();r["results"][0]["findings"]=[];assert score(r,o)["rows"][0]["outcome"]=="silent_miss"

def test_partial_coverage_invalid_fixture_and_packet_binding():
    r,o=setup();r["results"][0]["status"]="partial"
    assert score(r,o)["rows"][0]["outcome"]=="detected"
    r["results"][0]["reviewed_obligations"]=[];assert score(r,o)["rows"][0]["outcome"]=="uncovered"
    r["results"][0]["packet_sha256"]="c"*64
    with pytest.raises(ValueError,match="bytes"):score(r,o)
    o["cases"][0].update(status="invalid_fixture",expectations=[],reasons=["collateral"])
    assert score(r,o)["invalid_rate"]=={"numerator":1,"denominator":1}

def test_compare_oracle_and_profile_revision():
    r,o=setup();base={"manifest":dict(suite_sha256="a",oracle_sha256="b",profile_sha256="c"),"score":score(r,o)}
    for key in base["manifest"]:
        other=copy.deepcopy(base);other["manifest"][key]="changed"
        with pytest.raises(ValueError,match="incompatible"):compare(base,other)

def test_adjudication_bound_to_raw_and_oracle():
    r,o=setup();item=r["results"][0]["findings"][0]
    a={"raw_sha256":"raw","oracle_sha256":"oracle","decisions":[{"case_id":r["results"][0]["case_id"],"finding_sha256":digest(item),"reason":"Evidence inspected","original_category":"diameter","mapped_category":"bore"}]}
    assert apply_adjudications(r,a,"raw","oracle")["results"][0]["findings"][0]["category"]=="bore"
    with pytest.raises(ValueError,match="stale"):apply_adjudications(r,a,"changed","oracle")

def test_units_metric_and_missing_artifact_cannot_match():
    r,o=setup();e=o["cases"][0]["expectations"][0]
    e["evidence"]=[{"artifact":"part.step","quote":"H1 diameter_mm=6.000000"},{"artifact":"drawing.pdf","quote":"H1 diameter=6.00 mm"}]
    item=r["results"][0]["findings"][0]
    item["evidence"]=[{"artifact":"part.step","quote":"H1 diameter_mm=6.000000"},{"artifact":"drawing.pdf","quote":"H1 diameter=6.00 in"}]
    assert score(r,o)["rows"][0]["outcome"]=="silent_miss"
    item["evidence"][1]["quote"]="H1 diameter=6.00 mm"
    assert score(r,o)["rows"][0]["outcome"]=="detected"
    item["evidence"][0]["quote"]="H1 depth_mm=6.000000"
    assert score(r,o)["rows"][0]["outcome"]=="silent_miss"

def test_per_track_hand_counts_and_root_grouping():
    r,o=setup();e=copy.deepcopy(o["cases"][0]["expectations"][0]);e.update(obligation_id="wall",track="cnc_advisory",category="wall",feature_id="W1",conclusion="advisory",root_cause="wall",operator="A01")
    o["cases"][0]["expectations"].append(e)
    row=r["results"][0];row["reviewed_obligations"].append("wall")
    item=copy.deepcopy(row["findings"][0]);item.update(obligation_id="wall",category="wall",feature_id="W1",conclusion="profile_exclusion");row["findings"].append(item)
    s=score(r,o);assert s["tracks"]["package_consistency"]["detected"]==1 and s["tracks"]["cnc_advisory"]["reasoning_errors"]==1
    o["cases"][0]["expectations"][1]["root_cause"]="units";o["cases"][0]["expectations"][1]["track"]="package_consistency"
    with pytest.raises(ValueError,match="root cause"):score(r,o)
