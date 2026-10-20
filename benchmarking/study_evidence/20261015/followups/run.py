"""Append-only execution ledger and exclusive logs for follow-up work."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
label, *command = sys.argv[1:]
env = dict(os.environ, TMPDIR=str(Path.home() / '.hermes/cache/scratch'))
with (HERE / 'command-ledger.jsonl').open('a') as ledger:
    ledger.write(json.dumps({'event':'start','label':label,'command':command,'cwd':str(ROOT),'time':datetime.datetime.now().astimezone().isoformat()})+'\n')
with (HERE / (label + '.log')).open('x') as log:
    result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
with (HERE / 'command-ledger.jsonl').open('a') as ledger:
    ledger.write(json.dumps({'event':'end','label':label,'exit':result.returncode,'log':label+'.log'})+'\n')
print(label, 'exit', result.returncode)
sys.exit(result.returncode)
