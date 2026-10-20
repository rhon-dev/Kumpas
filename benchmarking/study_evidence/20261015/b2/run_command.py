"""Durable exclusive command logs for B2; does not suppress command failure."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
if __name__ == '__main__':
    name, *command = sys.argv[1:]
    log = HERE / (name + '.log')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(Path.home()/'.hermes/cache/scratch'))
    started = datetime.datetime.now().astimezone().isoformat()
    with (HERE/'command-ledger.jsonl').open('a') as ledger:
        ledger.write(json.dumps({'event':'start','at':started,'name':name,'command':command,'log':str(log)})+'\n')
        ledger.flush(); os.fsync(ledger.fileno())
    with log.open('x') as stream:
        result = subprocess.run(command, cwd=HERE.parents[3], env=env, stdout=stream, stderr=subprocess.STDOUT)
    with (HERE/'command-ledger.jsonl').open('a') as ledger:
        ledger.write(json.dumps({'event':'exit','at':datetime.datetime.now().astimezone().isoformat(),'name':name,'exit':result.returncode,'log':str(log)})+'\n')
        ledger.flush(); os.fsync(ledger.fileno())
    print(log.read_text()[-18000:]); sys.exit(result.returncode)
