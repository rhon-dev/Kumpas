"""Phase 1 of RETRAINING_PLAN.md: read-only data and leakage audit on fit and validation only.

usage: python -E -B -m training.holistic_migration.retraining.audit OUT_DIR
Writes new files into OUT_DIR (must not exist). Trains no classifier; the probes are small
logistic regressions. The official test split is sealed: no test tensor or test raw file is opened.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .. import dataset as d
from . import data, report

PHASE4 = data.DATA / 'evidence/phase-4-20261116/full-source-v1'
RETRAINING = data.DATA / 'evidence/retraining-v1'
DUPLICATES = data.DATA / 'evidence/rejection-calibration-public-v1/source-audit/parent-duplicate-adjudication.json'
# Clips published twice under conflicting labels (rejection-calibration source audit).
CONFLICTING_DUPLICATES = ['clips/23/6.MOV', 'clips/57/9.MOV', 'clips/23/8.MOV']
FACE_PROBE_LIMIT = .15          # section 5: face-only accuracy above 15% needs investigation
CLEAR_SILHOUETTE = .5           # predeclared: signer clusters are used only if this clear
W, H = 640, 360                 # detector input size; landmarks are normalized to it


# ---------- near-duplicates ----------

def _distances(a, b):
    a, b = a.reshape(len(a), -1).astype(np.float64), b.reshape(len(b), -1).astype(np.float64)
    sq = (a * a).sum(1)[:, None] + (b * b).sum(1)[None, :] - 2 * a @ b.T
    return np.sqrt(np.maximum(sq, 0))


def near_duplicates(fit, val, percentile=1.0):
    """Threshold = given percentile of each fit clip's distance to its nearest other fit clip.
    Flag every validation-fit pair and fit-fit pair closer than that."""
    ff = _distances(fit, fit)
    np.fill_diagonal(ff, np.inf)
    threshold = float(np.percentile(ff.min(axis=1), percentile))
    vf = _distances(val, fit) if len(val) else np.zeros((0, len(fit)))
    flagged = sorted((int(i), int(j), float(vf[i, j])) for i, j in zip(*np.nonzero(vf < threshold)))
    iu = np.triu_indices(len(fit), 1)
    close = ff[iu] < threshold
    fit_pairs = sorted((int(i), int(j), float(ff[i, j])) for i, j in zip(iu[0][close], iu[1][close]))
    return dict(threshold=threshold, flagged=flagged, fit_pairs=fit_pairs,
                val_nearest=vf.min(axis=1).tolist() if len(val) else [])


# ---------- probes and clustering ----------

def fit_logistic(x, y, classes, l2=1e-3, steps=600, lr=.05):
    """Multinomial logistic regression, standardized on the given data, full-batch Adam. Deterministic."""
    x = np.asarray(x, np.float64)
    mean, std = x.mean(0), x.std(0)
    std[std == 0] = 1
    z = (x - mean) / std
    w, b = np.zeros((z.shape[1], classes)), np.zeros(classes)
    onehot = np.eye(classes)[y]
    m = [np.zeros_like(w), np.zeros_like(b)]
    v = [np.zeros_like(w), np.zeros_like(b)]
    for t in range(1, steps + 1):
        logits = z @ w + b
        p = np.exp(logits - logits.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        g = (p - onehot) / len(z)
        grads = [z.T @ g + l2 * w, g.sum(0)]
        for k, (param, grad) in enumerate(zip((w, b), grads)):
            m[k] = .9 * m[k] + .1 * grad
            v[k] = .999 * v[k] + .001 * grad * grad
            param -= lr * (m[k] / (1 - .9 ** t)) / (np.sqrt(v[k] / (1 - .999 ** t)) + 1e-8)
    return dict(mean=mean, std=std, w=w, b=b)


def predict_logistic(model, x):
    logits = ((np.asarray(x, np.float64) - model['mean']) / model['std']) @ model['w'] + model['b']
    p = np.exp(logits - logits.max(1, keepdims=True))
    return p / p.sum(1, keepdims=True)


def kmeans(x, k, seed, iterations=100, restarts=10):
    rng = np.random.default_rng(seed)
    best, best_cost = None, np.inf
    for _ in range(restarts):
        centres = [x[rng.integers(len(x))]]
        for _ in range(k - 1):                      # k-means++ seeding
            dist = ((x[:, None] - np.array(centres)[None]) ** 2).sum(-1).min(1)
            centres.append(x[rng.choice(len(x), p=dist / dist.sum())])
        centres = np.array(centres)
        for _ in range(iterations):
            labels = ((x[:, None] - centres[None]) ** 2).sum(-1).argmin(1)
            new = np.array([x[labels == c].mean(0) if (labels == c).any() else centres[c] for c in range(k)])
            if np.allclose(new, centres):
                break
            centres = new
        cost = ((x - centres[labels]) ** 2).sum()
        if cost < best_cost:
            best, best_cost = labels, cost
    return best


def silhouette(x, labels):
    dist = _distances(x, x)
    scores = []
    for i, c in enumerate(labels):
        same = labels == c
        if same.sum() < 2:
            scores.append(0.0)
            continue
        a = dist[i, same].sum() / (same.sum() - 1)
        b = min(dist[i, labels == o].mean() for o in set(labels.tolist()) if o != c)
        scores.append((b - a) / max(a, b))
    return float(np.mean(scores))


def mutual_information_norm(a, b):
    """Normalized mutual information, arithmetic mean of entropies."""
    n = len(a)
    joint = Counter(zip(a, b))
    pa, pb = Counter(a), Counter(b)
    mi = sum(c / n * np.log(c * n / (pa[x] * pb[y])) for (x, y), c in joint.items())
    ha = -sum(c / n * np.log(c / n) for c in pa.values())
    hb = -sum(c / n * np.log(c / n) for c in pb.values())
    return float(2 * mi / (ha + hb)) if ha + hb else 0.0


def signer_block(number):
    """FSL-105 clip numbers 0-4, 5-9, 10-14 and 15+ (Phase 1 finding: likely one signer each)."""
    return min(number // 5, 3)


def eta_squared(values, groups):
    """Share of variance explained by group means."""
    v = np.asarray(values, np.float64)
    v = v - v.mean()
    g = np.asarray(groups)
    total = (v * v).sum()
    return float(sum((g == k).sum() * v[g == k].mean() ** 2 for k in set(g.tolist())) / total) if total else 0.0


def signer_block_test(x, numbers, signs, seed, permutations=200):
    """Use clip-number blocks as signer groups only if, for every feature column, clip number explains
    at least 25% of the variance and more than every one of the permutations that shuffle clip
    numbers within each sign (p < 1/(permutations+1)), and the 4 blocks explain at least 90% of
    what the full clip number explains. Rule added after the k-means result (post hoc), before
    any fold or model run."""
    numbers, signs = np.asarray(numbers), np.asarray(signs)
    blocks = np.array([signer_block(int(n)) for n in numbers])
    rng = np.random.default_rng(seed)
    out = []
    for f in range(x.shape[1]):
        null = []
        for _ in range(permutations):
            p = numbers.copy()
            for s in set(signs.tolist()):
                m = signs == s
                p[m] = rng.permutation(p[m])
            null.append(eta_squared(x[:, f], p))
        out.append(dict(eta_clip_number=eta_squared(x[:, f], numbers), eta_block=eta_squared(x[:, f], blocks),
                        null_max=max(null)))
    use = all(o['eta_clip_number'] >= .25 and o['eta_clip_number'] > o['null_max']
              and o['eta_block'] >= .9 * o['eta_clip_number'] for o in out)
    return dict(features=out, use_blocks=use)


# ---------- per-clip measurements ----------

def hand_motion(x):
    """Wrist path length per hand ([N,2], left then right) over consecutive rows where that hand is present."""
    out = np.zeros((len(x), 2))
    for h, (col, mask) in enumerate([(0, 150), (63, 151)]):
        xy = x[:, :, col:col + 2].astype(np.float64)
        both = (x[:, 1:, mask] == 1) & (x[:, :-1, mask] == 1)
        out[:, h] = (np.linalg.norm(np.diff(xy, axis=1), axis=2) * both).sum(1)
    return out


def _px(points):
    return points[..., :2] * np.array([W, H])


def body_proportions(frames):
    """Scale-free body measurements in pixels (median over usable frames); None if unusable."""
    rows = []
    for f in frames:
        if f.pose is None or (f.pose[11:17, 3] < .5).any():
            continue
        p = _px(f.pose)
        shoulder = np.linalg.norm(p[11] - p[12])
        upper = (np.linalg.norm(p[11] - p[13]) + np.linalg.norm(p[12] - p[14])) / 2
        fore = (np.linalg.norm(p[13] - p[15]) + np.linalg.norm(p[14] - p[16])) / 2
        row = [fore / upper, (upper + fore) / shoulder, np.nan, np.nan]
        if f.face is not None and len(f.face) >= 455:
            q = _px(f.face)
            face_width = np.linalg.norm(q[234] - q[454])
            row[2] = face_width / shoulder
            row[3] = np.linalg.norm(q[33] - q[263]) / face_width
        rows.append(row)
    if not rows:
        return None
    return np.nanmedian(np.array(rows), axis=0)


def face_gaps(frames):
    """(observations inside the hand interval, of which face missing)."""
    present = [i for i, f in enumerate(frames) if f.left_hand is not None or f.right_hand is not None]
    if not present:
        return 0, 0
    inside = frames[present[0]:present[-1] + 1]
    return len(inside), sum(f.face is None for f in inside)


# ---------- main ----------

def _write_csv(path, rows):
    with open(path, 'x', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _baseline_file(name):
    manifest = json.loads((RETRAINING / 'baseline-manifest.json').read_text())
    path = PHASE4 / name
    entry = next(e for e in manifest['files'] if e['path'] == str(path))
    d.same(d.sha256(path), entry['sha256'], 'baseline ' + name)
    return np.load(path, allow_pickle=False)


def main(out):
    out = Path(out)
    rows = data.campaign_rows()
    data.install_guard(data.test_raw_paths(rows))
    decoy = Path.home() / '.hermes/cache/scratch/retraining-phase1-decoy_test.npy'
    try:
        open(decoy, 'rb')
        raise SystemExit('test guard did not block a test path')
    except PermissionError:
        pass
    out.mkdir(parents=False, exist_ok=False)

    classes = json.loads((data.BUNDLES['hm1588'] / 'data_manifest.json').read_text())['classes']
    labels = [c['label'] for c in classes]
    by_id = {r['clip_id']: r for r in rows}
    fx, fy, fids = data.load('hm153', 'fit')
    vx, vy, vids = data.load('hm153', 'validation')
    result = dict(schema=1, scope='fit (663) and validation (150) clips only; test sealed',
                  counts=dict(fit=len(fids), validation=len(vids)))

    # 1. near-duplicates (hands and arms, hm153)
    nd = near_duplicates(fx, vx)
    pairs = [dict(kind='validation-fit', a=str(vids[i]), b=str(fids[j]), distance=dist,
                  a_label=labels[vy[i]], b_label=labels[fy[j]]) for i, j, dist in nd['flagged']]
    pairs += [dict(kind='fit-fit', a=str(fids[i]), b=str(fids[j]), distance=dist,
                   a_label=labels[fy[i]], b_label=labels[fy[j]]) for i, j, dist in nd['fit_pairs']]
    if pairs:
        _write_csv(out / 'near-duplicates.csv', pairs)
    vf_nn = np.array(nd['val_nearest'])
    result['near_duplicates'] = dict(
        rule='threshold = 1st percentile of each fit clip\'s distance to its nearest other fit clip '
             '(Euclidean over the flattened [30,153] hm153 tensor); flag validation-fit and fit-fit pairs below it',
        threshold=nd['threshold'], validation_fit_pairs=len(nd['flagged']), fit_fit_pairs=len(nd['fit_pairs']),
        cross_label_pairs=sum(p['a_label'] != p['b_label'] for p in pairs),
        validation_nearest_fit_distance=dict(min=float(vf_nn.min()), median=float(np.median(vf_nn))),
        exact_zero_distance_pairs=sum(p['distance'] == 0 for p in pairs),
        decision='keep all; when a flagged clip is scored, its partner is left out of that fold\'s training (Phase 2)')
    groups = [[p['a'], p['b']] for p in pairs]

    # 2. labels
    dup = json.loads(DUPLICATES.read_text())
    affected = sorted(a['clip_id'] for a in dup['affected_known_sources'])
    d.same(affected, sorted(CONFLICTING_DUPLICATES), 'conflicting duplicate clips')
    fit_p, fit_ids = _baseline_file('fit_probabilities.npy'), _baseline_file('fit_ids.npy')
    val_p, val_ids = _baseline_file('validation_probabilities.npy'), _baseline_file('validation_ids.npy')
    misses = []
    for part, p, ids in [('fit', fit_p, fit_ids), ('validation', val_p, val_ids)]:
        for clip, probs in zip(ids.tolist(), p):
            true = by_id[clip]['dense_id']
            if probs.argmax() != true:
                misses.append(dict(partition=part, clip_id=clip, label=labels[true],
                                   predicted=labels[int(probs.argmax())], p_true=float(probs[true])))
    result['labels'] = dict(
        conflicting_duplicates=[dict(clip_id=a['clip_id'], label=a['label'], partition=a['partition'])
                                for a in dup['affected_known_sources']],
        source=dict(path=str(DUPLICATES), sha256=d.sha256(DUPLICATES)),
        baseline_misses_fit_and_validation=misses,
        four_five_confusions=sum({m['label'], m['predicted']} == {'FOUR', 'FIVE'} for m in misses),
        decision='quarantine the 3 conflicting duplicates (view file only). Keep the FIVE clips: '
                 'no evidence separates label noise from genuine FOUR/FIVE overlap; no visual review requested.')
    view = dict(schema=1, name='quarantine-view-v2', quarantined=CONFLICTING_DUPLICATES,
                reason='identical video published under two labels', source=result['labels']['source'],
                note='originals unchanged; clips/23/8.MOV is a test clip and stays sealed (listed by id only)')
    with open(out / 'quarantine-view-v2.json', 'x') as f:
        f.write(json.dumps(view, indent=1) + '\n')

    # 3-5. per-clip measurements from raw observations (fit and validation only)
    open_rows = [r for r in rows if r['partition'] in data.OPEN_PARTITIONS]
    clip_rows, props = [], {}
    for r in open_rows:
        frames = data.raw_frames(r)
        inside, missing = face_gaps(frames)
        prop = body_proportions(frames)
        if prop is not None and np.isfinite(prop).all():
            props[r['clip_id']] = prop
        number = int(re.fullmatch(r'clips/\d+/(\d+)\.MOV', r['clip_id']).group(1))
        clip_rows.append(dict(clip_id=r['clip_id'], partition=r['partition'], label=r['label'],
                              clip_number=number, hand_interval_observations=inside,
                              face_missing_inside=missing))

    # 3. signers
    ids = sorted(props)
    x = np.array([props[i] for i in ids])
    z = (x - x.mean(0)) / x.std(0)
    numbers = [int(re.fullmatch(r'clips/\d+/(\d+)\.MOV', i).group(1)) for i in ids]
    solutions = []
    for k in range(2, 7):
        lab = kmeans(z, k, seed=20260705)
        solutions.append(dict(k=k, silhouette=silhouette(z, lab), nmi_with_clip_number=mutual_information_norm(
            lab.tolist(), numbers), sizes=sorted(Counter(lab.tolist()).values(), reverse=True), labels=lab))
    best = max(solutions, key=lambda s: s['silhouette'])
    clear = best['silhouette'] >= CLEAR_SILHOUETTE
    eta = []
    for f in range(z.shape[1]):
        groups_n = defaultdict(list)
        for n, v in zip(numbers, z[:, f]):
            groups_n[n].append(v)
        between = sum(len(v) * np.mean(v) ** 2 for v in groups_n.values())
        eta.append(float(between / (z[:, f] ** 2).sum()))
    cluster_of = dict(zip(ids, best['labels'].tolist()))
    sign_of = [by_id[i]['dense_id'] for i in ids]
    blocks = signer_block_test(z[:, [2, 3]], numbers, sign_of, seed=20260705)
    block_means = {str(b): [float(v) for v in x[[signer_block(n) == b for n in numbers]].mean(0)] for b in range(4)}
    if blocks['use_blocks']:
        decision = 'signer groups = clip-number blocks 0-4, 5-9, 10-14, 15+ (4 groups; leave-one-signer-out folds)'
    elif clear:
        decision = 'signer groups = clusters'
    else:
        decision = 'signer-unknown: clusters not clear; not used as fold groups'
    for c in clip_rows:
        c.update(zip(['forearm_upperarm', 'arm_shoulder', 'face_shoulder', 'eyes_face'],
                     [float(v) for v in props.get(c['clip_id'], [np.nan] * 4)]))
        c['cluster'] = cluster_of.get(c['clip_id'], '')
        c['signer_block'] = signer_block(c['clip_number'])
    result['signers'] = dict(
        features=['forearm/upper-arm', '(upper-arm+forearm)/shoulder width', 'face width/shoulder width',
                  'outer-eye distance/face width'], clips_measured=len(ids),
        solutions=[{k: v for k, v in s.items() if k != 'labels'} for s in solutions],
        best_k=best['k'], clear=clear, clear_rule=f'best silhouette >= {CLEAR_SILHOUETTE}',
        clip_number_eta_squared=dict(zip(['forearm_upperarm', 'arm_shoulder', 'face_shoulder', 'eyes_face'], eta)),
        clip_number_block_test=dict(blocks, columns=['face_shoulder', 'eyes_face'], rule=signer_block_test.__doc__,
                                    block_feature_means=block_means),
        decision=decision)
    signer_groups = 'clip_number_block' if blocks['use_blocks'] else 'clusters' if clear else None

    # 4-5. handedness and face visibility per sign
    motion = np.concatenate([hand_motion(fx), hand_motion(vx)])
    present = np.concatenate([fx[:, :, 150:152].mean(1), vx[:, :, 150:152].mean(1)])
    yy = np.concatenate([fy, vy])
    per = []
    for k, label in enumerate(labels):
        mine = yy == k
        cr = [c for c in clip_rows if by_id[c['clip_id']]['dense_id'] == k]
        lm, rm = motion[mine].mean(0)
        per.append(dict(dense_id=k, label=label, clips=int(mine.sum()),
                        left_present=float(present[mine, 0].mean()), right_present=float(present[mine, 1].mean()),
                        left_motion=float(lm), right_motion=float(rm),
                        moving_hand='left' if lm > 1.5 * rm else 'right' if rm > 1.5 * lm else 'both',
                        clips_with_face_gap=sum(c['face_missing_inside'] > 0 for c in cr),
                        face_missing_fraction=sum(c['face_missing_inside'] for c in cr)
                        / max(1, sum(c['hand_interval_observations'] for c in cr))))
    result['handedness'] = dict(note='SDK left/right slots, not anatomical; owner: no special handling',
                                moving_hand=dict(Counter(p['moving_hand'] for p in per)))
    result['face_visibility'] = dict(
        clips_with_face_gap=sum(p['clips_with_face_gap'] for p in per),
        signs=[dict(label=p['label'], clips=p['clips_with_face_gap']) for p in per if p['clips_with_face_gap']])

    # 6. shortcut probes: logistic regression fit on fit, scored on validation (hm1588 for the face)
    gx, gy, gids = data.load('hm1588', 'fit')
    hx, hy, hids = data.load('hm1588', 'validation')
    probes = {
        'face_only_time_mean': (gx[:, :, 153:1587].mean(1), gy, hx[:, :, 153:1587].mean(1), hy),
        'first_observation_hands_arms': (fx[:, 0, :], fy, vx[:, 0, :], vy),
        'reference_full_sequence_hands_arms': (fx.reshape(len(fx), -1), fy, vx.reshape(len(vx), -1), vy),
    }
    result['probes'] = {}
    for name, (a, ay, b, by) in probes.items():
        p = predict_logistic(fit_logistic(a, ay, 50), b)
        s = report.summary(by, p, labels)
        result['probes'][name] = dict(validation_accuracy=s['accuracy'], macro_f1=s['macro_f1'], clips=s['clips'])
        for row, ps in zip(per, report.per_sign(by, p, labels)):
            row[f'{name}_recall'] = ps['recall']
    face_acc = result['probes']['face_only_time_mean']['validation_accuracy']
    result['probes']['interpretation'] = dict(
        chance=1 / 50, face_only_above_limit=face_acc > FACE_PROBE_LIMIT,
        note=('Face-only probe uses face landmarks averaged over time. Above 15% means face position/shape '
              'carries sign or signer information the CNN could use as a shortcut; the face-dropout and '
              'face-only checks in Phases 3-4 must measure it. A static first-observation probe close to the '
              'full-sequence probe would mean the start posture alone identifies most clips.'))

    _write_csv(out / 'per-sign.csv', per)
    _write_csv(out / 'clips.csv', clip_rows)
    with open(out / 'fold-groups.json', 'x') as f:
        f.write(json.dumps(dict(schema=1, near_duplicate_groups=groups, signer_groups=signer_groups,
                                signer_group_of={c['clip_id']: c['signer_block'] for c in clip_rows}
                                if signer_groups == 'clip_number_block' else None), indent=1) + '\n')
    with open(out / 'audit.json', 'x') as f:
        f.write(json.dumps(result, indent=1, default=float) + '\n')
    print(json.dumps({k: result[k] for k in ['counts', 'near_duplicates', 'signers', 'probes', 'face_visibility']},
                     indent=1, default=float)[:6000])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
