"""Paired-frame parity checks, without making an anatomical claim."""
import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_parity import (compare_vectors, write_frames, select_frame_indices,
                             generate_python_reference, prepare_video)


class ParityTests(unittest.TestCase):
    def _frame(self, index, digest, value, left=True):
        return {"index": index, "sha256": hashlib.sha256(digest.encode()).hexdigest(), "features": [value] * 258,
                "pose_seen": True, "left_seen": left, "right_seen": False}

    def test_same_frame_comparison_and_explicit_anatomical_unknown(self):
        ref = {"schema": "kumpas-feature-reference-v1", "frames": [self._frame(0, "abc", 0), self._frame(1, "def", 1)]}
        app = {"schema": "kumpas-android-replay-v1", "frames": [self._frame(0, "abc", 0), self._frame(1, "def", 2, False)]}
        report = compare_vectors(ref, app)
        self.assertEqual(report["matched_frames"], 2)
        self.assertAlmostEqual(report["block_mae"]["pose"], .5)
        self.assertEqual(report["presence_disagreements"]["left_seen"], 1)
        self.assertEqual(report["anatomical_left_right"], "unverified")

    def test_image_digest_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "hash"):
            compare_vectors({"schema": "kumpas-feature-reference-v1", "frames": [self._frame(0, "one", 0)]},
                            {"schema": "kumpas-android-replay-v1", "frames": [self._frame(0, "two", 0)]})

    def test_missing_frame_or_wrong_dimension_fails(self):
        with self.assertRaisesRegex(ValueError, "frame"):
            compare_vectors({"schema": "kumpas-feature-reference-v1", "frames": [self._frame(0, "same", 0)]}, {"schema": "kumpas-android-replay-v1", "frames": []})
        bad = self._frame(0, "same", 0)
        bad["features"] = [0] * 257
        with self.assertRaisesRegex(ValueError, "258"):
            compare_vectors({"schema": "kumpas-feature-reference-v1", "frames": [self._frame(0, "same", 0)]}, {"schema": "kumpas-android-replay-v1", "frames": [bad]})

    def test_missing_or_malformed_equal_digests_rejected(self):
        for digest in (None, "", "abc", "g" * 64, 7, [], True):
            with self.subTest(digest=digest):
                ref = {"schema": "kumpas-feature-reference-v1", "frames": [self._frame(0, "same", 0)]}
                app = copy.deepcopy(ref)
                for doc in (ref, app):
                    if digest is None:
                        doc["frames"][0].pop("sha256")
                    else:
                        doc["frames"][0]["sha256"] = digest
                with self.assertRaisesRegex(ValueError, "invalid frame hash"):
                    compare_vectors(ref, app)

    def test_document_and_frame_types_fail_with_fixed_safe_errors(self):
        good = {"schema": "kumpas-feature-reference-v1", "frames": [self._frame(0, "same", 0)]}
        cases = [None, [], "private-marker", {}, {"frames": good["frames"]}]
        for schema in (None, 1, True, [], "private-marker"):
            cases.append(dict(good, schema=schema))
        for frames in (None, {}, "private-marker", [None], [[]], ["private-marker"]):
            cases.append(dict(good, frames=frames))
        for index in (True, False, -1, 1.0, "0", [], {}, None, 2):
            bad = copy.deepcopy(good)
            bad["frames"][0]["index"] = index
            cases.append(bad)
        for value in (True, False, float("nan"), float("inf"), "private-marker", 10 ** 400):
            bad = copy.deepcopy(good)
            bad["frames"][0]["features"][0] = value
            cases.append(bad)
        for presence in (1, None, "private-marker", []):
            bad = copy.deepcopy(good)
            bad["frames"][0]["left_seen"] = presence
            cases.append(bad)
        duplicate = copy.deepcopy(good)
        duplicate["frames"] *= 2
        cases.append(duplicate)
        reordered = copy.deepcopy(good)
        reordered["frames"] = [self._frame(1, "b", 0), self._frame(0, "a", 0)]
        cases.append(reordered)
        for i, bad in enumerate(cases):
            for left, right in ((bad, good), (good, bad), (bad, bad)):
                with self.subTest(case=i):
                    with self.assertRaises(ValueError) as caught:
                        compare_vectors(left, right)
                    self.assertNotIn("private-marker", str(caught.exception))

    def test_clip_binding_required_mode_and_identity_mismatch(self):
        good = {"schema": "kumpas-feature-reference-v1", "frames": [self._frame(0, "same", 0)]}
        self.assertIn("clip_identity", compare_vectors(good, good))
        self.assertEqual(compare_vectors(good, good)["clip_identity"], "unbound_legacy_frames_only")
        with self.assertRaises(ValueError):
            compare_vectors(good, good, require_clip_binding=True)
        binding = {"schema": "kumpas-clip-binding-v1", "clip_id": "clips_22_14.npz",
                   "source_video_sha256": "a" * 64, "replay_manifest_sha256": "b" * 64}
        bound = dict(good, fixture_binding=binding)
        self.assertEqual(compare_vectors(bound, bound, require_clip_binding=True)["clip_identity"], "bound_v1")
        for changed in (None, {}, dict(binding, clip_id="clips_24_10.npz"),
                        dict(binding, source_video_sha256="c" * 64),
                        dict(binding, schema=True), dict(binding, clip_id="../private-marker")):
            other = dict(good, fixture_binding=changed)
            with self.assertRaises(ValueError):
                compare_vectors(bound, other)
        with self.assertRaises(ValueError):
            compare_vectors(bound, good)

    def test_prediction_payloads_not_mistaken_for_equivalent_class_results(self):
        good = {"schema": "kumpas-feature-reference-v1", "frames": [self._frame(0, "same", 0)]}
        report = compare_vectors(dict(good, prediction={"class_id": 22}),
                                 dict(good, prediction={"class_id": 22}, attempt_result={"predictedLabel": "THREE"}))
        self.assertNotIn("prediction_agreement", report)
        self.assertEqual(report["prediction_comparison"], "not_evaluated_feature_only")

    def test_compare_cli_requires_clip_binding_unless_legacy_mode_is_explicit(self):
        import json
        import subprocess
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            good = {"schema": "kumpas-feature-reference-v1", "frames": [self._frame(0, "same", 0)]}
            (root / "ref.json").write_text(json.dumps(good))
            command = [sys.executable, "-E", str(Path(__file__).with_name("pipeline_parity.py")),
                       "compare", str(root / "ref.json"), str(root / "ref.json"), str(root / "report.json")]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "report.json").exists())
            result = subprocess.run(command + ["--legacy-frame-only"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((root / "report.json").read_text())["clip_identity"], "unbound_legacy_frames_only")

    def test_frame_index_selection_preserves_endpoints_and_count(self):
        indices = select_frame_indices(244, 30)
        self.assertEqual(len(indices), 30)
        self.assertEqual(indices[0], 0)
        self.assertEqual(indices[-1], 243)
        self.assertEqual(len(set(indices)), 30)
        self.assertEqual(select_frame_indices(3, 30), [0, 1, 2])

    def test_reference_rejects_unsafe_manifest_before_detector_or_output(self):
        import json
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            frames = root / "frames"
            manifest = write_frames([np.zeros((4, 6, 3), np.uint8)], frames)
            (root / "private-marker.png").write_bytes((frames / "frame_00000.png").read_bytes())
            for filename in ("../private-marker.png", str((frames / "frame_00000.png").absolute())):
                bad = copy.deepcopy(manifest)
                bad["frames"][0]["filename"] = filename
                (frames / "manifest.json").write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError, "invalid replay"):
                    generate_python_reference(frames, root / "output.json")
                self.assertFalse((root / "output.json").exists())
            (frames / "manifest.json").write_text(json.dumps(manifest))
            (frames / "frame_00000.png").rename(root / "external.png")
            (frames / "frame_00000.png").symlink_to(root / "external.png")
            with self.assertRaisesRegex(ValueError, "symlink"):
                generate_python_reference(frames, root / "output.json")

    def test_prepare_video_counts_and_samples_actual_decode(self):
        import cv2
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            video = root / "synthetic.avi"
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10, (16, 16))
            self.assertTrue(writer.isOpened())
            for i in range(9):
                writer.write(np.full((16, 16, 3), i * 20, np.uint8))
            writer.release()
            manifest = prepare_video(video, root / "frames", 3)
            self.assertEqual(manifest["decoded_frames"], 9)
            self.assertEqual([f["source_frame_index"] for f in manifest["frames"]], [0, 4, 8])
            self.assertEqual(manifest["source_fps"], 10)
            self.assertEqual(manifest["source_video_sha256"], hashlib.sha256(video.read_bytes()).hexdigest())
            with self.assertRaises(FileExistsError):
                prepare_video(video, root / "frames", 3)

    def test_reference_records_actual_detector_presence_counts(self):
        import importlib.util
        if importlib.util.find_spec("mediapipe") is None:
            self.skipTest("MediaPipe unavailable in this interpreter")
        import mediapipe
        if not hasattr(mediapipe, "solutions"):
            self.skipTest("This interpreter's MediaPipe lacks Holistic solutions; training/.venv exercised separately")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_frames([np.zeros((16, 16, 3), np.uint8)], root / "frames")
            result = generate_python_reference(root / "frames", root / "output.json")
            self.assertIn("detector_presence_counts", result)
            self.assertEqual(result["detector_presence_counts"],
                             {"pose": 0, "face": 0, "left_hand": 0, "right_hand": 0})

    def test_prepare_retains_only_sampled_frames_not_all_decoded_frames(self):
        import weakref
        from unittest.mock import patch
        live, peak = [], [0]
        class Capture:
            def __init__(self, *args):
                self.index = 0
            def isOpened(self):
                return True
            def get(self, key):
                return 10.0
            def release(self):
                pass
            def read(self):
                if self.index == 40:
                    return False, None
                self.index += 1
                frame = np.zeros((16, 16, 3), np.uint8)
                live.append(weakref.ref(frame))
                peak[0] = max(peak[0], sum(x() is not None for x in live))
                return True, frame
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "video").write_bytes(b"synthetic-video-input")
            with patch("cv2.VideoCapture", Capture):
                result = prepare_video(root / "video", root / "frames", 3)
            self.assertEqual(len(result["frames"]), 3)
            self.assertLessEqual(peak[0], 5)

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
