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
