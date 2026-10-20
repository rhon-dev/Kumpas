"""Read-back verification and safe aggregate evidence; no PNG/vector copies."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'benchmarking'))
from pipeline_parity import compare_vectors, validate_replay

EVIDENCE = Path(__file__).resolve().parent
REPO = EVIDENCE.parents[3]
CAMPAIGN = REPO.parent / 'kumpas-data/parity/20261017-validation-v1'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def load(path):
    return json.loads(path.read_text())

assert ROOT == REPO, (ROOT, REPO)
manifest = load(CAMPAIGN / 'manifest.json')
frozen = load(CAMPAIGN / 'selection.json')
assert len(manifest['fixtures']) == len(frozen['clips']) == 6
assert manifest['selection_sha256'] == sha(CAMPAIGN / 'selection.json')
assert not (CAMPAIGN / 'INCOMPLETE').exists()
rows = []
for fixture, clip in zip(manifest['fixtures'], frozen['clips']):
    directory = CAMPAIGN / fixture['directory']
    assert fixture['clip_id'] == clip['clip_id']
    assert fixture['fixture_manifest_sha256'] == sha(directory / 'fixture.json')
    replay = validate_replay(directory / 'frames')
    assert len(replay['frames']) == 30
    assert len(list((directory / 'frames').glob('*.png'))) == 30
    for name, digest in fixture['files'].items():
        assert sha(directory / name) == digest
    reference = load(directory / 'python.json')
    # Validation-only self-check. Do not retain/label a self-comparison as parity.
    compare_vectors(reference, reference, require_clip_binding=True)
    assert [x['sha256'] for x in reference['frames']] == [x['sha256'] for x in replay['frames']]
    assert reference['fixture_binding'] == fixture['binding'] == load(directory / 'binding.json')
    assert fixture['binding']['replay_manifest_sha256'] == sha(directory / 'frames/manifest.json')
    assert sha(REPO.parent / 'kumpas-data' / clip['video']) == clip['source_video_sha256']
    assert sha(REPO.parent / 'kumpas-data' / clip['landmarks']) == clip['landmarks_sha256']
    rows.append({'clip_id': fixture['clip_id'], 'directory': str(directory),
                 'fixture_manifest_sha256': fixture['fixture_manifest_sha256'],
                 'python_sha256': fixture['python_sha256'], 'replay_manifest_sha256': fixture['replay_manifest_sha256'],
                 'source_video_sha256': clip['source_video_sha256'], 'landmarks_sha256': clip['landmarks_sha256'],
                 'summary': fixture['summary']})
for name, digest in frozen['source_sha256'].items():
    assert sha(REPO / name) == digest, name
baseline = load(EVIDENCE.parent / 'controller/host-baseline.json')
protected = {name: {'expected': record['expected'], 'actual': sha(REPO / name)}
             for name, record in baseline['protected'].items()}
assert len(protected) == 82
mismatches = [name for name, record in protected.items() if record['expected'] != record['actual']]
assert not mismatches, mismatches
binding = load(EVIDENCE.parent / 'controller/a3a-acceptance-and-consumer-binding.json')
native_path = REPO / binding['manifest']
assert sha(native_path) == binding['manifest_sha256']
native = load(native_path)
assert len(native['source_hashes']) == 42
assert all(sha(REPO / name) == expected for name, expected in native['source_hashes'].items())
a3b = load(EVIDENCE.parent / 'controller/a3b-acceptance-20261017.json')
assert all(sha(REPO / name) == expected for name, expected in a3b['source_hashes'].items())
suites = {}
for logname in ('green-strict-cli.log', 'focused-campaign-final.log', 'full-benchmarking-compatible.log'):
    text = (EVIDENCE / logname).read_text()
    n = int(re.search(r'Ran (\d+) tests', text).group(1))
    skips = re.search(r'OK \(skipped=(\d+)\)', text)
    assert '\nOK' in text
    suites[logname] = {'run': n, 'skipped': int(skips.group(1)) if skips else 0}
report = {'status': 'DONE_WITH_CONCERNS_pending_parent_review', 'campaign': str(CAMPAIGN),
          'manifest_sha256': sha(CAMPAIGN / 'manifest.json'), 'selection_sha256': sha(CAMPAIGN / 'selection.json'),
          'source_sha256': frozen['source_sha256'], 'runtime': frozen['runtime'],
          'fixture_count': len(rows), 'png_count': sum(row['summary']['frames'] for row in rows),
          'fixtures': rows, 'tests': suites, 'protected_count': len(protected), 'protected_mismatches': mismatches,
          'native_source_hashes_verified': len(native['source_hashes']),
          'a3b_source_hashes_verified': len(a3b['source_hashes']),
          'limits': frozen['limitations']}
if '--check-only' not in sys.argv:
    with (EVIDENCE / 'verification.json').open('x') as f:
        json.dump(report, f, indent=2, allow_nan=False)
    with (EVIDENCE / 'protected-hashes.json').open('x') as f:
        json.dump({'count': len(protected), 'mismatches': mismatches, 'files': protected}, f, indent=2)
print(json.dumps(report, indent=2))
