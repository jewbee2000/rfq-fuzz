"""Retain separately authored artifacts and coordinator independent checks."""
import shutil
from pathlib import Path
from rfqfuzz.v1.contracts import load_json,sha256,write_json
from rfqfuzz.v1.validation import attest_case

source=Path("work/transfer-author-v2");target=Path("evidence/M5/transfer-v2")
assert not target.exists()
shutil.copytree(source,target/"author")
shutil.copytree("work/transfer-validation-v2",target/"independent-observation")
folder=target/"author/pk-48bd731ca9e2"
record=load_json(target/"independent-observation/inspection.json")
attestation={"cases":[{"case_id":folder.name,"pdf_sha256":sha256(folder/"drawing.pdf"),"png_sha256":sha256(folder/"drawing.png"),"legible_unclipped":True,"view_associations_checked":True,"reviewer":"Coordinator AI separately viewed complete2500x1806 exported PNG and independent STEP/PDF measurements; no human engineer claim","visible_annotation_lines":[s for lines in record["drawing"]["annotations"].values() for s in lines]}]}
write_json(target/"attestation.json",attestation)
attest_case(record,folder,attestation)
write_json(target/"oracle.json",{"schema_version":"1.0","oracle_version":"1.0-observed-1","status":record["status"],"cases":[record],"counts":{record["status"]:1},"limitations":["Separately agent-authored synthetic layout; still same OCCT kernel and finite annotation grammar; no engineer review or manufacture"]})
author=load_json(target/"author/PRIVATE_AUTHOR_EXPECTATIONS.json")
print(record["status"],[(e["category"],e["conclusion"]) for e in record["expectations"]])
print("Private author record retained for post-validation disagreement audit:",author)
