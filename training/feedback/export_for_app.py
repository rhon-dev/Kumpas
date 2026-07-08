#!/usr/bin/env python3
"""Export gold standards + parity fixtures for the Kotlin feedback engine.

1. gold_standards.bin — raw float32 little-endian, class-major
   (50 * 30 * 258 floats). Loaded by FeedbackEngine.kt from app assets.
2. Parity fixtures (app/android/app/src/test/resources/feedback_case_*.json):
   real wrong-attempt sequences + the Python engine's output. The Kotlin
   JVM unit test replays them and must flag the same dimensions with
   severities within tolerance — keeps the port honest (PRD: feedback math
   is high-risk, dual implementations must not drift).

Usage:
    ~/.kumpas-venvs/tf/bin/python export_for_app.py
"""

import json
from pathlib import Path

import numpy as np

from feedback_engine import compare

REPO_ROOT = Path(__file__).resolve().parents[2]
SEQ_DIR = REPO_ROOT.parent / "kumpas-data" / "sequences"
GOLD_NPZ = REPO_ROOT.parent / "kumpas-data" / "feedback" / "gold_standards.npz"
ASSETS = REPO_ROOT / "app" / "android" / "app" / "src" / "main" / "assets"
TEST_RES = REPO_ROOT / "app" / "android" / "app" / "src" / "test" / "resources"

POSE, FACE = 132, 1404
KEEP = np.r_[0:POSE, POSE + FACE:1662]


def main():
    gold = np.load(GOLD_NPZ)["gold"].astype("<f4")  # (50, 30, 258) LE
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "gold_standards.bin").write_bytes(gold.tobytes(order="C"))
    print(f"gold_standards.bin: {gold.nbytes / 1e6:.1f} MB -> assets/")

    labels = {v["label"]: int(k) for k, v in
              json.loads((SEQ_DIR / "label_map.json").read_text()).items()}
    X = np.load(SEQ_DIR / "X_test.npy")[:, :, KEEP]
    y = np.load(SEQ_DIR / "y_test.npy")

    def clip(name, nth=0):
        return X[np.where(y == labels[name])[0][nth]]

    cases = [
        ("case_confused_pair", "THANK YOU", clip("YOURE WELCOME")),
        ("case_handshape", "FOUR", clip("FIVE")),
        ("case_correct", "HELLO", clip("HELLO", 1)),
    ]
    TEST_RES.mkdir(parents=True, exist_ok=True)
    for fname, target, attempt in cases:
        rep = compare(attempt, gold[labels[target]], target)
        (TEST_RES / f"feedback_{fname}.json").write_text(json.dumps({
            "target_class": labels[target],
            "target_label": target,
            "attempt": [[round(float(v), 6) for v in row] for row in attempt],
            "expected_overall_match": rep.overall_match,
            "expected_items": [{"dimension": i.dimension, "hand": i.hand,
                                "severity": i.severity} for i in rep.items],
        }))
        print(f"{fname}: {len(rep.items)} expected items, match {rep.overall_match}")


if __name__ == "__main__":
    main()
