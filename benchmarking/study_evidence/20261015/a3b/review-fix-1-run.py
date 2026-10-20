"""Append-only execution evidence for bounded F1 repair."""
import datetime
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
label, cwd, *command = sys.argv[1:]
log = OUT / ('review-fix-1-' + label + '.log')
env = dict(os.environ, TMPDIR=str(Path.home() / '.hermes/cache/scratch/kumpas-a3b'))
Path(env['TMPDIR']).mkdir(parents=True, exist_ok=True)
with (Path.home() / '.hermes/cache/scratch/kumpas-gradle.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    with log.open('x') as stream:
        result = subprocess.run(command, cwd=ROOT / cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
record = {'at': datetime.datetime.now().astimezone().isoformat(), 'label': label,
          'command': command, 'cwd': str(ROOT / cwd), 'exit': result.returncode,
          'log': str(log.relative_to(ROOT)), 'TMPDIR': env['TMPDIR'],
          'lock': str(Path.home() / '.hermes/cache/scratch/kumpas-gradle.lock')}
with (OUT / 'review-fix-1-ledger.jsonl').open('a') as stream:
    stream.write(json.dumps(record) + '\n')
with (OUT / 'review-fix-1-report.md').open('a') as stream:
    stream.write(f"\n- `{label}` exit {result.returncode}: `{log.name}`; exact command/environment in fix ledger.\n")
print(json.dumps(record))
print(log.read_text()[-6000:])
sys.exit(result.returncode)
