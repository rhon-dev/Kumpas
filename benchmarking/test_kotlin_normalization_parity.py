"""Compare the compiled live Kotlin normalizer with the training Python math."""
import json
import subprocess
import unittest
from pathlib import Path

import numpy as np
from training.preprocessing.build_sequences import normalize

ROOT = Path(__file__).resolve().parents[1]


class KotlinNormalizationParityTest(unittest.TestCase):
    def test_pose_and_present_hand_match_python(self):
        result = subprocess.run(["python", "benchmarking/compile_feature_smoke.py"],
                                cwd=ROOT, check=True, capture_output=True, text=True)
        vector = np.array(json.loads(result.stdout.strip().splitlines()[-1]), dtype=np.float32)
        raw = np.zeros((1, 1662), dtype=np.float32)
        for i in range(33):
            raw[0, i * 4:i * 4 + 4] = (0.5, 0.5, 0.1, 1.0)
        raw[0, 11 * 4 + 1] = raw[0, 12 * 4 + 1] = 0.2
        raw[0, 1599:1662] = 0.6
        expected = normalize(raw)[0, np.r_[0:132, 1536:1662]]
        self.assertEqual(vector.shape, (258,))
        np.testing.assert_allclose(vector, expected, rtol=1e-5, atol=1e-6)

    def test_python_training_discards_hands_if_pose_is_absent(self):
        raw = np.zeros((1, 1662), dtype=np.float32)
        raw[0, 1536:1599] = 0.6
        self.assertFalse(np.any(normalize(raw)[0]))
        # Shipped Kotlin deliberately preserves this hand without a pose.
        # This is an identified parity gap, not an anatomy assertion.


if __name__ == "__main__":
    unittest.main()
