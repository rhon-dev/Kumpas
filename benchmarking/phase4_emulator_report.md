# Phase 4/5 — Emulator Benchmark Report (fallback, no real device available)

Date: 2026-07-07. Device: Android emulator (AVD `kumpas_test`, medium_phone,
Android 35 arm64, 4GB RAM / 4 cores, host: Apple M1 Mac, `-gpu host`,
synthetic front camera). Per AGENTS.md amendment, emulator fallback is
authorized when no physical device is present. **These numbers are an M1
proxy, not mid-range-phone numbers — re-run on real hardware (Helio G /
Snapdragon 6 series) before the thesis benchmarking chapter.**

## Results (debug APK, 55s continuous run)

| Metric | Target | Measured |
|---|---|---|
| Camera pipeline FPS | 24–30 | **28.6–29.9** |
| Landmark extraction (pose+hands, per sampled frame) | — | 35–63 ms |
| TFLite inference (30×258 CNN-LSTM, dynamic quant) | <150 ms | **0–2 ms** |
| Crashes (FATAL) over run | 0 | **0** |

Pipeline: CameraX 640×480 RGBA → sample every 4th frame (~7.5/s, matches
training timescale) → MediaPipe Tasks pose+hand landmarkers (VIDEO mode) →
258-dim normalized features → 30-sample ring buffer → TFLite every 4th
sample (~0.5s cadence) → EventChannel → Flutter overlay.

## Known issues (Phase 7 backlog)

- Model predicts confidently on all-zero input (no person in frame) — gate
  predictions on pose/hand presence before showing them to learners.
- Handedness mapping vs front-camera mirroring not yet calibrated against
  training data conventions — verify with a human signer on real hardware.
- Cold start slow: VisionEngine loads 3 models synchronously on main thread.
