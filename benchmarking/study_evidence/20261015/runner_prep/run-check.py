"""Evidence-only fixed unittest launcher; no training entrypoint."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PYTHON = Path.home() / '.kumpas-venvs/tf/bin/python'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def preservation(label):
    b = ROOT / 'benchmarking/study_evidence/20261015'
    groups = {
        'protected82': {p: v['expected'] for p,v in json.loads((b/'controller/host-baseline.json').read_text())['protected'].items()},
        'accepted69': {p:v['sha256'] for p,v in json.loads((b/'d/current-accepted-source-readback.json').read_text())['sources'].items()},
        'frozen279': json.loads((b/'d/source-freeze.json').read_text())['files'],
        'evidence206': json.loads((b/'d/evidence-freeze.json').read_text())['files'],
    }
    result = {k: {'count': len(v), 'mismatches': [p for p,h in v.items() if digest(ROOT/p) != h]} for k,v in groups.items()}
    with (OUT/(label+'.json')).open('x') as f: json.dump(result,f,indent=2)
    print(json.dumps(result,sort_keys=True))
    return int(any(x['mismatches'] for x in result.values()))

if __name__ == '__main__':
    label = sys.argv[1]
    if label in ('preservation-before','preservation-after'):
        raise SystemExit(preservation(label))
    # Method selectors are unittest names, never shell commands.
    args = [str(PYTHON), '-B', '-E', '-m', 'unittest']
    args += (['discover','-s','training/tests','-p','test_*.py','-v'] if label == 'full' else (sys.argv[2:] or ['training.tests.test_experiment_runner','-v']))
    record = {'label':label,'command':args,'at':datetime.datetime.now().astimezone().isoformat()}
    with (OUT/'command-ledger.jsonl').open('a') as f: f.write(json.dumps(dict(record,event='start'))+'\n')
    env = dict(os.environ, TMPDIR=str(Path.home()/'.hermes/cache/scratch'), MPLBACKEND='Agg', PYTHONDONTWRITEBYTECODE='1')
    with (OUT/(label+'.log')).open('xb') as log:
        result = subprocess.run(args,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    record.update(event='end',exit=result.returncode,log=label+'.log',sha256=digest(OUT/(label+'.log')))
    with (OUT/'command-ledger.jsonl').open('a') as f: f.write(json.dumps(record)+'\n')
    print(json.dumps(record))
    print((OUT/(label+'.log')).read_text()[-5000:])
    raise SystemExit(result.returncode)
