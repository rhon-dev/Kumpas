#!/usr/bin/env python3
"""KUMPAS Phase 6 — provisional gold-standard selection.

FSL-105 ships no flagged gold-standard clips, so for each of the 50 classes
this picks the MEDOID of its training sequences: the clip with the smallest
mean distance to all other clips of the same class — the most "typical"
execution. Output is marked provisional pending expert validation of each
chosen clip (PRD §9 provenance rule).

Output: ../kumpas-data/feedback/gold_standards.npz
            gold      (50, 30, 258)  one normalized sequence per class
            class_ids (50,)          dense label ids 0..49
        gold_standards_manifest.json (committed) — which source clip was
            chosen per class, with its medoid distance.

Usage:
    ~/.kumpas-venvs/tf/bin/python build_gold_standards.py
"""

import json
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SEQ_DIR = REPO_ROOT.parent / "kumpas-data" / "sequences"
OUT_DIR = REPO_ROOT.parent / "kumpas-data" / "feedback"
MANIFEST = Path(__file__).resolve().parent / "gold_standards_manifest.json"

POSE, FACE = 132, 1404
KEEP = np.r_[0:POSE, POSE + FACE:1662]  # no_face feature indices


def main():
    X = np.load(SEQ_DIR / "X_train.npy")[:, :, KEEP]  # raw (non-augmented) train
    y = np.load(SEQ_DIR / "y_train.npy")
    clips = json.loads((SEQ_DIR / "clips_train.json").read_text())
    label_map = {int(k): v for k, v in
                 json.loads((SEQ_DIR / "label_map.json").read_text()).items()}

    gold, manifest = [], {}
    for cid in range(50):
        idx = np.where(y == cid)[0]
        seqs = X[idx].reshape(len(idx), -1)
        d = np.linalg.norm(seqs[:, None, :] - seqs[None, :, :], axis=2)
        medoid_local = int(d.mean(axis=1).argmin())
        gold.append(X[idx[medoid_local]])
        manifest[str(cid)] = {
            "label": label_map[cid]["label"],
            "source_clip": clips[idx[medoid_local]],
            "mean_distance_to_class": round(float(d.mean(axis=1)[medoid_local]), 3),
            "n_candidates": int(len(idx)),
            "status": "provisional — medoid pick, pending expert validation",
        }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT_DIR / "gold_standards.npz",
                        gold=np.stack(gold).astype(np.float32),
                        class_ids=np.arange(50))
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    print(f"gold standards: {np.stack(gold).shape} -> {OUT_DIR / 'gold_standards.npz'}")
    print(f"manifest -> {MANIFEST.name}")


if __name__ == "__main__":
    main()
