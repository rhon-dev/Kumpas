import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent

class HandoffTest(unittest.TestCase):
    def test_generator_uses_actual_dense_classes_and_leaves_every_observation_blank(self):
        with tempfile.TemporaryDirectory() as directory:
            run = subprocess.run([sys.executable, str(ROOT / 'generate_handoff.py'), '--output-dir', directory], capture_output=True, text=True)
            self.assertEqual(0, run.returncode, run.stderr)
            root = Path(directory)
            labels = json.loads((ROOT.parent / 'app/android/app/src/main/assets/label_map.json').read_text())
            rows = list(csv.DictReader((root / 'sign_trials.csv').read_text().splitlines()))
            self.assertEqual(300, len(rows))
            ids = {(r['candidate_id'], r['condition'], int(r['class_id'])) for r in rows}
            self.assertEqual(300, len(ids))
            for row in rows:
                self.assertEqual(labels[row['class_id']]['label'], row['target_label'])
                self.assertEqual('BLOCKED', row['status'])
                for field in ('run_id', 'attempt_id', 'signer_code', 'predicted_class_id', 'outcome', 'analyzer_to_feedback_ms'):
                    self.assertEqual('', row[field])
            confusion = list(csv.DictReader((root / 'confusion_matrix.csv').read_text().splitlines()))
            self.assertEqual(300, len(confusion))
            self.assertTrue(all(r['predicted_' + str(i)] == '' for r in confusion for i in range(50)))
            self.assertEqual(6, len(list(csv.DictReader((root / 'condition_runs.csv').read_text().splitlines()))))
            self.assertEqual(2, len(list(csv.DictReader((root / 'candidate_devices.csv').read_text().splitlines()))))
            self.assertTrue(any(r['target_label'] == 'FIVE' and r['class_id'] == '24' for r in rows))

if __name__ == '__main__': unittest.main()
