"""Recovery audit and narrowly scoped generated-output preservation."""
from pathlib import Path
import datetime
import fcntl
import hashlib
import json
import os
import subprocess
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
SCRATCH=Path.home()/'.hermes/cache/scratch/kumpas-d-20261018'
def state(p):
    s=p.stat()
    return {'path':str(p),'bytes':s.st_size,'inode':s.st_ino,'device':s.st_dev,'flags':s.st_flags,'sha256':None if s.st_flags & 0x40000000 else hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,obj):
    with p.open('x') as f: json.dump(obj,f,indent=2)
def ledger(obj):
    with (D/'command-ledger.jsonl').open('a') as f: f.write(json.dumps(obj)+'\n')
with (SCRATCH.parent/'kumpas-gradle.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    ttf=SCRATCH/'generated-quarantine/CupertinoIcons 2.ttf'
    peer=ROOT/'app/build/app/intermediates/flutter/release/flutter_assets/packages/cupertino_icons/assets/CupertinoIcons.ttf'
    recovery={'event':'quarantine-recovery','at':datetime.datetime.now().astimezone().isoformat(),'original_command':['/opt/homebrew/bin/python3.11','-B','-E','benchmarking/study_evidence/20261015/d/quarantine-generated.py'],'original_exit':1,'error':'AssertionError at post-rename all metadata equality assertion','preserved':state(ttf),'canonical':state(peer),'original_observed':{'bytes':257628,'flags':1073741920,'sha256':None},'limits':'Original pre-rename inode was not durably recorded; observed DATALESS cleared after rename. Do not claim flags unchanged or a before-byte hash. Now-readable preserved bytes equal canonical digest; no content replacement performed. Origin of suffix and flag transition unknown.'}
    assert recovery['preserved']['sha256']==recovery['canonical']['sha256']
    save(D/'generated-quarantine-ttf-recovery.json',recovery)
    ledger(recovery)
    source=ROOT/'app/build/app/intermediates/flutter/release/arm64-v8a/app 2.so'
    canonical=source.with_name('app.so')
    target=SCRATCH/'generated-quarantine/app 2.so'
    assert source.exists() and canonical.exists() and not target.exists()
    ignored=subprocess.run(['git','check-ignore','-v',str(source.relative_to(ROOT)),str(canonical.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    before=state(source)
    canonical_state=state(canonical)
    record={'event':'generated-quarantine','at':datetime.datetime.now().astimezone().isoformat(),'failure_log':'release-build-retry1.log','source':before,'canonical':canonical_state,'git_check_ignore':ignored,'method':'same-volume rename of exact generated obstruction; no broad cleanup, deletion or source edit'}
    save(D/'generated-quarantine-so-before.json',record)
    os.rename(source,target)
    after=state(target)
    assert all(before[k]==after[k] for k in ('bytes','inode','device'))
    record['preserved']=after
    record['limits']='DATALESS source was not opened before rename; flags may change. Digest, when readable, is post-rename capture, not invented preimage. Same inode/device/size verified. Equal content with current rebuilt canonical is not required; no filesystem-origin claim.'
    save(D/'generated-quarantine-so-after.json',record)
    ledger(record)
    print(json.dumps({'ttf':recovery,'so':record},indent=2))
