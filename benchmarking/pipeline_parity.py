#!/usr/bin/env python3
"""Reproducible paired-frame extraction and Python/Android feature comparison.

Generated PNGs, vectors and reports contain identifiable material: keep them
in ../kumpas-data/parity/, never in git. Parity does NOT establish anatomy.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BLOCKS = {"pose": (0, 132), "left_hand": (132, 195), "right_hand": (195, 258)}
PRESENCE = ("pose_seen", "left_seen", "right_seen")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def select_frame_indices(n_frames: int, max_frames: int | None) -> list[int]:
    if n_frames < 1 or (max_frames is not None and max_frames < 1):
        raise ValueError("frame counts must be positive")
    if max_frames is None or max_frames >= n_frames:
        return list(range(n_frames))
    return np.linspace(0, n_frames - 1, max_frames).round().astype(int).tolist()


def write_frames(frames, output_dir: Path, source_indices=None) -> dict:
    """Serialize BGR uint8 frames as lossless PNGs; hash the exact PNG bytes."""
    import cv2
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    entries = []
    source_indices = list(range(len(frames))) if source_indices is None else list(source_indices)
    if len(source_indices) != len(frames):
        raise ValueError("source frame index length mismatch")
    for i, frame in enumerate(frames):
        if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError("frames must be BGR uint8 HxWx3")
        ok, png = cv2.imencode(".png", frame)
        if not ok:
            raise ValueError(f"PNG encode failed: frame {i}")
        filename = f"frame_{i:05d}.png"
        data = png.tobytes()
        (output_dir / filename).write_bytes(data)
        entries.append({"index": i, "source_frame_index": source_indices[i],
                        "filename": filename, "sha256": sha256_bytes(data)})
    if not entries:
        raise ValueError("no frames decoded")
    manifest = {"schema": "kumpas-replay-v1", "frames": entries, "color": "RGB after PNG decode"}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def reject_symlinks(path: Path) -> Path:
    path = Path(path).absolute()
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("symlink paths forbidden")
    return path


def validate_replay(frames_dir: Path) -> dict:
    """Validate the actual native replay-v1 format before detector work."""
    frames_dir = reject_symlinks(frames_dir)
    manifest_path = reject_symlinks(frames_dir / "manifest.json")
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError):
        raise ValueError("invalid replay manifest") from None
    if type(manifest) is not dict or manifest.get("schema") != "kumpas-replay-v1":
        raise ValueError("invalid replay schema")
    frames = manifest.get("frames")
    if type(frames) is not list or not frames:
        raise ValueError("invalid replay frames")
    previous_source = -1
    for i, row in enumerate(frames):
        if type(row) is not dict or type(row.get("index")) is not int or row["index"] != i:
            raise ValueError("invalid replay frame index")
        if row.get("filename") != f"frame_{i:05d}.png":
            raise ValueError("invalid replay filename")
        source = row.get("source_frame_index")
        if type(source) is not int or source <= previous_source:
            raise ValueError("invalid replay source index")
        previous_source = source
        digest = row.get("sha256")
        if type(digest) is not str or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("invalid replay hash")
        png_path = reject_symlinks(frames_dir / row["filename"])
        try:
            data = png_path.read_bytes()
        except OSError:
            raise ValueError("invalid replay PNG") from None
        if sha256_bytes(data) != digest:
            raise ValueError("invalid replay PNG hash")
    return manifest


def prepare_video(video_path: Path, output_dir: Path, max_frames: int | None = None) -> dict:
    """Two sequential decode passes; retain only selected BGR frames."""
    import cv2
    video_path = reject_symlinks(video_path)
    output_dir = reject_symlinks(output_dir)
    if output_dir.exists():
        raise FileExistsError("output already exists")
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError("cannot decode video")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    count = 0
    try:
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            count += 1
    finally:
        cap.release()
    del bgr
    indices = select_frame_indices(count, max_frames)
    wanted, frames = set(indices), []
    cap = cv2.VideoCapture(str(video_path))
    decoded = 0
    try:
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            if decoded in wanted:
                frames.append(bgr)
            decoded += 1
    finally:
        cap.release()
    if decoded != count or len(frames) != len(indices):
        raise ValueError("video decode changed between passes")
    manifest = write_frames(frames, output_dir, indices)
    manifest["source_video_sha256"] = sha256_bytes(video_path.read_bytes())
    manifest["source_fps"] = fps
    manifest["decoded_frames"] = count
    manifest["sampling"] = "all" if max_frames is None else f"uniform-{max_frames}; detector tracking differs from full-video training extraction"
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def _finite_number(value) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _frame_map(document: dict) -> dict:
    if type(document) is not dict or type(document.get("schema")) is not str or document["schema"] not in (
            "kumpas-feature-reference-v1", "kumpas-android-replay-v1"):
        raise ValueError("unsupported feature document schema")
    rows = document.get("frames")
    if type(rows) is not list or not rows:
        raise ValueError("invalid or empty frame list")
    mapping = {}
    for expected, frame in enumerate(rows):
        if type(frame) is not dict:
            raise ValueError("invalid frame object")
        index = frame.get("index")
        if type(index) is not int or index != expected:
            raise ValueError("duplicate or invalid frame index")
        digest = frame.get("sha256")
        if type(digest) is not str or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("invalid frame hash")
        features = frame.get("features")
        if not isinstance(features, list) or len(features) != 258:
            raise ValueError("each feature vector must have 258 floats")
        if any(not _finite_number(x) for x in features):
            raise ValueError("nonfinite or nonnumeric feature")
        if not all(isinstance(frame.get(k), bool) for k in PRESENCE):
            raise ValueError("presence flags missing")
        mapping[index] = frame
    return mapping


def _clip_binding(document):
    if "fixture_binding" not in document:
        return None
    binding = document["fixture_binding"]
    keys = {"schema", "clip_id", "source_video_sha256", "replay_manifest_sha256"}
    import re
    if (type(binding) is not dict or set(binding) != keys or
            binding.get("schema") != "kumpas-clip-binding-v1" or
            type(binding.get("clip_id")) is not str or
            re.fullmatch(r"clips_[0-9]+_[0-9]+\.npz", binding["clip_id"]) is None):
        raise ValueError("invalid clip binding")
    for key in ("source_video_sha256", "replay_manifest_sha256"):
        digest = binding[key]
        if type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError("invalid clip binding")
    return binding


def compare_vectors(python_doc: dict, android_doc: dict, *, require_clip_binding=False) -> dict:
    """Compare actual v1 producers; strict new fixtures additionally require a binding.

    Unbound historical documents support recorded frame-only diagnostics, never
    clip qualification. A companion binding must not be invented for old bytes.
    """
    reference, observed = _frame_map(python_doc), _frame_map(android_doc)
    left_binding, right_binding = _clip_binding(python_doc), _clip_binding(android_doc)
    if left_binding != right_binding or (require_clip_binding and left_binding is None):
        raise ValueError("clip identities missing or different")
    if reference.keys() != observed.keys():
        raise ValueError("frame indices differ between pipelines")
    ordered = sorted(reference)
    for index in ordered:
        if reference[index].get("sha256") != observed[index].get("sha256"):
            raise ValueError(f"frame image hash mismatch at index {index}")
    # Finite operands do not guarantee finite differences or reductions.
    # Reject overflow rather than clamp inputs or alter the existing math.
    try:
        with np.errstate(over="raise", invalid="raise"):
            errors = np.abs(np.asarray([reference[i]["features"] for i in ordered], dtype=np.float64) -
                            np.asarray([observed[i]["features"] for i in ordered], dtype=np.float64))
            block_mae = {k: float(errors[:, lo:hi].mean()) for k, (lo, hi) in BLOCKS.items()}
            block_max_abs = {k: float(errors[:, lo:hi].max()) for k, (lo, hi) in BLOCKS.items()}
    except FloatingPointError:
        raise ValueError("nonfinite comparison arithmetic") from None
    if (not np.isfinite(errors).all() or
            not all(math.isfinite(x) for x in (*block_mae.values(), *block_max_abs.values()))):
        raise ValueError("nonfinite comparison arithmetic")
    presence = {k: sum(reference[i][k] != observed[i][k] for i in ordered) for k in PRESENCE}
    report = {"matched_frames": len(ordered),
              "block_mae": block_mae,
              "block_max_abs": block_max_abs,
              "presence_disagreements": presence,
              "anatomical_left_right": "unverified",
              "reason": "No independently labeled anatomical hands or on-phone signer calibration.",
              "interpretation": "Feature errors include detector differences (Python Holistic vs Android pose+hands)."}
    report["clip_identity"] = "bound_v1" if left_binding is not None else "unbound_legacy_frames_only"
    # Actual Python references contain no classifier result. Native produces
    # attempt_result.predictedLabel (not prediction); arbitrary payload equality
    # is not evidence of equivalent class predictions. No inference in B1.
    report["prediction_comparison"] = "not_evaluated_feature_only"
    return report


def reference_from_vectors(raw: np.ndarray, manifest: dict) -> dict:
    """Apply the original training normalization, then drop the face channel."""
    from training.preprocessing.build_sequences import normalize
    frames = manifest.get("frames", [])
    if raw.ndim != 2 or raw.shape != (len(frames), 1662) or not frames:
        raise ValueError("reference frame count or 1662-feature shape mismatch")
    raw = raw.astype(np.float32, copy=False)
    normalized = normalize(raw)
    features = np.concatenate((normalized[:, :132], normalized[:, 1536:1662]), axis=1)
    rows = []
    for i, frame in enumerate(frames):
        if frame["index"] != i:
            raise ValueError("nonsequential frame index")
        rows.append({"index": i, "sha256": frame["sha256"],
                     "features": features[i].astype(float).tolist(),
                     "pose_seen": bool(np.any(raw[i, :132])),
                     "left_seen": bool(np.any(raw[i, 1536:1599])),
                     "right_seen": bool(np.any(raw[i, 1599:1662]))})
    return {"schema": "kumpas-feature-reference-v1", "extractor": "Python MediaPipe Holistic",
            "anatomical_left_right": "unverified", "frames": rows}


def generate_python_reference(frames_dir: Path, output_path: Path) -> dict:
    """Run Holistic VIDEO mode over exact replay PNGs in their listed order."""
    frames_dir = reject_symlinks(frames_dir)
    output_path = reject_symlinks(output_path)
    if output_path.exists():
        raise FileExistsError("output already exists")
    manifest = validate_replay(frames_dir)
    import cv2
    import mediapipe as mp
    from training.preprocessing.extract_landmarks import frame_vector
    raw = []
    detected_counts = np.zeros(4, dtype=np.int64)
    with mp.solutions.holistic.Holistic(static_image_mode=False,
                                        model_complexity=1,
                                        refine_face_landmarks=False) as holistic:
        for frame in manifest["frames"]:
            png = (frames_dir / frame["filename"]).read_bytes()
            if sha256_bytes(png) != frame["sha256"]:
                raise ValueError(f"frame image hash mismatch at {frame['index']}")
            bgr = cv2.imdecode(np.frombuffer(png, dtype=np.uint8), cv2.IMREAD_COLOR)
            if bgr is None:
                raise ValueError(f"PNG decode failed at {frame['index']}")
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            vector, detected = frame_vector(holistic.process(rgb))
            raw.append(vector)
            detected_counts += np.asarray(detected, dtype=np.int64)
    result = reference_from_vectors(np.stack(raw), manifest)
    result["detector_presence_counts"] = dict(zip(
        ("pose", "face", "left_hand", "right_hand"), detected_counts.tolist()))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise FileExistsError(output_path)
    output_path.write_text(json.dumps(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("video", type=Path)
    prepare.add_argument("output", type=Path)
    prepare.add_argument("--max-frames", type=int, default=None)
    reference = commands.add_parser("reference")
    reference.add_argument("frames_dir", type=Path)
    reference.add_argument("output", type=Path)
    compare = commands.add_parser("compare")
    compare.add_argument("python_json", type=Path)
    compare.add_argument("android_json", type=Path)
    compare.add_argument("output", type=Path)
    compare.add_argument("--legacy-frame-only", action="store_true",
                         help="explicit unbound historical frame diagnostics, not clip qualification")
    args = parser.parse_args()
    if args.command == "prepare":
        print(json.dumps({k: v for k, v in prepare_video(args.video, args.output, args.max_frames).items() if k != "frames"}, indent=2))
    elif args.command == "reference":
        result = generate_python_reference(args.frames_dir, args.output)
        print(f"Python Holistic reference: {len(result['frames'])} frames -> {args.output}")
    else:
        try:
            result = compare_vectors(json.loads(args.python_json.read_text()), json.loads(args.android_json.read_text()),
                                     require_clip_binding=not args.legacy_frame_only)
            serialized = json.dumps(result, indent=2, allow_nan=False)
            args.output.write_text(serialized)
        except (ValueError, OSError):
            print(json.dumps({"ok": False, "error": "comparison_failed"}, allow_nan=False))
            raise SystemExit(1)
        print(serialized)
