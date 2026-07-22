# Phase 1 — Project Brief

## System Name

**Kumpas** — Real-time Filipino Sign Language Gesture Recognition with Corrective Feedback

## Problem Statement

Filipino Sign Language (FSL) learners — both Deaf/hard-of-hearing individuals and hearing people studying FSL — currently rely on static, one-way references (videos, picture dictionaries, in-person instructors) with no automated mechanism to verify whether their own sign execution is correct.

Existing sign-language recognition research largely stops at classification: the system identifies "this is sign X" but does not tell the learner what specifically is wrong with their attempt. The learner receives a binary correct/incorrect signal (at best) with no guidance on how to improve.

Kumpas addresses this gap: real-time, fully offline, on-device recognition that classifies the attempted sign against a gold-standard reference and produces **specific corrective feedback** across four dimensions — handshape, orientation, motion path, and timing.

## Thesis Contribution (Novelty Claim)

The thesis does NOT claim novelty in:
- Sign language classification using deep learning (established)
- CNN-LSTM architectures for sequential gesture recognition (established)
- MediaPipe landmark extraction (existing tool)
- TFLite on-device inference (existing framework)

The thesis DOES claim novelty in:
- **The corrective-feedback layer:** A real-time, per-dimension feedback system that compares a learner's sign execution against a gold-standard reference and generates actionable correction guidance across handshape, orientation, motion, and timing — running entirely on-device for FSL.

This is the distinction the thesis panel will scrutinize. Every architectural decision should protect and serve this claim.

## Target Users

| User | Primary Need | Interaction |
|------|-------------|-------------|
| Hearing FSL learners | Immediate practice feedback without an instructor | Signs in front of camera, receives per-dimension corrections |
| Deaf/HoH FSL learners | Refine sign accuracy with objective measurement | Same practice flow |
| FSL Expert/Validator | Validate gold-standard reference accuracy | Reviews reference clips/landmarks for correctness |
| Researcher | Analyze learning outcomes (pre/post study) | Accesses evaluation data through study tooling |

## Success Criteria (Measurable)

| Criterion | Target | Measurement Point |
|-----------|--------|-------------------|
| Test accuracy | ≥90% | Post-quantization, on held-out data, measured with the deployed .tflite model |
| Inference latency | <150ms | End-to-end (frame → landmark → inference → feedback → render), on named mid-range device |
| Frame rate | 24–30 FPS | Sustained during live camera capture on target hardware |
| Feedback coverage | 100% of MVP signs | Each of the 50 signs has ≥1 gold-standard reference with worked feedback examples |
| Evaluation study | Statistically sound pre/post comparison | Completed with documented methodology and results |
| Release readiness | Installs and runs full flow | On every device in test matrix without crash |

## Constraints

- **Fully offline at inference:** Zero network calls during normal app operation.
- **Android only:** No iOS for MVP.
- **FSL only:** No ASL, ISL, or other sign languages.
- **Isolated signs only:** Single-sign recognition; not continuous/sentence-level.
- **50-sign vocabulary:** Closed set selected from FSL-105.
- **No backend:** No cloud sync, accounts, or server-side processing.
- **Reproducibility:** Every reported number must be traceable to a specific model checkpoint, dataset version, and device.
- **Privacy:** No raw video committed to repo; RA 10173 compliance for any participant data.

## Out of Scope (Explicit)

- Full FSL-105 vocabulary beyond the 50-sign subset
- Cloud sync, accounts, backend, or any server-side component
- iOS support
- ASL or any non-FSL sign language
- Open-vocabulary / continuous sentence-level recognition
- Two-way communication / sign-to-speech translation
- Gamification, leaderboards, social features
- 3D avatar/skeleton overlay correction
- Play Store public distribution (internal/defense distribution only)
- Adaptive/personalized learning paths beyond the corrective-feedback loop itself

## Architecture Summary

```
Training Pipeline (Python/Colab, offline)
  └─ FSL-105 raw video → MediaPipe landmarks → augmentation → CNN-LSTM training → TFLite export
       │
       ▼ exports .tflite + label map + gold-standard references
       
Kumpas Mobile App (Flutter/Android, fully offline)
  └─ Camera (24–30 FPS) → MediaPipe Holistic → TFLite inference (<150ms) → Feedback Engine → UI
```

## Risk Summary (Top 5)

1. **Post-quantization accuracy drop** — validate on quantized model specifically, not just float32.
2. **Feedback thresholds lack justification** — require worked examples and empirical/literature-based thresholds at Phase 10 gate.
3. **Device fragmentation** — benchmark on named devices, not just "mid-range Android."
4. **Evaluation study underpowered** — flag for statistician review if needed.
5. **Class imbalance** — audit confirmed, mitigation applied (augmentation + class weighting).

## Current Status

Substantial implementation already exists (per phase-gates.md, Phases 0–7 of old numbering complete). This project brief formalizes the scope and contribution for the Kiro SDLC framework. Remaining work: formal benchmarking harness, real-device validation, privacy verification, evaluation study, and release build.
