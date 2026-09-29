"""Python reference uses the training pipeline's feature layout and normalization."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_parity import reference_from_vectors


class ReferenceTests(unittest.TestCase):
    def test_frame_layout_and_absent_left_hand(self):
        raw = np.zeros((2, 1662), np.float32)
        for frame in raw:
            for point in range(33):
                frame[point * 4:point * 4 + 4] = [0.5, 0.5, 0.1, 1.0]
            frame[11 * 4 + 1] = frame[12 * 4 + 1] = 0.2
            frame[1536:1599] = 0  # left missing
            frame[1599:1662] = 0.6  # right present
        manifest = {"frames": [{"index": i, "sha256": f"hash-{i}"} for i in range(2)]}
        result = reference_from_vectors(raw, manifest)
        self.assertEqual(len(result["frames"]), 2)
        for row in result["frames"]:
            self.assertEqual(len(row["features"]), 258)
            self.assertTrue(row["pose_seen"])
            self.assertFalse(row["left_seen"])
            self.assertTrue(row["right_seen"])
            self.assertTrue(np.allclose(row["features"][132:195], 0))
            self.assertEqual(row["sha256"], manifest["frames"][row["index"]]["sha256"])

    def test_frame_count_mismatch_fails(self):
        with self.assertRaisesRegex(ValueError, "frame"):
            reference_from_vectors(np.zeros((1, 1662), np.float32), {"frames": []})


if __name__ == "__main__":
    unittest.main()
