from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import pytest
from pypdf import PdfReader
from rfqfuzz.v1.contracts import load_json, private_scan, read_packet
from rfqfuzz.v1.mutations import specifications, objective_group, generate_suite, verify_spec


def test_finite_plan_and_no_core_layout_split_leakage():
    rows = specifications(42)
    assert len(rows) == 145 and len({r["case_id"] for r in rows}) == 145
    objective = [r for r in rows if r["operator"].startswith("O") and r["variant"] != "underdetermined" and r["ancestry"] != "source-sparse-00"]
    assert Counter(r["operator"] for r in objective) == {f"O{i:02}": 18 for i in range(1, 7)}
    assert Counter(r["variant"] for r in objective) == {"defective": 36, "repaired": 36, "valid_alternative": 36}
    assert all(verify_spec(r) is r for r in rows)
    for key in ("ancestry",):
        assert all(len({r["partition"] for r in rows if r[key] == value}) == 1 for value in {r[key] for r in rows})
    assert {r["partition"] for r in rows} == {"development"}
    assert {r["source_parameters"]["layout_ancestry"] for r in rows} == {"bounded-vector-a4-v1"}


def test_semantic_replay_and_seed_recording():
    assert specifications(42) == specifications(42)
    a, b = specifications(42), specifications(43)
    assert all(x["source_parameters"] == y["source_parameters"] for x, y in zip(a, b))
    assert {r["case_id"] for r in a}.isdisjoint({r["case_id"] for r in b})
    for bad in (-1, 2**32, "42"):
        with pytest.raises(ValueError):
            specifications(bad)


@pytest.mark.parametrize("operator,changes", [("O01", {"family": "pocket_block"}), ("O02", {"parameters": {"count": 2}}), ("A01", {"family": "plate"}), ("A02", {"family": "plate"})])
def test_unsupported_operator_application_refused_before_export(tmp_path, operator, changes):
    row = next(r for r in specifications() if r["operator"] == operator)
    row = deepcopy(row)
    row["source_parameters"].update(changes)
    row["source_parameters"]["parameters"] = changes.get("parameters", {})
    with pytest.raises(ValueError):
        generate_suite(tmp_path / "bad", specs=[row])
    assert not (tmp_path / "bad").exists()


@pytest.mark.parametrize("operator", [f"O{i:02}" for i in range(1, 7)])
def test_objective_final_artifact_edit_and_repair(tmp_path, operator):
    rows = objective_group(operator)
    summary = generate_suite(tmp_path / "suite", specs=rows)
    assert summary["public_cases"] == 3
    texts = []
    for row in rows:
        folder = tmp_path / "suite" / "public" / row["case_id"]
        packet = read_packet(folder)
        private_scan(packet)
        assert set(p.name for p in folder.iterdir()) == {"packet.json", "part.step", "drawing.pdf", "drawing.png"}
        texts.append(PdfReader(folder / "drawing.pdf").pages[0].extract_text())
    defective, repaired, alternative = texts
    if operator == "O01":
        assert "H1 DIAMETER = 6.80" in defective and "H1 DIAMETER = 6.00" in repaired
        assert "MODEL STAGE = intermediate" in alternative and "TRANSITION = ream H1" in alternative
    elif operator == "O02":
        assert "H1 COUNT = 3" in defective and "H1 COUNT = 4" in repaired
        assert "H1 COUNT = 2" in alternative and alternative.count("OTHER") == 2
    elif operator == "O03":
        assert "ENVELOPE = 80.0000 x 50.0000 x 8.0000 in" in defective
        assert "UNITS = mm" in repaired and "H1 DIAMETER = 0.2362" in alternative
    elif operator == "O04":
        assert "MATERIAL = 7075-T6" in defective and "MATERIAL = 6061-T6" in repaired
        assert "MATERIAL = AL6061-T6" in alternative
    elif operator == "O05":
        assert "SURFACE ROUGHNESS =" not in defective and "SURFACE ROUGHNESS = 3.20 um" in repaired
        p = read_packet(tmp_path / "suite" / "public" / rows[2]["case_id"])
        assert p["requirements"] == []
    else:
        assert "DRAWING REV = B" in defective and "DRAWING REV = A" in repaired
        p = read_packet(tmp_path / "suite" / "public" / rows[2]["case_id"])
        assert "DRAWING REV = B" in alternative and p["release_association"]["permitted_pairs"] == [["A", "B"]]
    private = load_json(tmp_path / "suite" / "private" / "mutations.json")
    assert len(private["mutations"]) == 3


def test_authoritative_alternate_roughness_wording_is_public(tmp_path):
    rows = objective_group("O05", index=1)
    generate_suite(tmp_path / "suite", specs=[rows[2]])
    folder = tmp_path / "suite" / "public" / rows[2]["case_id"]
    packet = read_packet(folder)
    assert "SURFACE FINISH" in packet["requirements"][0]["description"]
    text = PdfReader(folder / "drawing.pdf").pages[0].extract_text()
    assert "SURFACE FINISH = Ra 3.20 um" in text


def test_sparse_cad_authority_does_not_hide_drawing_only_requirement(tmp_path):
    row = next(r for r in specifications() if r["ancestry"] == "source-sparse-00")
    generate_suite(tmp_path / "suite", specs=[row])
    folder = tmp_path / "suite" / "public" / row["case_id"]
    packet = read_packet(folder)
    assert packet["authority"]["dimensions"] == "step" and packet["requirements"][0]["representation"] == "drawing"
    text = PdfReader(folder / "drawing.pdf").pages[0].extract_text()
    assert "H1 DIAMETER =" not in text and "H1 COUNT =" not in text
    assert "SURFACE ROUGHNESS = 3.20 um" in text
