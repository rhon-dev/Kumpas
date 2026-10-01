"""The historical test is only evaluated after validation selection is frozen."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
from evaluate_frozen import evaluate_frozen, render_report
from eval_report import select_historical_run


class FrozenEvaluationTests(unittest.TestCase):
    def test_no_automatic_selection_by_test_score(self):
        runs = [{"run_id": "a", "test_accuracy": .99}, {"run_id": "b", "test_accuracy": .1}]
        with self.assertRaisesRegex(ValueError, "explicit"):
            select_historical_run(runs, None)
        self.assertEqual(select_historical_run(runs, "b")["run_id"], "b")

    def test_report_labels_test_reuse_and_signer_uncertainty(self):
        text = render_report({"run_id": "new", "correct": 193, "n": 203,
                              "accuracy": 193 / 203, "macro_f1": .95,
                              "wilson_95": [.91, .97], "per_class": []})
        self.assertIn("exploratory", text.lower())
        self.assertIn("signer-independent", text.lower())

    def test_missing_freeze_refuses_evaluation_before_loading_model(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            with self.assertRaises((ValueError, FileNotFoundError)):
                evaluate_frozen(root / "absent.json", root, root, root / "report")

    def test_conflicting_manifest_refuses_evaluation_before_loading_model(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            (root / "manifest.json").write_text("{}")
            frozen = root / "frozen.json"
            frozen.write_text(json.dumps({"run_id": "r", "protocol_sha256": "bad"}))
            with self.assertRaisesRegex(ValueError, "manifest"):
                evaluate_frozen(frozen, root, root, root / "report")


if __name__ == "__main__":
    unittest.main()
