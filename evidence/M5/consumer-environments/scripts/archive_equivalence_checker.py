"""Independently compare tested Windows-byte kit to the portable Git kit."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import tarfile

def files(path):
    with tarfile.open(path) as handle:
        return {entry.name:handle.extractfile(entry).read() for entry in handle.getmembers() if entry.isfile()}
tested=files(sys.argv[1]);portable=files(sys.argv[2]);records=[];failures=[]
for name,data in tested.items():
    other=portable.get(name)
    if other is None:
        failures.append({'path':name,'reason':'missing portable file'});continue
    exact=data==other
    normalized=data.replace(b'\r\n',b'\n')==other.replace(b'\r\n',b'\n')
    protected=name.startswith('examples/v1-demo/')
    code=name.startswith('src/') and name.endswith('.py')
    ast_equal=None
    if code:
        ast_equal=ast.dump(ast.parse(data.decode('utf-8')),include_attributes=False)==ast.dump(ast.parse(other.decode('utf-8')),include_attributes=False)
    okay=exact if protected else normalized
    if code:okay=okay and ast_equal
    if not okay:failures.append({'path':name,'reason':'protected byte/source normalization mismatch'})
    records.append({'path':name,'exact_bytes':exact,'crlf_lf_normalized_equal':normalized,'source_ast_equal':ast_equal,'protected_demo_bytes':protected,'tested_sha256':hashlib.sha256(data).hexdigest(),'portable_sha256':hashlib.sha256(other).hexdigest()})
added=sorted(set(portable)-set(tested))
assert added==['.gitattributes'],added
record={'status':'passed' if not failures else 'failed','tested_archive_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'portable_archive_sha256':hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),'tested_implementation_commit':'55b288a8df0d1b3ced607c8d97d23847b2f122ba','portable_commit':'348c5f1ea5a6e99bc0acdb4f0d0af52f3a8146e0','protected_demo_files_checked':sum(x['protected_demo_bytes']for x in records),'source_modules_checked':sum(x['source_ast_equal'] is not None for x in records),'additional_files':added,'files':records,'failures':failures,'scope':'All audited inputs must be byte-identical; all source modules must have equal normalized bytes and AST. Normal text checkout line endings are the only accepted file difference.'}
Path(sys.argv[3]).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='files'},indent=2))
sys.exit(0 if not failures else 2)
