# Phase Gates — Live Status

Source of truth for where the project is. Update this file when a gate opens/closes.
Full phase descriptions: `PRD.md` §6.

| Phase | Deliverable | Status | Gate |
|-------|-------------|--------|------|
| 0 | Repo skeleton, AGENTS.md, Flutter scaffold, Colab template, .gitignore | ✅ Delivered 2026-07-05 | ⏳ Awaiting PM structure confirm |
| 1 | Dataset audit script + report | ✅ Audit delivered 2026-07-05 | ⏳ Awaiting PM sign-off on dataset + 50-class pick |
| 1 | Preprocessing pipeline (video → landmarks → fixed-length sequences) | ✅ Delivered 2026-07-05 (1016 clips, 0 errors — `training/preprocessing/preprocessing_report.md`) | — |
| 1 | Augmentation pipeline | ✅ Delivered 2026-07-05 (813 → 3252 train samples, seeded + logged) | — |
| 2 | CNN-LSTM baseline + experiment log | ✅ 4 experiments logged 2026-07-05 (`training/models/experiments_log.json`); best: `no_face`, 258 features | ✅ Confusion matrix reviewed, model accepted 2026-07-06 |
| 3 | Eval report (acc/prec/rec/F1, per-gesture errors) | ✅ **Test accuracy 95.07% — gate PASS** (`training/models/reports/20260705_194813_no_face_eval.md`) | ✅ ≥90% met, accepted 2026-07-06 |
| 4 | Quantized .tflite + latency/FPS report | ✅ Emulator fallback 2026-07-07 (`benchmarking/phase4_emulator_report.md`): inference 0–2ms, 28.6–29.9 fps — re-run on real mid-range hardware for thesis chapter | ✅ <150ms + 24–30 FPS met (emulator; M1 proxy caveat) |
| 5 | Flutter skeleton: camera → MediaPipe → inference e2e | ✅ Delivered 2026-07-07: live prediction overlay, 0 crashes, 29.9 fps on emulator (screenshot in session log) | ✅ Runs at target FPS (emulator fallback) |
| 6 | Corrective feedback engine | ✅ Python reference delivered 2026-07-07 (`training/feedback/`, demo on 5 wrong attempts + control: `demo_report.md`); Kotlin port + parity test delivered 2026-07-10 | ✅ FSL Expert validation complete 2026-07-23: all 50 gold standards approved, prompt copy accepted |
| 7 | Practice UI from approved Figma | ✅ Rebuilt to approved Figma 2026-07-14 (exports in `docs/design/*.png`): light green theme + dark mode toggle, 5-tab shell (Home / Isalin / Diksyunaryo / Mag-aral / Profile), Filipino UI copy, practice screen in Figma camera-panel style. Stats computed from real attempt history (no fake numbers). Stubs where MVP has no backend: Boses-sa-Senyas mode (labeled unavailable), favorites session-only, notifications toggles cosmetic. Emulator-verified: all 5 tabs render, live translate camera runs, practice attempt loop works. Success-path feedback sheet still needs real-device check (Phase 9) | ✅ Closed 2026-07-14 against real Figma. Earlier 2026-07-13 close used interim design system (no Figma existed then); superseded |
| 8 | Session logging / optional backend | ⬜ | PM decides cloud sync in/out of scope |
| 9 | Integration testing (50 gestures × signers) | ⬜ | No open blocking bugs |
| 9a | Benchmarking harness (accuracy/latency/FPS scripts + structured logging) | ✅ Delivered 2026-07-23: `benchmarking/` — accuracy_benchmark.py, collect_latency.py, collect_fps.py, plot_history.py, environment_protocol.md, BenchmarkMode.kt, LatencyBenchmarkTest.kt | ✅ Harness code complete; execution pending TF env + device |
| 10 | Field benchmarking (3 conditions × devices) | ⬜ | — |
| 11 | 40-participant study tooling | ⬜ | — |
| 12 | Stats/analysis scripts | ⬜ | — |
| 13 | Final polish, reproducibility notes, defense readiness | ⬜ | — |

## Open decisions

1. **PM confirm repo structure** (Phase 0 gate).
2. ~~**50-class subset**~~ — RESOLVED 2026-07-05: everyday-usage pick approved by team, see `selected-50-signs.md` + `training/preprocessing/selected_classes.json`. FSL Expert may still swap individual signs before training.
3. **Dataset provenance**: PRD assumed team-collected data; actual dataset is public FSL-105. See `dataset-notes.md` — needs adviser acknowledgment for methodology chapter.
4. **Gold-standard clips**: FSL-105 has no gold-standard flags. Decide: FSL Expert picks one reference clip per chosen class, or team records fresh gold-standard clips.
