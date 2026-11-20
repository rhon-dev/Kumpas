"""Phase 4 experiments and Phase 5 final fit (RETRAINING_PLAN.md). The training loop is train_cv.run_arrays with
the recipe switches below; with E1 settings it is bit-identical to it (tested).

usage:
  python -E -B -m training.holistic_migration.retraining.train_v2 run OUT FOLDS_FILE FOLDS_SHA256 EXP SEED [FOLD ...]
  python -E -B -m training.holistic_migration.retraining.train_v2 summarize OUT FOLDS_FILE EXP B0CV_DIR SEED [SEED ...]
  python -E -B -m training.holistic_migration.retraining.train_v2 final OUT FOLDS_FILE FOLDS_SHA256 EXP SEED EPOCHS
EXP is E1..E6, or E7:<base> (hm337 with base recipe E3..E6).
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

from .. import augmentation
from .. import dataset as d
from ..evaluate import probabilities
from . import augment_v2, build_v2, data, features_v2, report
from .model import build_model
from .train_cv import _loss, split

EXPERIMENTS = {
    'E1': dict(feature='hm153', copies='rot5', face_dropout=0, label_smoothing=0, l2=0),
    'E2': dict(feature='hm211', copies='rot5', face_dropout=0, label_smoothing=0, l2=0),
    'E3': dict(feature='hm211', copies='rot5', face_dropout=.5, label_smoothing=0, l2=0),
    'E4': dict(feature='hm211', copies='spatial3', face_dropout=.5, label_smoothing=0, l2=0),
    'E5': dict(feature='hm211', copies='spatial_timing3', face_dropout=.5, label_smoothing=0, l2=0),
    'E6': dict(feature='hm211', copies='spatial_timing3', face_dropout=.5, label_smoothing=.1, l2=1e-4),
}
BUNDLES = data.DATA / 'evidence/retraining-v1/bundles/v1'


def recipe(name):
    if name.startswith('E7:'):
        base = name.split(':')[1]
        if base not in ('E3', 'E4', 'E5', 'E6'):
            raise ValueError('E7 base must be one of E3-E6')
        return dict(EXPERIMENTS[base], feature='hm337')
    return EXPERIMENTS[name]


def build(width, seed, l2=0, label_smoothing=0):
    """model.build_model, optionally with L2 on every kernel and label smoothing (same layers and init)."""
    if not l2 and not label_smoothing:
        return build_model(width, seed)
    import tensorflow as tf
    tf.keras.utils.set_random_seed(seed)
    layers, reg = tf.keras.layers, (tf.keras.regularizers.l2(l2) if l2 else None)
    model = tf.keras.Sequential(name=f'w{width}_cnnlstm_c64-128_l128-64')
    model.add(layers.Input((30, width), dtype='float32'))
    for filters in [64, 128]:
        model.add(layers.Conv1D(filters, 3, padding='same', activation='relu', kernel_regularizer=reg))
        model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling1D(2))
    for units, sequences in [(128, True), (64, False)]:
        model.add(layers.LSTM(units, return_sequences=sequences, kernel_regularizer=reg, recurrent_regularizer=reg))
        model.add(layers.Dropout(.4))
    model.add(layers.Dense(128, activation='relu', kernel_regularizer=reg))
    model.add(layers.Dropout(.4))
    model.add(layers.Dense(50, activation='softmax', kernel_regularizer=reg))
    model.compile(tf.keras.optimizers.Adam(.001), tf.keras.losses.CategoricalCrossentropy(label_smoothing=label_smoothing),
                  metrics=['accuracy'])
    return model


def face_views(x):
    """(face zeroed, face only) copies: face block and mask zeroed; or hands, arms, hand masks and local channels zeroed."""
    zero, only = x.copy(), x.copy()
    zero[..., 153:211] = 0
    only[..., :152] = 0
    only[..., 211:] = 0
    return zero, only


def _predict(model, x):
    p = np.concatenate([model(x[i:i + 32], training=False).numpy() for i in range(0, len(x), 32)])
    return probabilities(p, len(x))


def _copies(r, tx, train, seed, observations):
    if r['copies'] == 'rot5':
        if r['feature'] == 'hm153':
            return augmentation.rotate_fit(tx, list(train), partition='fit', seed=seed)
        return augment_v2.rotate5(tx, train, seed)
    rng = np.random.default_rng([seed, 1])
    if r['copies'] == 'spatial3':
        copies = [augment_v2.spatial(tx, rng) for _ in range(3)]
    elif r['copies'] == 'spatial_timing3':
        copies = [augment_v2.spatial(np.stack([augment_v2.timing(*observations[c], rng) for c in train]), rng)
                  for _ in range(3)]
    else:
        raise ValueError(r['copies'])
    return np.concatenate(copies), dict(seed=seed, policy=r['copies'], copies_per_clip=3, source_ids=list(train),
                                        real_observations_added=0, partition='fit')


def _fit(model, tx, ty, seed, r, epochs, stopping=None):
    """train_cv's epoch loop. stopping=(ix, iy) uses the inner set; None trains a fixed number of epochs with the
    plateau schedule on the epoch's mean training loss (Phase 5 final fit)."""
    import tensorflow as tf
    callbacks = [tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', mode='min', patience=6, factor=.5)]
    if stopping is not None:
        callbacks.insert(0, tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=15))
    for cb in callbacks:
        cb.set_model(model)
        cb.set_params(dict(epochs=epochs, steps=None, verbose=0))
        cb.on_train_begin({})
    rng, drop_rng = np.random.default_rng(seed), np.random.default_rng([seed, 2])
    smooth = bool(r['label_smoothing'] or r['l2'])
    convert = r['feature'] == 'hm337'
    best, best_epoch, best_weights, history = -1, None, None, []
    for epoch in range(epochs):
        for cb in callbacks:
            cb.on_epoch_begin(epoch, {})
        order = rng.permutation(len(tx))
        losses = []
        for offset in range(0, len(order), 32):
            batch = order[offset:offset + 32]
            bx = tx[batch]
            if r['face_dropout']:
                bx = augment_v2.face_dropout(bx, drop_rng, r['face_dropout'])
            if convert:
                bx = features_v2.add_hand_local(bx)
            by = np.eye(50, dtype=np.float32)[ty[batch]] if smooth else ty[batch]
            result = model.train_on_batch(bx, by, return_dict=True)
            if not np.isfinite(list(result.values())).all():
                raise ValueError('nonfinite optimizer result')
            losses.append(result['loss'])
        if stopping is not None:
            p = _predict(model, stopping[0])
            logs = dict(val_accuracy=float((p.argmax(1) == stopping[1]).mean()), val_loss=_loss(stopping[1], p))
        else:
            logs = dict(val_loss=float(np.mean(losses)))  # no stopping set: plateau schedule on mean training loss
        history.append(dict(epoch=epoch + 1, steps=int(model.optimizer.iterations.numpy()),
                            learning_rate=float(model.optimizer.learning_rate.numpy()), **logs))
        if stopping is not None and logs['val_accuracy'] > best:
            best, best_epoch, best_weights = logs['val_accuracy'], epoch + 1, model.get_weights()
        for cb in callbacks:
            cb.on_epoch_end(epoch, logs)
        if model.stop_training:
            break
    if best_weights is not None:
        model.set_weights(best_weights)
    return history, best_epoch, best


def run_arrays(x, y, ids, scored, inner, train, seed, r, observations=None, max_epochs=120):
    index = {c: i for i, c in enumerate(ids.tolist())}
    pick = lambda cs: np.array([index[c] for c in cs], dtype=np.int64)
    tx, ty = x[pick(train)], y[pick(train)]
    copies, receipt = _copies(r, tx, train, seed, observations)
    tx, ty = np.concatenate([tx, copies]), np.concatenate([ty] * (1 + len(copies) // len(train)))
    final = (lambda a: features_v2.add_hand_local(a)) if r['feature'] == 'hm337' else (lambda a: a)
    ix, iy = final(x[pick(inner)]), y[pick(inner)]
    sx, sy = final(x[pick(scored)]), y[pick(scored)]
    model = build(final(x[:1]).shape[2], seed, r['l2'], r['label_smoothing'])
    history, best_epoch, best = _fit(model, tx, ty, seed, r, max_epochs, (ix, iy))
    out = dict(probabilities=_predict(model, sx), ids=list(scored), labels=sy, history=history, best_epoch=best_epoch,
               best_inner_accuracy=best, augmentation=receipt, model=model, train_sequences=len(tx))
    if r['feature'] != 'hm153':
        zero, only = face_views(sx)
        out.update(face_zero_probabilities=_predict(model, zero), face_only_probabilities=_predict(model, only))
    return out


def load_open(feature):
    """Fit+validation (X, y, ids, observations or None) of a feature's base tensor (hm337 trains from hm211)."""
    if feature == 'hm153':
        parts = [data.load('hm153', p) for p in data.OPEN_PARTITIONS]
        return (*(np.concatenate([p[i] for p in parts]) for i in range(3)), None)
    parts = [build_v2.load(BUNDLES / 'hm211', p, observations=True) for p in data.OPEN_PARTITIONS]
    return (*(np.concatenate([p[i] for p in parts]) for i in range(3)), {**parts[0][3], **parts[1][3]})


def provenance(feature):
    """Bundle manifest and code digests bound into every run receipt."""
    here = Path(__file__).parent
    code = {p.name: d.sha256(p) for p in sorted(here.glob('*.py')) + [here.parent / n for n in
            ('features.py', 'sequence.py', 'dataset.py', 'augmentation.py', 'evaluate.py')]}
    bundle = (data.BUNDLES['hm153'] / 'data_manifest.json' if feature == 'hm153' else BUNDLES / 'hm211' / 'manifest.json')
    return dict(bundle_manifest=str(bundle), bundle_manifest_sha256=d.sha256(bundle), code_sha256=code)


def _save_run(target, r, config, t0):
    names = ['probabilities.npy', 'ids.npy', 'labels.npy', 'model.keras', 'history.json', 'augmentation.json']
    np.save(target / 'probabilities.npy', r['probabilities'])
    np.save(target / 'ids.npy', np.array(r['ids']))
    np.save(target / 'labels.npy', r['labels'])
    for key in ['face_zero_probabilities', 'face_only_probabilities']:
        if key in r:
            np.save(target / f'{key}.npy', r[key])
            names.append(f'{key}.npy')
    r['model'].save(target / 'model.keras')
    (target / 'history.json').write_text(json.dumps(r['history']) + '\n')
    (target / 'augmentation.json').write_text(json.dumps(r['augmentation']) + '\n')
    done = dict(config, best_epoch=r['best_epoch'], best_inner_accuracy=r['best_inner_accuracy'],
                epochs=len(r['history']), seconds=round(time.monotonic() - t0, 1), train_sequences=r['train_sequences'],
                scored_correct=int((r['probabilities'].argmax(1) == r['labels']).sum()) if len(r['labels']) else None,
                files={n: d.sha256(target / n) for n in names})
    with open(target / 'run.json', 'x') as f:
        f.write(json.dumps(done, indent=1) + '\n')
    return done


def run(out, folds_file, folds_sha256, exp, seed, folds):
    d.same(d.sha256(folds_file), folds_sha256, 'frozen folds file')
    doc = json.loads(Path(folds_file).read_text())
    data.install_guard(data.test_raw_paths(data.campaign_rows()))
    r = recipe(exp)
    x, y, ids, obs = load_open(r['feature'])
    eligible = set(ids.tolist())
    for fold in folds:
        target = Path(out) / f'fold{fold}-seed{seed}'
        target.mkdir(parents=True, exist_ok=False)
        scored, inner, train = split(doc, fold, eligible)
        config = dict(experiment=exp, recipe=r, fold=fold, seed=seed, provenance=provenance(r['feature']), folds_file=str(folds_file), folds_sha256=folds_sha256,
                      scored=len(scored), inner=len(inner), train=len(train), max_epochs=120, batch=32,
                      threads={k: os.environ.get(k) for k in ['OMP_NUM_THREADS', 'TF_NUM_INTRAOP_THREADS']})
        (target / 'start.json').write_text(json.dumps(config, indent=1) + '\n')
        t0 = time.monotonic()
        done = _save_run(target, run_arrays(x, y, ids, scored, inner, train, seed, r, obs), config, t0)
        print(json.dumps({k: done[k] for k in ['experiment', 'fold', 'seed', 'best_epoch', 'epochs', 'seconds',
                                               'scored', 'scored_correct']}), flush=True)


def final(out, folds_file, folds_sha256, exp, seed, epochs):
    """Phase 5: every non-quarantined official train clip the input can use, fixed epochs, no stopping set."""
    d.same(d.sha256(folds_file), folds_sha256, 'frozen folds file')
    doc = json.loads(Path(folds_file).read_text())
    data.install_guard(data.test_raw_paths(data.campaign_rows()))
    r = recipe(exp)
    x, y, ids, obs = load_open(r['feature'])
    train = sorted(c for c in doc['fold_of'] if c in set(ids.tolist()))
    if set(train) & set(doc['quarantined']) or len(train) != len(set(doc['fold_of']) & set(ids.tolist())):
        raise ValueError('final training set must be the eligible non-quarantined fold clips')
    target = Path(out)
    target.mkdir(parents=True, exist_ok=False)
    config = dict(experiment=exp, recipe=r, seed=seed, epochs=epochs, folds_sha256=folds_sha256, train=len(train),
                  quarantined_left_out=doc['quarantined'], batch=32, provenance=provenance(r['feature']))
    (target / 'start.json').write_text(json.dumps(config, indent=1) + '\n')
    t0 = time.monotonic()
    index = {c: i for i, c in enumerate(ids.tolist())}
    pick = np.array([index[c] for c in train])
    tx, ty = x[pick], y[pick]
    copies, receipt = _copies(r, tx, train, seed, obs)
    tx, ty = np.concatenate([tx, copies]), np.concatenate([ty] * (1 + len(copies) // len(train)))
    width = 337 if r['feature'] == 'hm337' else x.shape[2]
    model = build(width, seed, r['l2'], r['label_smoothing'])
    history, _, _ = _fit(model, tx, ty, seed, r, epochs)
    done = _save_run(target, dict(probabilities=np.zeros((0, 50), np.float32), ids=[], labels=np.zeros(0, np.int64),
                                  history=history, best_epoch=None, best_inner_accuracy=None, augmentation=receipt,
                                  model=model, train_sequences=len(tx)), config, t0)
    print(json.dumps({k: done[k] for k in ['experiment', 'epochs', 'seconds', 'train_sequences']}), flush=True)


# ---------- summaries and the section 5 decision rule ----------

def oof(out, doc, seeds, expected, check=()):
    """{seed: (ids, labels, probs, face_zero or None, face_only or None)} with every file hash and clip set checked."""
    digest_folds = doc.get('_sha256')
    res = {}
    for seed in seeds:
        parts = []
        for fold in range(doc['k']):
            target = Path(out) / f'fold{fold}-seed{seed}'
            info = json.loads((target / 'run.json').read_text())
            for key, value in [('fold', fold), ('seed', seed), *check] + ([('folds_sha256', digest_folds)] if digest_folds else []):
                d.same(info[key], value, f'{target.name} {key}')
            for n, h in info['files'].items():
                d.same(d.sha256(target / n), h, f'{target.name} {n}')
            load = lambda n: np.load(target / n) if (target / n).exists() else None
            parts.append([np.load(target / 'ids.npy').tolist(), load('labels.npy'), load('probabilities.npy'),
                          load('face_zero_probabilities.npy'), load('face_only_probabilities.npy')])
        cs = sum((p[0] for p in parts), [])
        if len(set(cs)) != len(cs) or sorted(cs) != sorted(expected):
            raise ValueError(f'{out} seed {seed}: out-of-fold clips are not the {len(expected)} eligible clips')
        cat = lambda i: None if parts[0][i] is None else np.concatenate([p[i] for p in parts])
        res[seed] = (np.array(cs), cat(1), cat(2), cat(3), cat(4))
    return res


def _subset(o, clips):
    ids, *arrays = o
    keep = np.isin(ids, sorted(clips))
    order = np.argsort(ids[keep], kind='stable')
    return (ids[keep][order], *[None if a is None else a[keep][order] for a in arrays])


def summarize(out, folds_file, exp, b0cv, seeds, labels):
    doc = dict(json.loads(Path(folds_file).read_text()), _sha256=d.sha256(folds_file))
    r = recipe(exp)
    ids = load_open(r['feature'])[2].tolist()
    expected = [c for c in doc['fold_of'] if c in set(ids)]
    base_ids = [c for c in doc['fold_of'] if c in set(data.load('hm1588', 'fit')[2].tolist() + data.load('hm1588', 'validation')[2].tolist())]
    data.install_guard(data.test_raw_paths(data.campaign_rows()))
    cand = oof(out, doc, seeds, expected, [('experiment', exp)])
    base = oof(b0cv, doc, seeds, base_ids, [('feature', 'hm1588')])
    common = set(base_ids) & set(expected)
    recovered = sorted(set(expected) - set(base_ids))
    per_seed, tables, mcnemar, reliance, face_only, zero_tables = {}, {}, {}, [], [], {}
    for s in seeds:
        c, b = _subset(cand[s], common), _subset(base[s], common)
        if not ((c[0] == b[0]).all() and (c[1] == b[1]).all()):
            raise ValueError('candidate and B0-CV common clips or labels differ')
        per_seed[s] = dict(common=report.summary(c[1], c[2], labels),
                           all=report.summary(cand[s][1], cand[s][2], labels))
        if recovered:
            rc = _subset(cand[s], recovered)
            per_seed[s]['recovered'] = dict(clips=len(recovered), correct=int((rc[2].argmax(1) == rc[1]).sum()))
        tables[s] = report.per_sign(c[1], c[2], labels)
        right_c, right_b = c[2].argmax(1) == c[1], b[2].argmax(1) == b[1]
        bb, cc = int((right_c & ~right_b).sum()), int((~right_c & right_b).sum())
        mcnemar[s] = dict(candidate_only=bb, baseline_only=cc, p=report.mcnemar(bb, cc))
        if c[3] is not None:
            reliance.append(per_seed[s]['common']['macro_f1'] - report.summary(c[1], c[3], labels)['macro_f1'])
            face_only.append(float((c[4].argmax(1) == c[1]).mean()))
            zero_tables[s] = report.per_sign(c[1], c[3], labels)
    base_tables = {s: report.per_sign(*_subset(base[s], common)[1:3], labels) for s in seeds}
    mean = lambda t, k, key: float(np.mean([t[s][k][key] for s in seeds]))
    rows = [dict(label=labels[k], clips=tables[seeds[0]][k]['clips'], mean_correct=mean(tables, k, 'correct'),
                 b0cv_mean_correct=mean(base_tables, k, 'correct'), mean_recall=mean(tables, k, 'recall'),
                 b0cv_mean_recall=mean(base_tables, k, 'recall'), mean_f1=mean(tables, k, 'f1'),
                 mean_top3_recall=float(np.mean([tables[s][k]['top3_correct'] / tables[s][k]['clips'] for s in seeds])),
                 pooled_wilson=report.wilson(sum(tables[s][k]['correct'] for s in seeds),
                                             sum(tables[s][k]['clips'] for s in seeds)),
                 most_common_wrong=';'.join(sorted({tables[s][k]['most_common_wrong'] for s in seeds} - {''})))
            for k in range(len(labels))]
    f1 = [per_seed[s]['common']['macro_f1'] for s in seeds]
    result = dict(experiment=exp, recipe=r, seeds=seeds, common_clips=len(common), recovered_clips=recovered,
                  per_seed={str(s): v for s, v in per_seed.items()}, mcnemar={str(s): v for s, v in mcnemar.items()},
                  macro_f1_mean=float(np.mean(f1)), macro_f1_seed_sd=float(np.std(f1, ddof=1)),
                  signs_below_90=sum(row['mean_recall'] < .9 for row in rows),
                  per_sign_mean_correct=[row['mean_correct'] for row in rows],
                  face_reliance=float(np.mean(reliance)) if reliance else None,
                  face_only_accuracy=float(np.mean(face_only)) if face_only else None,
                  best_epochs=[json.loads((Path(out) / f'fold{f}-seed{s}' / 'run.json').read_text())['best_epoch']
                               for s in seeds for f in range(doc['k'])],
                  face_dependent_signs=[labels[k] for k in range(len(labels)) if zero_tables and
                                        mean(tables, k, 'recall') - mean(zero_tables, k, 'recall') > .2],
                  b0cv=dict(macro_f1_mean=float(np.mean([report.summary(*_subset(base[s], common)[1:3], labels)['macro_f1']
                                                         for s in seeds])),
                            signs_below_90=sum(row['b0cv_mean_recall'] < .9 for row in rows),
                            per_sign_mean_correct=[row['b0cv_mean_correct'] for row in rows]),
                  per_sign=rows)
    return result


def keep(cand, base, threshold):
    """Section 5 rule against B0-CV (same common clips, folds and seeds)."""
    loss = [c - b for c, b in zip(cand['per_sign_mean_correct'], base['per_sign_mean_correct'])]
    rules = dict(
        macro_f1_gain=cand['macro_f1_mean'] - base['macro_f1_mean'] >= threshold,
        no_sign_loses_more_than_1=min(loss) >= -1 - 1e-9,
        signs_below_90_not_more=cand['signs_below_90'] <= base['signs_below_90'],
        face_reliance_at_most_5=cand['face_reliance'] is None or cand['face_reliance'] <= .05,
        face_only_at_most_15=cand['face_only_accuracy'] is None or cand['face_only_accuracy'] <= .15)
    return dict(rules, keep=all(rules.values()), worst_sign_change=min(loss),
                face_only_investigation_needed=not rules['face_only_at_most_15'],
                face_dependent_signs=cand.get('face_dependent_signs', []))


def select(results, threshold):
    """Best passing experiment, except the simplest (earliest) passing one within the noise threshold wins."""
    passing = {k: v for k, v in results.items() if v['keep']}
    if not passing:
        return None
    best = max(v['macro_f1_mean'] for v in passing.values())
    order = sorted(passing, key=lambda k: int(k[1:].split(':')[0]))
    return next(k for k in order if passing[k]['macro_f1_mean'] >= best - threshold)


def decide(summaries, threshold):
    """Apply keep() to every summary (each against the B0-CV block on its own common clips), select, and give the
    E7 base (best macro-F1 of E3-E6) and the Phase 5 epoch count (median best epoch of the selected recipe)."""
    by = {s['experiment']: s for s in summaries}
    results = {e: dict(keep(s, s['b0cv'], threshold), macro_f1_mean=s['macro_f1_mean'],
                       gain=s['macro_f1_mean'] - s['b0cv']['macro_f1_mean']) for e, s in by.items()}
    chosen = select(results, threshold)
    pool = [e for e in by if e in ('E3', 'E4', 'E5', 'E6')]
    return dict(threshold=threshold, results=results, selected=chosen,
                e7_base=max(pool, key=lambda e: by[e]['macro_f1_mean']) if pool else None,
                final_epochs=int(np.median(by[chosen]['best_epochs'])) if chosen else None)


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'run':
        out, folds_file, digest, exp, seed, *folds = args
        run(out, folds_file, digest, exp, int(seed),
            [int(f) for f in folds] or list(range(json.loads(Path(folds_file).read_text())['k'])))
    elif cmd == 'summarize':
        out, folds_file, exp, b0cv, *seeds = args
        labels = [c['label'] for c in json.loads((data.BUNDLES['hm1588'] / 'data_manifest.json').read_text())['classes']]
        print(json.dumps(summarize(out, folds_file, exp, b0cv, [int(s) for s in seeds], labels), indent=1))
    elif cmd == 'decide':
        threshold, *files = args
        print(json.dumps(decide([json.loads(Path(f).read_text()) for f in files], float(threshold)), indent=1))
    elif cmd == 'final':
        out, folds_file, digest, exp, seed, epochs = args
        final(out, folds_file, digest, exp, int(seed), int(epochs))
    else:
        raise SystemExit(__doc__)
