"""Phase 1 audit helpers (RETRAINING_PLAN.md). Synthetic data only."""
import math
import unittest

import numpy as np

from training.holistic_migration.retraining import audit, data, report


class ReportStatisticsTest(unittest.TestCase):
    def test_wilson_interval_for_small_counts(self):
        low, high = report.wilson(0, 3)
        self.assertEqual(low, 0.0)
        self.assertAlmostEqual(high, 0.5614970317550454, places=12)
        self.assertEqual(report.wilson(3, 3)[1], 1.0)

    def test_exact_mcnemar(self):
        self.assertEqual(report.mcnemar(0, 0), 1.0)
        self.assertAlmostEqual(report.mcnemar(0, 6), 2 * 0.5 ** 6)
        self.assertAlmostEqual(report.mcnemar(6, 0), 2 * 0.5 ** 6)
        self.assertEqual(report.mcnemar(3, 3), 1.0)

    def test_per_sign_rows_and_summary(self):
        y = np.array([0, 0, 1, 1])
        p = np.array([[.9, .1, 0], [.2, .8, 0], [.1, .9, 0], [.6, .4, 0]], np.float32)
        rows = report.per_sign(y, p, ['A', 'B', 'C'])
        self.assertEqual([r['correct'] for r in rows], [1, 1, 0])
        self.assertEqual(rows[0]['most_common_wrong'], 'B')
        self.assertEqual(rows[2]['clips'], 0)
        self.assertEqual(rows[2]['f1'], 0.0)
        s = report.summary(y, p, ['A', 'B', 'C'])
        self.assertEqual(s['correct'], 2)
        self.assertAlmostEqual(s['macro_f1'], (0.5 + 0.5 + 0) / 3)
        self.assertEqual(s['top3_accuracy'], 1.0)
        self.assertEqual(s['signs_below_90_recall'], ['A', 'B'])


class NearDuplicateTest(unittest.TestCase):
    def test_copied_validation_clip_is_flagged_and_novel_one_is_not(self):
        rng = np.random.default_rng(0)
        fit = rng.normal(size=(40, 30, 5)).astype(np.float32)
        val = np.stack([fit[7] + 1e-4, rng.normal(size=(30, 5)).astype(np.float32)])
        result = audit.near_duplicates(fit, val)
        self.assertEqual([(i, j) for i, j, _ in result['flagged']], [(0, 7)])

    def test_threshold_is_percentile_of_fit_nearest_neighbours(self):
        fit = np.array([[[0.]], [[1.]], [[3.]], [[7.]]], np.float32)
        result = audit.near_duplicates(fit, fit[:0], percentile=50)
        # nearest-other-fit distances: 1, 1, 2, 4
        self.assertEqual(result['threshold'], 1.5)


class SignerBlockTest(unittest.TestCase):
    def test_block_of_clip_number(self):
        self.assertEqual([audit.signer_block(n) for n in [0, 4, 5, 9, 10, 14, 15, 19, 20, 21]],
                         [0, 0, 1, 1, 2, 2, 3, 3, 3, 3])

    def test_eta_squared(self):
        v = np.array([1., 1., 3., 3.])
        self.assertAlmostEqual(audit.eta_squared(v, [0, 0, 1, 1]), 1.0)
        self.assertAlmostEqual(audit.eta_squared(v, [0, 1, 0, 1]), 0.0)

    def test_block_rule_accepts_block_structure_and_rejects_noise(self):
        rng = np.random.default_rng(3)
        numbers = np.tile(np.arange(20), 10)
        signs = np.repeat(np.arange(10), 20)
        block_means = np.array([0., 1., -1., 2.])
        x = np.stack([block_means[[audit.signer_block(n) for n in numbers]] + rng.normal(0, .1, 200)] * 2, 1)
        self.assertTrue(audit.signer_block_test(x, numbers, signs, seed=0)['use_blocks'])
        noise = rng.normal(size=(200, 2))
        self.assertFalse(audit.signer_block_test(noise, numbers, signs, seed=0)['use_blocks'])


class ProbeAndClusterTest(unittest.TestCase):
    def test_logistic_probe_learns_separable_classes(self):
        rng = np.random.default_rng(1)
        x = np.concatenate([rng.normal(-3, 1, (30, 4)), rng.normal(3, 1, (30, 4))])
        y = np.repeat([0, 1], 30)
        model = audit.fit_logistic(x, y, classes=2)
        self.assertGreaterEqual((audit.predict_logistic(model, x).argmax(1) == y).mean(), .95)

    def test_two_far_blobs_cluster_clearly(self):
        rng = np.random.default_rng(2)
        x = np.concatenate([rng.normal(0, .1, (20, 3)), rng.normal(5, .1, (20, 3))])
        labels = audit.kmeans(x, 2, seed=0)
        self.assertEqual(len(set(labels[:20])), 1)
        self.assertGreater(audit.silhouette(x, labels), .9)

    def test_hand_motion_ignores_absent_rows(self):
        x = np.zeros((1, 30, 153), np.float32)
        x[0, :, 152] = 1
        x[0, :10, 150] = 1                      # left hand present in 10 rows, moving
        x[0, :10, 0] = np.arange(10) * .1
        left, right = audit.hand_motion(x)[0]
        self.assertAlmostEqual(left, .9, places=5)
        self.assertEqual(right, 0.0)


class GuardTest(unittest.TestCase):
    def test_loader_refuses_test_partition(self):
        with self.assertRaises(ValueError):
            data.load('hm153', 'test')

    def test_guard_blocks_test_paths(self):
        self.assertTrue(data.blocked('/x/X_test.npy', set()))
        self.assertTrue(data.blocked('/x/raw/000002.npz', {'/x/raw/000002.npz'}))
        self.assertFalse(data.blocked('/x/X_fit.npy', set()))


if __name__ == '__main__':
    unittest.main()
