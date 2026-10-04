import copy
from pathlib import Path
from rfqfuzz.v1.contracts import load_json,read_packet
from rfqfuzz.v1.scoring import score,matches

def test_actual_count_witness_four_does_not_credit_forty():
    root=Path(__file__).resolve().parents[2];cid="pk-d0f406e22f58"
    oracle={"cases":[load_json(root/"evidence/M4/core-validated"/cid/"inspection.json")]}
    response=load_json(root/"evidence/M3/reference-core/review.json")
    response["results"]=[row for row in response["results"] if row["case_id"]==cid]
    finding=next(f for f in response["results"][0]["findings"] if f["obligation_id"]=="obj-count")
    expected=next(e for e in oracle["cases"][0]["expectations"] if e["obligation_id"]=="obj-count")
    assert matches(finding,expected)
    for witness in finding["evidence"]:
        witness["quote"]=witness["quote"].replace("H1 count=4","H1 count=40").replace("H1 COUNT = 3","H1 COUNT = 30")
    assert not matches(finding,expected)
    result=score(response,oracle,{cid:read_packet(root/"evidence/M2/core-suite/public"/cid)})
    row=next(r for r in result["rows"] if r["obligation_id"]=="obj-count")
    assert row["outcome"]=="silent_miss"
    assert len(result["unadjudicated"])==1
