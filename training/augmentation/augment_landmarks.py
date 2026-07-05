#!/usr/bin/env python3
"""KUMPAS Phase 1 — geometric augmentation in landmark space.

Applies the methodology's geometric augmentations to the TRAIN split only
(never test): per-sample random in-plane rotation ±10–15°, scale 0.90–1.10,
x/y shift ±0.10 (in normalized landmark units). Brightness 80–120% is a
pixel-space augmentation and is handled at extraction time instead
(extract_landmarks.py --brightness) — landmarks carry no photometry.

Reproducibility (Data Agent rule, PRD §7): the RNG is seeded and every
per-sample transform (angle, scale, dx, dy) is written to augment_log.json.
Re-running with the same seed reproduces identical arrays.

Input : <data-root>/sequences/X_train.npy, y_train.npy  (build_sequences.py)
Output: <data-root>/sequences/X_train_aug.npy, y_train_aug.npy
        (originals + factor× augmented copies, shuffled consistently),
        training/augmentation/augment_log.json (committed)

Usage:
    ../.venv/bin/python augment_landmarks.py [--factor 3] [--seed 20260705]
"""

import argparse
import json
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT.parent / "kumpas-data"
LOG_PATH = Path(__file__).resolve().parent / "augment_log.json"

POSE, FACE = 33 * 4, 468 * 3

ROT_RANGE = (10.0, 15.0)      # degrees, magnitude; sign randomized
SCALE_RANGE = (0.90, 1.10)
SHIFT_RANGE = (-0.10, 0.10)   # normalized landmark units


def transform(seq, angle_deg, scale, dx, dy):
    """Rotate (in xy-plane about origin), scale, shift all landmarks of (T, F) seq.

    Landmarks are already root-centered by build_sequences.py, so rotating
    about the origin rotates about the signer's mid-hip. Zero-filled missing
    blocks stay zero except for the shift — so shift is applied only to
    non-zero blocks, keeping "missing" encoded as all-zeros.
    """
    out = seq.copy()
    a = np.deg2rad(angle_deg)
    rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], dtype=np.float32)

    def apply(block, n_pts, dims):
        pts = block.reshape(len(out), n_pts, dims).copy()
        missing = (np.abs(pts).sum(axis=(1, 2)) == 0)  # per-frame missing block
        xy = pts[:, :, :2]
        pts[:, :, :2] = (xy @ rot.T) * scale + np.array([dx, dy], dtype=np.float32)
        if dims > 2:
            pts[:, :, 2] = pts[:, :, 2] * scale  # z scales, no in-plane rotation effect
        pts[missing] = 0.0
        return pts.reshape(len(out), n_pts * dims)

    out[:, :POSE] = apply(out[:, :POSE], 33, 4)
    if out.shape[1] == 1662:  # full features
        out[:, POSE:POSE + FACE] = apply(out[:, POSE:POSE + FACE], 468, 3)
        out[:, POSE + FACE:] = apply(out[:, POSE + FACE:], 42, 3)
    else:  # no_face variant (258)
        out[:, POSE:] = apply(out[:, POSE:], 42, 3)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    ap.add_argument("--sequences-subdir", default="sequences")
    ap.add_argument("--factor", type=int, default=3,
                    help="augmented copies per original train sample")
    ap.add_argument("--seed", type=int, default=20260705)
    args = ap.parse_args()

    seq_dir = args.data_root / args.sequences_subdir
    X = np.load(seq_dir / "X_train.npy")
    y = np.load(seq_dir / "y_train.npy")
    rng = np.random.default_rng(args.seed)

    Xs, ys, log_rows = [X], [y], []
    for k in range(args.factor):
        for i in range(len(X)):
            sign = rng.choice([-1.0, 1.0])
            angle = sign * rng.uniform(*ROT_RANGE)
            scale = rng.uniform(*SCALE_RANGE)
            dx, dy = rng.uniform(*SHIFT_RANGE), rng.uniform(*SHIFT_RANGE)
            Xs.append(transform(X[i], angle, scale, dx, dy)[None])
            log_rows.append({"copy": k, "orig_index": i, "class": int(y[i]),
                             "angle_deg": round(float(angle), 3),
                             "scale": round(float(scale), 4),
                             "dx": round(float(dx), 4), "dy": round(float(dy), 4)})
        ys.append(y)

    X_aug = np.concatenate(Xs)
    y_aug = np.concatenate(ys)
    perm = rng.permutation(len(y_aug))
    X_aug, y_aug = X_aug[perm], y_aug[perm]

    np.save(seq_dir / "X_train_aug.npy", X_aug.astype(np.float32))
    np.save(seq_dir / "y_train_aug.npy", y_aug)
    LOG_PATH.write_text(json.dumps({
        "seed": args.seed, "factor": args.factor,
        "rotation_deg_range": ROT_RANGE, "scale_range": SCALE_RANGE,
        "shift_range": SHIFT_RANGE,
        "n_original": int(len(y)), "n_output": int(len(y_aug)),
        "note": "brightness 80-120% handled in pixel space at extraction "
                "(extract_landmarks.py --brightness); test split never augmented",
        "transforms": log_rows,
    }, indent=1))
    print(f"train {X.shape} -> augmented {X_aug.shape}; log -> {LOG_PATH.name}")


if __name__ == "__main__":
    main()
