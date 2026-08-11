# Product Context — Kumpas

## Problem

Filipino Sign Language (FSL) learners — both Deaf/hard-of-hearing and hearing people learning FSL — rely on static, one-way references (videos, picture dictionaries, in-person instructors) with no automated way to verify whether their own sign execution is correct. Existing sign-language recognition research stops at classification ("this is sign X") without telling the learner what specifically is wrong.

## Thesis Contribution (Novelty Claim)

Kumpas's novel contribution is **not** sign classification itself, but the **corrective-feedback layer** built on top of it: real-time, fully offline, on-device recognition that classifies the attempted sign against a gold-standard reference and produces specific corrective feedback across four dimensions — handshape, orientation, motion path, and timing.

Every design and implementation decision must protect this distinction. Classification is a solved prerequisite; feedback is the contribution.

## Target Users

- **Primary:** Hearing learners studying FSL who need immediate practice feedback without an instructor present
- **Secondary:** Deaf/hard-of-hearing FSL learners refining sign accuracy
- **Evaluators:** FSL experts validating gold-standard references; researchers analyzing pre/post study data

## MVP Scope (In)

- 50 high-frequency FSL signs (selected subset of FSL-105)
- Android only, mid-range hardware (Helio G-series / Snapdragon 6-series, 4GB RAM min)
- Fully offline inference — zero network calls during use
- Real-time corrective feedback: handshape, orientation, motion, timing
- Practice mode: capture → recognize → feedback → retry
- Pre/post evaluation study support tooling
- Benchmarking harness with logged history across iterations

## Explicitly Out of Scope (MVP)

- Full FSL-105 vocabulary beyond the 50-sign subset
- Cloud sync, accounts, backend, or any server-side component
- iOS support
- ASL or any non-FSL sign language
- Open-vocabulary / continuous sentence-level recognition
- Two-way communication / sign-to-speech translation
- Gamification, leaderboards, social features
- 3D avatar/skeleton overlay correction
- Play Store public distribution (internal/defense distribution only)

## Performance Targets (Non-Negotiable)

- Recognition accuracy ≥ 90% on held-out test set (post-quantization)
- Inference latency < 150ms end-to-end per gesture window
- Sustained 24–30 FPS video pipeline on target mid-range hardware
- Benchmarking under: optimal light / low light / cluttered background

## Dataset

FSL-105 (Tupal & Villaverde, Mendeley Data, 2023) — public dataset, 105 classes, 2130 clips. Kept outside the repo. 50-sign subset selected for MVP. No raw video committed. RA 10173 applies to any participant data from the evaluation study.
