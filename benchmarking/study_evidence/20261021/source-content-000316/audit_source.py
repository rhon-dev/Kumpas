"""Read-only Kumpas source-content audit. No model or detector is loaded.

Outputs are fresh audit evidence, not a replacement inference campaign.
Run with the existing TensorFlow environment's Python solely for NumPy.
"""
import csv
from collections import Counter
from datetime import datetime
from fractions import Fraction
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path, PureWindowsPath
import platform
import stat
import subprocess
import sys
import zipfile

import numpy as np

ROOT = Path('/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis')
REPO = ROOT / 'kumpas'
OLD = ROOT / 'kumpas-data/diagnostics/20261017-validation-v1-3'
CONFIG = REPO / 'benchmarking/study_evidence/20261015/b2/current-inputs-v3.json'
BASELINE = REPO / 'benchmarking/study_evidence/20261015/controller/host-baseline.json'
ARCHIVE = ROOT / 'FSL-105 A dataset for recognizing 105 Filipino sign language videos/clips.zip'
DATALESS = 0x40000000
EXPECTED_OLD = '013f3933fe898dadf2fc25fcf7a12cc50689964f7fba39400cba38e0199b497d'
EXPECTED_CONFIG = '0df969259b620e64ea0b3ea40484492178dfcb4f719437684af94471c50bb78e'
FFPROBE = '/opt/homebrew/bin/ffprobe'
FFMPEG = '/opt/homebrew/bin/ffmpeg'


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def safe_stat(path):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts, 'UNSAFE_PATH'
    for ancestor in (path, *path.parents):
        assert not ancestor.is_symlink(), 'SYMLINK'
    s = path.lstat()
    assert stat.S_ISREG(s.st_mode), 'NOT_REGULAR'
    assert not s.st_flags & DATALESS, 'SOURCE_NOT_RESIDENT'
    return s


def identity(s):
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)


def read_bytes(path):
    before = safe_stat(path)
    with Path(path).open('rb') as f:
        assert identity(os.fstat(f.fileno())) == identity(before), 'OPEN_IDENTITY'
        data = f.read()
        assert identity(os.fstat(f.fileno())) == identity(before), 'READ_MUTATION'
    assert len(data) == before.st_size and identity(safe_stat(path)) == identity(before), 'PATH_MUTATION'
    return data


def hash_file(path):
    before = safe_stat(path)
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        assert identity(os.fstat(f.fileno())) == identity(before), 'OPEN_IDENTITY'
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
        assert identity(os.fstat(f.fileno())) == identity(before), 'READ_MUTATION'
    assert identity(safe_stat(path)) == identity(before), 'PATH_MUTATION'
    return h.hexdigest()


def load_json(path, expected=None):
    blob = read_bytes(path)
    if expected is not None:
        assert digest(blob) == expected, 'INPUT_DIGEST'
    return json.loads(blob), digest(blob)


def save_json(path, value):
    blob = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    with path.open('xb') as f:
        f.write(blob)
    assert path.read_bytes() == blob, 'OUTPUT_READBACK'
    return digest(blob)


def run_tool(args, blob):
    result = subprocess.run(args, input=blob, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
    return result


def main():
    now = datetime.now().astimezone()
    out = REPO / 'benchmarking/study_evidence' / now.strftime('%Y%m%d') / ('source-content-' + now.strftime('%H%M%S'))
    out.mkdir(parents=True, exist_ok=False)
    script_bytes = read_bytes(Path(__file__).resolve())
    with (out / 'audit_source.py').open('xb') as f:
        f.write(script_bytes)
    save_json(out / 'scope.json', {
        'created_at': now.isoformat(),
        'authorization': 'User selected: Verify resident source contents and provenance; no inference, training or devices.',
        'acceptance': 'Current byte readability/integrity and semantic/array/archive consistency for exactly 150 ordered validation pairs; historical hashes compared only where present.',
        'not_authorized': ['model inference', 'detector inference', 'training', 'model conversion/deployment', 'devices', 'participant records', 'rewriting old evidence'],
        'script_sha256': digest(script_bytes), 'python': sys.version, 'numpy': np.__version__,
        'missing_dependency_note': 'OpenCV is absent in this environment; installed FFmpeg tools decode video instead. No dependency installation.',
        'outputs': ['scope.json', 'before.json', 'sources.jsonl', 'summary.json', 'receipt.json', 'audit_source.py'],
    })
    print('AUDIT_DIRECTORY', out, flush=True)
    old, _ = load_json(OLD / 'INCOMPLETE-manifest.json', EXPECTED_OLD)
    config, _ = load_json(CONFIG, EXPECTED_CONFIG)
    preserved = {str(CONFIG): EXPECTED_CONFIG, str(OLD / 'INCOMPLETE-manifest.json'): EXPECTED_OLD}
    for name, expected in old['outputs'].items():
        path = OLD / name
        assert hash_file(path) == expected, 'HISTORICAL_OUTPUT_CHANGED'
        preserved[str(path)] = expected
    historical = [json.loads(line) for line in read_bytes(OLD / 'clips.jsonl').splitlines()]
    assert [r['clip'] for r in historical] == config['ordered_clips'], 'CLIP_ORDER'
    assert len(historical) == len({r['clip'] for r in historical}) == 150, 'CLIP_COUNT'
    assert sum(r['metadata_status'] == 'unavailable' for r in historical) == old['source_metadata_unavailable'] == 134
    baseline, _ = load_json(BASELINE)
    protected_mismatches = []
    for path, record in baseline['protected'].items():
        full = Path(path) if Path(path).is_absolute() else REPO / path
        actual = hash_file(full)
        preserved[str(full)] = actual
        if actual != record['expected']:
            protected_mismatches.append(str(full))
    assert len(baseline['protected']) == 82 and not protected_mismatches, 'PROTECTED_MISMATCH'
    current_roles = {}
    role_drift = []
    for role, filename in config['paths'].items():
        actual = hash_file(Path(filename))
        current_roles[role] = {'path': filename, 'current_sha256': actual, 'historical_sha256': config['sha256'][role]}
        preserved[filename] = actual
        if actual != config['sha256'][role]:
            role_drift.append(role)
    # Current audit uses protected preprocessing only; unrelated accepted helper changes are disclosed, not rebound.
    assert all(role.startswith('source_code_') for role in role_drift), 'NON_SOURCE_ROLE_DRIFT'
    normalization = REPO / 'training/preprocessing/build_sequences.py'
    assert hash_file(normalization) == config['sha256']['source_code_7'], 'NORMALIZATION_CHANGED'
    spec = importlib.util.spec_from_file_location('audit_build_sequences', normalization)
    preprocessing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preprocessing)
    manifest, _ = load_json(Path(config['paths']['manifest']), config['sha256']['manifest'])
    val_rows = [r for r in manifest['rows'] if r['partition'] == 'validation']
    assert [r['clip'] for r in val_rows] == config['ordered_clips']
    assert len({r['index'] for r in val_rows}) == 150
    label_map, _ = load_json(Path(config['paths']['label_map']), config['sha256']['label_map'])
    originals = np.load(io.BytesIO(read_bytes(Path(config['paths']['original_X']))), allow_pickle=False)
    original_y = np.load(io.BytesIO(read_bytes(Path(config['paths']['original_y']))), allow_pickle=False)
    validation = np.load(io.BytesIO(read_bytes(Path(config['paths']['val_X']))), allow_pickle=False)
    val_y = np.load(io.BytesIO(read_bytes(Path(config['paths']['val_y']))), allow_pickle=False)
    original_names, _ = load_json(Path(config['paths']['clips_train']), config['sha256']['clips_train'])
    assert validation.shape == (150, 30, 1662) and val_y.shape == (150,)
    csv_blob = read_bytes(Path(config['paths']['source_train_csv']))
    assert digest(csv_blob) == config['sha256']['source_train_csv']
    csv_lookup = {}
    for r in csv.DictReader(io.StringIO(csv_blob.decode('utf-8-sig'))):
        p = PureWindowsPath(r['vid_path'])
        assert len(p.parts) == 3 and p.parts[0] == 'clips' and p.parts[1].isdigit() and p.stem.isdigit() and p.suffix == '.MOV'
        name = '_'.join(p.with_suffix('.npz').parts)
        assert name not in csv_lookup
        csv_lookup[name] = r
    archive_hash = hash_file(ARCHIVE)
    preserved[str(ARCHIVE)] = archive_hash
    before = {'captured_at': datetime.now().astimezone().isoformat(), 'ordered_clips': config['ordered_clips'], 'preserved_sha256': preserved,
              'historical_role_drift': role_drift, 'current_role_bindings': current_roles, 'protected_count': 82,
              'archive_sha256_current_capture': archive_hash, 'ffmpeg': subprocess.check_output([FFMPEG, '-version']).decode().splitlines()[0],
              'ffprobe': subprocess.check_output([FFPROBE, '-version']).decode().splitlines()[0]}
    save_json(out / 'before.json', before)
    failures = []
    results = []
    with ARCHIVE.open('rb') as archive_stream, zipfile.ZipFile(archive_stream) as archive, (out / 'sources.jsonl').open('x') as ledger:
        assert len(archive.namelist()) == len(set(archive.namelist())), 'ARCHIVE_DUPLICATE_NAMES'
        for index, (row, previous) in enumerate(zip(val_rows, historical)):
            result = {'index': index, 'clip': row['clip'], 'historical_metadata_status': previous['metadata_status'], 'status': 'FAIL'}
            try:
                source = csv_lookup[row['clip']]
                parts = PureWindowsPath(source['vid_path']).parts
                semantic = label_map[str(row['class_id'])]
                assert int(source['id_label']) == semantic['id'] == previous['source_class_id'], 'CLASS_ID'
                assert all(source[k] == semantic[k] for k in ('label', 'category')), 'LABEL_SEMANTICS'
                assert previous['dense_label'] == row['class_id'] and previous['original_index'] == row['index'], 'HISTORICAL_ROW'
                assert original_names[row['index']] == row['clip'], 'ORIGINAL_MEMBERSHIP'
                npz_path = ROOT / 'kumpas-data/landmarks' / row['clip']
                video_path = ROOT / 'kumpas-data/clips_raw' / Path(*parts)
                npz_blob, video_blob = read_bytes(npz_path), read_bytes(video_path)
                npz_hash, video_hash = digest(npz_blob), digest(video_blob)
                result.update({'npz_path': str(npz_path), 'npz_sha256': npz_hash, 'video_path': str(video_path), 'video_sha256': video_hash})
                archive_name = '/'.join(parts)
                archived = archive.read(archive_name)
                assert archived == video_blob, 'ARCHIVE_VIDEO_MISMATCH'
                result['archive_entry'] = archive_name
                result['archive_video_equal'] = True
                with zipfile.ZipFile(io.BytesIO(npz_blob)) as z:
                    assert len(z.namelist()) == len(set(z.namelist())), 'NPZ_DUPLICATE_NAMES'
                    assert z.testzip() is None, 'NPZ_CRC'
                with np.load(io.BytesIO(npz_blob), allow_pickle=False) as data:
                    assert set(data.files) == {'landmarks','class_id','split','fps','brightness','detection_rates'}, 'NPZ_SCHEMA'
                    a = data['landmarks']; cid = data['class_id']; split = data['split']; rates = data['detection_rates']
                    assert a.dtype.kind == 'f' and a.ndim == 2 and a.shape[1] == 1662 and len(a) >= 5 and np.isfinite(a).all(), 'LANDMARK_SCHEMA'
                    assert cid.shape == () and cid.dtype.kind in 'iu' and int(cid) == semantic['id'], 'NPZ_CLASS'
                    assert split.shape == () and split.dtype.kind == 'U' and str(split) == 'train', 'NPZ_SPLIT'
                    assert rates.shape == (4,) and rates.dtype.kind == 'f' and np.isfinite(rates).all() and ((0 <= rates)&(rates <= 1)).all(), 'RATES'
                    values = {}
                    for key in ('fps','brightness'):
                        scalar = data[key]
                        assert scalar.shape == () and scalar.dtype.kind in 'fi' and math.isfinite(float(scalar)) and float(scalar) > 0, 'NPZ_SCALAR'
                        values[key] = float(scalar)
                    indices = preprocessing.sample_indices(len(a), 30)
                    sampled = a[indices]
                    normalized = preprocessing.normalize(sampled).astype(np.float32)
                    assert np.isfinite(normalized).all(), 'NORMALIZED_NONFINITE'
                    assert np.array_equal(normalized, originals[row['index']]), 'ORIGINAL_RECONSTRUCTION'
                    assert np.array_equal(normalized, validation[index]), 'VALIDATION_RECONSTRUCTION'
                    assert int(original_y[row['index']]) == int(val_y[index]) == row['class_id'], 'ARRAY_LABEL'
                    sample_digests = [digest(np.ascontiguousarray(frame).tobytes()) for frame in sampled]
                    result.update({'landmark_shape': list(a.shape), 'landmark_dtype': str(a.dtype), 'dense_label': row['class_id'],
                                   'original_index': row['index'], 'sample_indices': indices.tolist(), 'sampled_frame_sha256': sample_digests,
                                   'normalized_array_sha256': digest(np.ascontiguousarray(normalized).tobytes()),
                                   'original_reconstruction_equal': True, 'validation_reconstruction_equal': True, **values})
                    if previous['metadata_status'] == 'available':
                        assert previous['npz_sha256'] == npz_hash and previous['video_sha256'] == video_hash, 'HISTORICAL_SOURCE_DIGEST'
                        assert previous['landmark_frame_sha256'] == sample_digests and previous['sample_indices'] == indices.tolist(), 'HISTORICAL_FRAME_DIGEST'
                        assert previous['sequence_frames'] == len(a), 'HISTORICAL_FRAME_COUNT'
                        result['historical_source_hash_comparison'] = 'MATCH'
                    else:
                        assert 'npz_sha256' not in previous and 'video_sha256' not in previous, 'UNEXPECTED_OLD_HASH'
                        result['historical_source_hash_comparison'] = 'NOT_AVAILABLE_CURRENT_CAPTURE_ONLY'
                    probe = run_tool([FFPROBE, '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                                      'stream=codec_name,width,height,avg_frame_rate,nb_read_frames', '-of', 'json', '-i', 'pipe:0'], video_blob)
                    assert probe.returncode == 0 and not probe.stderr.strip(), 'VIDEO_PROBE'
                    streams = json.loads(probe.stdout)['streams']
                    assert len(streams) == 1, 'VIDEO_STREAM_COUNT'
                    stream = streams[0]
                    assert int(stream['nb_read_frames']) == len(a) and int(stream['width']) > 0 and int(stream['height']) > 0, 'VIDEO_FRAME_COUNT'
                    assert round(float(Fraction(stream['avg_frame_rate'])),2) == values['fps'], 'VIDEO_FPS'
                    decoded = run_tool([FFMPEG, '-v', 'error', '-xerror', '-threads', '1', '-i', 'pipe:0', '-map', '0:v:0', '-an', '-f', 'null', '-'], video_blob)
                    assert decoded.returncode == 0 and not decoded.stderr.strip(), 'VIDEO_DECODE'
                    result.update({'video_stream': stream, 'ffprobe_exit': probe.returncode, 'ffmpeg_exit': decoded.returncode, 'video_full_decode': True, 'status': 'PASS'})
            except Exception as exc:
                result['error_type'] = type(exc).__name__
                result['error_code'] = str(exc) if isinstance(exc, AssertionError) else 'SOURCE_CHECK_FAILED'
                failures.append({'clip': row['clip'], 'error_code': result['error_code'], 'error_type': result['error_type']})
            ledger.write(json.dumps(result, allow_nan=False) + '\n'); ledger.flush()
            results.append(result)
            if (index + 1) % 15 == 0 or result['status'] != 'PASS':
                print(json.dumps({'processed':index+1,'passed':sum(r['status']=='PASS' for r in results),'failures':len(failures)}), flush=True)
    after_mismatches = [p for p, expected in preserved.items() if hash_file(Path(p)) != expected]
    assert not after_mismatches, 'PRESERVATION_CHANGED'
    for r in results:
        if r['status'] == 'PASS':
            assert hash_file(Path(r['npz_path'])) == r['npz_sha256'] and hash_file(Path(r['video_path'])) == r['video_sha256'], 'SOURCE_POST_READ_CHANGED'
    assert not any(m == 'tensorflow' or m.startswith(('tensorflow.', 'mediapipe', 'tflite')) for m in sys.modules), 'MODEL_RUNTIME_IMPORTED'
    summary = {'completed_at': datetime.now().astimezone().isoformat(), 'status': 'PASS_SOURCE_CONTENT_ONLY' if not failures else 'INCOMPLETE_SOURCE_CHECK_FAILURE',
               'required_pairs':150,'processed_pairs':len(results),'passed_pairs':sum(r['status']=='PASS' for r in results),'failures':failures,
               'historical_hash_matched_pairs':sum(r.get('historical_source_hash_comparison')=='MATCH' for r in results),
               'current_capture_only_pairs':sum(r.get('historical_source_hash_comparison')=='NOT_AVAILABLE_CURRENT_CAPTURE_ONLY' for r in results),
               'archive_equal_videos':sum(r.get('archive_video_equal',False) for r in results),
               'full_decoded_videos':sum(r.get('video_full_decode',False) for r in results),
               'original_reconstructions_equal':sum(r.get('original_reconstruction_equal',False) for r in results),
               'validation_reconstructions_equal':sum(r.get('validation_reconstruction_equal',False) for r in results),
               'protected_originals_unchanged':82,'preserved_paths':len(preserved),'preservation_mismatches':after_mismatches,
               'historical_role_drift':role_drift,'source_hashes_rechecked_after_scan':not failures,
               'no_tensorflow_mediapipe_tflite_import':True, 'inference_performed':False,'training_performed':False,'devices_used':False,
               'limits':['Current capture does not retroactively supply absent historical source hashes.',
                         'Archive equality binds videos to the local archive, not independently authenticated publisher bytes.',
                         'Exact sequence reconstruction does not prove detector correctness, linguistic validity or signer independence.',
                         'Original incomplete inference campaign remains incomplete; no new full-provenance inference campaign is authorized.',
                         'No accuracy, deployment, installed runtime, physical performance or participant-study gate is closed.']}
    save_json(out/'summary.json',summary)
    assert len(results)==150
    for name in ['sources.jsonl','before.json','scope.json','summary.json','audit_source.py']:
        assert (out/name).is_file()
    receipt = {'scope':'SOURCE_CONTENT_ONLY_NOT_INFERENCE_CAMPAIGN','status':summary['status'],
               'outputs':{name:hash_file(out/name) for name in ['sources.jsonl','before.json','scope.json','summary.json','audit_source.py']},
               'historical_manifest_sha256':EXPECTED_OLD,'historical_configuration_sha256':EXPECTED_CONFIG}
    save_json(out/'receipt.json',receipt)
    print(json.dumps(summary,indent=2),flush=True)
    print('AUDIT_DIRECTORY',out,flush=True)
    return 0 if not failures else 2


if __name__ == '__main__':
    raise SystemExit(main())
