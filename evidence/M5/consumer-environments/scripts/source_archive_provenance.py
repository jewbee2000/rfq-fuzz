"""Bind the received archive's file bytes to the declared local Git commit."""
import hashlib
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tarfile

parser=argparse.ArgumentParser()
parser.add_argument('archive',type=Path);parser.add_argument('repo',type=Path);parser.add_argument('output',type=Path)
parser.add_argument('--commit',default='55b288a8df0d1b3ced607c8d97d23847b2f122ba')
parser.add_argument('--archive-sha256',default='e859283037daac28e2664b3939ed3846a3b602d511610f0d6362705436719931')
args=parser.parse_args()
archive=args.archive;repo=args.repo;output=args.output
commit=args.commit;expected_archive=args.archive_sha256
actual_archive=hashlib.sha256(archive.read_bytes()).hexdigest()
assert actual_archive==expected_archive
tree=subprocess.run(['git','-C',str(repo),'ls-tree','-r',commit],check=True,capture_output=True,text=True).stdout
blobs={}
for line in tree.splitlines():
    metadata,name=line.split('\t',1)
    mode,kind,sha=metadata.split()
    if kind=='blob':blobs[name]=sha
files=[]
with tarfile.open(archive,'r:gz') as handle:
    for entry in handle.getmembers():
        if entry.isdir():continue
        assert entry.isfile() and not entry.name.startswith('/') and '..' not in Path(entry.name).parts
        data=handle.extractfile(entry).read()
        sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        exact=blobs[entry.name]==sha
        protected=entry.name.startswith('examples/v1-demo/') or Path(entry.name).suffix.lower() in {'.step','.pdf','.png'}
        normalized=data.replace(b'\r\n',b'\n')
        normalized_sha=hashlib.sha1(b'blob '+str(len(normalized)).encode()+b'\0'+normalized).hexdigest()
        assert exact or (not protected and blobs[entry.name]==normalized_sha),entry.name
        files.append({'path':entry.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob':blobs[entry.name],'archive_git_blob':sha,'exact_git_blob':exact,'protected_bytes':protected,'only_crlf_checkout_conversion':not exact})
record={'source_commit':commit,'archive_sha256':actual_archive,'archive_file_count':len(files),'exact_git_blobs':sum(f['exact_git_blob']for f in files),'text_crlf_checkout_conversions':sum(f['only_crlf_checkout_conversion']for f in files),'protected_input_files_exact':sum(f['protected_bytes']for f in files),'git_blob_checks':'Protected inputs match exact Git blobs; ordinary text can differ only by core.autocrlf CRLF checkout conversion, with normalized blob identity verified. No source code executed or conclusion logic inspected.','files':files,'scope':'Consumer distribution subset created by git archive on Windows core.autocrlf=true, not full repository archive.'}
output.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='files'},indent=2))
