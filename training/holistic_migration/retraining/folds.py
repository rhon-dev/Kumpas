"""Phase 2: frozen fold split over the official train clips (fit + validation).

Two modes. With signer groups (Phase 1 found them), each signer group is one fold
(leave-one-signer-out). Without them, 5 folds stratified by sign, balanced separately for clips the
strictest input (hm1588) can use, with near-duplicate groups kept in one fold. Quarantined clips
are left out. Each fold gets an inner stopping set: one strict-eligible, ungrouped clip per sign
from the other folds. Near-duplicate partners of a scored clip never train in that fold (split()).
"""
import numpy as np

K = 5
SEED = 20260705


def _units(pool, groups):
    parent = {c: c for c in pool}

    def find(c):
        while parent[c] != c:
            parent[c] = parent[parent[c]]
            c = parent[c]
        return c
    for group in groups:
        members = [c for c in group if c in parent]
        for c in members[1:]:
            parent[find(c)] = find(members[0])
    units = {}
    for c in sorted(pool):
        units.setdefault(find(c), []).append(c)
    return list(units.values())


def make_folds(rows, quarantine, groups, strict, k=K, seed=SEED, signer_of=None):
    sign = {r['clip_id']: r['dense_id'] for r in rows if r['partition'] in ('fit', 'validation')}
    pool = set(sign) - set(quarantine)
    rng = np.random.default_rng(seed)
    near = [sorted(c for c in g if c in pool) for g in groups]
    near = [g for g in near if len(g) > 1]
    if signer_of is not None:
        names = sorted({signer_of[c] for c in pool})
        k = len(names)
        fold_of = {c: names.index(signer_of[c]) for c in pool}
        mode = 'leave-one-signer-out'
    else:
        units = _units(pool, near)
        near = [u for u in units if len(u) > 1]
        order = sorted(range(len(units)), key=lambda i: (-len(units[i]), rng.random()))
        strict_n, sign_n, total, fold_of = {}, {}, [0] * k, {}
        for i in order:
            unit = units[i]
            f = min(range(k), key=lambda f: (sum(strict_n.get((f, sign[c]), 0) for c in unit if c in strict),
                                             sum(sign_n.get((f, sign[c]), 0) for c in unit), total[f], f))
            for c in unit:
                fold_of[c] = f
                total[f] += 1
                sign_n[(f, sign[c])] = sign_n.get((f, sign[c]), 0) + 1
                if c in strict:
                    strict_n[(f, sign[c])] = strict_n.get((f, sign[c]), 0) + 1
        mode = 'stratified'
    grouped = {c for g in near for c in g}
    inner = {}
    for f in range(k):
        chosen = []
        for s in sorted(set(sign.values())):
            options = sorted(c for c in pool if sign[c] == s and fold_of[c] != f and c in strict and c not in grouped)
            if not options:
                raise ValueError(f'no inner stopping clip for sign {s} in fold {f}')
            chosen.append(options[int(rng.integers(len(options)))])
        inner[str(f)] = chosen
    return dict(schema=1, mode=mode, k=k, seed=seed, quarantined=sorted(quarantine), groups=near,
                fold_of=dict(sorted(fold_of.items())), inner=inner)


def validate(doc, rows, quarantine, groups, strict, signer_of=None):
    """Raise ValueError unless the fold document meets every Phase 2 leakage rule."""
    sign = {r['clip_id']: r['dense_id'] for r in rows if r['partition'] in ('fit', 'validation')}
    fold_of, k = doc['fold_of'], doc['k']
    if set(fold_of) != set(sign) - set(quarantine):
        raise ValueError('fold membership must be every official train clip except quarantined ones, once')
    if any(type(f) is not int or not 0 <= f < k for f in fold_of.values()):
        raise ValueError('invalid fold index')
    if signer_of is not None:
        names = sorted({signer_of[c] for c in fold_of})
        if any(fold_of[c] != names.index(signer_of[c]) for c in fold_of):
            raise ValueError('signer group split across folds')
    else:
        for group in groups:
            if len({fold_of[c] for c in group if c in fold_of}) > 1:
                raise ValueError(f'group split across folds: {group}')
    listed = {tuple(g) for g in doc['groups']}
    for group in groups:
        g = tuple(sorted(c for c in group if c in fold_of))
        if len(g) > 1 and not any(set(g) <= set(h) for h in listed):
            raise ValueError(f'near-duplicate group missing from the fold document: {g}')
    grouped = {c for g in doc['groups'] for c in g}
    # Leave-one-signer-out: a signer may have no clip the strict input can use for some sign
    # (face hidden throughout); such gaps are recorded, so require only that the sign is present.
    usable = set(fold_of) if signer_of is not None else strict
    for s in set(sign.values()):
        for f in range(k):
            if not any(fold_of[c] == f and sign[c] == s and c in usable for c in fold_of):
                raise ValueError(f'sign {s} has no usable clip in fold {f}')
    for f in range(k):
        inner = doc['inner'][str(f)]
        if sorted(sign[c] for c in inner) != sorted(set(sign.values())):
            raise ValueError(f'fold {f}: inner set needs exactly one clip per sign')
        if any(fold_of[c] == f or c not in strict or c in grouped for c in inner):
            raise ValueError(f'fold {f}: invalid inner stopping clip')


def freeze(out_file, audit_dir):
    """Build, validate and exclusively write folds-v1.json from the Phase 1 audit outputs."""
    import json
    from pathlib import Path
    from .. import dataset as d
    from . import data
    audit_dir = Path(audit_dir)
    partitions = json.loads(data.PARTITION_FILE.read_text())
    rows = partitions['rows']
    quarantine = json.loads((audit_dir / 'quarantine-view-v2.json').read_text())['quarantined']
    groups_doc = json.loads((audit_dir / 'fold-groups.json').read_text())
    groups, signer_of = groups_doc['near_duplicate_groups'], groups_doc['signer_group_of']
    strict = {c for p in data.OPEN_PARTITIONS for c in data.load('hm1588', p)[2].tolist()}
    doc = make_folds(rows, quarantine, groups, strict, signer_of=signer_of)
    validate(doc, rows, quarantine, groups, strict, signer_of=signer_of)
    sign = {r['clip_id']: r['dense_id'] for r in rows}
    doc['inputs'] = {str(data.PARTITION_FILE): d.sha256(data.PARTITION_FILE),
                     str(audit_dir / 'quarantine-view-v2.json'): d.sha256(audit_dir / 'quarantine-view-v2.json'),
                     str(audit_dir / 'fold-groups.json'): d.sha256(audit_dir / 'fold-groups.json')}
    doc['counts'] = {str(f): dict(clips=sum(v == f for v in doc['fold_of'].values()),
                                  strict_eligible=sum(v == f and c in strict for c, v in doc['fold_of'].items()),
                                  min_strict_per_sign=min(sum(v == f and c in strict and sign[c] == s
                                                              for c, v in doc['fold_of'].items())
                                                          for s in set(sign.values())))
                     for f in range(doc['k'])}
    labels = {r['dense_id']: r['label'] for r in rows}
    doc['strict_gaps'] = [dict(fold=f, sign=labels[s]) for f in range(doc['k']) for s in sorted(set(sign.values()))
                          if not any(v == f and c in strict and sign[c] == s for c, v in doc['fold_of'].items())]
    with open(out_file, 'x') as f:
        f.write(json.dumps(doc, indent=1) + '\n')
    print(json.dumps({k: doc[k] for k in ['mode', 'k', 'quarantined', 'groups', 'counts', 'strict_gaps']}, indent=1))
    print('sha256', d.sha256(out_file))


if __name__ == '__main__':
    import sys
    freeze(sys.argv[1], sys.argv[2])
