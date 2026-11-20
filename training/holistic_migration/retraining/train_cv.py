"""Phase 2 cross-validation runner: the Phase 4 recipe (face_train) on frozen folds.

Same model, optimizer, batch 32, max 120 epochs, EarlyStopping(val_accuracy, patience 15),
ReduceLROnPlateau(val_loss, patience 6, factor .5), earliest best inner-set accuracy wins, and one
seeded +-5 degree rotation copy per training clip. Differences from face_train, all recorded:
the stopping set is the fold's inner set; the run seed drives initialisation, shuffling and the
rotation angles; per-epoch training-set metrics (logged only, never used) are not computed; the
best weights are kept in memory instead of a candidate file.

usage:
  python -E -B -m training.holistic_migration.retraining.train_cv run OUT FOLDS_FILE FOLDS_SHA256 SEED [FOLD ...]
  python -E -B -m training.holistic_migration.retraining.train_cv summarize OUT FOLDS_FILE SEED [SEED ...]
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

from .. import dataset as d
from .. import augmentation, face_augmentation
from ..evaluate import probabilities
from . import data, report
from .model import build_model

FEATURE = 'hm1588'


def split(doc, fold, eligible):
    """(scored, inner, train) clip ids for one fold, restricted to clips the input can use.
    Near-duplicate partners of a scored clip are left out of training."""
    inner = [c for c in doc['inner'][str(fold)] if c in eligible]
    scored = sorted(c for c, f in doc['fold_of'].items() if f == fold and c in eligible)
    partners = {c for g in doc['groups'] if any(doc['fold_of'][m] == fold for m in g) for c in g}
    train = sorted(c for c, f in doc['fold_of'].items()
                   if f != fold and c in eligible and c not in set(inner) and c not in partners)
    return scored, inner, train


def _predict(model, x):
    p = np.concatenate([model(x[i:i + 32], training=False).numpy() for i in range(0, len(x), 32)])
    return probabilities(p, len(x))


def _loss(y, p):
    return float(-np.log(np.clip(p[np.arange(len(y)), y].astype(np.float64), 1e-300, 1)).mean())


def run_arrays(x, y, ids, scored, inner, train, seed, max_epochs=120):
    import tensorflow as tf
    index = {c: i for i, c in enumerate(ids.tolist())}
    pick = lambda cs: np.array([index[c] for c in cs], dtype=np.int64)
    tx, ty = x[pick(train)], y[pick(train)]
    rotate = face_augmentation.rotate_fit if x.shape[2] == 1588 else augmentation.rotate_fit
    rotated, receipt = rotate(tx, list(train), partition='fit', seed=seed)
    tx, ty = np.concatenate([tx, rotated]), np.concatenate([ty, ty])
    ix, iy = x[pick(inner)], y[pick(inner)]
    sx, sy = x[pick(scored)], y[pick(scored)]
    model = build_model(x.shape[2], seed)
    callbacks = [tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=15),
                 tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', mode='min', patience=6, factor=.5)]
    for cb in callbacks:
        cb.set_model(model)
        cb.set_params(dict(epochs=max_epochs, steps=None, verbose=0))
        cb.on_train_begin({})
    rng = np.random.default_rng(seed)
    best, best_epoch, best_weights, history = -1, None, None, []
    for epoch in range(max_epochs):
        for cb in callbacks:
            cb.on_epoch_begin(epoch, {})
        order = rng.permutation(len(tx))
        for offset in range(0, len(order), 32):
            batch = order[offset:offset + 32]
            result = model.train_on_batch(tx[batch], ty[batch], return_dict=True)
            if not np.isfinite(list(result.values())).all():
                raise ValueError('nonfinite optimizer result')
        p = _predict(model, ix)
        logs = dict(val_accuracy=float((p.argmax(1) == iy).mean()), val_loss=_loss(iy, p))
        history.append(dict(epoch=epoch + 1, steps=int(model.optimizer.iterations.numpy()), **logs))
        if logs['val_accuracy'] > best:
            best, best_epoch, best_weights = logs['val_accuracy'], epoch + 1, model.get_weights()
        for cb in callbacks:
            cb.on_epoch_end(epoch, logs)
        if model.stop_training:
            break
    model.set_weights(best_weights)
    return dict(probabilities=_predict(model, sx), ids=list(scored), labels=sy, history=history,
                best_epoch=best_epoch, best_inner_accuracy=best, augmentation=receipt, model=model)


def _load_all():
    parts = [data.load(FEATURE, p) for p in data.OPEN_PARTITIONS]
    return tuple(np.concatenate([p[i] for p in parts]) for i in range(3))


def run(out, folds_file, folds_sha256, seed, folds):
    d.same(d.sha256(folds_file), folds_sha256, 'frozen folds file')
    doc = json.loads(Path(folds_file).read_text())
    data.install_guard(data.test_raw_paths(data.campaign_rows()))
    x, y, ids = _load_all()
    eligible = set(ids.tolist())
    for fold in folds:
        target = Path(out) / f'fold{fold}-seed{seed}'
        target.mkdir(parents=True, exist_ok=False)
        scored, inner, train = split(doc, fold, eligible)
        config = dict(feature=FEATURE, fold=fold, seed=seed, folds_file=str(folds_file), folds_sha256=folds_sha256,
                      scored=len(scored), inner=len(inner), train=len(train), max_epochs=120, batch=32,
                      threads={k: os.environ.get(k) for k in ['OMP_NUM_THREADS', 'TF_NUM_INTRAOP_THREADS',
                                                                'TF_NUM_INTEROP_THREADS']})
        (target / 'start.json').write_text(json.dumps(config, indent=1) + '\n')
        t0 = time.monotonic()
        r = run_arrays(x, y, ids, scored, inner, train, seed)
        np.save(target / 'probabilities.npy', r['probabilities'])
        np.save(target / 'ids.npy', np.array(r['ids']))
        np.save(target / 'labels.npy', r['labels'])
        r['model'].save(target / 'model.keras')
        (target / 'history.json').write_text(json.dumps(r['history']) + '\n')
        (target / 'augmentation.json').write_text(json.dumps(r['augmentation']) + '\n')
        done = dict(config, best_epoch=r['best_epoch'], best_inner_accuracy=r['best_inner_accuracy'],
                    epochs=len(r['history']), seconds=round(time.monotonic() - t0, 1),
                    scored_correct=int((r['probabilities'].argmax(1) == r['labels']).sum()),
                    files={n: d.sha256(target / n) for n in ['probabilities.npy', 'ids.npy', 'labels.npy',
                                                             'model.keras', 'history.json', 'augmentation.json']})
        with open(target / 'run.json', 'x') as f:
            f.write(json.dumps(done, indent=1) + '\n')
        print(json.dumps({k: done[k] for k in ['fold', 'seed', 'best_epoch', 'epochs', 'seconds', 'scored',
                                               'scored_correct']}), flush=True)


def summarize(out, folds_file, seeds, eligible=None, labels=None):
    """Out-of-fold metrics per seed, per-sign means over seeds, seed SD and the Phase 4 keep threshold.
    Every run must name this folds file and its fold/seed, and each seed must score every eligible clip once."""
    doc = json.loads(Path(folds_file).read_text())
    digest = d.sha256(folds_file)
    if labels is None:
        labels = [c['label'] for c in json.loads((data.BUNDLES[FEATURE] / 'data_manifest.json').read_text())['classes']]
    if eligible is None:
        eligible = set(_load_all()[2].tolist())
    expected = sorted(c for c in doc['fold_of'] if c in eligible)
    per_seed, tables = {}, {}
    for seed in seeds:
        ys, ps, cs = [], [], []
        for fold in range(doc['k']):
            target = Path(out) / f'fold{fold}-seed{seed}'
            run_info = json.loads((target / 'run.json').read_text())
            for key, value in [('fold', fold), ('seed', seed), ('folds_sha256', digest)]:
                d.same(run_info[key], value, f'{target.name} {key}')
            for n, file_digest in run_info['files'].items():
                d.same(d.sha256(target / n), file_digest, f'{target.name} {n}')
            ys.append(np.load(target / 'labels.npy'))
            ps.append(np.load(target / 'probabilities.npy'))
            cs += np.load(target / 'ids.npy').tolist()
        if len(set(cs)) != len(cs) or sorted(cs) != expected:
            raise ValueError(f'seed {seed}: out-of-fold clips are not exactly the {len(expected)} eligible clips')
        y, p = np.concatenate(ys), np.concatenate(ps)
        per_seed[seed] = report.summary(y, p, labels)
        tables[seed] = report.per_sign(y, p, labels)
    f1 = np.array([per_seed[s]['macro_f1'] for s in seeds])
    sd = float(f1.std(ddof=1)) if len(seeds) > 1 else None
    rows = []
    for k, label in enumerate(labels):
        rs = [tables[s][k] for s in seeds]
        rows.append(dict(dense_id=k, label=label, clips=rs[0]['clips'],
                         mean_correct=float(np.mean([r['correct'] for r in rs])),
                         mean_recall=float(np.mean([r['recall'] for r in rs])),
                         wilson_low_pooled=report.wilson(sum(r['correct'] for r in rs), sum(r['clips'] for r in rs))[0],
                         wilson_high_pooled=report.wilson(sum(r['correct'] for r in rs), sum(r['clips'] for r in rs))[1],
                         mean_precision=float(np.mean([r['precision'] for r in rs])),
                         mean_f1=float(np.mean([r['f1'] for r in rs])),
                         mean_top3_recall=float(np.mean([r['top3_correct'] / r['clips'] for r in rs])),
                         most_common_wrong=';'.join(sorted({r['most_common_wrong'] for r in rs if r['most_common_wrong']}))))
    return dict(per_seed={str(s): v for s, v in per_seed.items()}, per_seed_tables={str(s): t for s, t in tables.items()},
                per_sign_mean=rows, macro_f1_mean=float(f1.mean()), macro_f1_seed_sd=sd,
                keep_threshold_macro_f1=max(.01, 2 * sd) if sd is not None else None,
                signs_below_90_mean_recall=[r['label'] for r in rows if r['mean_recall'] < .9])


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'run':
        out, folds_file, digest, seed, *folds = sys.argv[2:]
        run(out, folds_file, digest, int(seed),
            [int(f) for f in folds] or list(range(json.loads(Path(folds_file).read_text())['k'])))
    elif cmd == 'summarize':
        out, folds_file, *seeds = sys.argv[2:]
        print(json.dumps(summarize(out, folds_file, [int(s) for s in seeds]), indent=1))
    else:
        raise SystemExit(__doc__)
