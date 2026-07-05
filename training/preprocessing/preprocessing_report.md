# Phase 1 Preprocessing Report

Generated 2026-07-05. Pipeline: `extract_landmarks.py` -> `build_sequences.py` -> `augment_landmarks.py`.

## Extraction (MediaPipe Holistic, mediapipe==0.10.14)

- Clips processed: **1016** (50 classes, train+test), errors: **0**
- Frames per clip: min 242, median 244, max 246
- Mean detection rates: pose 1.000, any-hand 0.352
- Clips with any-hand rate < 10% (weak hand visibility — review before Phase 3 error analysis): **2**
  - `5/3.MOV` class 5 (0.099)
  - `5/4.MOV` class 5 (0.091)
- Full log: `extraction_log.csv`. Landmark arrays (1.3GB) live outside the repo in `../kumpas-data/landmarks/`.

## Sequences (`build_sequences.py`)

- seq_len 30, features 1662 (full: pose 132 + face 1404 + hands 126)
- Normalization: mid-hip root-centered, torso-scaled, per frame; missing detections stay zero-filled
- X_train (813, 30, 1662) / X_test (203, 30, 1662) — split preserved from FSL-105 CSVs, never reshuffled
- Degenerate clips skipped: 0

## Augmentation (`augment_landmarks.py`, train split only)

- Seed 20260705, factor 3: 813 -> 3252 samples
- Geometric in landmark space: rotation +/-10-15 deg, scale 0.90-1.10, shift +/-0.10; every transform logged in `../augmentation/augment_log.json` (replayable)
- Brightness 80-120% is pixel-domain: available via `extract_landmarks.py --brightness` (not run for baseline; note for methodology chapter)
- Test split untouched

## Handoff to Phase 2

`../kumpas-data/kumpas_sequences.zip` (721MB) -> upload to Google Drive `MyDrive/kumpas/` -> run `training/notebooks/kumpas_cnn_lstm_training.ipynb` in Colab.
