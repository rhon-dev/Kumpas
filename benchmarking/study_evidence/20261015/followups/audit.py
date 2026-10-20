"""Verify historical identities without rerunning or rebinding old campaigns."""
import hashlib
import json
from pathlib import Path
import sys
from capture import sha, save, HERE, ROOT, ALLOWED
sys.path.insert(0, str(ROOT / 'benchmarking'))
from pipeline_parity import compare_vectors

E = HERE.parent
before = json.loads((HERE / 'before.json').read_text())
postimages = {}
for name in ALLOWED:
    snapshot = HERE / 'after' / name
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if not snapshot.exists():
        with snapshot.open('xb') as stream:
            stream.write((ROOT / name).read_bytes())
    assert sha(snapshot) == sha(ROOT / name)
    postimages[name] = sha(snapshot)
assert sha(HERE / 'before/benchmarking/pipeline_parity.py') == 'cc905b5494e1fe78d7c4d3de3bcf05772499946538d42f404f17acad3c43d93d'

campaign = ROOT.parent / 'kumpas-data/parity/20261017-validation-v1'
manifest = json.loads((campaign / 'manifest.json').read_text())
frozen = json.loads((campaign / 'selection.json').read_text())
source_drift = []
for name, expected in frozen['source_sha256'].items():
    current = sha(ROOT / name)
    historical = sha(HERE / 'before' / name) if name in ALLOWED else current
    assert historical == expected, name
    if current != expected:
        source_drift.append({'path': name, 'historical_sha256': expected, 'current_sha256': current})
assert [row['path'] for row in source_drift] == ['benchmarking/pipeline_parity.py']
frames = 0
for fixture in manifest['fixtures']:
    directory = campaign / fixture['directory']
    assert sha(directory / 'fixture.json') == fixture['fixture_manifest_sha256']
    for name, expected in fixture['files'].items():
        assert sha(directory / name) == expected
    replay = json.loads((directory / 'frames/manifest.json').read_text())
    for frame in replay['frames']:
        assert sha(directory / 'frames' / frame['filename']) == frame['sha256']
        frames += 1
    reference = json.loads((directory / 'python.json').read_text())
    json.dumps(compare_vectors(reference, reference, require_clip_binding=True), allow_nan=False)
assert len(manifest['fixtures']) == 6 and frames == 180

# Expected bytes are taken from immutable historical records, not learned now.
b2 = json.loads((E / 'b2/verification.json').read_text())
b2_root = Path(b2['external_output'])
if not b2_root.is_absolute():
    b2_root = ROOT / b2_root
b2_output_checks = {}
for name, expected in b2['outputs_sha256'].items():
    path = b2_root / name
    assert sha(path) == expected, name
    b2_output_checks[str(path)] = expected
assert sha(b2_root / 'campaign.json') == b2['campaign_sha256']
assert sha(b2_root / 'INCOMPLETE-manifest.json') == b2['incomplete_manifest_sha256']
b2_accepted = json.loads((E / 'controller/b2-bounded-acceptance-20261018.json').read_text())['source_hashes']
assert all(sha(ROOT / p) == expected for p, expected in b2_accepted.items())

historical_test_bindings = {}
for package in ('c1', 'c2'):
    accepted = json.loads((E / ('controller/' + package + '-parent-verification-1.json')).read_text())
    # The parent records are checked below using their declared hash maps.
    historical_test_bindings[package] = {'parent_record_sha256': sha(E / ('controller/' + package + '-parent-verification-1.json'))}
for name in ('benchmarking/test_inspect_release.py', 'evaluation/test_export_cli.py'):
    historical_test_bindings[name] = {'historical_sha256': before['sources'][name], 'current_sha256': postimages[name], 'historical_snapshot': 'before/' + name}
artifacts = json.loads((ROOT / 'benchmarking/study_evidence/20261007/controller/owner-parent-verification-1.json').read_text())['artifacts']
for record in artifacts.values():
    assert sha(ROOT / record['path']) == record['sha256']
save('historical-identities.json', {'b1_fixture_count': len(manifest['fixtures']), 'b1_png_count': frames,
    'b1_expected_current_checkout_binding_drift': source_drift,
    'b1_historical_manifest_sha256': sha(campaign / 'manifest.json'),
    'b1_historical_selection_sha256': sha(campaign / 'selection.json'),
    'old_verify_evidence': 'Expected assertion at line 56 for benchmarking/pipeline_parity.py; not run because it also reads original video/NPZ sources. No manifests changed.',
    'b2_outputs_verified_against_historical_record': b2_output_checks,
    'b2_current_accepted_sources': b2_accepted, 'historical_c1_c2_test_identities': historical_test_bindings,
    'historical_apks_verified': artifacts, 'postimages': postimages,
    'limits': 'B1 self-comparison is only current structural validation, not fresh generation/native parity. B2 outputs are historical incomplete diagnostics, not new inference. No retroactive binding.'})
print(json.dumps({'fixtures': 6, 'pngs': frames, 'b1_drift': source_drift, 'b2_output_count': len(b2_output_checks), 'apk_count': len(artifacts), 'postimages': postimages}, indent=2))
