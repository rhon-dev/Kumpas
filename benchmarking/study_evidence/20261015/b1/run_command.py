"""Run real commands and append durable B1 execution evidence."""
import datetime
import json
from pathlib import Path
import subprocess
import sys
import os

os.environ['TMPDIR'] = str(Path.home() / '.hermes/cache/scratch')
Path(os.environ['TMPDIR']).mkdir(parents=True, exist_ok=True)

root = Path(__file__).resolve().parent
name, *command = sys.argv[1:]
log = root / (name + '.log')
with log.open('x') as stream:
    result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
record = {'timestamp': datetime.datetime.now().astimezone().isoformat(),
          'command': command, 'exit': result.returncode, 'log': str(log.relative_to(root))}
with (root / 'command-ledger.jsonl').open('a') as stream:
    stream.write(json.dumps(record) + '\n')
with (root / 'report.md').open('a') as stream:
    stream.write(f"\n- Executed `{name}`: exit {result.returncode}; log `{log.name}`; command in ledger.\n")
print(json.dumps(record))
print(log.read_text()[-10000:])
sys.exit(result.returncode)
