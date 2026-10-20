"""Explicit-file APK inspection; no runtime, signature or build attestation.

Required: --repo-root DIR --expectation JSON --apk FILE. Optional output requires
both --output-root DIR and --output NEW_FILE (existing directories, POSIX only).
Without output flags, emit strict JSON to stdout only. Failures emit one fixed
JSON error with nonzero exit; no ZIP extraction, builds or device calls occur.

Expectation v1 has exact keys: schema_version (integer 1), artifact_kind
(historical/fresh_build; caller description only), apk_sha256 (independent
lowercase digest), abis (unique supported ABI names), native_files (exact lib/
ABI/lib*.so paths), assets (all five fixed Android assets, each with source and
sha256), protected (nonempty relative source-path/digest map including assets).
No expected hash is inferred from the APK. Historical capture or a fresh_build
label cannot establish source-to-build identity. Current source hashes are
inspection-time captures only. Trust the expectation issuer, host, checkout and
filesystem; this is not adversarial concurrent-filesystem or power-loss proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import re
import stat
import os
import secrets
import zipfile

ASSET_NAMES = ('gold_standards.bin', 'hand_landmarker.task', 'kumpas_50sign.tflite', 'label_map.json', 'pose_landmarker_lite.task')
SUPPORTED_ABIS = {'arm64-v8a', 'armeabi-v7a', 'x86', 'x86_64'}


def require(condition):
    if not condition:
        raise ValueError('invalid')


def safe_path(name):
    require(type(name) is str and re.fullmatch(r'[A-Za-z0-9_./+-]+', name) is not None)
    require(all(part not in ('', '.', '..') for part in name.split('/')))
    return name


def valid_hash(value):
    require(type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('nonfinite')


def validate(expectation):
    require(type(expectation) is dict and set(expectation) == {'schema_version', 'artifact_kind', 'apk_sha256', 'abis', 'native_files', 'assets', 'protected'})
    require(type(expectation['schema_version']) is int and expectation['schema_version'] == 1)
    require(type(expectation['artifact_kind']) is str and expectation['artifact_kind'] in ('historical', 'fresh_build'))
    valid_hash(expectation['apk_sha256'])
    abis = expectation['abis']
    require(type(abis) is list and abis and all(type(a) is str for a in abis))
    require(len(set(abis)) == len(abis) and set(abis) <= SUPPORTED_ABIS)
    native = expectation['native_files']
    require(type(native) is list and native and all(type(n) is str for n in native))
    require(len(set(native)) == len(native))
    for name in native:
        safe_path(name)
        parts = name.split('/')
        require(len(parts) == 3 and parts[0] == 'lib' and parts[1] in abis and re.fullmatch(r'lib[A-Za-z0-9_.+-]+\.so', parts[2]) is not None)
    require({n.split('/')[1] for n in native} == set(abis))
    protected = expectation['protected']
    require(type(protected) is dict and bool(protected))
    for name, value in protected.items():
        safe_path(name)
        valid_hash(value)
    assets = expectation['assets']
    require(type(assets) is dict and set(assets) == {'assets/' + n for n in ASSET_NAMES})
    for name, binding in assets.items():
        require(type(binding) is dict and set(binding) == {'source', 'sha256'})
        source = 'app/android/app/src/main/assets/' + name[7:]
        require(binding['source'] == source)
        valid_hash(binding['sha256'])
        require(protected.get(source) == binding['sha256'])
    return expectation


def sha(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()


def file_hash(path):
    with path.open('rb') as stream:
        return sha(stream)


def directory_fd(path):
    """Open each directory component without following symlinks (POSIX)."""
    path = Path(path).absolute()
    require('..' not in path.parts)
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def checkout_hash(root, name):
    safe_path(name)
    path = root / name
    parent = directory_fd(path.parent)
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, 'rb') as stream:
            require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode))
            return sha(stream)
    finally:
        os.close(parent)


def publish(output_root, output, payload):
    """Stage/read back, link exclusively, read back final, clean owned failures."""
    root, target = Path(output_root).absolute(), Path(output).absolute()
    require('..' not in root.parts and '..' not in target.parts)
    require(bool(target.relative_to(root).parts))
    root_fd = directory_fd(root)
    os.close(root_fd)
    safe_path(target.name)
    parent = directory_fd(target.parent)
    stage = '.inspect-' + secrets.token_hex(16)
    linked = False
    staged = False
    identity = None
    try:
        fd = os.open(stage, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        staged = True
        with os.fdopen(fd, 'w+b') as stream:
            identity = os.fstat(stream.fileno()).st_ino
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
            stream.seek(0)
            require(stream.read() == payload)
        os.link(stage, target.name, src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
        linked = True
        fd = os.open(target.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        with os.fdopen(fd, 'rb') as stream:
            require(os.fstat(stream.fileno()).st_ino == identity and stream.read() == payload)
        os.unlink(stage, dir_fd=parent)
        os.fsync(parent)
    except BaseException:
        if linked:
            try:
                if os.stat(target.name, dir_fd=parent, follow_symlinks=False).st_ino == identity:
                    os.unlink(target.name, dir_fd=parent)
            except FileNotFoundError:
                pass
        raise
    finally:
        if staged:
            try:
                os.unlink(stage, dir_fd=parent)
            except FileNotFoundError:
                pass
        os.close(parent)


def inspect(root, apk, expectation):
    validate(expectation)
    protected = {name: checkout_hash(root, name) for name in expectation['protected']}
    require(protected == expectation['protected'])
    with apk.open('rb') as snapshot:
        require(stat.S_ISREG(os.fstat(snapshot.fileno()).st_mode))
        actual = sha(snapshot)
        require(actual == expectation['apk_sha256'])
        snapshot.seek(0)
        assets, native = inspect_archive(snapshot, root, expectation)
        snapshot.seek(0)
        require(sha(snapshot) == actual)
        size = os.fstat(snapshot.fileno()).st_size
    require({name: checkout_hash(root, name) for name in protected} == protected)
    flutter_abis = sorted(abi for abi in expectation['abis'] if all('lib/' + abi + '/' + name in native for name in ('libapp.so', 'libflutter.so')))
    return dict(schema_version=1, ok=True, apk_sha256=actual, apk_size_bytes=size, assets=assets,
                native_files=native, abis=sorted(expectation['abis']), flutter_abis=flutter_abis,
                artifact_kind=expectation['artifact_kind'], protected_current_sha256=protected,
                current_source_build_provenance=False, signature_verified=False, runtime_verified=False)


def inspect_archive(snapshot, root, expectation):
    assets, native = {}, {}
    with zipfile.ZipFile(snapshot) as archive:
        files, directories = set(), set()
        for info in archive.infolist():
            require(info.orig_filename == info.filename)
            name = info.filename[:-1] if info.is_dir() else info.filename
            safe_path(name)
            # Android resource ZIP lookup is case-sensitive (aapt may emit
            # both res/9N.9.png and res/9n.9.png). No files are extracted.
            # Asset/native namespaces additionally reject case aliases.
            key = name.lower() if name.split('/')[0].lower() in ('assets', 'lib') else name
            require(key not in files and key not in directories)
            mode = stat.S_IFMT(info.external_attr >> 16)
            require(mode in (0, stat.S_IFDIR if info.is_dir() else stat.S_IFREG))
            (directories if info.is_dir() else files).add(key)
        for key in files | directories:
            parts = key.split('/')
            require(not any('/'.join(parts[:i]) in files for i in range(1, len(parts))))
        actual_native = {info.filename for info in archive.infolist() if not info.is_dir() and info.filename.startswith('lib/')}
        require(actual_native == set(expectation['native_files']))
        require({name.split('/')[1] for name in actual_native} == set(expectation['abis']))
        require(archive.testzip() is None)
        for name, binding in expectation['assets'].items():
            with archive.open(name) as stream:
                actual = sha(stream)
            if actual != binding['sha256'] or checkout_hash(root, binding['source']) != actual:
                raise ValueError('asset_mismatch')
            assets[name] = actual
        for name in expectation['native_files']:
            with archive.open(name) as stream:
                native[name] = sha(stream)
    return assets, native


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError('arguments')


def main():
    parser = SafeParser(description=__doc__)
    for name in ('repo-root', 'expectation', 'apk'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--output-root')
    parser.add_argument('--output')
    try:
        args = parser.parse_args()
        expectation_bytes = Path(args.expectation).read_bytes()
        expectation = validate(json.loads(expectation_bytes, object_pairs_hook=unique_object, parse_constant=reject_constant))
        report = inspect(Path(args.repo_root), Path(args.apk), expectation)
        report['expectation_sha256'] = hashlib.sha256(expectation_bytes).hexdigest()
        report['inspector_current_sha256'] = file_hash(Path(__file__))
        payload = json.dumps(report, sort_keys=True, allow_nan=False) + '\n'
        require(bool(args.output) == bool(args.output_root))
        if args.output:
            publish(args.output_root, args.output, payload.encode('utf-8'))
        print(payload, end='')
        return 0
    except Exception:
        # CLI trust boundary: malformed ZIP/JSON/IO failures never echo payloads.
        print(json.dumps({'ok': False, 'error': 'verification_failed'}, allow_nan=False))
        return 1


if __name__ == '__main__':
    sys.exit(main())
