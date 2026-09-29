"""Paired-frame parity checks, without making an anatomical claim."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_parity import compare_vectors, write_frames, select_frame_indices


class ParityTests(unittest.TestCase):
    def _frame(self, index, digest, value, left=True):
        return {"index": index, "sha256": digest, "features": [value] * 258,
                "pose_seen": True, "left_seen": left, "right_seen": False}

    def test_same_frame_comparison_and_explicit_anatomical_unknown(self):
        ref = {"frames": [self._frame(0, "abc", 0), self._frame(1, "def", 1)]}
        app = {"frames": [self._frame(0, "abc", 0), self._frame(1, "def", 2, False)]}
        report = compare_vectors(ref, app)
        self.assertEqual(report["matched_frames"], 2)
        self.assertAlmostEqual(report["block_mae"]["pose"], .5)
        self.assertEqual(report["presence_disagreements"]["left_seen"], 1)
        self.assertEqual(report["anatomical_left_right"], "unverified")

    def test_image_digest_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "hash"):
            compare_vectors({"frames": [self._frame(0, "one", 0)]},
                            {"frames": [self._frame(0, "two", 0)]})

    def test_missing_frame_or_wrong_dimension_fails(self):
        with self.assertRaisesRegex(ValueError, "frame"):
            compare_vectors({"frames": [self._frame(0, "same", 0)]}, {"frames": []})
        bad = self._frame(0, "same", 0)
        bad["features"] = [0] * 257
        with self.assertRaisesRegex(ValueError, "258"):
            compare_vectors({"frames": [self._frame(0, "same", 0)]}, {"frames": [bad]})

    def test_frame_index_selection_preserves_endpoints_and_count(self):
        indices = select_frame_indices(244, 30)
        self.assertEqual(len(indices), 30)
        self.assertEqual(indices[0], 0)
        self.assertEqual(indices[-1], 243)
        self.assertEqual(len(set(indices)), 30)
        self.assertEqual(select_frame_indices(3, 30), [0, 1, 2])

    def test_png_manifest_uses_actual_file_bytes_and_stable_indices(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "frames"
            frames = [np.zeros((4, 6, 3), np.uint8), np.full((4, 6, 3), 255, np.uint8)]
            manifest = write_frames(frames, out)
            self.assertEqual([f["index"] for f in manifest["frames"]], [0, 1])
            for entry in manifest["frames"]:
                self.assertEqual(entry["sha256"], hashlib.sha256((out / entry["filename"]).read_bytes()).hexdigest())
            self.assertNotEqual(manifest["frames"][0]["sha256"], manifest["frames"][1]["sha256"])


if __name__ == "__main__":
    unittest.main()
