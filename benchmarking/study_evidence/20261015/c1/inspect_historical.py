"""Read-only historical inventory; not a successful release verification."""
import hashlib
import json
from pathlib import Path
import zipfile
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent

def sha(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()

def file_hash(path):
    with path.open('rb') as stream:
        return sha(stream)

baseline = json.loads((ROOT / 'benchmarking/study_evidence/20261015/controller/host-baseline.json').read_text())
protected = {name: binding['expected'] for name, binding in baseline['protected'].items()}
assert all(file_hash(ROOT / name) == value for name, value in protected.items())
assets = {('assets/' + Path(name).name): {'source': name, 'sha256': value} for name, value in protected.items() if name.startswith('app/android/app/src/main/assets/')}
assert len(assets) == 5
# Intended strict ARM64 native surface, declared explicitly, not auto-filled
# from each inspected archive. These names were discovered in the historical
# artifact directory and dependency configuration. No native hash baseline is
# inferred: exact APK hash is independently supplied from historical evidence.
native = ['lib/arm64-v8a/' + name for name in ('libapp.so', 'libflutter.so', 'libimage_processing_util_jni.so', 'libmediapipe_tasks_vision_jni.so', 'libsurface_util_jni.so', 'libtensorflowlite_jni.so')]
historical = json.loads((ROOT / 'benchmarking/study_evidence/20261007/controller/owner-parent-verification-1.json').read_text())
# Preserve the original artifact records wholesale as the independent digest source.
print('historical top-level fields:', list(historical))
records = []
for apk in sorted((ROOT / 'app/build').glob('**/*.apk')):
    with apk.open('rb') as stream:
        apk_sha = sha(stream)
    with zipfile.ZipFile(apk) as archive:
        native_paths = sorted(n for n in archive.namelist() if n.startswith('lib/') and not n.endswith('/'))
        observed_assets = {}
        for name, binding in assets.items():
            if name in archive.namelist():
                with archive.open(name) as stream:
                    value = sha(stream)
                observed_assets[name] = {'sha256': value, 'matches_protected_checkout': value == binding['sha256']}
            else:
                observed_assets[name] = {'missing': True}
        record = dict(path=str(apk.relative_to(ROOT)), bytes=apk.stat().st_size, sha256=apk_sha,
            all_native_abis=sorted({n.split('/')[1] for n in native_paths}),
            flutter_abis=sorted({n.split('/')[1] for n in native_paths if n.endswith('/libflutter.so')}),
            native_files=native_paths, assets=observed_assets, historical_artifact=True,
            current_source_build_provenance=False, strict_arm64_native_match=native_paths == sorted(native))
        records.append(record)
output = dict(kind='read_only_historical_inventory_not_acceptance', protected_count=len(protected),
              protected_mismatches=[], assets_expected_from='controller/host-baseline.json protected expected map', artifacts=records)
payload = json.dumps(output, indent=2, allow_nan=False) + '\n'
with (HERE / 'historical-apk-inventory.json').open('x') as out:
    out.write(payload)
assert (HERE / 'historical-apk-inventory.json').read_text() == payload
print(payload)
# Strict independent historical release APK digest and protected asset values.
# Not inferred from the APK being verified.
expected_release_digest = 'da66697f562d56ef34ea22e70c515c537f8cff640e3dda99007e8cf3fd617266'
assert expected_release_digest in json.dumps(historical)
expectation = dict(schema_version=1, artifact_kind='historical', apk_sha256=expected_release_digest,
                   abis=['arm64-v8a'], native_files=native, assets=assets, protected=protected)
with (HERE / 'historical-release-arm64-expectation.json').open('x') as out:
    out.write(json.dumps(expectation, indent=2, allow_nan=False) + '\n')
print('inventory sha256', file_hash(HERE / 'historical-apk-inventory.json'))
print('expectation sha256', file_hash(HERE / 'historical-release-arm64-expectation.json'))
