"""Validation-only model selection and protocol integrity tests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
from evaluation_protocol import build_protocol
from train_cnn_lstm import load_protocol_data
from freeze_selection import freeze_selection


class TrainingProtocolTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        source = self.root / "source"
        source.mkdir()
        np.save(source / "X_train.npy", np.ones((12, 30, 258), np.float32))
        np.save(source / "y_train.npy", np.repeat([0, 1], 6))
        (source / "clips_train.json").write_text(json.dumps([f"c{i}.npz" for i in range(12)]))
        (source / "clips_test.json").write_text("[]")
        self.protocol = source / "evaluation-v1"
        build_protocol(source, self.protocol, factor=1)
        self.source = source

    def test_load_explicit_unaugmented_validation(self):
        fit, val, _, manifest = load_protocol_data(self.protocol, drop_face=False)
        self.assertEqual(len(val[0]), manifest["n_validation"])
        self.assertEqual(len(fit[0]), manifest["n_fit_original"] * 2)
        self.assertTrue(np.array_equal(val[0], np.load(self.protocol / "X_val.npy")))

    def test_source_tampering_prevents_training(self):
        np.save(self.source / "X_train.npy", np.zeros((12, 30, 258), np.float32))
        with self.assertRaisesRegex(ValueError, "digest"):
            load_protocol_data(self.protocol, drop_face=False)

    def test_selection_uses_validation_not_historical_test(self):
        models = self.root / "models"
        models.mkdir()
        for name in ("low", "high"):
            (models / f"{name}.keras").write_bytes(name.encode())
        import hashlib
        from evaluation_protocol import sha256
        rows = [{"run_id": name, "best_val_accuracy": val, "best_val_macro_f1": val,
                 "checkpoint": str(models / f"{name}.keras"),
                 "checkpoint_sha256": sha256(models / f"{name}.keras"),
                 "protocol_sha256": sha256(self.protocol / "manifest.json"),
                 "test_accuracy": test}
                for name, val, test in (("low", .4, .99), ("high", .8, .1))]
        log = self.root / "runs.json"
        log.write_text(json.dumps(rows))
        frozen = self.root / "frozen.json"
        result = freeze_selection(log, self.protocol, frozen)
        self.assertEqual(result["run_id"], "high")
        self.assertEqual(json.loads(frozen.read_text())["run_id"], "high")
        self.assertNotIn("test_accuracy", result)


if __name__ == "__main__":
    unittest.main()
