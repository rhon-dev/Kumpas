"""Readback only by default; --freeze exclusively creates new evidence inventories."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CAMP = OUT.parent
SOURCES = [ROOT/'training/models/experiment_runner.py',ROOT/'training/tests/test_experiment_runner.py']


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def write_new(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True,allow_nan=False)


def verify():
    source=json.loads((OUT/'source-freeze.json').read_bytes())
    evidence=json.loads((OUT/'evidence-freeze.json').read_bytes())
    for inventory in (source,evidence):
        for path,h in inventory['files'].items():assert sha(ROOT/path)==h,path
    groups={
      'protected82':{p:v['expected'] for p,v in json.loads((CAMP/'controller/host-baseline.json').read_bytes())['protected'].items()},
      'accepted69':{p:v['sha256'] for p,v in json.loads((CAMP/'d/current-accepted-source-readback.json').read_bytes())['sources'].items()},
      'frozen279':json.loads((CAMP/'d/source-freeze.json').read_bytes())['files'],
      'evidence206':json.loads((CAMP/'d/evidence-freeze.json').read_bytes())['files']}
    for values in groups.values():
        for path,h in values.items():assert sha(ROOT/path)==h,path
    cli=json.loads((OUT/'cli-evidence.json').read_bytes());base=Path(cli['external_root'])
    for path,h in cli['external_hashes'].items():assert sha(base/path)==h,path
    for label,h in cli['config_hashes'].items():assert sha(OUT/('cli-'+label+'-config.json'))==h
    assert cli['count']==len(cli['results'])==9
    for item in cli['results']:
        assert sha(OUT/(item['label']+'.stdout.log'))==item['stdout_sha256']
        assert sha(OUT/(item['label']+'.stderr.log'))==item['stderr_sha256']
        assert json.loads((OUT/(item['label']+'.stdout.log')).read_bytes())==item['payload']
        assert (OUT/(item['label']+'.stderr.log')).read_bytes()==b''
    counts={}
    for label,expected in [('focused-final',22),('full',51)]:
        text=(OUT/(label+'.log')).read_text()
        count=int(re.search(r'Ran (\d+) tests in ',text).group(1))
        assert count==expected and text.rstrip().endswith('OK')
        counts[label]=count
    assert len([p for p in base.rglob('*') if p.is_file()])==len(cli['external_hashes'])==18
    for config_label,subdir in [('prepare','prepare'),('dry-run','dry-run'),('timeout','timeout')]:
        manifest=json.loads((base/subdir/'manifest.json').read_bytes())
        assert manifest['runner_sha256']==source['files']['training/models/experiment_runner.py']
        assert not manifest['config']['training_authorized'] and manifest['config']['synthetic_only']
        config=json.loads((OUT/('cli-'+config_label+'-config.json')).read_bytes())
        assert manifest['config']==config
        canonical=json.dumps(config,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        assert hashlib.sha256(canonical).hexdigest()==manifest['config_sha256']
        assert manifest['input_hashes']=={role:binding['sha256'] for role,binding in config['bindings'].items()}
        for binding in config['bindings'].values():assert sha(Path(binding['path']))==binding['sha256']
        if subdir!='prepare':
            receipt=json.loads((base/subdir/'completion.json').read_bytes())
            for path,h in receipt['output_hashes'].items():assert sha(base/subdir/path)==h
            assert receipt['success']==(subdir=='dry-run')
            assert (receipt['selected_synthetic_run_id'] is None)==(subdir=='timeout')
        result=next(r for r in cli['results'] if r['label']=={'prepare':'cli-prepare','dry-run':'cli-demo','timeout':'cli-timeout'}[config_label])
        assert sha(base/subdir/'manifest.json')==result['payload']['manifest_sha256']
    diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True)
    assert diff.returncode==0
    return {'ok':True,'sources':source['files'],'source_file_count':len(source['files']),
      'evidence_file_count':len(evidence['files']),'preserved':{k:len(v) for k,v in groups.items()},
      'tests':counts,'cli_exits':{r['label']:r['exit'] for r in cli['results']},
      'external_file_count':len(cli['external_hashes']),'git_diff_check_exit':diff.returncode,
      'scope':'SYNTHETIC_PREPARATION_ONLY_PARENT_REVIEW_REQUIRED'}


if __name__=='__main__':
    if sys.argv[1:]==['--freeze']:
        files={str(p.relative_to(ROOT)):sha(p) for p in SOURCES+sorted(OUT.glob('*.py'))}
        write_new(OUT/'source-freeze.json',{'files':files,'count':len(files),'scope':'new runner helper/test and evidence scripts only'})
        excluded={'evidence-freeze.json','verification.json'}
        files={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in excluded}
        write_new(OUT/'evidence-freeze.json',{'files':files,'count':len(files),'excludes':['self','verification.json']})
        result=verify();write_new(OUT/'verification.json',result)
    else:
        assert sys.argv[1:]==[], 'Use no arguments for readback'
        result=verify()
    print(json.dumps(result,indent=2,sort_keys=True))
