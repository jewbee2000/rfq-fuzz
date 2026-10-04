import copy
import json
from pathlib import Path
import pytest
from rfqfuzz.v1 import contracts as c

def profile():
    return {"schema_version":"1.0", "id":"synthetic-standard", "version":"1", "synthetic":True, "scope":"Finite synthetic setup", "unsupported_operations":["CAM"],
            "rules":[{"id":f"A{i:02}","version":"1","source":"project release contract","retrieved":"2026-10-04","paraphrase":"Conditional synthetic policy","applicability":["metal"],"units":"mm","threshold":1,"comparison":"less_than","severity":"advisory" if i<3 else "profile_exclusion" if i==3 else "missing_information","precedence":"explicit requirement first","limits":"Not universal feasibility","synthetic_value":True} for i in range(1,5)]}

def packet():
    return {"schema_version":"1.0","case_id":"pk-012345abcdef","part_id":"P1","family":"plate","units":{"model":"mm","drawing":"mm"},
            "release_association":{"model_id":"P1","model_revision":"A","drawing_id":"P1","drawing_revision":"B","permitted_pairs":[["A","B"]]},
            "authority":{"geometry":"step","dimensions":"drawing","material_precedence":"equal","process":"Explicit public stage","release":"Approved pairs govern"},
            "manufacturing":{"model_stage":"finished","drawing_stage":"finished","transition":None,"material":"6061-T6","material_class":"metal","finish":"none","tolerance_stage":"after_finish"},
            "setup":{"orientation":"XYZ","stock_allowance_mm":[2,2,2],"fixture_allowance_mm":[0,0,5]},"profile":profile(),
            "features":[{"id":"H1","type":"through_bore_group","drawing_association":"Plan H1 leader","centers_mm":[[0,0,0]]}],
            "requirements":[{"id":"C1","representation":"drawing","description":"INSPECT H1 after finish"}],
            "obligations":[{"id":"bore_consistency","track":"package_consistency","category":"diameter","feature_id":"H1","required_modalities":["step","pdf","context"]}],
            "artifacts":[{"path":path,"sha256":"a"*64,"media_type":media} for path,media in [("part.step","model/step"),("drawing.pdf","application/pdf"),("drawing.png","image/png")]],"render":{"renderer":"Poppler","dpi":200}}

def review(conclusion="supported_clear"):
    item={"id":"f1","obligation_id":"bore_consistency","category":"diameter","feature_id":"H1","conclusion":conclusion,"evidence":[{"artifact":"drawing.pdf","quote":"H1 6.00"}],"rationale":"Supported by public evidence"}
    return {"schema_version":"1.0","reviewer":{"name":"independent","version":"1","configuration":"manual"},"results":[{"case_id":"pk-012345abcdef","packet_sha256":"b"*64,"status":"completed","reviewed_modalities":["pdf","step","context"],"reviewed_obligations":["bore_consistency"],"findings":[] if conclusion in {"supported_clear","missing_information","unsupported"} else [item],"assertions":[item] if conclusion in {"supported_clear","missing_information","unsupported"} else [],"runtime_seconds":None,"raw_ref":None,"reason":None}]}

def test_public_complete_and_legitimately_different_revisions():
    assert c.validate_packet(packet())["release_association"]["permitted_pairs"] == [["A","B"]]

@pytest.mark.parametrize("key",["authority","units","release_association","manufacturing","requirements"])
def test_missing_public_premise(key):
    p=packet(); del p[key]
    with pytest.raises(ValueError): c.validate_packet(p)

@pytest.mark.parametrize("key",list(c.PRIVATE_KEYS))
def test_private_metadata_rejected(key):
    p=packet(); p["profile"][key]="answer"
    with pytest.raises(ValueError): c.validate_packet(p)

@pytest.mark.parametrize("bad",["../secret.step","C:/secret.step","other.step"])
def test_artifact_paths(bad):
    p=packet(); p["artifacts"][0]["path"]=bad
    with pytest.raises(ValueError): c.validate_packet(p)

@pytest.mark.parametrize("conclusion",sorted(c.CONCLUSIONS))
def test_every_conclusion(conclusion):
    assert c.validate_review(review(conclusion))

def test_unknown_is_never_a_clear_or_bad_state():
    r=review("missing_information"); assert c.validate_review(r)["results"][0]["assertions"][0]["conclusion"]=="missing_information"
    r["results"][0]["status"]="pass"
    with pytest.raises(ValueError): c.validate_review(r)

def test_conflicting_decisions_and_failed_decisions_rejected():
    r=review(); r["results"][0]["findings"]=[copy.deepcopy(r["results"][0]["assertions"][0])]; r["results"][0]["findings"][0]["conclusion"]="contradiction"
    with pytest.raises(ValueError): c.validate_review(r)
    r=review(); r["results"][0]["status"]="timeout"
    with pytest.raises(ValueError): c.validate_review(r)

def test_invalid_oracle_not_scorable():
    o={"schema_version":"1.0","oracle_version":"1","case_id":"p","packet_sha256":"a"*64,"status":"invalid_fixture","reasons":["hidden label"],"measurements":{},"drawing":{},"expectations":[],"isolation":{}}
    assert c.validate_oracle(o)
    o["expectations"]=[{}]
    with pytest.raises(ValueError): c.validate_oracle(o)

def test_duplicate_keys_nonfinite_and_oversized_json(tmp_path):
    p=tmp_path/"x.json"
    for content in ['{"a":1,"a":2}','{"a":NaN}']:
        p.write_text(content)
        with pytest.raises(ValueError): c.load_json(p)
    p.write_text("123456")
    with pytest.raises(ValueError): c.load_json(p,3)

def test_m0_migration_refused():
    with pytest.raises(ValueError,match="immutable"): c.migrate_m0({})
