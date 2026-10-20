#!/usr/bin/env python3
"""Versioned host-only FIVE/THREE validation fixture campaign; no classifier inference.

Output must be a NEW directory under ../kumpas-data/parity. selection.json is
frozen for all six clips before decoding. Only manifest.json denotes completion.
No historical manifests are updated. Local trusted filesystem, not attestation.
"""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

import numpy as np
from pipeline_parity import (REPO_ROOT, reject_symlinks, prepare_video, generate_python_reference,
                             validate_replay, compare_vectors, BLOCKS, PRESENCE)

TARGETS = ((22, 14, 'THREE'), (22, 8, 'THREE'), (22, 9, 'THREE'),
           (24, 10, 'FIVE'), (24, 11, 'FIVE'), (24, 18, 'FIVE'))
SOURCES = ('benchmarking/pipeline_parity.py', 'benchmarking/parity_fixtures.py',
           'training/preprocessing/extract_landmarks.py', 'training/preprocessing/build_sequences.py')


def digest(path):
    path = reject_symlinks(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_new(path, document):
    path = reject_symlinks(path)
    with path.open('x') as stream:
        json.dump(document, stream, indent=2, allow_nan=False)
        stream.write('\n')


def read_json(path):
    try:
        return json.loads(reject_symlinks(path).read_text())
    except (OSError, ValueError):
        raise ValueError('invalid campaign input JSON') from None


def freeze_campaign(repo, output):
    repo, output = reject_symlinks(repo), reject_symlinks(output)
    data = repo.parent / 'kumpas-data'
    allowed = data / 'parity'
    if '..' in output.parts or not output.is_relative_to(allowed) or output == allowed:
        raise ValueError('output must be a new external parity campaign')
    if output.exists():
        raise FileExistsError('campaign already exists')
    protocol = data / 'sequences/evaluation-v1/manifest.json'
    selection = repo / 'training/models/protocol_selection_evaluation_v1.json'
    labels_path = data / 'sequences/label_map.json'
    manifest, selected, labels = read_json(protocol), read_json(selection), read_json(labels_path)
    if (type(manifest) is not dict or manifest.get('version') != 'evaluation-v1' or
            type(manifest.get('rows')) is not list or type(selected) is not dict or
            selected.get('protocol_sha256') != digest(protocol) or type(labels) is not dict):
        raise ValueError('protocol selection mismatch')
    clips = []
    for source_id, clip, label in TARGETS:
        matches = [(key, value) for key, value in labels.items()
                   if type(value) is dict and type(value.get('id')) is int and value['id'] == source_id
                   and value.get('label') == label]
        if len(matches) != 1 or not matches[0][0].isdigit():
            raise ValueError('class map mismatch')
        dense_id = int(matches[0][0])
        clip_id = f'clips_{source_id}_{clip}.npz'
        rows = [row for row in manifest['rows'] if type(row) is dict and row.get('clip') == clip_id]
        if (len(rows) != 1 or rows[0].get('partition') != 'validation' or
                type(rows[0].get('class_id')) is not int or rows[0]['class_id'] != dense_id or
                type(rows[0].get('index')) is not int or rows[0]['index'] < 0):
            raise ValueError('validation membership mismatch')
        video_rel = f'clips_raw/clips/{source_id}/{clip}.MOV'
        landmark_rel = f'landmarks/{clip_id}'
        video, landmark = data / video_rel, data / landmark_rel
        with np.load(reject_symlinks(landmark), allow_pickle=False) as npz:
            arr = npz['landmarks']
            cid = npz['class_id']
            if (arr.ndim != 2 or arr.shape[1] != 1662 or arr.shape[0] < 30 or
                    arr.dtype.kind != 'f' or not np.isfinite(arr).all() or
                    cid.shape != () or cid.dtype.kind not in 'iu' or int(cid) != source_id or
                    str(npz['split']) != 'train'):
                raise ValueError('landmark identity or values mismatch')
        clips.append({'clip_id': clip_id, 'source_class': source_id, 'dense_class': dense_id,
                      'label': label, 'partition': 'validation', 'original_index': rows[0]['index'],
                      'video': video_rel, 'landmarks': landmark_rel,
                      'source_video_sha256': digest(video), 'landmarks_sha256': digest(landmark)})
    frozen = {'schema': 'kumpas-validation-parity-selection-v1', 'status': 'frozen_before_extraction',
              'created_at': datetime.datetime.now().astimezone().isoformat(),
              'clips': clips, 'protocol_sha256': digest(protocol), 'selection_sha256': digest(selection),
              'class_map_sha256': digest(labels_path),
              'source_sha256': {name: digest(REPO_ROOT / name) for name in SOURCES},
              'sampling': '30 uniform endpoint-inclusive frames; sequential Holistic VIDEO tracking on sampled PNGs differs from stored full-video tracking',
              'runtime': {'python': platform.python_version(),
                          **{name: importlib.metadata.version(name) for name in ('numpy', 'mediapipe', 'opencv-python')}},
              'limitations': ['No Android execution', 'Anatomical handedness unverified',
                              'No classifier prediction or accuracy measurement', 'Parent independent review required']}
    output.mkdir(parents=True, exist_ok=False)
    (output / 'INCOMPLETE').open('x').close()
    write_new(output / 'selection.json', frozen)
    return frozen


def generate_campaign(repo, output, frozen):
    """Execute sequential preparation from an already frozen selection."""
    from training.preprocessing.build_sequences import normalize, sample_indices
    data = Path(repo).absolute().parent / 'kumpas-data'
    output = reject_symlinks(output)
    selection_hash = digest(output / 'selection.json')
    fixtures = []
    for clip in frozen['clips']:
        for key, hash_key in (('video', 'source_video_sha256'), ('landmarks', 'landmarks_sha256')):
            if digest(data / clip[key]) != clip[hash_key]:
                raise ValueError('frozen input changed')
        directory = output / clip['clip_id'].removesuffix('.npz')
        directory.mkdir(exist_ok=False)
        replay = prepare_video(data / clip['video'], directory / 'frames', 30)
        if len(replay['frames']) != 30 or replay['source_video_sha256'] != clip['source_video_sha256']:
            raise ValueError('sample count or video identity changed')
        replay_hash = digest(directory / 'frames/manifest.json')
        binding = {'schema': 'kumpas-clip-binding-v1', 'clip_id': clip['clip_id'],
                   'source_video_sha256': clip['source_video_sha256'], 'replay_manifest_sha256': replay_hash}
        write_new(directory / 'binding.json', binding)
        reference = generate_python_reference(directory / 'frames', directory / 'python-detection-v1.json')
        reference['fixture_binding'] = binding
        compare_vectors(reference, reference, require_clip_binding=True)  # structural validation only, NOT parity evidence
        write_new(directory / 'python.json', reference)
        with np.load(data / clip['landmarks'], allow_pickle=False) as stored:
            raw = stored['landmarks']
            indices = sample_indices(len(raw), 30)
            normalized = normalize(raw[indices])
            full_path = np.concatenate((normalized[:, :132], normalized[:, 1536:1662]), axis=1)
            full_presence = {name: int(np.any(raw[:, lo:hi] != 0, axis=1).sum())
                             for name, (lo, hi) in {'pose': (0,132), 'face': (132,1536),
                                                   'left_hand': (1536,1599), 'right_hand': (1599,1662)}.items()}
            stored_rates = stored['detection_rates'].astype(float).tolist()
            full_count = len(raw)
        sampled = np.asarray([row['features'] for row in reference['frames']], dtype=np.float64)
        if not np.isfinite(full_path).all() or not np.isfinite(sampled).all():
            raise ValueError('nonfinite host features')
        delta = np.abs(full_path.astype(np.float64) - sampled)
        summary = {'frames': 30, 'decoded_frames': replay['decoded_frames'], 'source_fps': replay['source_fps'],
                   'stored_full_video_frames': full_count, 'stored_resample_indices': indices.tolist(),
                   'sampled_presence': {key: sum(row[key] for row in reference['frames']) for key in PRESENCE},
                   'sampled_detector_presence_counts': reference['detector_presence_counts'],
                   'stored_full_video_presence_counts': full_presence, 'stored_detection_rates': stored_rates,
                   'sampled_feature_min': float(sampled.min()), 'sampled_feature_max': float(sampled.max()),
                   'finite_feature_count': int(np.isfinite(sampled).sum()),
                   'host_path_block_mae': {key: float(delta[:,lo:hi].mean()) for key,(lo,hi) in BLOCKS.items()},
                   'host_path_block_max_abs': {key: float(delta[:,lo:hi].max()) for key,(lo,hi) in BLOCKS.items()},
                   'interpretation': 'Different detector tracking paths: stored full-video normalize/resample vs sampled-PNG Holistic re-detection. Not Android parity, normalization defect, anatomy or accuracy evidence.'}
        fixture = {'schema': 'kumpas-validation-parity-fixture-v1', 'clip_id': clip['clip_id'],
                   'directory': directory.name, 'binding': binding, 'selection_sha256': selection_hash,
                   'partition': clip['partition'], 'dense_class': clip['dense_class'], 'source_class': clip['source_class'],
                   'original_index': clip['original_index'], 'class_map_sha256': frozen['class_map_sha256'],
                   'protocol_sha256': frozen['protocol_sha256'], 'protocol_selection_sha256': frozen['selection_sha256'],
                   'landmarks_sha256': clip['landmarks_sha256'], 'source_sha256': frozen['source_sha256'],
                   'runtime': frozen['runtime'], 'sampling': frozen['sampling'],
                   'replay_manifest_sha256': replay_hash, 'python_sha256': digest(directory / 'python.json'),
                   'files': {name: digest(directory / name) for name in
                             ('binding.json', 'python.json', 'python-detection-v1.json', 'frames/manifest.json')},
                   'summary': summary}
        write_new(directory / 'fixture.json', fixture)
        fixtures.append({**fixture, 'fixture_manifest_sha256': digest(directory / 'fixture.json')})
        print(json.dumps({'clip': clip['clip_id'], 'status': 'prepared', 'frames': 30}), flush=True)
    # Verify every named output and every PNG again before publishing completion.
    for fixture in fixtures:
        directory = output / fixture['directory']
        validate_replay(directory / 'frames')
        if digest(directory / 'fixture.json') != fixture['fixture_manifest_sha256']:
            raise ValueError('fixture manifest changed')
        for name, expected in fixture['files'].items():
            if digest(directory / name) != expected:
                raise ValueError('fixture output changed')
    if selection_hash != digest(output / 'selection.json'):
        raise ValueError('selection changed')
    for name, expected in frozen['source_sha256'].items():
        if digest(REPO_ROOT / name) != expected:
            raise ValueError('extractor source changed')
    for clip in frozen['clips']:
        if digest(data / clip['video']) != clip['source_video_sha256'] or digest(data / clip['landmarks']) != clip['landmarks_sha256']:
            raise ValueError('frozen input changed')
    manifest = {'schema': 'kumpas-validation-parity-campaign-v1', 'status': 'prepared_python_references_only',
                'selection_sha256': selection_hash, 'fixtures': fixtures, 'limitations': frozen['limitations']}
    write_new(output / 'manifest.json', manifest)
    (output / 'INCOMPLETE').unlink()
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=REPO_ROOT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--freeze-only', action='store_true')
    args = parser.parse_args()
    frozen = freeze_campaign(args.repo, args.output)
    if not args.freeze_only:
        result = generate_campaign(args.repo, args.output, frozen)
        print(json.dumps({'status': result['status'], 'clips': len(result['fixtures'])}))
    else:
        print(json.dumps({'status': frozen['status'], 'clips': len(frozen['clips'])}))


if __name__ == '__main__':
    main()
