"""Generate transport required-field schemas from the frozen semantic boundary."""
import ast
import json
from pathlib import Path

source=Path("src/rfqfuzz/v1/contracts.py")
names={"validate_packet":"PacketSpec","validate_profile":"CapabilityProfile","validate_mutation":"MutationSpec","validate_oracle":"OracleRecord","validate_review":"ReviewResult","validate_manifest":"RunManifest"}
for node in ast.parse(source.read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in names:
        call=node.body[0].value
        required=ast.literal_eval(call.args[1])
        schema={"$schema":"https://json-schema.org/draft/2020-12/schema","title":names[node.name],"description":"Transport boundary; semantic nested and evidence checks require rfqfuzz.v1.contracts.","type":"object","required":list(required),"additionalProperties":False,"properties":{key:({"const":"1.0"} if key=="schema_version" else {}) for key in required}}
        target=Path("schemas/v1")/(names[node.name]+".schema.json")
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(schema,indent=2)+"\n")
