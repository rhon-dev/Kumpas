"""Regression tests for the leak-free original-clip partition."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
from evaluation_protocol import build_manifest, build_protocol, validate_manifest


class EvaluationProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "source"
        self.source.mkdir()
        self.output = Path(self.tmp.name) / "evaluation_v1"
        self.X = np.ones((18, 30, 258), dtype=np.float32)
        self.y = np.repeat(np.arange(3), 6)
        np.save(self.source / "X_train.npy", self.X)
        np.save(self.source / "y_train.npy", self.y)
        (self.source / "clips_train.json").write_text(json.dumps([f"clips_{i // 6}_{i % 6}.npz" for i in range(18)]))
        (self.source / "clips_test.json").write_text(json.dumps(["clips_0_99.npz"]))

    def test_original_clips_split_before_augmentation(self):
        manifest = build_manifest(self.source)
        self.assertEqual(manifest, build_manifest(self.source))
        result = build_protocol(self.source, self.output, factor=1)
        fit = {r["clip"] for r in manifest["rows"] if r["partition"] == "fit"}
        val = {r["clip"] for r in manifest["rows"] if r["partition"] == "validation"}
        self.assertFalse(fit & val)
        self.assertEqual(set(self.y), {r["class_id"] for r in manifest["rows"] if r["partition"] == "validation"})
        self.assertEqual(len(result["augmentations"]), len(fit))
        self.assertEqual({r["source_clip"] for r in result["augmentations"]}, fit)
        self.assertTrue(np.array_equal(np.load(self.output / "X_val.npy"), self.X[[r["index"] for r in manifest["rows"] if r["partition"] == "validation"]]))
        self.assertEqual(len(np.load(self.output / "X_fit.npy")), 2 * len(fit))

    def test_source_digest_change_is_rejected(self):
        manifest = build_manifest(self.source)
        np.save(self.source / "X_train.npy", self.X * 2)
        with self.assertRaisesRegex(ValueError, "digest"):
            validate_manifest(manifest, self.source)

    def test_duplicate_clip_name_is_rejected(self):
        clips = json.loads((self.source / "clips_train.json").read_text())
        clips[1] = clips[0]
        (self.source / "clips_train.json").write_text(json.dumps(clips))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            build_manifest(self.source)

    def test_original_train_test_clip_overlap_is_rejected(self):
        (self.source / "clips_test.json").write_text(json.dumps(["clips_0_0.npz"]))
        with self.assertRaisesRegex(ValueError, "overlap"):
            build_manifest(self.source)

    def test_mismatched_clip_count_is_rejected(self):
        (self.source / "clips_train.json").write_text(json.dumps(["only_one.npz"]))
        with self.assertRaisesRegex(ValueError, "length"):
            build_manifest(self.source)


if __name__ == "__main__":
    unittest.main()
