"""Freeze C2 new-file postimages after checking the final execution binding."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

binding=json.loads((HERE/'synthetic-cli-final-bound/independent-cli-verification.json').read_bytes())
assert all(digest(ROOT/name)==expected for name,expected in binding['source_hashes'].items())
for name,expected in binding['output_hashes'].items():
    assert digest(HERE/'synthetic-cli-final-bound'/name)==expected
preservation=json.loads((HERE/'after-verified.json').read_bytes())
assert preservation['preexisting_count']==1248
assert preservation['protected_count']==82
assert not preservation['changed'] and not preservation['protected_mismatches'] and not preservation['protected_before_after_mismatches']
before=json.loads((HERE/'before.json').read_bytes())
assert all(digest(ROOT/name)==expected for name,expected in before['file_hashes'].items())
assert all(digest(ROOT/name)==expected for name,expected in before['protected'].items())
log=(HERE/'slice8-normalized-green-final.log').read_text()
assert re.search(r'Ran 16 tests in ',log) and log.rstrip().endswith('OK')
assert len(re.findall(r'^test_.* \.\.\. ok$',log,re.M))==16
files=sorted(p for p in (ROOT/'evaluation').rglob('*') if p.is_file() and p.name != '.gitkeep')
files += sorted(p for p in HERE.rglob('*') if p.is_file() and p.name not in ('handoff-snapshot-final.json','command-ledger.jsonl','handoff-verification.log'))
assert all(not p.is_symlink() for p in files)
result={'status':'BOUNDED_IMPLEMENTATION_PENDING_INDEPENDENT_REVIEW','tests':16,'preservation':preservation,'new_file_count':len(files),'new_files':{str(p.relative_to(ROOT)):digest(p) for p in files},'final_cli_output_hashes':binding['output_hashes'],'source_binding_matches':True}
with (HERE/'handoff-snapshot-final.json').open('x') as f:
    json.dump(result,f,indent=2,sort_keys=True); f.write('\n')
# Read back the frozen handoff receipt itself.
assert json.loads((HERE/'handoff-snapshot-final.json').read_bytes())==result
print(json.dumps({'tests':16,'new_file_count':len(files),'preexisting_unchanged':1248,'protected_unchanged':82,'source_binding_matches':True,'handoff_sha256':digest(HERE/'handoff-snapshot-final.json')},sort_keys=True))
