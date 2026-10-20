"""Verify landed C1 evidence and append final normal-prose report."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, obj):
    payload = json.dumps(obj, indent=2, allow_nan=False) + '\n'
    with (HERE / name).open('x') as out:
        out.write(payload)
    assert (HERE / name).read_text() == payload

before = json.loads((HERE / 'preservation-before.json').read_text())
changed = [name for name, value in before.items() if not (ROOT / name).is_file() or sha(ROOT / name) != value]
baseline = json.loads((ROOT / 'benchmarking/study_evidence/20261015/controller/host-baseline.json').read_text())
protected_mismatches = [name for name, binding in baseline['protected'].items() if sha(ROOT / name) != binding['expected']]
assert not changed and not protected_mismatches
files = set(subprocess.check_output(['git', 'ls-files', '-co', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0'))
new = sorted(name for name in files if name and name not in before and '/c1/' not in name)
assert new == ['benchmarking/inspect_release.py', 'benchmarking/test_inspect_release.py'], new
sources = {name: sha(ROOT / name) for name in new}
result_path = HERE / 'historical-release-current-source-result.json'
result = json.loads(result_path.read_text())
assert result['ok'] is True
assert result['inspector_current_sha256'] == sources['benchmarking/inspect_release.py']
assert result['expectation_sha256'] == sha(HERE / 'historical-release-packaging-expectation.json')
assert result['protected_current_sha256'] == {n: b['expected'] for n, b in baseline['protected'].items()}
assert not (HERE / 'historical-release-strict-arm64-final-success.json').exists()
assert result_path.read_bytes() == (HERE / 'historical-release-current-source.log').read_bytes()
for line in (HERE / 'command-ledger.jsonl').read_text().splitlines():
    entry = json.loads(line)
    assert sha(ROOT / entry['log']) == entry['log_sha256']
counts = {}
for log in ('slice8-green-final-focused.log', 'current-source-broad.log'):
    text = (HERE / log).read_text()
    total = int(re.search(r'Ran (\d+) tests', text).group(1))
    skips = int(re.search(r'OK \(skipped=(\d+)\)', text).group(1)) if 'OK (skipped=' in text else 0
    assert '\nOK' in text and '\nFAILED' not in text
    counts[log] = dict(total=total, passed=total-skips, skipped=skips, failures=0, errors=0)
inventory = json.loads((HERE / 'historical-apk-inventory.json').read_text())
assert all(all(asset.get('matches_protected_checkout') is True for asset in row['assets'].values()) for row in inventory['artifacts'] if '/androidTest/' not in row['path'])
summary = dict(disposition='DONE_WITH_CONCERNS', source_hashes=sources, tests=counts,
    preserved_preexisting_files=len(before), preexisting_mismatches=changed,
    protected_count=len(baseline['protected']), protected_mismatches=protected_mismatches,
    existing_apk_count=len(inventory['artifacts']), real_result=str(result_path.relative_to(ROOT)),
    real_result_sha256=sha(result_path), inventory_sha256=sha(HERE / 'historical-apk-inventory.json'),
    real_apk_sha256=result['apk_sha256'], real_apk_bytes=result['apk_size_bytes'],
    native_abis=result['abis'], flutter_abis=result['flutter_abis'],
    strict_arm64_acceptance=False, current_source_build_provenance=False,
    new_source_files=new, evidence_files=sorted(p.name for p in HERE.iterdir() if p.is_file()))
save('verification-summary.json', summary)
lines = [
    '\n## Final disposition: DONE_WITH_CONCERNS\n',
    'The additive release inspector and tests are complete for parent review. No existing repository file changed. Fresh builds and independent acceptance remain parent-owned. The concern is historical packaging, not an unreported source edit: the release contains three native ABI namespaces despite ARM64-only Flutter code.\n',
    '### Implemented contract and scope\n',
    'The stdlib CLI requires explicit repository, APK and independently supplied version-1 expectation JSON. It binds exact APK digest, all five fixed Android asset hashes, current protected source bytes, exact intended ABI/native-file names and observed native digests. It rejects malformed/duplicate-key/nonfinite JSON, wrong exact types or hash syntax, missing or changed protected assets, corrupt ZIPs, duplicate members, traversal and path aliases, symlinks, missing/extra native files and wrong ABIs. Asset and native case aliases are rejected; Android resources remain case-sensitive because aapt legitimately generated names such as res/9N.9.png and res/9n.9.png. Nothing is extracted.\n',
    'One open APK descriptor supplies digest and ZIP reads, with a final rehash. Expectations are read once and their exact byte digest is retained. Protected bytes are checked before and after ZIP inspection. Optional output requires an existing explicit directory and a new contained target. POSIX no-follow directory walks, exclusive staging, fsync, exact staged/final byte readback and exclusive hard-link publication preserve existing outputs; fault tests cover fsync/link/readback and staging collisions. All CLI errors are fixed JSON without payload/argument echoes.\n',
    '### Regression and execution evidence\n',
    'Eight incremental RED/GREEN slices are retained in command-ledger.jsonl and slice logs. The first RED executed the public CLI and failed its valid-verification assertion against an explicit verification_unavailable result, not import absence. Later REDs demonstrated schema acceptance, unchecked ZIP/native surfaces, symlink/escape output, digest/ZIP path replacement, unsupported compression leakage, Android-resource over-rejection and nonexistent output-root acceptance. Some later tests were already-GREEN characterization (missing/changed assets, existing-output preservation, fault cleanup); they are not claimed as newly repaired defects. The initial schema RED also retained cascaded output failures, then isolated each mutation target for the GREEN run.\n',
]
for name, count in counts.items():
    lines.append(f"- `{name}`: {count['total']} run; {count['passed']} passed, {count['skipped']} skipped, zero failures/errors.\n")
lines += [
    '\nThe two broad skips explicitly report unavailable MediaPipe Holistic `solutions`; they are not passes. Their inherited skip text mentions another environment, but this worker did not run that environment. Existing Python 3.11 was used with -B -E and scratch TMPDIR; no installation or training occurred.\n',
    '### Real historical APK observations\n',
    'All existing APK paths below were read-only inventoried. Five main-app artifacts contain all five assets with hashes matching the independently protected checkout. The instrumentation APK lacks those app assets, as recorded rather than treated as an application release. The extra `app-release 2.apk` is a distinct artifact, not silently selected.\n',
    '| Existing APK | Bytes | SHA-256 | Native ABIs | Flutter ABIs |\n',
    '|---|---:|---|---|---|\n',
]
for row in inventory['artifacts']:
    lines.append(f"| `{row['path']}` | {row['bytes']} | `{row['sha256']}` | {', '.join(row['all_native_abis']) or 'none'} | {', '.join(row['flutter_abis']) or 'none'} |\n")
lines += [
    '\n`historical-release-current-source-result.json` is the final successful CLI output and supersedes earlier successful captures for current inspector-source identity only. Its APK digest came from the historical owner-parent-verification-1.json record, not from the APK under verification; asset/protected expectations came from host-baseline.json. Its explicit three-ABI/native-file packaging policy was frozen after current observation, not preregistered. That bounded consistency success is not strict ARM64-only acceptance. The separate strict ARM64 expectation was rejected (exit 1); no strict-acceptance result exists. Earlier real-APK failures due to over-broad resource case folding remain preserved, followed by the behavioral regression and repair.\n',
    f"Final real-result SHA-256: `{summary['real_result_sha256']}`. Inventory SHA-256: `{summary['inventory_sha256']}`.\n",
    '### Preservation and handoff\n',
    f"All {len(before)} pre-existing tracked/untracked non-C1 files in preservation-before.json are unchanged, including accepted native/A3/B1/B2 sources, manifests and source-bound fixtures. All {len(baseline['protected'])} original protected hashes match. Only two source files were added:\n",
]
for name, value in sources.items():
    lines.append(f'- `{name}`: `{value}`.\n')
lines += [
    '\nSupporting additions are confined to this c1 directory: task brief, incremental report, append-only command ledger, evidence runners, preservation snapshot, versioned explicit expectations, actual logs, historical inventory/diagnostic records, immutable CLI results and verification-summary.json. No app/build/Gradle/model/label/training/normalization/math/XP/privacy source changed. B2 remains accepted bounded tooling with full provenance blocked by 134 missing metadata records.\n',
    '### Remaining limitations\n',
    'This inspected historical bytes, not a fresh build. Current source capture is not build-source provenance; neither artifact_kind=fresh_build nor a matching APK hash changes that. Native names and archive hashes do not establish ELF ABI correctness, APK signatures, Android manifest policy, runtime behavior, physical performance or study authorization. Trust in the expectation issuer, host and checkout remains required. Descriptor checks and publication readback are not adversarial concurrent-filesystem or power-loss guarantees. A strict ARM64-only requirement needs parent adjudication; this slice did not change release configuration. Parent independently reruns/reviews, constructs expectations for its fresh artifact and retains all installed/physical/human gates.\n',
]
with (HERE / 'report.md').open('a') as out:
    out.write('\n'.join(lines))
print(json.dumps(summary, indent=2))
