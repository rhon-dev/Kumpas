#!/usr/bin/env python3
"""KUMPAS Phase 1 — build fixed-length training sequences from extracted landmarks.

Turns per-clip .npz landmark files (extract_landmarks.py output) into
fixed-length, normalized arrays ready for CNN-LSTM training in Colab:

    X_train.npy (N, T, F) float32     y_train.npy (N,) int64
    X_test.npy  (M, T, F)             y_test.npy  (M,)
    label_map.json                    {"0": {"label": ..., "orig_id": ...}, ...}

Train/test split is taken from the clip metadata (which preserved the FSL-105
CSV split) — never re-shuffled here.

Temporal: uniform sampling of T frames across the clip (long clips are
subsampled, short clips pad by repeating the last frame).

Normalization (per frame, landmark space):
  - translate so the pose root (mid-hip, pose landmarks 23/24) is the origin
  - scale by torso size (mid-hip to mid-shoulder distance) so signer distance
    from camera doesn't matter
  - x/y/z only; pose visibility values are kept unscaled

Features: --features full (1662) keeps pose+face+hands as extracted;
--features no_face (258) drops the 1404 face values — documented latency
fallback for Phase 4 quantization if the full model misses the <150ms target.

Usage:
    ../.venv/bin/python build_sequences.py [--seq-len 30] [--features full]
"""

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT.parent / "kumpas-data"
SELECTED_JSON = Path(__file__).resolve().parent / "selected_classes.json"

POSE, FACE, HANDS = 33 * 4, 468 * 3, 2 * 21 * 3  # 132, 1404, 126
# pose landmark indices (x,y,z,vis blocks of 4)
L_SHOULDER, R_SHOULDER, L_HIP, R_HIP = 11, 12, 23, 24


def sample_indices(n_frames, seq_len):
    if n_frames >= seq_len:
        return np.linspace(0, n_frames - 1, seq_len).round().astype(int)
    idx = np.arange(n_frames)
    return np.concatenate([idx, np.full(seq_len - n_frames, n_frames - 1, dtype=int)])


def normalize(seq):
    """seq (T, 1662) -> root-centered, torso-scaled, in place semantics kept."""
    out = seq.copy()
    pose = out[:, :POSE].reshape(len(out), 33, 4)
    xyz = pose[:, :, :3]

    root = (xyz[:, L_HIP] + xyz[:, R_HIP]) / 2  # (T, 3)
    neck = (xyz[:, L_SHOULDER] + xyz[:, R_SHOULDER]) / 2
    scale = np.linalg.norm(neck - root, axis=1, keepdims=True)  # (T, 1)
    # frames with no pose detection are all-zeros: keep them zeros
    dead = (np.abs(pose).sum(axis=(1, 2)) == 0)
    scale[scale < 1e-4] = 1.0

    def norm_block(block, n_pts, dims):
        pts = block.reshape(len(out), n_pts, dims)
        pts[:, :, :3] = (pts[:, :, :3] - root[:, None, :]) / scale[:, None, :]
        pts[dead] = 0.0
        return pts.reshape(len(out), n_pts * dims)

    out[:, :POSE] = norm_block(out[:, :POSE], 33, 4)
    out[:, POSE:POSE + FACE] = norm_block(out[:, POSE:POSE + FACE], 468, 3)
    out[:, POSE + FACE:] = norm_block(out[:, POSE + FACE:], 42, 3)

    # zero-filled missing face/hand blocks got shifted by -root/scale; restore zeros
    for lo, hi, npts in ((POSE, POSE + FACE, 468),
                         (POSE + FACE, POSE + FACE + 63, 21),
                         (POSE + FACE + 63, POSE + FACE + 126, 21)):
        block = seq[:, lo:hi].reshape(len(seq), npts, 3)
        missing = (np.abs(block).sum(axis=(1, 2)) == 0)
        out[missing, lo:hi] = 0.0
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    ap.add_argument("--landmarks-subdir", default="landmarks",
                    help="input subdir under data-root (e.g. landmarks_bright_0.8)")
    ap.add_argument("--out-subdir", default="sequences")
    ap.add_argument("--seq-len", type=int, default=30)
    ap.add_argument("--features", choices=["full", "no_face"], default="full")
    args = ap.parse_args()

    with open(SELECTED_JSON, encoding="utf-8") as f:
        selected = json.load(f)["selected"]
    # dense label ids 0..49 sorted by original id, mapping saved alongside arrays
    label_map = {new: c for new, c in enumerate(sorted(selected, key=lambda c: c["id"]))}
    orig_to_new = {c["id"]: new for new, c in label_map.items()}

    in_dir = args.data_root / args.landmarks_subdir
    files = sorted(in_dir.glob("*.npz"))
    if not files:
        raise SystemExit(f"no .npz files in {in_dir}")

    data = {"train": ([], [], []), "test": ([], [], [])}  # X, y, clip names
    skipped = []
    for f in files:
        d = np.load(f)
        arr, cid, split = d["landmarks"], int(d["class_id"]), str(d["split"])
        if cid not in orig_to_new:
            continue
        if arr.shape[0] < 5:  # degenerate decode
            skipped.append(f.name)
            continue
        seq = normalize(arr[sample_indices(arr.shape[0], args.seq_len)])
        if args.features == "no_face":
            seq = np.concatenate([seq[:, :POSE], seq[:, POSE + FACE:]], axis=1)
        X, y, names = data[split]
        X.append(seq.astype(np.float32))
        y.append(orig_to_new[cid])
        names.append(f.name)

    out_dir = args.data_root / args.out_subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {"seq_len": args.seq_len, "features": args.features,
               "n_features": None, "skipped_degenerate": skipped,
               "source_subdir": args.landmarks_subdir}
    for split, (X, y, names) in data.items():
        X, y = np.stack(X), np.array(y, dtype=np.int64)
        np.save(out_dir / f"X_{split}.npy", X)
        np.save(out_dir / f"y_{split}.npy", y)
        (out_dir / f"clips_{split}.json").write_text(json.dumps(names, indent=1))
        summary["n_features"] = int(X.shape[2])
        summary[f"n_{split}"] = int(len(y))
        summary[f"class_counts_{split}"] = dict(sorted(Counter(y.tolist()).items()))
        print(f"{split}: X{X.shape} y{y.shape} classes={len(set(y.tolist()))}")

    (out_dir / "label_map.json").write_text(json.dumps(
        {str(k): v for k, v in label_map.items()}, indent=1, ensure_ascii=False))
    (out_dir / "build_summary.json").write_text(json.dumps(summary, indent=1))
    print(f"wrote arrays + label_map.json + build_summary.json -> {out_dir}")
    if skipped:
        print(f"skipped degenerate clips: {skipped}")


if __name__ == "__main__":
    main()
