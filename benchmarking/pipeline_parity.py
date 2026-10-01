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


def prepare_video(video_path: Path, output_dir: Path, max_frames: int | None = None) -> dict:
    import cv2
    video_path = Path(video_path)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"cannot decode video: {video_path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frames = []
    try:
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            frames.append(bgr)
    finally:
        cap.release()
    indices = select_frame_indices(len(frames), max_frames)
    manifest = write_frames([frames[i] for i in indices], output_dir, indices)
    manifest["source_video_sha256"] = sha256_bytes(video_path.read_bytes())
    manifest["source_fps"] = fps
    manifest["decoded_frames"] = len(frames)
    manifest["sampling"] = "all" if max_frames is None else f"uniform-{max_frames}; detector tracking differs from full-video training extraction"
    (Path(output_dir) / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def _frame_map(document: dict) -> dict:
    rows = document.get("frames", [])
    if not rows:
        raise ValueError("frame list empty")
    mapping = {}
    for frame in rows:
        index = frame.get("index")
        if index in mapping or not isinstance(index, int):
            raise ValueError("duplicate or invalid frame index")
        features = frame.get("features")
        if not isinstance(features, list) or len(features) != 258:
            raise ValueError("each feature vector must have 258 floats")
        if any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in features):
            raise ValueError("nonfinite or nonnumeric feature")
        if not all(isinstance(frame.get(k), bool) for k in PRESENCE):
            raise ValueError("presence flags missing")
        mapping[index] = frame
    return mapping


def compare_vectors(python_doc: dict, android_doc: dict) -> dict:
    reference, observed = _frame_map(python_doc), _frame_map(android_doc)
    if reference.keys() != observed.keys():
        raise ValueError("frame indices differ between pipelines")
    ordered = sorted(reference)
    for index in ordered:
        if reference[index].get("sha256") != observed[index].get("sha256"):
            raise ValueError(f"frame image hash mismatch at index {index}")
    errors = np.abs(np.asarray([reference[i]["features"] for i in ordered], dtype=np.float64) -
                    np.asarray([observed[i]["features"] for i in ordered], dtype=np.float64))
    presence = {k: sum(reference[i][k] != observed[i][k] for i in ordered) for k in PRESENCE}
    report = {"matched_frames": len(ordered),
              "block_mae": {k: float(errors[:, lo:hi].mean()) for k, (lo, hi) in BLOCKS.items()},
              "block_max_abs": {k: float(errors[:, lo:hi].max()) for k, (lo, hi) in BLOCKS.items()},
              "presence_disagreements": presence,
              "anatomical_left_right": "unverified",
              "reason": "No independently labeled anatomical hands or on-phone signer calibration.",
              "interpretation": "Feature errors include detector differences (Python Holistic vs Android pose+hands)."}
    if "prediction" in python_doc and "prediction" in android_doc:
        report["prediction_agreement"] = python_doc["prediction"] == android_doc["prediction"]
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
    import cv2
    import mediapipe as mp
    from training.preprocessing.extract_landmarks import frame_vector
    frames_dir = Path(frames_dir)
    manifest = json.loads((frames_dir / "manifest.json").read_text())
    if manifest.get("schema") != "kumpas-replay-v1":
        raise ValueError("unsupported replay manifest")
    raw = []
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
            raw.append(frame_vector(holistic.process(rgb))[0])
    result = reference_from_vectors(np.stack(raw), manifest)
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
    args = parser.parse_args()
    if args.command == "prepare":
        print(json.dumps({k: v for k, v in prepare_video(args.video, args.output, args.max_frames).items() if k != "frames"}, indent=2))
    elif args.command == "reference":
        result = generate_python_reference(args.frames_dir, args.output)
        print(f"Python Holistic reference: {len(result['frames'])} frames -> {args.output}")
    else:
        result = compare_vectors(json.loads(args.python_json.read_text()), json.loads(args.android_json.read_text()))
        args.output.write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
