"""Evidence-only command runner, not application source."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
label, *args = sys.argv[1:]
log = HERE / (label + '.log')
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg', TMPDIR='/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch')
with log.open('x') as out:
    result = subprocess.run(args, cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT)
entry = dict(at=datetime.datetime.now().astimezone().isoformat(), command=args, exit=result.returncode, log=str(log.relative_to(ROOT)), log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
with (HERE / 'command-ledger.jsonl').open('a') as out:
    out.write(json.dumps(entry, allow_nan=False) + '\n')
with (HERE / 'report.md').open('a') as out:
    out.write(f'\nExecution `{label}`: exit {result.returncode}; `{log.name}`.\n')
print(json.dumps(entry)); print(log.read_text()[-7000:])
sys.exit(result.returncode)
