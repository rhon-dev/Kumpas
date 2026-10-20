"""Snapshot only repository source/evidence inventory, never app stores."""
import hashlib, json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

if __name__ == '__main__':
    import sys
    base = json.loads((ROOT/'benchmarking/study_evidence/20261015/controller/host-baseline.json').read_text())
    if sys.argv[1] == 'before':
        names = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'], cwd=ROOT).decode().split('\0')
        # These are repository-controlled source/evidence paths, not installed stores.
        names = [n for n in names if n and not n.startswith('benchmarking/study_evidence/20261015/c2/')]
        hashes = {n:digest(ROOT/n) for n in names if (ROOT/n).is_file() and not (ROOT/n).is_symlink()}
        result = {'file_hashes':hashes,'protected':{n:digest(ROOT/n) for n in base['protected']}}
    else:
        before = json.loads((HERE/'before.json').read_text())
        result = {'preexisting_count':len(before['file_hashes']), 'changed':[n for n,h in before['file_hashes'].items() if not (ROOT/n).is_file() or digest(ROOT/n)!=h], 'protected_count':len(base['protected']), 'protected_mismatches':[n for n,h in base['protected'].items() if digest(ROOT/n)!=h['expected']], 'protected_before_after_mismatches':[n for n,h in before['protected'].items() if digest(ROOT/n)!=h]}
    target=HERE/(sys.argv[1]+'.json')
    with target.open('x') as f: json.dump(result,f,indent=2); f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('file_hashes','protected')}))
