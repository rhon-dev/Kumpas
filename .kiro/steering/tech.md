# Technical Context — Kumpas

## Stack (Locked — No Substitutions Without PM Approval)

| Layer | Technology | Notes |
|-------|-----------|-------|
| Mobile app | Flutter (Dart), Android only | State management TBD in architecture spec |
| Landmark extraction | MediaPipe Holistic | Hand + face + pose landmarks |
| Model training | TensorFlow / Keras | CNN-LSTM architecture |
| On-device inference | TensorFlow Lite (quantized) | Post-training quantization baseline; QAT if needed |
| Training environment | Google Colab (GPU) | Free tier sufficient for FSL-105 scale |
| IDE / Dev environment | Kiro (steering + spec-driven workflow) | Replaces earlier VS Code + Cursor setup |
| Design | Figma (already delivered) | Future UI changes: Kiro generates from spec |
| Backend | None for MVP | Explicitly out of scope per SDLC kickoff |

## Architecture Overview

```
┌─────────────────────────────────┐
│  Training Pipeline (Python)     │  Google Colab, offline
│  - MediaPipe landmark extraction│
│  - Augmentation (seeded, logged)│
│  - CNN-LSTM training            │
│  - TFLite quantization + export │
└───────────────┬─────────────────┘
                │ exports: .tflite model + label map
                ▼
┌─────────────────────────────────┐
│  Kumpas Mobile App (Flutter)    │  Fully offline at runtime
│  - Camera capture (24–30 FPS)   │
│  - MediaPipe Holistic landmarks │
│  - TFLite inference (<150ms)    │
│  - Feedback Engine              │
│    (gold-standard comparison)   │
│  - Practice UI + session log    │
└─────────────────────────────────┘
```

## Key Technical Constraints

- **Offline-only at inference:** No network calls during normal app operation. Period.
- **Latency budget:** Camera frame → landmark extraction → model inference → feedback generation → UI render, all within 150ms total.
- **Device target:** Mid-range Android (Helio G / Snapdragon 6 series, 4GB RAM). Named test devices to be specified in mobile architecture spec.
- **Reproducibility:** Every training run records dataset version/hash, split seed, augmentation config, and architecture version alongside the checkpoint.
- **No raw video in repo:** Only extracted landmark sequences. .gitignore enforces this.

## Build & Run

```bash
# Training pipeline
python3 training/preprocessing/dataset_audit.py
python3 training/preprocessing/extract_landmarks.py --dataset-dir "../FSL-105 ..."
python3 training/augmentation/augment_landmarks.py
python3 training/models/train_cnn_lstm.py

# TFLite export
python3 training/tflite_export/export_tflite.py

# Flutter app
cd app && flutter run

# Benchmarking
python3 benchmarking/run_benchmarks.py
```
