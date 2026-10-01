# Shipped pipeline verification — design

Date: 2026-09-29. Status: Approved to continue offline; physical phone unavailable now. The user cannot supply a labeled anatomical left/right calibration; that assertion remains unverified.

## Goal and claims

Separate (A) feature parity on identical prerecorded frames, (B) correctness of left/right anatomy, and (C) latency of real camera input to feedback delivered by the app. A result in one category does not establish another. The Android pipeline uses PoseLandmarker + HandLandmarker while Python training uses Holistic; differing detections are findings, not reasons to force equality. Do not change the model or hand convention based only on a parity failure.

## Approach

1. Export numbered lossless RGB frames from a small, named FSL-105 subset into an ignored data directory, with clip metadata, frame indices and SHA-256 digests. Run Python Holistic on those exact frames using the same preprocessing state/mode as training, capture 258-feature vectors after `build_sequences.normalize`, presence and prediction if available.
2. Add an Android instrumented replay that reads those same PNGs from app-specific external storage, passes them in timestamp order to the **same extraction/normalization path** as live `VisionEngine`, and writes per-frame 258-feature vectors and model predictions to app-private files for `adb pull`. A host comparator aligns by frame index/hash, reports detection disagreements, per-block error statistics, classifier agreement, and recording conditions. No test frame/video enters git.
3. Extract normalization into a pure, tested Kotlin seam and compare it with Python on synthetic exact landmark inputs (including missing hand and mirrored cases) independently of differing detector models. This only verifies math/layout parity, not anatomical truth.
4. Add clock-consistent timing at the analyzer callback before bitmap allocation, through landmark extraction, inference, feedback comparison and main-thread event delivery. Report last sampled frame callback to feedback delivery separately from the multi-frame collection interval and from UI paint time. A host collector refuses missing device metadata, emulator or absent real measurements; outputs per-attempt latencies and p50/p95 for the named physical device and condition. Do not reuse interpreter-only timings or emitted-event FPS as camera-to-feedback.
5. When a real phone and Android SDK are available, run replay and live capture on that phone, recording model/asset hashes, Android build ID, device chipset/RAM, app revision, lighting/background and n attempts. Until then publish scripts, offline fixtures/tests and a blocked-device checklist, **not** numeric on-device claims.

## Anatomical left/right gate

The dataset provides no trusted per-frame anatomical left/right annotation. Python and Android may agree while both are mirrored; image-coordinate heuristics are insufficient. This gate is explicitly `UNVERIFIED`, requiring a consenting person performing left-only/right-only calibration or independently verified annotated ground truth on the actual camera pipeline. Do not relabel based on `Left`/`Right` strings alone.

## Failure conditions and tests

Fail closed on image hash mismatch, missing frames, absent physical device, empty latency samples, inconsistent timing boundaries, and feature dimension mismatch. JVM unit tests cover normalization on synthetic vectors and timing boundary arithmetic; Python tests cover deterministic extraction indices, alignment/report calculations, missing data, and no false anatomical claim. No media or biometric captures committed. Keep previously modified README/benchmark_history and evaluation work untouched.
