"""Build hm211-v1 / hm337-v1 bundles from the raw campaign without the detector (RETRAINING_PLAN.md Phase 3).

usage: python -E -B -m training.holistic_migration.retraining.build_v2 OUT PARTITION [PARTITION ...]
OUT must not exist. The test partition is opened only when named (Phase 5).
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from .. import dataset as d
from . import data, features_v2


def _save(path, array):
    with open(path, 'xb') as f:
        np.save(f, array, allow_pickle=False)
    return d.sha256(path)


def build(out, partitions):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    rows = data.campaign_rows()
    for feature in features_v2.WIDTH:
        (out / feature).mkdir()
    manifest = {f: dict(feature=f'{f}-v1', partitions={}, artifacts={}) for f in features_v2.WIDTH}
    for partition in partitions:
        selected = [r for r in rows if r['partition'] == partition]
        xs, ys, ids, ts, obs, offsets, excluded = [], [], [], [], [], [0], []
        for r in selected:
            raw = (d.read_raw(data.CAMPAIGN / r['raw_file'], r['raw_sha256']) if partition == 'test'
                   else data.raw_frames(r))
            result = features_v2.prepare_capture(raw)
            if result.reason != 'eligible':
                excluded.append(dict(clip_id=r['clip_id'], label=r['label'], reason=result.reason))
                continue
            t, o = features_v2.bounded_observations(raw)
            xs.append(result.tensor), ys.append(r['dense_id']), ids.append(r['clip_id'])
            ts.append(t), obs.append(o), offsets.append(offsets[-1] + len(t))
        x = np.stack(xs)
        per_sign = Counter(r['label'] for r in selected if r['clip_id'] in set(ids))
        for feature, tensor in [('hm211', x), ('hm337', features_v2.add_hand_local(x))]:
            art = manifest[feature]['artifacts']
            art[f'X_{partition}.npy'] = _save(out / feature / f'X_{partition}.npy', tensor)
            art[f'y_{partition}.npy'] = _save(out / feature / f'y_{partition}.npy', np.array(ys, dtype=np.int64))
            art[f'clip_ids_{partition}.npy'] = _save(out / feature / f'clip_ids_{partition}.npy', np.array(ids))
            if feature == 'hm211':
                with open(out / feature / f'obs_{partition}.npz', 'xb') as f:
                    np.savez(f, timestamps=np.concatenate(ts), rows=np.concatenate(obs),
                             offsets=np.array(offsets, dtype=np.int64))
                art[f'obs_{partition}.npz'] = d.sha256(out / feature / f'obs_{partition}.npz')
            manifest[feature]['partitions'][partition] = dict(
                declared=len(selected), eligible=len(ids), excluded=excluded, eligible_per_sign=dict(sorted(per_sign.items())),
                raw_sha256_digest=hashlib.sha256('\n'.join(r['raw_sha256'] for r in selected).encode()).hexdigest())
    code = {p.name: d.sha256(p) for p in [Path(features_v2.__file__), Path(__file__)]}
    for feature, m in manifest.items():
        m.update(width=features_v2.WIDTH[feature], code_sha256=code, campaign=str(data.CAMPAIGN),
                 campaign_rows_sha256=d.sha256(data.CAMPAIGN / 'rows.jsonl'))
        with open(out / feature / 'manifest.json', 'x') as f:
            f.write(json.dumps(m, indent=1) + '\n')
    return {f: {p: (m['partitions'][p]['declared'], m['partitions'][p]['eligible']) for p in m['partitions']}
            for f, m in manifest.items()}


def load(bundle, partition, observations=False):
    """(X, y, ids[, observations]) checked against the bundle manifest."""
    bundle = Path(bundle)
    art = json.loads((bundle / 'manifest.json').read_text())['artifacts']
    out = []
    for prefix in ('X', 'y', 'clip_ids'):
        file = f'{prefix}_{partition}.npy'
        d.same(d.sha256(bundle / file), art[file], f'{bundle.name} {file}')
        out.append(np.load(bundle / file, allow_pickle=False))
    if observations:
        file = f'obs_{partition}.npz'
        d.same(d.sha256(bundle / file), art[file], f'{bundle.name} {file}')
        with np.load(bundle / file, allow_pickle=False) as z:
            o = z['offsets']
            out.append({c: (z['timestamps'][o[i]:o[i + 1]], z['rows'][o[i]:o[i + 1]])
                        for i, c in enumerate(out[2].tolist())})
    return tuple(out)


if __name__ == '__main__':
    out, *partitions = sys.argv[1:]
    if not partitions or set(partitions) - {'fit', 'validation', 'test'}:
        raise SystemExit(__doc__)
    if 'test' not in partitions:
        data.install_guard(data.test_raw_paths(data.campaign_rows()))
    print(json.dumps(build(out, partitions), indent=1))
