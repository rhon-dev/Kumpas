"""Phases 3-4 (RETRAINING_PLAN.md): hm211/hm337 features, v2 augmentation, v2 runner. Synthetic data only."""
import unittest

import numpy as np

from training.holistic_migration import face_features, sequence
from training.holistic_migration.features import RawFrame, pack_frame
from training.holistic_migration.retraining import augment_v2, features_v2, train_cv, train_v2


def frame(t, rng, face=True, left=True, right=True, pose=True):
    p = np.zeros((33, 4))
    p[:, :3] = rng.uniform(.2, .8, (33, 3))
    p[:, 3] = 1
    p[11, :2], p[12, :2] = [.6, .5], [.4, .5]
    hand = lambda: rng.uniform(.3, .7, (21, 3))
    return RawFrame(t, p if pose else None, hand() if left else None, hand() if right else None,
                    rng.uniform(.3, .7, (478, 3)) if face else None)


def clip(rng, n=20, face_gap=(), hands=range(3, 17)):
    return [frame(67 * i, rng, face=i not in face_gap, left=i in hands, right=i in hands) for i in range(n)]


class Hm211Test(unittest.TestCase):
    def test_layout_is_hm153_then_hm1588_anchor_columns_then_mask(self):
        f = frame(0, np.random.default_rng(1))
        row, full = features_v2.pack_frame(f), face_features.pack_frame(f)
        self.assertEqual(row.dtype, np.float32)
        self.assertEqual(row.shape, (211,))
        np.testing.assert_array_equal(row[:153].view(np.uint32), pack_frame(f).view(np.uint32))
        cols = np.array([153 + 3 * a + c for a in features_v2.ANCHORS for c in range(3)])
        np.testing.assert_array_equal(row[153:210].view(np.uint32), full[cols].view(np.uint32))
        self.assertEqual(row[210], 1)

    def test_anchor_list_is_the_plan_list(self):
        self.assertEqual(features_v2.ANCHORS, (10, 1, 152, 234, 454, 33, 133, 362, 263,
                                               70, 105, 107, 336, 334, 300, 61, 291, 13, 14))

    def test_missing_face_zeroes_block_and_mask_only(self):
        f = frame(0, np.random.default_rng(2), face=False)
        row = features_v2.pack_frame(f)
        self.assertTrue((row[153:211] == 0).all())
        np.testing.assert_array_equal(row[:153], pack_frame(f))

    def test_unusable_pose_zeroes_everything(self):
        self.assertTrue((features_v2.pack_frame(frame(0, np.random.default_rng(3), pose=False)) == 0).all())

    def test_wrong_face_cardinality_is_rejected(self):
        f = frame(0, np.random.default_rng(4))
        with self.assertRaises(ValueError):
            features_v2.pack_frame(RawFrame(0, f.pose, f.left_hand, f.right_hand, f.face[:468]))


class CaptureTest(unittest.TestCase):
    def test_face_gap_inside_the_hand_interval_no_longer_excludes(self):
        frames = clip(np.random.default_rng(5), face_gap={8, 9})
        self.assertEqual(face_features.prepare_capture(frames).reason, 'invalid_face')
        result = features_v2.prepare_capture(frames)
        self.assertEqual(result.reason, 'eligible')
        self.assertEqual(result.tensor.shape, (30, 211))
        self.assertIn(0, result.tensor[:, 210])

    def test_same_interval_and_indices_as_hm153(self):
        frames = clip(np.random.default_rng(6))
        old, new = sequence.prepare_capture(frames), features_v2.prepare_capture(frames)
        self.assertEqual(old.reason, new.reason)
        np.testing.assert_array_equal(new.tensor[:, :153].view(np.uint32), old.tensor.view(np.uint32))
        np.testing.assert_array_equal(new.tensor[:, 153:210].view(np.uint32),
                                      face_features.prepare_capture(frames).tensor[:, [153 + 3 * a + c for a in features_v2.ANCHORS for c in range(3)]].view(np.uint32))

    def test_hm153_reasons_are_kept(self):
        frames = clip(np.random.default_rng(7), hands=range(3, 5))
        self.assertEqual(features_v2.prepare_capture(frames).reason, sequence.prepare_capture(frames).reason)
        self.assertIsNone(features_v2.prepare_capture(frames).tensor)

    def test_observations_reproduce_the_tensor(self):
        frames = clip(np.random.default_rng(8))
        t, rows = features_v2.bounded_observations(frames)
        np.testing.assert_array_equal(rows[features_v2.grid_indices(t)], features_v2.prepare_capture(frames).tensor)


class Hm337Test(unittest.TestCase):
    def test_local_channels(self):
        x = features_v2.prepare_capture(clip(np.random.default_rng(9))).tensor
        out = features_v2.add_hand_local(x)
        self.assertEqual(out.shape, (30, 337))
        np.testing.assert_array_equal(out[:, :211], x)
        h = x[5, 0:63].reshape(21, 3).astype(np.float64)
        d = np.hypot(*(h[9, :2] - h[0, :2]))
        np.testing.assert_allclose(out[5, 211:274].reshape(21, 3)[:, :2], (h[:, :2] - h[0, :2]) / d, rtol=1e-6)
        np.testing.assert_allclose(out[5, 211:274].reshape(21, 3)[:, 2], h[:, 2] / d, rtol=1e-6)
        self.assertAlmostEqual(float(np.hypot(*out[5, 211:274].reshape(21, 3)[9, :2])), 1, places=5)

    def test_absent_hand_local_stays_zero(self):
        x = features_v2.prepare_capture(clip(np.random.default_rng(10))).tensor.copy()
        x[:, 63:126], x[:, 151] = 0, 0
        self.assertTrue((features_v2.add_hand_local(x)[:, 274:337] == 0).all())


def tensor(rng, n=4):
    xs = [features_v2.prepare_capture(clip(rng, face_gap={6})).tensor for _ in range(n)]
    x = np.stack(xs)
    if n > 1:
        x[1, :, 63:126], x[1, :, 151] = 0, 0  # one sequence without a right hand
    return x


def absent_zero(test, x):
    for start, mask in [(0, 150), (63, 151)]:
        test.assertTrue((x[..., start:start + 63][x[..., mask] == 0] == 0).all())
    test.assertTrue((x[..., 153:210][x[..., 210] == 0] == 0).all())


class AugmentTest(unittest.TestCase):
    def test_spatial_keeps_absent_parts_zero_and_masks_unchanged(self):
        x = tensor(np.random.default_rng(11))
        out = augment_v2.spatial(x, np.random.default_rng(0))
        absent_zero(self, out)
        np.testing.assert_array_equal(out[..., [150, 151, 152, 210]], x[..., [150, 151, 152, 210]])
        self.assertFalse(np.array_equal(out, x))
        pose = out[..., 126:150].reshape(*out.shape[:2], 6, 4)
        self.assertTrue((pose[x[..., 126:150].reshape(*x.shape[:2], 6, 4)[..., 3] < .5] == 0).all())

    def test_spatial_leaves_depth_and_visibility(self):
        x = tensor(np.random.default_rng(12))
        out = augment_v2.spatial(x, np.random.default_rng(1))
        z = [3 * i + 2 for i in range(42)] + [126 + 4 * i + k for i in range(6) for k in (2, 3)] + [155 + 3 * i for i in range(19)]
        np.testing.assert_array_equal(out[..., z], x[..., z])

    def test_rotation_only_matches_a_pure_rotation(self):
        x = tensor(np.random.default_rng(13), n=1)
        out = augment_v2.spatial(x, np.random.default_rng(2), scale=(1, 1), shift=0, jitter=0)
        p, q = x[0, 4, 0:63].reshape(21, 3)[:, :2], out[0, 4, 0:63].reshape(21, 3)[:, :2]
        np.testing.assert_allclose(np.linalg.norm(p, axis=1), np.linalg.norm(q, axis=1), rtol=1e-5)

    def test_rotate5_copy_rotates_face_with_the_historical_angles(self):
        x = tensor(np.random.default_rng(14))
        out, receipt = augment_v2.rotate5(x, [f'c{i}' for i in range(len(x))], seed=7)
        from training.holistic_migration import augmentation
        prefix, old = augmentation.rotate_fit(x[..., :153], [f'c{i}' for i in range(len(x))], partition='fit', seed=7)
        np.testing.assert_array_equal(out[..., :153], prefix)
        self.assertEqual(receipt['angles_degrees'], old['angles_degrees'])
        absent_zero(self, out)
        np.testing.assert_array_equal(out[..., 210], x[..., 210])

    def test_face_dropout_zeroes_whole_face_of_chosen_sequences(self):
        x = tensor(np.random.default_rng(15), n=40)
        out = augment_v2.face_dropout(x, np.random.default_rng(3), .5)
        dropped = (out[..., 210] == 0).all(axis=1) & (x[..., 210] == 1).any(axis=1)
        self.assertTrue(5 < dropped.sum() < 35)
        self.assertTrue((out[dropped][..., 153:211] == 0).all())
        np.testing.assert_array_equal(out[..., :153], x[..., :153])
        np.testing.assert_array_equal(out[~dropped], x[~dropped])

    def test_timing_uses_only_actual_observations(self):
        frames = clip(np.random.default_rng(16), n=30, hands=range(2, 28))
        t, rows = features_v2.bounded_observations(frames)
        rng = np.random.default_rng(4)
        for _ in range(20):
            out = augment_v2.timing(t, rows, rng, hand_drop=0)
            self.assertEqual(out.shape, (30, 211))
            for r in out:
                self.assertTrue((rows == r).all(axis=1).any())

    def test_timing_identity_settings_reproduce_the_tensor(self):
        frames = clip(np.random.default_rng(17))
        t, rows = features_v2.bounded_observations(frames)
        out = augment_v2.timing(t, rows, np.random.default_rng(5), trim=0, speed=(1, 1), hand_drop=0)
        np.testing.assert_array_equal(out, features_v2.prepare_capture(frames).tensor)

    def test_hand_drop_zeroes_one_hand_for_one_or_two_rows(self):
        frames = clip(np.random.default_rng(18))
        t, rows = features_v2.bounded_observations(frames)
        base = augment_v2.timing(t, rows, np.random.default_rng(6), trim=0, speed=(1, 1), hand_drop=0)
        out = augment_v2.timing(t, rows, np.random.default_rng(6), trim=0, speed=(1, 1), hand_drop=1)
        changed = np.flatnonzero((out != base).any(axis=1))
        self.assertIn(len(changed), (1, 2))
        absent_zero(self, out)
        diff = (out != base).any(axis=0)
        self.assertTrue(diff[:126].any() and not diff[126:150].any() and not diff[152:].any())


class RecipeTest(unittest.TestCase):
    def test_experiment_list_is_fixed(self):
        self.assertEqual(list(train_v2.EXPERIMENTS), ['E1', 'E2', 'E3', 'E4', 'E5', 'E6'])
        self.assertEqual(train_v2.EXPERIMENTS['E1'], dict(feature='hm153', copies='rot5', face_dropout=0,
                                                         label_smoothing=0, l2=0))
        self.assertEqual(train_v2.EXPERIMENTS['E6'], dict(feature='hm211', copies='spatial_timing3', face_dropout=.5,
                                                         label_smoothing=.1, l2=1e-4))

    def test_regularised_model_has_the_same_parameters(self):
        from training.holistic_migration.retraining.model import build_model
        self.assertEqual(train_v2.build(211, 1, 1e-4).count_params(), build_model(211, 1).count_params())

    def test_e1_recipe_is_bit_identical_to_the_phase2_runner(self):
        rng = np.random.default_rng(19)
        x = np.stack([sequence.prepare_capture(clip(rng)).tensor for _ in range(12)])
        y = np.array([i % 3 for i in range(12)])
        ids = np.array([f'clips/{i % 3}/{i}.MOV' for i in range(12)])
        ids_l = ids.tolist()
        a = train_cv.run_arrays(x, y, ids, ids_l[:3], ids_l[3:6], ids_l[6:], 5, max_epochs=3)
        b = train_v2.run_arrays(x, y, ids, ids_l[:3], ids_l[3:6], ids_l[6:], 5, train_v2.EXPERIMENTS['E1'], max_epochs=3)
        np.testing.assert_array_equal(a['probabilities'], b['probabilities'])
        self.assertEqual(a['history'], [{k: v for k, v in h.items() if k != 'learning_rate'} for h in b['history']])

    def test_e6_recipe_runs_and_scores_face_checks(self):
        rng = np.random.default_rng(20)
        frames = [clip(rng, face_gap={7}) for _ in range(12)]
        obs = [features_v2.bounded_observations(f) for f in frames]
        x = np.stack([features_v2.prepare_capture(f).tensor for f in frames])
        y = np.array([i % 3 for i in range(12)])
        ids = [f'clips/{i % 3}/{i}.MOV' for i in range(12)]
        r = train_v2.run_arrays(x, y, np.array(ids), ids[:3], ids[3:6], ids[6:], 5, train_v2.EXPERIMENTS['E6'],
                                observations=dict(zip(ids, obs)), max_epochs=2)
        for key in ['probabilities', 'face_zero_probabilities', 'face_only_probabilities']:
            self.assertEqual(r[key].shape, (3, 50))
        self.assertEqual(r['train_sequences'], 4 * 6)

    def test_face_views(self):
        x = tensor(np.random.default_rng(21))
        zero, only = train_v2.face_views(x)
        self.assertTrue((zero[..., 153:211] == 0).all())
        np.testing.assert_array_equal(zero[..., :153], x[..., :153])
        self.assertTrue((only[..., :152] == 0).all())
        np.testing.assert_array_equal(only[..., 152:], x[..., 152:])


class DecisionTest(unittest.TestCase):
    def test_keep_rule(self):
        base = dict(macro_f1_mean=.60, signs_below_90=40, per_sign_mean_correct=[5.0] * 50)
        good = dict(macro_f1_mean=.64, signs_below_90=39, per_sign_mean_correct=[5.0] * 49 + [4.0],
                    face_reliance=.03, face_only_accuracy=.05)
        self.assertTrue(train_v2.keep(good, base, .0325)['keep'])
        self.assertFalse(train_v2.keep(dict(good, macro_f1_mean=.63), base, .0325)['keep'])
        self.assertFalse(train_v2.keep(dict(good, per_sign_mean_correct=[5.0] * 49 + [3.67]), base, .0325)['keep'])
        self.assertFalse(train_v2.keep(dict(good, signs_below_90=41), base, .0325)['keep'])
        self.assertFalse(train_v2.keep(dict(good, face_reliance=.06), base, .0325)['keep'])
        self.assertFalse(train_v2.keep(dict(good, face_only_accuracy=.2), base, .0325)['keep'])
        self.assertTrue(train_v2.keep(dict(good, face_reliance=None, face_only_accuracy=None), base, .0325)['keep'])

    def test_select_prefers_simpler_within_threshold(self):
        results = {'E1': dict(keep=True, macro_f1_mean=.70), 'E3': dict(keep=True, macro_f1_mean=.73),
                   'E5': dict(keep=True, macro_f1_mean=.76), 'E6': dict(keep=False, macro_f1_mean=.80)}
        self.assertEqual(train_v2.select(results, .0325), 'E3')
        self.assertIsNone(train_v2.select({'E1': dict(keep=False, macro_f1_mean=.9)}, .0325))


class ReviewFixTest(unittest.TestCase):
    """Regressions for review-1 findings 2, 3, 4, 5 and 1."""

    def test_spatial_moves_shoulders_by_rotation_only(self):
        x = tensor(np.random.default_rng(30))
        out = augment_v2.spatial(x, np.random.default_rng(7))
        sh = out[..., 126:134].reshape(*out.shape[:2], 2, 4)
        np.testing.assert_allclose(sh[..., :2].mean(axis=2), 0, atol=1e-6)
        np.testing.assert_allclose(np.linalg.norm(sh[..., 0, :2] - sh[..., 1, :2], axis=-1), 1, atol=1e-5)

    def test_spatial_keeps_invisible_arm_points_zero(self):
        x = tensor(np.random.default_rng(31))
        x[:, :, 126 + 4 * 3:126 + 4 * 4] = 0  # one elbow invisible everywhere
        out = augment_v2.spatial(x, np.random.default_rng(8))
        self.assertTrue((out[:, :, 138:142] == 0).all())

    def test_timing_always_keeps_hand_rows(self):
        frames = clip(np.random.default_rng(32), n=20, hands=[3, 4, 5, 6, 7, 8, 9, 10, 15])
        t, rows = features_v2.bounded_observations(frames)
        rng = np.random.default_rng(9)
        for _ in range(200):
            out = augment_v2.timing(t, rows, rng, hand_drop=0)
            hands = out[:, 150].astype(bool) | out[:, 151].astype(bool)
            self.assertTrue(hands[0] and hands[-1])

    def test_keep_lists_face_dependent_signs_and_flags_investigation(self):
        base = dict(macro_f1_mean=.60, signs_below_90=40, per_sign_mean_correct=[5.0] * 50)
        good = dict(macro_f1_mean=.64, signs_below_90=39, per_sign_mean_correct=[5.0] * 50, face_reliance=.03,
                    face_only_accuracy=.2, face_dependent_signs=['SON'])
        k = train_v2.keep(good, base, .0325)
        self.assertFalse(k['keep'])
        self.assertTrue(k['face_only_investigation_needed'])
        self.assertEqual(k['face_dependent_signs'], ['SON'])

    def test_decide_uses_the_b0cv_block_of_each_summary(self):
        mk = lambda exp, f1, keep_ok=True: dict(
            experiment=exp, macro_f1_mean=f1, signs_below_90=30 if keep_ok else 45, per_sign_mean_correct=[5.0] * 50,
            face_reliance=None, face_only_accuracy=None, face_dependent_signs=[], best_epochs=[10, 20, 30],
            b0cv=dict(macro_f1_mean=.6, signs_below_90=40, per_sign_mean_correct=[5.0] * 50))
        d = train_v2.decide([mk('E1', .70), mk('E3', .74), mk('E4', .80), mk('E5', .90, False)], .0325)
        self.assertEqual(d['selected'], 'E4')
        self.assertEqual(d['e7_base'], 'E5')
        self.assertEqual(d['final_epochs'], 20)
        self.assertFalse(d['results']['E5']['keep'])


if __name__ == '__main__':
    unittest.main()
