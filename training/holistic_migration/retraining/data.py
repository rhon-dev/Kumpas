"""Read-only access to fit/validation data. The official test split stays sealed until Phase 5."""
import json
import os
import sys

import numpy as np

from .. import dataset as d

DATA = d.REPO.parent / 'holistic-migration-data'
BUNDLES = {'hm153': DATA / 'hm153-canonical-bundle-20261113-accepted-c1',
           'hm1588': DATA / 'hm1588-canonical-bundle-20261116-v1'}
CAMPAIGN = DATA / 'hm153-full-campaign-20261113-accepted-c1'
PARTITION_FILE = DATA / 'candidate-partitions-v1.json'
OPEN_PARTITIONS = ('fit', 'validation')


def load(name, partition):
    """Return (X, y, ids) of one open partition, each array checked against the bundle manifest."""
    if partition not in OPEN_PARTITIONS:
        raise ValueError(f'partition {partition!r} is sealed or unknown')
    bundle = BUNDLES[name]
    artifacts = json.loads((bundle / 'data_manifest.json').read_text())['artifacts']
    out = []
    for prefix in ('X', 'y', 'clip_ids'):
        file = f'{prefix}_{partition}.npy'
        d.same(d.sha256(bundle / file), artifacts[file]['sha256'], f'{name} {file}')
        out.append(np.load(bundle / file, allow_pickle=False))
    return tuple(out)


def campaign_rows():
    """Row metadata of all 1,016 clips (metadata only; raw observations are separate)."""
    manifest = json.loads((CAMPAIGN / 'extraction_manifest.json').read_text())
    d.same(d.sha256(CAMPAIGN / 'rows.jsonl'), manifest['rows_sha256'], 'campaign rows')
    return [json.loads(line) for line in (CAMPAIGN / 'rows.jsonl').read_text().splitlines()]


def test_raw_paths(rows):
    return {str(CAMPAIGN / r['raw_file']) for r in rows if r['partition'] not in OPEN_PARTITIONS}


def raw_frames(row):
    """Digest-checked raw observations of one fit or validation clip."""
    if row['partition'] not in OPEN_PARTITIONS:
        raise ValueError('raw observations of sealed clips are not opened')
    return d.read_raw(CAMPAIGN / row['raw_file'], row['raw_sha256'])


def blocked(path, extra):
    path = os.fspath(path)
    path = path.decode() if isinstance(path, bytes) else path
    return '_test.' in os.path.basename(path) or os.path.abspath(path) in extra


def install_guard(extra):
    """Refuse opening test arrays and sealed raw files. Trusted-script instrumentation, not an OS sandbox."""
    extra = {os.path.abspath(p) for p in extra}

    def hook(event, args):
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)) and blocked(args[0], extra):
            raise PermissionError(f'sealed path: {args[0]!r}')
    sys.addaudithook(hook)
