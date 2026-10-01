"""Freeze-bound export must reject unverified selections before conversion."""
import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tflite_export"))
from evaluation_protocol import build_protocol, sha256
from export_frozen import verified_selection, export_candidate
import numpy as np


class FrozenExportTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        source = root / "source"
        source.mkdir()
        np.save(source / "X_train.npy", np.ones((12, 30, 258), np.float32))
        np.save(source / "y_train.npy", np.repeat([0, 1], 6))
        (source / "clips_train.json").write_text(json.dumps([f"c{i}" for i in range(12)]))
        (source / "clips_test.json").write_text("[]")
        (source / "label_map.json").write_text('{"0":{"label":"A"},"1":{"label":"B"}}')
        self.protocol = source / "evaluation-v1"
        build_protocol(source, self.protocol, factor=0)
        self.checkpoint = root / "selected.keras"
        self.checkpoint.write_bytes(b"selected-model")
        self.freeze = root / "freeze.json"
        self.freeze.write_text(json.dumps({
            "run_id": "run1", "checkpoint": str(self.checkpoint),
            "checkpoint_sha256": sha256(self.checkpoint),
            "protocol_sha256": sha256(self.protocol / "manifest.json"),
            "selection_method": "validation accuracy only",
            "test_status": "exploratory-reused-test",
        }))

    def test_accepts_only_frozen_checkpoint_from_validated_protocol(self):
        result = verified_selection(self.freeze, self.protocol)
        self.assertEqual(result["run_id"], "run1")
        self.assertEqual(result["checkpoint_sha256"], sha256(self.checkpoint))

    def test_rejects_checkpoint_changed_after_freeze(self):
        self.checkpoint.write_bytes(b"replaced-model")
        with self.assertRaisesRegex(ValueError, "checkpoint.*digest"):
            verified_selection(self.freeze, self.protocol)

    def test_rejects_other_protocol_manifest(self):
        freeze = json.loads(self.freeze.read_text())
        freeze["protocol_sha256"] = "0" * 64
        self.freeze.write_text(json.dumps(freeze))
        with self.assertRaisesRegex(ValueError, "protocol.*digest"):
            verified_selection(self.freeze, self.protocol)

    @unittest.skipUnless(importlib.util.find_spec("tensorflow"), "TensorFlow environment required")
    def test_frozen_export_preserves_validation_predictions_and_hashes(self):
        import tensorflow as tf
        tf.keras.utils.set_random_seed(13)
        model = tf.keras.Sequential([
            tf.keras.Input((30, 258)), tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(2, activation="softmax")
        ])
        model.save(self.checkpoint)
        freeze = json.loads(self.freeze.read_text())
        freeze["checkpoint_sha256"] = sha256(self.checkpoint)
        self.freeze.write_text(json.dumps(freeze))
        output = self.protocol.parent.parent / "exported"
        result = export_candidate(self.freeze, self.protocol, output,
                                  self.protocol.parent / "label_map.json")
        self.assertEqual(result["checkpoint_sha256"], sha256(self.checkpoint))
        self.assertEqual(result["tflite_sha256"], sha256(output / result["filename"]))
        self.assertEqual(result["validation_samples"], 4)
        self.assertEqual(result["validation_prediction_disagreements"], 0)
        self.assertTrue((output / "provenance.json").is_file())


if __name__ == "__main__":
    unittest.main()
