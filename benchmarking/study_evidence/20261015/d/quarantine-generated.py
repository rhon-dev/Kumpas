"""Preserve only the exact generated unreadable file named by failed build."""
from pathlib import Path
import fcntl
import hashlib
import json
import os
import subprocess
import datetime
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
SCRATCH=Path.home()/'.hermes/cache/scratch/kumpas-d-20261018'
source=ROOT/'app/build/app/intermediates/flutter/release/flutter_assets/packages/cupertino_icons/assets/CupertinoIcons 2.ttf'
canonical=source.with_name('CupertinoIcons.ttf')
target=SCRATCH/'generated-quarantine'/'CupertinoIcons 2.ttf'
def state(p):
    s=p.stat()
    return {'path':str(p),'bytes':s.st_size,'inode':s.st_ino,'device':s.st_dev,'flags':s.st_flags,'sha256':None if s.st_flags & 0x40000000 else hashlib.sha256(p.read_bytes()).hexdigest()}
with (SCRATCH.parent/'kumpas-gradle.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    assert source.exists() and canonical.exists() and not target.exists()
    ignored=subprocess.run(['git','check-ignore','-v',str(source.relative_to(ROOT)),str(canonical.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    before=state(source)
    peer=state(canonical)
    assert before['flags'] & 0x40000000 and not peer['flags'] & 0x40000000
    assert before['bytes']==peer['bytes']
    target.parent.mkdir()
    # Same-volume rename preserves the exact original inode and placeholder,
    # not a substituted canonical file or a fabricated content digest.
    os.rename(source,target)
    after=state(target)
    assert all(before[k]==after[k] for k in ('bytes','inode','device','flags','sha256'))
    record={'at':datetime.datetime.now().astimezone().isoformat(),'failure_log':'release-build.log','source':before,'canonical':peer,'preserved':after,'git_check_ignore':ignored,'method':'same-volume rename of exact generated obstruction; original inode/size/flags unchanged','limits':'DATALESS bytes not opened or hashed; equal size/name does not establish equal content, byte equality not asserted; filesystem duplication origin unknown. No raw dataset hydration, source edit or broad cleanup.'}
    with (D/'generated-quarantine.json').open('x') as f: json.dump(record,f,indent=2)
    with (D/'command-ledger.jsonl').open('a') as f: f.write(json.dumps({'event':'generated-quarantine',**record})+'\n')
    print(json.dumps(record,indent=2))
