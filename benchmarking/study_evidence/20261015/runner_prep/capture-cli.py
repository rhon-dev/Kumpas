"""Capture actual CLI subprocesses against retained synthetic fixtures only."""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from training.tests.test_experiment_runner import RunnerTests
from training.models import experiment_runner as runner


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(label, args, expected, expected_code=None, expected_status=None):
    cmd=[str(Path.home()/'.kumpas-venvs/tf/bin/python'),'-B','-E',str(ROOT/'training/models/experiment_runner.py'),*args]
    start={'event':'start','label':label,'command':cmd,'at':datetime.datetime.now().astimezone().isoformat()}
    with (OUT/'command-ledger.jsonl').open('a') as f:f.write(json.dumps(start)+'\n')
    proc=subprocess.run(cmd,cwd=ROOT,env=dict(os.environ,TMPDIR=str(runner.ISOLATION_BASE)),capture_output=True)
    for suffix,data in [('stdout',proc.stdout),('stderr',proc.stderr)]:
        with (OUT/(label+'.'+suffix+'.log')).open('xb') as f:f.write(data)
    payload=json.loads(proc.stdout)
    assert proc.returncode==expected,(label,proc.returncode,payload)
    assert not proc.stderr and b'PRIVATE' not in proc.stdout
    if expected_code:assert payload['code']==expected_code
    if expected_status:assert payload['status']==expected_status
    result=dict(start,event='end',exit=proc.returncode,stdout_sha256=sha(OUT/(label+'.stdout.log')),
                stderr_sha256=sha(OUT/(label+'.stderr.log')),payload=payload)
    with (OUT/'command-ledger.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
    return result


if __name__=='__main__':
    base=Path(tempfile.mkdtemp(prefix='kumpas-runner-prep-cli-',dir=runner.ISOLATION_BASE))
    inputs=base/'inputs';inputs.mkdir()
    fixture=RunnerTests();fixture.setUp()
    c=copy.deepcopy(fixture.config)
    for role,binding in c['bindings'].items():
        source=Path(binding['path']);target=inputs/source.name
        with target.open('xb') as f:f.write(source.read_bytes())
        binding['path']=str(target)
    fixture.temp.cleanup()
    configs={}
    for label in ('prepare','dry-run','timeout','invalid','authflag'):
        config=copy.deepcopy(c);config['output_root']=str(base/label)
        config['run_id']='SYNTHETIC-CLI-'+label
        if label=='timeout':config['budget']['max_variant_seconds']=1
        if label=='invalid':config['partition']='test'
        if label=='authflag':config['training_authorized']=True
        path=OUT/('cli-'+label+'-config.json')
        with path.open('x') as f:json.dump(config,f,indent=2,allow_nan=False)
        configs[label]=path
    results=[]
    results.append(record('cli-prepare',['prepare','--config',str(configs['prepare'])],0,expected_status='PREPARED'))
    results.append(record('cli-demo',['dry-run','--config',str(configs['dry-run'])],0,expected_status='SYNTHETIC_COMPLETE'))
    results.append(record('cli-timeout',['dry-run','--config',str(configs['timeout'])],1,expected_status='TIMEOUT'))
    results.append(record('cli-invalid',['prepare','--config',str(configs['invalid'])],2,expected_code='INVALID_REQUEST'))
    results.append(record('cli-authflag',['prepare','--config',str(configs['authflag'])],3,expected_code='TRAINING_NOT_AUTHORIZED'))
    for action in ('execute','train'):
        results.append(record('cli-'+action,[action,'--config',str(configs['prepare'])],3,expected_code='TRAINING_NOT_AUTHORIZED'))
    results.append(record('cli-command-refusal',['execute','--command','PRIVATE'],3,expected_code='TRAINING_NOT_AUTHORIZED'))
    prepared_hash=sha(base/'prepare/manifest.json')
    results.append(record('cli-no-overwrite',['prepare','--config',str(configs['prepare'])],2,expected_code='INVALID_REQUEST'))
    assert prepared_hash==sha(base/'prepare/manifest.json')
    for label in ('invalid','authflag'):assert not (base/label).exists()
    for label,status in [('dry-run','SYNTHETIC_COMPLETE'),('timeout','TIMEOUT')]:
        root=base/label;receipt=json.loads((root/'completion.json').read_bytes())
        assert receipt['status']==status and receipt['success']==(status=='SYNTHETIC_COMPLETE')
        for name,h in receipt['output_hashes'].items():assert sha(root/name)==h
        assert not receipt['training_authorized']
    hashes={str(p.relative_to(base)):sha(p) for p in sorted(base.rglob('*')) if p.is_file()}
    result={'kind':'SYNTHETIC_CLI_EVIDENCE_ONLY','external_root':str(base),'count':len(results),
            'results':results,'external_hashes':hashes,'config_hashes':{k:sha(v) for k,v in configs.items()}}
    with (OUT/'cli-evidence.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps({'external_root':str(base),'exits':{r['label']:r['exit'] for r in results},'artifact_count':len(hashes)},sort_keys=True))
