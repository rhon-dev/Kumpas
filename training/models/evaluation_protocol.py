#!/usr/bin/env python3
"""Versioned original-clip partitions and fit-only landmark augmentation.

Historical sequence arrays are read-only. New arrays live in a separate protocol
folder; the old augmented arrays and reports are never overwritten.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "training" / "augmentation"))
from augment_landmarks import ROT_RANGE, SCALE_RANGE, SHIFT_RANGE, transform

VERSION = "evaluation-v1"
SEED = 20260705
SOURCE_FILES = ("X_train.npy", "y_train.npy", "clips_train.json", "clips_test.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_digest(manifest: dict) -> str:
    return hashlib.sha256(json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _source(seq_dir: Path):
    seq_dir = Path(seq_dir)
    X = np.load(seq_dir / "X_train.npy", mmap_mode="r", allow_pickle=False)
    y = np.load(seq_dir / "y_train.npy", allow_pickle=False)
    names = json.loads((seq_dir / "clips_train.json").read_text())
    tests = json.loads((seq_dir / "clips_test.json").read_text())
    if X.ndim != 3 or y.ndim != 1 or len(X) != len(y) or len(y) != len(names):
        raise ValueError("source array/name length or shape mismatch")
    if len(set(names)) != len(names) or len(set(tests)) != len(tests):
        raise ValueError("duplicate clip name")
    if set(names) & set(tests):
        raise ValueError("original train/test clip overlap")
    if not all(isinstance(name, str) and name for name in names + tests):
        raise ValueError("clip names must be nonempty strings")
    if not np.issubdtype(y.dtype, np.integer) or (y < 0).any():
        raise ValueError("invalid class labels")
    return X, y, names


def build_manifest(seq_dir: Path, seed: int = SEED, fraction: float = 0.2) -> dict:
    seq_dir = Path(seq_dir)
    if not 0 < fraction < 1:
        raise ValueError("validation fraction must be between zero and one")
    X, y, names = _source(seq_dir)
    rng = np.random.default_rng(seed)
    partition = ["fit"] * len(names)
    for class_id in sorted(set(y.tolist())):
        indices = np.flatnonzero(y == class_id)
        if len(indices) < 3:
            raise ValueError(f"class {class_id} needs at least three originals")
        n_val = min(len(indices) - 1, max(2, round(len(indices) * fraction)))
        for index in rng.permutation(indices)[:n_val]:
            partition[int(index)] = "validation"
    rows = [{"index": i, "clip": name, "class_id": int(y[i]), "partition": partition[i]}
            for i, name in enumerate(names)]
    counts = {str(c): dict(Counter(partition[i] for i in range(len(y)) if y[i] == c))
              for c in sorted(set(y.tolist()))}
    return {"version": VERSION, "seed": seed, "validation_fraction": fraction,
            "algorithm": "stratified-original-clip-v1", "source_sha256":
            {name: sha256(seq_dir / name) for name in SOURCE_FILES},
            "n_fit_original": partition.count("fit"),
            "n_validation": partition.count("validation"),
            "class_counts": counts, "rows": rows}


def validate_manifest(manifest: dict, seq_dir: Path) -> None:
    seq_dir = Path(seq_dir)
    if manifest.get("version") != VERSION:
        raise ValueError("manifest version mismatch")
    for name in SOURCE_FILES:
        if manifest.get("source_sha256", {}).get(name) != sha256(seq_dir / name):
            raise ValueError(f"source digest mismatch: {name}")
    X, y, names = _source(seq_dir)
    rows = manifest.get("rows", [])
    if len(rows) != len(y):
        raise ValueError("manifest/source length mismatch")
    for i, row in enumerate(rows):
        if (row.get("index") != i or row.get("clip") != names[i] or
                row.get("class_id") != int(y[i]) or row.get("partition") not in ("fit", "validation")):
            raise ValueError(f"manifest row mismatch at index {i}")
    expected = build_manifest(seq_dir, manifest["seed"], manifest["validation_fraction"])
    if manifest != expected:
        raise ValueError("manifest partition or counts mismatch")


def build_protocol(seq_dir: Path, out_dir: Path, seed: int = SEED, factor: int = 3) -> dict:
    if factor < 0:
        raise ValueError("factor must be nonnegative")
    seq_dir, out_dir = Path(seq_dir), Path(out_dir)
    manifest = build_manifest(seq_dir, seed)
    validate_manifest(manifest, seq_dir)
    X, y, _ = _source(seq_dir)
    fit_indices = [r["index"] for r in manifest["rows"] if r["partition"] == "fit"]
    val_indices = [r["index"] for r in manifest["rows"] if r["partition"] == "validation"]
    out_dir.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(seed)
    fitted = [np.asarray(X[fit_indices], dtype=np.float32)]
    labels = [y[fit_indices]]
    provenance = []
    for copy in range(factor):
        transformed = []
        for index in fit_indices:
            sign = rng.choice([-1.0, 1.0])
            angle = float(sign * rng.uniform(*ROT_RANGE))
            scale = float(rng.uniform(*SCALE_RANGE))
            dx, dy = float(rng.uniform(*SHIFT_RANGE)), float(rng.uniform(*SHIFT_RANGE))
            transformed.append(transform(X[index], angle, scale, dx, dy))
            provenance.append({"source_clip": manifest["rows"][index]["clip"],
                               "source_index": index, "partition": "fit", "copy": copy,
                               "angle_deg": angle, "scale": scale, "dx": dx, "dy": dy})
        fitted.append(np.stack(transformed).astype(np.float32))
        labels.append(y[fit_indices])
    np.save(out_dir / "X_fit.npy", np.concatenate(fitted))
    np.save(out_dir / "y_fit.npy", np.concatenate(labels))
    np.save(out_dir / "X_val.npy", np.asarray(X[val_indices], dtype=np.float32))
    np.save(out_dir / "y_val.npy", y[val_indices])
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    (out_dir / "augmentations.json").write_text(json.dumps(provenance, indent=2))
    return {"n_fit_original": len(fit_indices), "n_validation": len(val_indices),
            "n_fit_augmented": len(fit_indices) * (factor + 1),
            "augmentations": provenance, "manifest_sha256": manifest_digest(manifest)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seq-dir", type=Path, default=REPO_ROOT.parent / "kumpas-data" / "sequences")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT.parent / "kumpas-data" / "sequences" / VERSION)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--factor", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps(build_protocol(args.seq_dir, args.out_dir, args.seed, args.factor), default=lambda o: str(o))[:250])
