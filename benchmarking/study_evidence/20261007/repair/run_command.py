"""Durable append-only repair command runner; no device operations."""
import datetime
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[4]
evidence = pathlib.Path(__file__).resolve().parent
label, cwd, *command = sys.argv[1:]
log = evidence / (label + '.log')
with log.open('x') as output:
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (evidence / 'command-ledger.jsonl').open('a') as ledger:
        ledger.write(json.dumps({'event': 'start', 'at': started, 'label': label, 'cwd': cwd, 'command': command, 'log': str(log)}) + '\n')
    result = subprocess.run(command, cwd=cwd, stdout=output, stderr=subprocess.STDOUT)
with (evidence / 'command-ledger.jsonl').open('a') as ledger:
    ledger.write(json.dumps({'event': 'finish', 'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'label': label, 'exit_code': result.returncode}) + '\n')
print(log.read_text())
print('EXIT_CODE:', result.returncode)
sys.exit(result.returncode)
