"""Phase 2 folds, model and cross-validation runner (RETRAINING_PLAN.md). Synthetic data only."""
import unittest

import numpy as np

from training.holistic_migration.retraining import folds, train_cv


def synthetic_rows(signs=3, per_sign=16):
    rows = []
    for k in range(signs):
        for n in range(per_sign):
            rows.append(dict(clip_id=f'clips/{k}/{n}.MOV', dense_id=k,
                             partition='validation' if n < 3 else 'fit'))
    return rows


class FoldTest(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_rows()
        self.quarantine = ['clips/0/5.MOV']
        self.groups = [['clips/1/2.MOV', 'clips/1/9.MOV'], ['clips/2/0.MOV', 'clips/1/4.MOV']]
        # sign 2 has 6 clips that the strict input cannot use
        self.strict = {r['clip_id'] for r in self.rows} - {f'clips/2/{n}.MOV' for n in range(6)}
        self.doc = folds.make_folds(self.rows, self.quarantine, self.groups, self.strict)

    def test_every_clip_once_except_quarantined(self):
        expected = {r['clip_id'] for r in self.rows} - set(self.quarantine)
        self.assertEqual(set(self.doc['fold_of']), expected)

    def test_groups_stay_together(self):
        for group in self.groups:
            self.assertEqual(len({self.doc['fold_of'][c] for c in group}), 1)

    def test_every_sign_has_strict_eligible_clips_in_every_fold(self):
        for k in range(3):
            for f in range(5):
                n = sum(1 for c, fold in self.doc['fold_of'].items()
                        if fold == f and c.startswith(f'clips/{k}/') and c in self.strict)
                self.assertGreaterEqual(n, 1, (k, f))

    def test_inner_stopping_set_is_one_strict_clip_per_sign_outside_the_scored_fold(self):
        grouped = {c for g in self.groups for c in g}
        for f in range(5):
            inner = self.doc['inner'][str(f)]
            self.assertEqual(sorted(int(c.split('/')[1]) for c in inner), [0, 1, 2])
            for c in inner:
                self.assertNotEqual(self.doc['fold_of'][c], f)
                self.assertIn(c, self.strict)
                self.assertNotIn(c, grouped)

    def test_validator_accepts_and_is_deterministic(self):
        folds.validate(self.doc, self.rows, self.quarantine, self.groups, self.strict)
        self.assertEqual(self.doc, folds.make_folds(self.rows, self.quarantine, self.groups, self.strict))

    def test_validator_rejects_a_split_group(self):
        bad = dict(self.doc, fold_of=dict(self.doc['fold_of']))
        bad['fold_of']['clips/1/9.MOV'] = (bad['fold_of']['clips/1/2.MOV'] + 1) % 5
        with self.assertRaises(ValueError):
            folds.validate(bad, self.rows, self.quarantine, self.groups, self.strict)


class SignerFoldTest(unittest.TestCase):
    def test_leave_one_signer_out_with_partner_exclusion(self):
        rows = synthetic_rows(per_sign=20)
        strict = {r['clip_id'] for r in rows}
        signer_of = {r['clip_id']: min(int(r['clip_id'].split('/')[2][:-4]) // 5, 3) for r in rows}
        groups = [['clips/0/3.MOV', 'clips/0/7.MOV']]          # crosses signers 0 and 1
        doc = folds.make_folds(rows, [], groups, strict, signer_of=signer_of)
        self.assertEqual(doc['k'], 4)
        folds.validate(doc, rows, [], groups, strict, signer_of=signer_of)
        scored, inner, train = train_cv.split(doc, 0, strict)
        self.assertIn('clips/0/3.MOV', scored)
        self.assertNotIn('clips/0/7.MOV', train)
        self.assertTrue(all(signer_of[c] != 0 for c in train + inner))

    def test_signer_mode_accepts_a_strict_gap_but_not_a_missing_sign(self):
        rows = synthetic_rows(per_sign=20)
        signer_of = {r['clip_id']: min(int(r['clip_id'].split('/')[2][:-4]) // 5, 3) for r in rows}
        strict = {r['clip_id'] for r in rows} - {f'clips/1/{n}.MOV' for n in range(15, 20)}
        doc = folds.make_folds(rows, [], [], strict, signer_of=signer_of)
        folds.validate(doc, rows, [], [], strict, signer_of=signer_of)
        missing = [f'clips/1/{n}.MOV' for n in range(15, 20)]
        with self.assertRaises(ValueError):
            folds.validate(doc, rows, missing, [], strict, signer_of=signer_of)

    def test_validator_rejects_wrong_signer_fold(self):
        rows = synthetic_rows(per_sign=20)
        strict = {r['clip_id'] for r in rows}
        signer_of = {r['clip_id']: min(int(r['clip_id'].split('/')[2][:-4]) // 5, 3) for r in rows}
        doc = folds.make_folds(rows, [], [], strict, signer_of=signer_of)
        doc['fold_of']['clips/1/0.MOV'] = 2
        with self.assertRaises(ValueError):
            folds.validate(doc, rows, [], [], strict, signer_of=signer_of)


class SplitTest(unittest.TestCase):
    def test_scored_and_inner_clips_never_train(self):
        rows = synthetic_rows()
        strict = {r['clip_id'] for r in rows}
        doc = folds.make_folds(rows, [], [], strict)
        for f in range(5):
            scored, inner, train = train_cv.split(doc, f, strict)
            self.assertFalse(set(train) & (set(scored) | set(inner)))
            self.assertEqual(set(scored) | set(inner) | set(train), strict)


class SummarizeTest(unittest.TestCase):
    def _runs(self, root, doc, eligible, seed, digest, drop=None):
        import json
        from training.holistic_migration import dataset as d
        for fold in range(doc['k']):
            scored, _, _ = train_cv.split(doc, fold, eligible)
            if drop in scored:
                scored.remove(drop)
            t = root / f'fold{fold}-seed{seed}'
            t.mkdir()
            y = np.array([int(c.split('/')[1]) for c in scored])
            np.save(t / 'probabilities.npy', np.eye(50, dtype=np.float32)[y])
            np.save(t / 'ids.npy', np.array(scored))
            np.save(t / 'labels.npy', y)
            files = {n: d.sha256(t / n) for n in ['probabilities.npy', 'ids.npy', 'labels.npy']}
            (t / 'run.json').write_text(json.dumps(dict(fold=fold, seed=seed, folds_sha256=digest, files=files)))

    def test_summarize_checks_completeness_and_identity(self):
        import json
        import tempfile
        from pathlib import Path
        from training.holistic_migration import dataset as d
        rows = synthetic_rows(signs=50, per_sign=20)
        signer_of = {r['clip_id']: min(int(r['clip_id'].split('/')[2][:-4]) // 5, 3) for r in rows}
        eligible = {r['clip_id'] for r in rows}
        doc = folds.make_folds(rows, [], [], eligible, signer_of=signer_of)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'folds.json').write_text(json.dumps(doc))
            digest = d.sha256(root / 'folds.json')
            (root / 'ok').mkdir()
            self._runs(root / 'ok', doc, eligible, 1, digest)
            self._runs(root / 'ok', doc, eligible, 2, digest)
            s = train_cv.summarize(root / 'ok', root / 'folds.json', [1, 2], eligible=eligible,
                                   labels=[str(i) for i in range(50)])
            self.assertEqual(s['macro_f1_mean'], 1.0)
            self.assertEqual(s['keep_threshold_macro_f1'], .01)
            (root / 'missing').mkdir()
            self._runs(root / 'missing', doc, eligible, 1, digest, drop='clips/3/0.MOV')
            with self.assertRaises(ValueError):
                train_cv.summarize(root / 'missing', root / 'folds.json', [1], eligible=eligible,
                                   labels=[str(i) for i in range(50)])
            (root / 'wrong').mkdir()
            self._runs(root / 'wrong', doc, eligible, 1, '0' * 64)
            with self.assertRaises(ValueError):
                train_cv.summarize(root / 'wrong', root / 'folds.json', [1], eligible=eligible,
                                   labels=[str(i) for i in range(50)])


class ModelTest(unittest.TestCase):
    def test_width_1588_reproduces_phase4_layers_and_parameters(self):
        from training.holistic_migration import face_train
        from training.holistic_migration.retraining import model
        ours, theirs = model.build_model(1588, seed=20260705), face_train.build_model()
        self.assertEqual(ours.count_params(), 526194)
        strip = lambda m: [dict(l.get_config(), name=None) for l in m.layers]
        self.assertEqual(strip(ours), strip(theirs))
        self.assertEqual(ours.optimizer.get_config()['learning_rate'], theirs.optimizer.get_config()['learning_rate'])


class RunnerTest(unittest.TestCase):
    def test_synthetic_run_trains_only_on_training_clips(self):
        rng = np.random.default_rng(0)
        n, width = 60, 153
        x = np.zeros((n, 30, width), np.float32)
        x[:, :, 126:150] = 0
        x[:, :, 152] = 1
        # usable shoulders: left (1/2,0), right (-1/2,0), visibility 1
        x[:, :, 126], x[:, :, 129], x[:, :, 130], x[:, :, 133] = .5, 1, -.5, 1
        x[:, :, 150] = 1
        x[:, :, 3:63] = rng.normal(size=(n, 30, 60)).astype(np.float32)
        x[:, :, 2:63:3] = 0
        y = np.arange(n) % 50
        ids = np.array([f'c{i}' for i in range(n)])
        scored, inner, train = ids[:10].tolist(), ids[10:12].tolist(), ids[12:].tolist()
        out = train_cv.run_arrays(x, y, ids, scored, inner, train, seed=1, max_epochs=2)
        self.assertEqual(out['augmentation']['source_ids'], train)
        self.assertEqual(out['probabilities'].shape, (10, 50))
        self.assertEqual(out['ids'], scored)
        self.assertLessEqual(len(out['history']), 2)


if __name__ == '__main__':
    unittest.main()
