# KUMPAS

Real-time Filipino Sign Language (FSL) gesture recognition with corrective feedback — thesis project.

A learner signs in front of the phone camera; an on-device quantized CNN-LSTM model (MediaPipe Holistic landmarks → TFLite) classifies the sign against a validated gold standard and tells the learner what to fix: handshape, orientation, motion, or timing. Android only, fully offline at inference time.

## Start here

- [docs/PRD.md](docs/PRD.md) — full development plan: scope, architecture, phases, roles
- [docs/phase-gates.md](docs/phase-gates.md) — where the project currently is
- [docs/dataset-notes.md](docs/dataset-notes.md) — FSL-105 dataset findings
- [AGENTS.md](AGENTS.md) — context for AI coding agents (read before any task)

## Layout

| Path | Contents |
|------|----------|
| `training/` | Python pipeline: preprocessing, augmentation, model experiments, TFLite export, Colab notebooks |
| `app/` | Flutter app (Android) |
| `benchmarking/` | Accuracy/latency/FPS test harnesses + results |
| `evaluation/` | Pre/post study statistics scripts |

## Dataset

FSL-105 (public, Mendeley 2023) — kept **outside** the repo, one directory up. Run the audit:

```bash
python3 training/preprocessing/dataset_audit.py
```

Performance targets: ≥90% test accuracy · <150ms inference · 24–30 FPS on mid-range Android.

## Known Limitations

Honest status as of 2026-09-23. These are the claims a reader should not take at face value yet, each traceable to an artifact in this repo. See [docs/phase-gates.md](docs/phase-gates.md) for the full gate-by-gate audit.

- **Performance numbers are emulator-only.** No physical device has ever run this app. The latency and FPS figures cited anywhere in the repo come from two retroactive entries in `benchmarking/benchmark_history.json`, both hand-seeded from an Android emulator on an Apple M1 host and both self-labelled `retroactive-estimate`. The latency figure (0–2ms) times the TFLite interpreter in isolation, while the same emulator report records MediaPipe landmarking at 35–63ms/frame — the dominant cost is excluded. The FPS window was 55s against the harness's own 60s minimum. Real mid-range-device measurement (Helio G / Snapdragon 6, 4GB) is pending.
- **The FSL Expert sign-off is not evidenced in the repo.** `docs/phase-gates.md` previously claimed expert validation of all 50 gold standards was complete. The only validation artifact, `docs/phase10-expert-validation-protocol.md`, is a blank template: no date, no expert name, empty ratings. A session may have happened offline, but the repo cannot show it. Feedback correctness on handshape and orientation therefore rests on an unverified sign-off.
- **The numerals are weak, and the headline accuracy hides it.** The 95.07% aggregate masks a semantic family that is near-unusable: FIVE has an F1 of 0.333 (recall 0.25), FOUR 0.600, THREE 0.667, TWO 0.800. The four signs that differ only by handshape are the four worst classes.
- **The test set is small (n=203).** 203 clips across 50 classes is roughly 4 per class, with no confidence interval reported and one training run showing validation accuracy 1.0. The accuracy claim should be read as "≥90% on this held-out split," not as a tight estimate. Growing or cross-validating the test set is deferred work.
- **Train–serve skew: the app does not run MediaPipe Holistic.** The stack is locked to MediaPipe Holistic (hand + face + pose) and the model was trained on Holistic landmarks, but the shipped Android pipeline (`VisionEngine.kt`) runs `PoseLandmarker` + `HandLandmarker` only, at 258 features with no face channel. Training and serving use different landmark sources. Reconciling this (the "Holistic v2" question) is unapproved, out of current scope, and tracked separately.
