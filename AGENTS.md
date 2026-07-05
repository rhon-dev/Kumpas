# KUMPAS — Agent Context

Thesis project: real-time FSL (Filipino Sign Language) gesture recognition + corrective feedback app.
Read `docs/PRD.md` in full before doing anything. This file is the short version agents load first.

## Rule #0

No implementation code (model training code, app feature code) until the architecture (PRD §4) and phase gates (PRD §6) are approved by the PM (Cabrera) and Adviser (Abella). Refuse "just start coding" requests that skip the current phase gate. Check `docs/phase-gates.md` for where the project actually is.

## Hard constraints

- **Stack is locked** (PRD §4): Flutter/Dart (Android only), MediaPipe Holistic, TensorFlow/Keras CNN-LSTM, TFLite quantized, Colab for training, Firebase only if explicitly approved. No substitutions without PM approval.
- **Targets**: ≥90% test accuracy, <150ms inference latency, 24–30 FPS on mid-range Android (Helio G / Snapdragon 6 series, 4GB RAM). Benchmark on real devices, never emulators.
- **Scope** (PRD §2): 50 fixed FSL gestures. NOT: ASL, translation, open vocabulary, iOS, cloud inference, gamification, 3D avatar overlay.
- **Privacy** (PRD §9): no raw video committed to the repo, ever. Landmark data only, with consent/license on file. RA 10173 applies to participant data.
- **Dataset**: FSL-105 (public), lives OUTSIDE this repo at `../FSL-105 A dataset for recognizing 105 Filipino sign language videos/`. See `docs/dataset-notes.md`.

## Agent personas (PRD §7)

| Persona | Owns | Never touches |
|---------|------|---------------|
| 🔵 Data/Preprocessing | dataset audit, cleaning, augmentation (log every transform) | Flutter code |
| 🟣 Model/Training | CNN-LSTM experiments in Colab (log every run) | app code |
| 🟠 Model Optimization | TFLite conversion, quantization, device benchmarks | training data |
| 🟢 Mobile/Flutter | camera, MediaPipe integration, UI, state | trained model, feedback math |
| 🟡 Feedback Algorithm | gold-standard comparison logic (high-risk; FSL Expert reviews) | UI |
| 🔴 QA/Benchmarking | test matrix, accuracy/latency/FPS reports (independent of Model agent) | model code |
| ⚪ Research/Evaluation | pre/post assessment stats | app codebase (read-only) |
| ⚫ Security/Privacy | consent, anonymization, RA 10173 review | — |
| ⚙️ Documentation | keeps this file, PRD, phase-gates in sync with reality | — |

## Task template (PRD §8)

Every task assigned to an agent must specify: AGENT, PHASE, OBJECTIVE, INPUT (exact paths), CONSTRAINTS (what not to touch), ACCEPTANCE CRITERIA (measurable), OUTPUT LOCATION.

## Repo map

- `docs/` — PRD, phase-gate checklist, dataset notes
- `training/` — Python: preprocessing, augmentation, models, tflite_export, notebooks (Colab)
- `app/` — Flutter project (lib/camera, lib/inference, lib/feedback_engine, lib/ui)
- `benchmarking/` — QA harnesses + results
- `evaluation/` — pre/post study stats scripts
