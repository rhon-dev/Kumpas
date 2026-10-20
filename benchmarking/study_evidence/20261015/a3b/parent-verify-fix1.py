"""Parent execution only; never opens installed stores or device transport."""
from pathlib import Path
import os, subprocess, fcntl, json, datetime, re
root = Path(__file__).resolve().parents[4]
evidence = Path(__file__).resolve().parent
env = os.environ.copy()
scratch = Path.home() / '.hermes/cache/scratch/kumpas-a3b'
scratch.mkdir(parents=True, exist_ok=True)
env.update(TMPDIR=str(scratch), PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg')
commands = [
    ('parent-fix1-python', ['/opt/homebrew/bin/python3.11', '-E', '-m', 'unittest', 'discover', '-s', 'benchmarking', '-p', 'test_*.py', '-v'], root),
    ('parent-fix1-analyze', ['/opt/homebrew/bin/flutter', 'analyze', '--no-pub'], root / 'app'),
    ('parent-fix1-flutter', ['/opt/homebrew/bin/flutter', 'test', '--no-pub', '--machine'], root / 'app'),
    ('parent-fix1-replay', ['/opt/homebrew/bin/python3.11', '-E', 'benchmarking/host_fixture_replay.py', 'replay', '--output', str(evidence / 'parent-fix1-replay')], root),
]
records = []
with (scratch.parent / 'kumpas-gradle.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    for label, command, cwd in commands:
        log = evidence / (label + '.log')
        with log.open('x') as out:
            result = subprocess.run(command, cwd=cwd, env=env, stdout=out, stderr=subprocess.STDOUT)
        text = log.read_text()
        record = {'at': datetime.datetime.now().astimezone().isoformat(), 'label': label, 'command': command, 'cwd': str(cwd), 'exit': result.returncode, 'log': str(log.relative_to(root))}
        if label == 'parent-fix1-python':
            record['summary'] = re.findall(r'Ran \d+ tests[^\n]*|^OK[^\n]*|^FAILED[^\n]*', text, re.MULTILINE)
        if label == 'parent-fix1-flutter':
            events = []
            for line in text.splitlines():
                try:
                    value = json.loads(line)
                    if isinstance(value, dict): events.append(value)
                except ValueError: pass
            done = [e for e in events if e.get('type') == 'testDone' and not e.get('hidden', False)]
            record['tests'] = len(done)
            record['failures'] = sum(e.get('result') != 'success' for e in done)
            record['skipped'] = sum(e.get('skipped', False) for e in done)
            record['done_events'] = [e for e in events if e.get('type') == 'done']
        if label == 'parent-fix1-analyze': record['summary'] = text.strip()
        records.append(record)
        print(json.dumps(record))
        if result.returncode:
            print(text[-6000:])
            break
with (evidence / 'parent-fix1-command-ledger.json').open('x') as out:
    json.dump(records, out, indent=2)
raise SystemExit(0 if len(records) == len(commands) and all(r['exit'] == 0 for r in records) else 1)
