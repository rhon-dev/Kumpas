"""Read-only resident-byte preservation capture; no data-source hydration."""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ALLOWED = ['benchmarking/pipeline_parity.py', 'benchmarking/test_pipeline_parity.py', 'benchmarking/test_inspect_release.py', 'evaluation/test_export_cli.py']

def sha(path):
    info = path.stat()
    if getattr(info, 'st_flags', 0) & 0x40000000:
        raise RuntimeError('DATALESS: ' + str(path))
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def save(name, data):
    with (HERE / name).open('x') as stream:
        json.dump(data, stream, indent=2)

if __name__ == '__main__':
    before = '--after' not in sys.argv
    if before:
        # Prior C2 inventory is an explicit resident-file allowlist, not a data crawl.
        previous = json.loads((HERE.parent / 'c2/before.json').read_text())
        print('prior inventory shape', type(previous).__name__, list(previous)[:8])
    baseline = json.loads((HERE.parent / 'controller/host-baseline.json').read_text())
    protected = {p: record['expected'] for p, record in baseline['protected'].items()}
    binding = json.loads((HERE.parent / 'controller/a3a-acceptance-and-consumer-binding.json').read_text())
    native = json.loads((ROOT / binding['manifest']).read_text())['source_hashes']
    consumer = json.loads((HERE.parent / 'controller/a3b-acceptance-20261017.json').read_text())['source_hashes']
    if before:
        # Capture pre-existing source/evidence only; exclude generated build/cache trees.
        inventory = {}
        for base in ['benchmarking', 'evaluation', 'docs']:
            for directory, dirs, files in os.walk(ROOT / base):
                dirs[:] = [d for d in dirs if d not in ('__pycache__', 'followups', '.venv')]
                for name in files:
                    path = Path(directory) / name
                    if path.is_symlink():
                        raise RuntimeError('unexpected symlink ' + str(path))
                    inventory[str(path.relative_to(ROOT))] = sha(path)
        # Include every prior explicitly inventoried file; inspect schema first.
        prior_files = previous['file_hashes']
        for p in prior_files:
            path = Path(p) if Path(p).is_absolute() else ROOT / p
            if path.is_file():
                inventory[str(path)] = sha(path)
        external = ROOT.parent / 'kumpas-data/parity/20261017-validation-v1'
        for path in external.rglob('*'):
            if path.is_file():
                inventory[str(path)] = sha(path)
        for mapping in (protected, native, consumer):
            for p in mapping:
                inventory[p] = sha(ROOT / p)
        for p in ALLOWED:
            destination = HERE / 'before' / p
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / p).read_bytes())
        save('before.json', {'inventory': inventory, 'protected': protected, 'native': native, 'consumer': consumer, 'sources': {p: sha(ROOT / p) for p in ALLOWED}})
    else:
        saved = json.loads((HERE / 'before.json').read_text())
        mismatches = []
        for p, expected in saved['inventory'].items():
            path = Path(p) if Path(p).is_absolute() else ROOT / p
            if str(path.relative_to(ROOT)) in ALLOWED if path.is_relative_to(ROOT) else False:
                continue
            if sha(path) != expected:
                mismatches.append(p)
        checks = {}
        for group in ('protected', 'native', 'consumer'):
            mapping = saved[group]
            checks[group] = {'count': len(mapping), 'mismatches': [p for p, expected in mapping.items() if sha(ROOT / p) != expected]}
        save('after.json', {'inventory_count': len(saved['inventory']), 'inventory_mismatches': mismatches, 'checks': checks, 'sources': {p: sha(ROOT / p) for p in ALLOWED}})
        print(json.dumps(checks), 'inventory mismatches', mismatches)
        assert not mismatches and all(not v['mismatches'] for v in checks.values())
