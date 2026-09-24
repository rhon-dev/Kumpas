# KUMPAS 30-Day Execution Plan

**Written by:** Documentation Agent (AGENTS.md, `docs/PRD.md` §7). This file is documentation only. It contains no app, model, training, or benchmark code, and running it was not part of producing it. Each day below delegates the actual work to a named PRD §7 persona through the Kiro prompt in that entry.

**Start:** 2026-09-21 (Monday). **Day 30:** 2026-10-20 (Tuesday). Every calendar day is counted.

**Assumed capacity (self-paced, rescalable):** 3h per weekday, 4h per weekend day. You said self-paced and did not give numbers, so these are my assumption, stated here so you can correct them. The dates are a nominal schedule. If a day slips, shift the later dates. Do not compress two days into one.

**Device:** none in hand. Target class is low-mid-range Android (Helio G series or Snapdragon 6 series, 4GB RAM per `AGENTS.md`). Access date unknown. Every hardware measurement is marked BLOCKED with its precondition named. No emulator figure is relabeled as a mid-range device result anywhere in this plan.

**Repo state:** current branch is `docs/30-day-plan-2026-09-21`, not `main`, verified by `git rev-parse --abbrev-ref HEAD` on 2026-09-23. `kiro-sdlc-framework` still exists as a separate local and remote branch; an earlier draft of this file named it as the working branch, which was wrong. `docs/hardening-plan.md` (PR #2) exists only as `remotes/origin/docs/hardening-plan` and is **not in the working tree of this branch**, so any day that reads it must materialise it first (see Day 1).

---

## THE TARGET DOES NOT FIT. READ THIS FIRST.

Your Day 30 target cannot be met at 3h/4h per day, and two items cannot be met at any capacity this month because they need hardware you do not have. Cut list, with reasons:

1. **Phase 10 field benchmarking: CUT ENTIRELY.** No device, access date unknown. `docs/phase-gates.md` Phase 4 and 5 rows already show what happens when this gets substituted with an emulator. Day 4 owns procurement as a real task; Day 29 owns the instrumentation and protocol so the run is one session long once a device arrives. The run itself moves to Day 31+.
2. **Phase 9a full execution: PARTIAL.** The accuracy benchmark can and will run for real (Day 15) because `benchmarking/.venv` has TensorFlow 2.21.0 and `X_test.npy` / `y_test.npy` exist in `../kumpas-data/sequences/`. Latency and FPS cannot run: they need a device. Phase 9a closes on accuracy only, and the plan says so on the gate row.
3. **Phase 9 integration testing: CANNOT CLOSE.** Its own predecessor blocks it. The `docs/phase-gates.md` Phase 7 row records "Success-path feedback sheet still needs real-device check (Phase 9)". Phase 9 therefore has a device dependency written into it by the previous phase. Days 19 and 20 define the full 50-gesture matrix and execute the emulator-runnable part. Device-dependent rows stay open.
4. **Phase 8: CLOSES, but as a status reconciliation, not new construction.** See Conflict 3. The classes are already wired.
5. **Stage G (model improvement) and Stage H (release readiness) from PR #2: not scheduled.** Day 18 documents the numerals and n=203 risk so it is named before defense, but fixing it needs a re-split and retraining, which is Rule #0 territory and does not fit.

What does fit, and what Day 30 delivers instead: an honest gate table, a repo a stranger can build, a declared Python environment, one real accuracy measurement, the two parity and handedness settlements that protect the thesis contribution, Phase 8 closed, Phase 11 tooling dry-run on synthetic data, a Phase 12 skeleton, and three thesis drafts. That is 79 delivery hours of the 98 available, with 16h of buffer and 3h of review held back.

Arithmetic: 98h total capacity, minus 16h buffer (Days 7, 14, 21, 28), minus 3h Day 30 review, leaves 79h across 25 working days. The five PR #2 stages this plan touches (A, B, C, E, F) are estimated in `docs/hardening-plan.md` §2 at roughly 0.5 + 1.5 + 2.5 + 1.5 + 4 = 10 full days. At 8h per full day that is about 80h. The fit is exact with no slack, which is why Stages D, G, and H are out.

---

# 1. Status Ledger, Conflict Log, and Work in Flight

## 1a. Status Ledger

Phase numbers are **PRD §6 (0 to 13)**, with the `.kiro/specs/` number in parentheses on first mention. This ledger, not the `docs/phase-gates.md` table, is the denominator for every "how much is left" statement in this plan.

| Phase | phase-gates.md claims | What the artifacts show | Evidence path | Verdict |
|---|---|---|---|---|
| 0 Repo and env setup | Delivered 2026-07-05, gate awaiting PM structure confirm | Repo, AGENTS.md, Flutter scaffold, .gitignore all present | `AGENTS.md`, `app/`, `.gitignore` | MATCHES (gate still open) |
| 1 Dataset audit and preprocessing (spec 01 to 03) | Delivered, 1016 clips, 0 errors, gate awaiting PM sign-off | `extraction_log.csv` has exactly 1016 data rows, all `status=ok` | `training/preprocessing/extraction_log.csv` | MATCHES (gate open) |
| 1 Augmentation | Delivered, 813 to 3252 train samples, seeded and logged | Both counts confirmed by `.npy` header arithmetic, no array load needed. A sample is 30×1662×4 = 199,440 bytes and the header is 128 bytes. `X_train.npy` is 162,144,848 bytes: (162,144,848 − 128) / 199,440 = **813** exactly. `X_train_aug.npy` is 648,579,008 bytes: (648,579,008 − 128) / 199,440 = **3252** exactly. Labels agree: `y_train.npy` 6,632 bytes → (6,632 − 128) / 8 = 813, `y_train_aug.npy` 26,144 bytes → (26,144 − 128) / 8 = 3252. The 4x ratio and the seeding claim are consistent with the manifest | `../kumpas-data/sequences/X_train.npy`, `X_train_aug.npy`, `y_train.npy`, `y_train_aug.npy` (sizes via `stat -f %z`) | MATCHES |
| 2 Model architecture and training | 4 experiments logged, best `no_face` at 258 features, confusion matrix reviewed, accepted 2026-07-06 | 4 runs present. `no_face` 258-dim at 0.9507 is genuinely the best of the four. The two 1662-dim runs scored 0.8571 and 0.8325 | `training/models/experiments_log.json` | MATCHES |
| 3 Model evaluation, 90% gate | Test accuracy 95.07%, gate PASS, accepted 2026-07-06 | 0.9507 is really in the report. But n=203 over 50 classes is about 4 clips per class, `best_val_accuracy` is 1.0 on the winning run (no model-selection signal), and no confidence interval is reported anywhere | `training/models/reports/20260705_194813_no_face_eval.md`, `training/models/experiments_log.json` | OVERSTATED |
| 4 TFLite and on-device benchmarking | Emulator fallback PASS, inference 0 to 2ms, 28.6 to 29.9 fps | The 0 to 2ms measures the TFLite interpreter alone. The same emulator report records MediaPipe at 35 to 63ms per frame, which `.kiro/steering/tech.md` includes in the budget. The FPS window is 55s against `collect_fps.py`'s own 60s minimum. Both entries self-label retroactive and M1 proxy | `benchmarking/benchmark_history.json`, `benchmarking/phase4_emulator_report.md` | OVERSTATED |
| 5 Mobile app skeleton | Delivered, 0 crashes, 29.9 fps on emulator | The app does run end to end. The performance claim rests on the same two retroactive emulator entries as Phase 4 | `benchmarking/phase4_emulator_report.md` | OVERSTATED |
| 6 Corrective feedback engine (spec 10) | Python reference plus Kotlin port and parity test. FSL Expert validation complete 2026-07-23, all 50 gold standards approved | Engine and `FeedbackEngineParityTest.kt` exist. The expert validation document is a blank template: no date, no expert name, empty ratings table, unsigned sign-off block | `docs/phase10-expert-validation-protocol.md` | OVERSTATED |
| 7 Practice UI | Closed 2026-07-14 against real Figma | UI code exists. The row itself records an open item: success-path feedback sheet still needs a real-device check. "Matches Figma" is not checkable from the repo alone | `app/lib/ui/`, `docs/design/` | UNVERIFIABLE |
| 8 Session logging (spec 21) | Tasks 1 to 15 COMPLETE, task 16 pending | Spec 21 `tasks.md` shows tasks 1 to 15 checked and task 16 unchecked, which agrees. The gate cell is contradicted by nothing in the spec, but see Conflict 3 for the branch-state disagreement with PR #2 | `.kiro/specs/21-session-logging/tasks.md` | MATCHES on this branch |
| 9 Integration testing | Not started | No integration test matrix exists. Blocked by the Phase 7 real-device open item | none | MATCHES |
| 9a Benchmarking harness (spec 13) | Delivered, execution pending TF env and device | Harness scripts all exist. The accuracy benchmark did execute, twice, on 2026-07-23. Latency and FPS never ran on any device | `benchmarking/`, `benchmarking/benchmark_history.json` | UNDERSTATED on accuracy, OVERSTATED on latency and FPS |
| 10 Field benchmarking | Not started | Nothing. No entry in `benchmark_history.json` has a `condition` other than `"n/a"` | `benchmarking/benchmark_history.json` | MATCHES |
| 11 Study tooling | Not started | `evaluation/` contains only `.gitkeep`. The in-app assessment screen does exist from spec 21 task 11 | `evaluation/.gitkeep`, `app/lib/ui/assessment_screen.dart` | MATCHES (with one part already built) |
| 12 Stats and analysis scripts | Not started | None | none | MATCHES |
| 13 Final polish and reproducibility | Not started | No CI at all (`.github/` absent), `training/requirements.txt` cannot rebuild the environment | `training/requirements.txt`, `.github/` absent | MATCHES |

**What the ledger changes about the denominator.** The remaining work is not "Phases 8 to 13". It is "Phases 8 to 13, plus repair of Phases 3, 4, 5, 6, and 9a before any of their numbers can be cited in the thesis". Four gates currently read PASS on evidence that the repo itself contradicts. That repair is Weeks 1 and 2 and it is the reason the Day 30 target had to shrink.

## 1b. Conflict Log

Both positions recorded, no side picked.

**1. Phase numbering.** `docs/PRD.md` §6 numbers phases 0 to 13. `.kiro/specs/` uses 00 to 21. These are different granularities, not a renumbering: PRD Phase 1 spans specs 01 to 03, and PRD Phase 9a is spec 13. **Scheme used for the rest of this document: PRD §6 (0 to 13), with the spec number in parentheses on first mention.** On the specific sub-question: `docs/phase10-expert-validation-protocol.md` is titled "Phase 10 Gate" but refers to **PRD Phase 6 (feedback engine) / spec 10-feedback-logic**, not PRD Phase 10 (field benchmarking). Its own Post-Session Actions list says to update `docs/phase-gates.md` Phase 6 status and `.kiro/specs/10-feedback-logic/design.md` §8. The filename is a spec-number reference and it collides with a PRD phase number. This is a naming trap that will cost you at defense if a panelist reads the title only.

**2. FSL Expert validation record.** `docs/phase-gates.md` Phase 6 gate cell states "FSL Expert validation complete 2026-07-23: all 50 gold standards approved, prompt copy accepted". `docs/phase10-expert-validation-protocol.md` has `**Date:** _______________`, `**Expert Name:** _______________`, all 50 rows of the Expert Rating column empty, the Block B tallies blank, and the sign-off block unsigned. **No filled record exists anywhere in the repo**: a search for the protocol's own field markers and for `expert-approved` did not return a completed instance. The git history does contain commit `3205220` "Phase 10 gate CLOSED, FSL Expert validation complete", so a session may genuinely have happened offline. The repo cannot evidence it. Day 17 drafts the question to you about this. It does not answer it.

**3. Phase 8 status, and a branch disagreement with PR #2.** Two separate conflicts here, and the second one matters. First: `docs/phase-gates.md` marks Phase 8 as delivered with tasks 1 to 15 complete, and `.kiro/specs/21-session-logging/tasks.md` agrees (1 to 15 checked, 16 unchecked). Second, and this is the live one: `docs/hardening-plan.md` §1.7 (PR #2, dated 2026-09-15) states that a repo-wide grep for `SessionManager`, `SessionDatabase`, `DataExporter` returns zero references outside the three files, calls them roughly 707 lines of dead code, and reports spec 21 as "tasks 1 to 3 `[x]`, tasks 4 to 16 `[ ]`". **On the current branch that is no longer true.** A grep returns `SessionManager` and `DataExporter` instantiated in `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt` (lines 22 to 23 declare them, 54 to 55 construct them), plus three Robolectric test files. The classes are wired. PR #2 §1.7 describes an earlier branch state and its Stage E1 keep-or-delete question is already answered by the code. Day 13 reconciles the status, it does not re-litigate keep-versus-delete.

**4. Phase 8 cloud sync decision.** `docs/PRD.md` §6 Phase 8 gate text says "PM confirms whether cloud sync is in-scope before any backend agent starts". `.kiro/specs/00-project-init/gap-reconciliation-report.md` §3.3 records the decision as already made: backend OUT, local-only, and `docs/hardening-plan.md` Stage E cites that same section as settled. **Current position: the decision is made, local-only.** The PRD gate text is stale. Day 13 confirms the recorded decision in writing and does not reopen it.

**5. Phase 9a tasks that were never executed, which is not the same as never written.** `docs/phase-gates.md` marks the harness delivered with "execution pending TF env + device", while `.kiro/specs/13-benchmarking-harness/tasks.md` marks **all 14 tasks checked**. The two tasks whose *results* cannot exist are **task 5** (`LatencyBenchmarkTest.kt`, an Android instrumented test, needs a connected device or emulator) and **task 7** (benchmark mode writing to `/sdcard/Download/`, needs a device, and per `docs/hardening-plan.md` §1.8 that path fails on API 29+ given the `maxSdkVersion="28"` permission in `AndroidManifest.xml`). The spec's own Notes section admits both "require on-device work".

**Correction to an earlier draft of this plan, verified 2026-09-23.** That draft told Day 1 to un-check tasks 5 and 7. That would have replaced one inaccuracy with its mirror image, because both tasks are worded as *create* tasks and both artifacts exist:

- Task 5 asks for `app/android/app/src/androidTest/.../LatencyBenchmarkTest.kt`. The file is present at `app/android/app/src/androidTest/kotlin/com/kumpas/kumpas_app/benchmark/LatencyBenchmarkTest.kt`.
- Task 7 asks for a benchmark mode in the app. `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/BenchmarkMode.kt` is present and **wired at `MainActivity.kt:56`** (`benchmarkMode = BenchmarkMode(applicationContext)`, declared at line 24, and the frame hook is live in the `VisionEngine` callback immediately below).

So the code is written and the runs never happened. The checkbox is the wrong instrument for that distinction: it tracks one axis and the defect is on the other. **Day 1 therefore keeps both boxes checked and appends a `NEVER EXECUTED` note to each**, naming the missing device and, for task 7, the API 29+ write-path bug. Task 10 did execute but only by hand-seeding retroactive entries, which is what task 10 says it does. Unchecking stays available as a Day 31+ action once item 3 of section 9 reaches a real device.

**6. Are the Phase 4 and 5 gates evidenced?** No. Both rest on the two entries in `benchmarking/benchmark_history.json` timestamped `2026-07-07T12:00:00`, which self-describe as `"Retroactive entry from Phase 4/5 emulator fallback report"` with `"note": "Retroactive from phase4_emulator_report.md; M1 proxy, not real device"`. The latency entry has `"cold_start_ms": null` and `"n_inferences": null`, so it cannot support a p95 claim. The FPS entry has `"duration_s": 55` against the 60s minimum that `benchmarking/collect_fps.py` enforces on real runs. Both carry `"condition": "n/a"` where `benchmarking/environment_protocol.md` defines `optimal`, `low_light`, and `cluttered`. And the 0 to 2ms latency is interpreter-only while the same emulator report records MediaPipe at 35 to 63ms per frame. `docs/holistic-v2-diagnosis.md` reaches the same conclusion independently and adds that a panelist who opens both files finds the inconsistency in minutes. Verdict: not evidenced, for either phase.

**7. MediaPipe Holistic lock versus what the app runs.** `AGENTS.md` Hard constraints and `.kiro/steering/tech.md` both lock MediaPipe Holistic (hand plus face plus pose). `docs/holistic-v2-kiro-prompt.md` claim D asserts the app does not run Holistic. **Verified: the prompt document is right.** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt` imports `PoseLandmarker` and `HandLandmarker` with no `HolisticLandmarker` import, and sets `N_FEATURES = 258` with no face channel. `app/fetch_assets.sh` downloads exactly two model files, `pose_landmarker_lite.task` and `hand_landmarker.task`, and no Holistic asset. Training used legacy Holistic. So there is a real train-serve skew and the steering lock is violated on device. Per `docs/holistic-v2-diagnosis.md`, `tasks-vision:0.10.14` already pinned in `build.gradle.kts` does ship `HolisticLandmarker`, so no dependency bump is needed to fix it. This plan does not fix it: that is spec 22 work, unapproved, and out of 30-day scope. Days 11 and 29 both note where the skew affects what they produce.

**8. Does the app actually deliver feedback on handshape, orientation, motion, and timing?** `docs/PRD.md` §1 and §2 promise all four. Measured from `training/preprocessing/extraction_log.csv` across all 1016 `ok` clips: mean `pose_rate` 1.0000, mean `face_rate` 0.9999, **mean `lh_rate` 0.0803, mean `rh_rate` 0.3445, mean `any_hand_rate` 0.3516**. 733 of 1016 clips (72.1%) have zero left-hand frames. 962 of 1016 (94.7%) have `any_hand_rate` below 0.5. **Required correction, from `docs/holistic-v2-diagnosis.md`:** that aggregate 0.3516 is mostly rest padding, not detection failure. Clips are roughly 39.6% leading rest and 24.8% trailing rest, and in-span hand detection is **0.954** (median 0.989). Numerals are among the best in-span (FIVE 0.996). Both numbers belong in the thesis: the aggregate explains why the 258-dim tensor is mostly zeros in the hand blocks, the in-span figure is the honest instrument for detection quality. The winning run also dropped the face channel (`"drop_face": true`, 258 features). Stated plainly: **timing and motion feedback stand on solid ground**, because `docs/holistic-v2-diagnosis.md` reports DTW aligns on pose wrists (landmarks 15 and 16) which are detected in essentially every frame. **Handshape and orientation feedback rest on hand landmarks that are absent from about two thirds of sampled timesteps**, and the diagnosis adds that even when present, wrist-relative fingertip configuration is a 7.5x smaller-amplitude component than the pose block, so the representation buries it. The corroborating evidence is in the results: the four signs that differ only by handshape are the four worst classes (FIVE F1 0.333, FOUR 0.600, THREE 0.667, TWO 0.800). Day 12 documents this and Day 17 drafts the resulting question for the FSL Expert.

**9. Can a clean clone build or benchmark?** **No for build, yes for benchmark but only on this machine.** `.gitignore` lines 11 and 12 exclude `*.tflite` and `*.task`. `git ls-files app/android/app/src/main/assets/` returns only `gold_standards.bin` and `label_map.json`. The three models the app loads are present on this disk but untracked, confirmed by `git check-ignore -v`. `app/fetch_assets.sh` downloads the two MediaPipe `.task` files from Google storage, which works anywhere, but copies the classifier and label map from `../../kumpas-data/`, a sibling directory. **Correction to `docs/hardening-plan.md` §1.1, which says that sibling "does not exist in a fresh clone":** it does exist on this machine at `Thesis/kumpas-data/`, holding `tflite/kumpas_50sign_builtins_dynamic.tflite` and `sequences/label_map.json`. So the script succeeds here and fails on any other machine. Same for benchmarking: `X_test.npy` and `y_test.npy` are in `../kumpas-data/sequences/`, so Day 15 can run the accuracy benchmark locally, and a stranger cannot.

**10. `training/requirements.txt` versus actual imports.** The file has three lines: `mediapipe==0.10.14`, `numpy==2.4.6`, `opencv-python==5.0.0.93`. Third-party imports actually present across `training/` and `benchmarking/` are `cv2`, `matplotlib`, `mediapipe`, `numpy`, `sklearn`, and `tensorflow`. So `tensorflow`, `sklearn`, and `matplotlib` are undeclared. The two real environments are also split and neither matches the file: `training/.venv` has mediapipe, numpy, opencv, matplotlib, scipy, and jax but **no TensorFlow and no sklearn**; `benchmarking/.venv` has **tensorflow 2.21.0**, keras 3.15.0, scikit-learn 1.9.0, numpy, matplotlib, scipy, but **no cv2 and no mediapipe**. It also carries two `ai_edge_litert` dist-infos (1.4.0 and 2.2.0), which is a duplicated install worth cleaning. **Can the Phase 9a accuracy benchmark run as-is? Yes, but only from `benchmarking/.venv`, and nothing in the repo declares that environment.** There is no requirements file for `benchmarking/` at all. Note the version skew for the methodology chapter: the eval report and all four logged runs record `tensorflow 2.19.0`, while the venv that would re-run the benchmark has 2.21.0.

**Added 2026-09-23, and it changes what Day 15 has to do.** The script cannot record the environment that this conflict is about. `benchmarking/accuracy_benchmark.py` builds its log entry in `main()` with `"device": "offline/python"` and `"condition": "n/a"` as hardcoded string literals, and it writes **no library versions into the entry at any point**: there is no `environment` key, no `tensorflow.__version__` read, no `platform` call. Confirmed by reading the whole file. The two existing accuracy entries show the consequence directly, both carrying `"device": "offline/python"` and nothing else about the machine. Since the whole point of re-running is to see whether 2.19.0 and 2.21.0 agree, **Day 15 must add an `environment` block to the script before running it**, not just pass a `--notes` string, or the new entry is as unattributable as the old ones. Day 15's acceptance criteria and Day 30 definition-of-done item 12 are written that way.

One thing that does **not** need fixing, checked in the same pass: the 1662-versus-258 mismatch is already handled. `X_test.npy` is `(203, 30, 1662)` while the deployed `no_face` model takes 258 features, and `run_tflite_inference()` reads `input_details[0]["shape"][2]`, detects the mismatch, and slices with `keep = np.r_[0:132, 1536:1662]` to drop the 1404 face features. So the shape will not stop the run.

**11. Missing infrastructure.** `.github/` does not exist, so there is no CI and PR #1 merged with no automated verification. `evaluation/` contains only `.gitkeep`, so all of Phase 11 and 12 is greenfield. Also worth recording: all four runs in `experiments_log.json` say `"environment": "local M1 (tensorflow 2.19.0)"` while `AGENTS.md` and `.kiro/steering/tech.md` lock Google Colab as the training environment. That is a fourth stack deviation alongside the Holistic one, and it needs either a steering amendment or a recorded deviation before the results are cited.

## 1c. Relationship to Work in Flight

### `docs/hardening-plan.md` (PR #2, branch `docs/hardening-plan`, dated 2026-09-15, not on `main`)

This plan **depends on** PR #2 for the diagnosis and the stage vocabulary, and **absorbs** five of its eight stages into dated days. It supersedes nothing and re-litigates nothing.

| PR #2 stage | Relationship | Days |
|---|---|---|
| A, tell the truth (A1 to A4) | ABSORBS in full | 1 (A1, A2), 2 (A3, A4) |
| B, make it reproducible (B1 to B5) | ABSORBS B1, B2, B4, B5. B3 (publish a GitHub Release) is a human task, it needs repo owner rights | 5 (B1), 6 (B2, B5), 8 (B4) |
| C, prove the math (C1 to C5) | ABSORBS in full. This is the highest-value block in the month | 9 (C3), 10 (C2), 11 (C1), 12 (C5, C4 partial) |
| D, measure for real (D1 to D7) | DEPENDS ON, cannot execute. No device. Day 29 does the D4 instrumentation design only | 29 (D4 design), rest to Day 31+ |
| E, session-logging decision (E1 to E5) | SUPERSEDES E1 and E2. Conflict 3 shows the classes are already wired on this branch, so the keep-or-delete question PR #2 poses is already answered by the code. E3, E4, E5 remain valid and are deferred | 13 (E1 confirm only) |
| F, study tooling (F1 to F5) | ABSORBS F1, F3, F4. F2 already exists (`assessment_screen.dart`). F5 (pilot with real people) is a human task and is gated, see below | 22 (F1, F3), 23, 24 (F4) |
| G, model improvement (G1 to G4) | DEPENDS ON, not scheduled. Day 18 documents the risk G1 and G2 address without fixing it | 18 (documentation only) |
| H, release readiness (H1 to H5) | Not scheduled. Out of 30-day scope | Day 31+ |

One correction to carry forward: PR #2 §1.7 and its Stage E rest on a grep result that no longer holds on this branch. Treat PR #2 §1.7 as describing an earlier state.

### `docs/holistic-v2-*` on `main` (`-kiro-prompt.md` 2026-09-20, plus `-diagnosis.md` and `-risks.md`)

These three are **planning inputs only**. `docs/holistic-v2-diagnosis.md` labels itself a planning input and not a gate decision, and `docs/holistic-v2-kiro-prompt.md` ends by instructing a stop before any implementation pending PM approval under Rule #0. **They have closed no gates and this plan treats none of their proposals as done.**

Where they collide with days below, the collision is stated on the day, not buried here:

- **They would invalidate a Phase 10 device run against the current pipeline.** `docs/holistic-v2-risks.md` R2 states the 150ms and 24 to 30 FPS gates cannot be honestly closed for either pipeline yet, and that the 258-dim baseline must be measured on the same device for the comparison to be fair, meaning two device runs, not one. Since Phase 10 is already cut for lack of a device, this costs nothing now. Day 29 records it so the eventual run is designed correctly.
- **They would invalidate a re-derived accuracy baseline.** R4 promotes the Stage G2 test-set fix to a prerequisite and says it changes the reported baseline away from 95.07%. Day 15 therefore re-runs the accuracy benchmark to establish provenance and reproducibility, and explicitly does **not** treat the result as a defensible final number. Day 18 records why.
- **They would partially invalidate the Phase 6 expert sign-off.** The diagnosis scopes this precisely: timing and motion keep their sign-off because DTW aligns on pose wrists, and only handshape and orientation would need fresh expert review. Day 17 drafts that scoped question.
- **They do not change handedness priority.** R1 rates handedness High likelihood and Critical impact and says not to fix it in the split-model path first because that work gets discarded. This plan schedules Day 11 as **calibration and documentation of the current convention plus a failing-or-passing assertion**, not as a rewrite of the pipeline. That stays useful under either future.

**Deliberate non-action:** this plan does not create `.kiro/specs/22-holistic-v2/`, does not start WS1 to WS7, and does not act on the prompt document. That work needs PM approval per Rule #0 and does not fit in 30 days at this capacity.

---

# 2. Summary

## Goal

Convert Kumpas from a project whose documentation overstates its evidence into one whose claims are each traceable to an artifact, and get the study tooling and thesis drafts far enough that the evaluation study can start as soon as the handedness question and a device are settled.

## Day 30 definition of done, as verifiable artifacts

Each line is checkable by opening a file or running one command.

1. `docs/phase-gates.md` contains no row claiming a device measurement, and Phases 4, 5, 6 carry CONDITIONAL or UNEVIDENCED markers with reasons. (Days 1, 2)
2. `.kiro/specs/13-benchmarking-harness/tasks.md` tasks 5 and 7 each carry a `NEVER EXECUTED` note naming the missing device, and task 7's note also names the API 29+ write-path bug. Both boxes stay `[x]`, because both are *create* tasks and both files exist. See Conflict 5. (Day 1)
3. `benchmarking/benchmark_history.json` contains no entry that both self-labels retroactive and carries `gate_pass: true`, and `plot_history.py` output contains only measured data. (Day 2)
4. `README.md` has a Known Limitations section naming: emulator-only performance, unevidenced expert sign-off, numerals weakness, n=203 test set, and the Holistic-versus-split-model skew. (Day 2)
5. Three requirements files exist and each installs clean in a fresh venv: `training/requirements-mediapipe.txt`, `training/requirements-tf.txt`, `benchmarking/requirements.txt`. (Day 5)
6. `docs/reproducibility.md` exists, and `app/fetch_assets.sh` has no out-of-repo dependency, with SHA-256 checksums recorded for every asset. (Day 6)
7. `.github/workflows/ci.yml` exists and a run is green, with the feedback parity test visible in the log. (Day 8)
8. A Kotlin unit test asserts `VisionEngine.normalize()` matches Python fixtures within tolerance, with at least 5 fixtures, running headless in CI. (Days 9, 10)
9. `docs/handedness-calibration.md` records the measured left-versus-right convention with a test that asserts it, and states whether the training and serving conventions agree. (Day 11)
10. `docs/feedback-thresholds.md` documents all four thresholds and all three divisors, marking arbitrary ones as arbitrary. (Day 12)
11. `docs/phase-gates.md` Phase 8 row and `.kiro/specs/21-session-logging/tasks.md` agree with each other and with a dated decision record confirming local-only. (Day 13)
12. `benchmarking/accuracy_benchmark.py` writes an `environment` block (TensorFlow version, Python version, platform) into every entry it appends, and `benchmarking/benchmark_history.json` has a new accuracy entry, not retroactive, carrying that block plus a reproducibility note against the 2026-07-23 pair. The script change is part of the criterion: as written it hardcodes `device` and `condition` and records no versions, so the run alone cannot satisfy this. See Conflict 10. (Day 15)
13. `docs/signer-leakage-check.md` states whether train and test clip indices overlap, with the method and its limits. (Day 16)
14. `docs/gold-standard-provenance.md` lists all 50 clips, how each was selected, and what validation is and is not on file. (Day 17)
15. `docs/defense-risks.md` names the numerals weakness and the n=203 test set with the per-class numbers. (Day 18)
16. `benchmarking/integration_test_matrix.md` enumerates 50 gestures by condition, marking each row runnable-now or device-blocked. (Day 19)
17. `evaluation/` contains a consent template, pre and post instruments, a rubric, and scoring plus stats scripts that run end to end on synthetic input with known answers. (Days 22 to 25)
18. `docs/thesis-drafts/` contains objectives aligned to the repo, Scope and Limitations, and the FSL-105 provenance note. (Days 26, 27)
19. `docs/e2e-latency-protocol.md` specifies camera-frame-in to feedback-out instrumentation and is marked BLOCKED with its precondition. (Day 29)
20. `docs/30-day-review.md` reports what closed, what did not, and the Day 31+ list. (Day 30)

## Must-cover items, mapped to owning days

| # | Item | Owning days |
|---|---|---|
| 1 | Clean-clone reproducibility | 6 |
| 2 | Python environment for Phase 9a | 5, closed by 15 |
| 3 | Truth-in-docs pass | 1, 2 |
| 4 | Real-device end-to-end latency and FPS | 29 (design), run deferred to Day 31+ |
| 5 | Handedness/mirroring plus `normalize()` parity | 9, 10, 11 |
| 6 | Hand coverage meaning, and whether the expert sign-off needs revisiting | 12, 17 |
| 7 | Signer-leakage check | 16 |
| 8 | Gold-standard provenance | 17 |
| 9 | Phase 8 decision confirm plus status reconcile | 13 |
| 10 | Pending sign-offs as tracked blockers | 3 |
| 11 | Feedback success-path check (Phase 7 open item) | 20 (emulator), device part deferred |
| 12 | RA 10173 consent and working delete path | 22 |
| 13 | Does feedback really cover all four dimensions | 12 |
| 14 | Numerals weakness and n=203 as defense risk | 18 |
| 15 | Thesis drafts | 26, 27 |

## Assumptions

1. Capacity is 3h weekdays and 4h weekend days. You said self-paced without numbers.
2. Dates are nominal. Slipping a day shifts later dates rather than compressing them.
3. `Thesis/kumpas-data/` stays on disk and intact. Days 10, 11, and 15 read fixtures and test arrays from it. Verified present 2026-09-23. Note for anyone auditing this: `du` reports 0 bytes for `X_train.npy`, `X_train_aug.npy`, and the label arrays, which looks like eviction but is APFS transparent compression (`com.apple.decmpfs` xattr, 0 on-disk blocks with a nonzero `stat -f %z` size). The data is local. Do not read that as a missing-file warning.
4. An Android emulator is available, since `benchmarking/phase4_emulator_report.md` records an AVD in use. Days 13 and 20 need it.
5. Work continues on `docs/30-day-plan-2026-09-21`, the branch actually checked out. If you merge to `main` or switch to `kiro-sdlc-framework` mid-month, Day 7 absorbs the reconciliation.
6. PR #2 is unchanged since 2026-09-15. If it moved, Day 1 re-reads it before acting. It is not in this branch's working tree, so "re-read" means `git show origin/docs/hardening-plan:docs/hardening-plan.md` rather than opening a local path.
7. No PM or adviser approval arrives before Day 3 plus buffer, so no day before Day 8 consumes one.

## Risks

1. **Handedness may be wrong (highest).** If Day 11 finds the conventions disagree, per-hand feedback prompts have been confidently wrong, and Day 15's accuracy number describes a pipeline that needs fixing. `docs/hardening-plan.md` §1.4 calls this the single most dangerous open bug. Day 11 has the whole 3h and Day 14 buffer behind it.
2. **Device may never arrive this month.** Already priced in: Phase 10 is cut, not scheduled-and-hoped.
3. **The expert sign-off may be unrecoverable.** If no offline record exists, Phase 6 cannot be evidenced and a re-validation session is needed, which is human-gated and outside 30 days.
4. **Holistic v2 may supersede this work.** Days 9 to 12 produce parity tests and threshold docs that survive the change. Day 15's accuracy number does not survive a test-set re-split.
5. **Environment drift.** The logged runs used TensorFlow 2.19.0, `benchmarking/.venv` has 2.21.0. Day 15 may not reproduce 0.9507 exactly. That is a finding to record, not a failure.
6. **Rule #0.** Several days repair existing code. If the PM reads Rule #0 strictly, Days 9 to 13 need approval first. Day 3 requests it.

## Cut list

Restated from the top, with destinations: Phase 10 field benchmarking (Day 31+, needs device), Phase 9a latency and FPS (Day 31+, needs device), Phase 9 full closure (partial, device-blocked rows stay open), PR #2 Stage D beyond the D4 design (Day 31+), Stage G model improvement (documented Day 18, not fixed), Stage H release readiness (Day 31+), Stage E3 to E5 (Day 31+), spec 22 Holistic v2 (needs PM approval, does not fit).

---

# 3. Week-by-Week Milestones

The suggested shape survives with one reorder, explained below.

**Week 1, Days 1 to 7. Truth, requests, and a repo that builds.** Correct the untrue status entries first, because every later decision depends on knowing the real state and because it costs almost nothing. Then get the human-gated requests out the door early so the waiting clock starts on Day 3, not Day 20. Then declare the Python environment and make the clean clone build. Milestone: `docs/phase-gates.md` no longer claims what the repo contradicts, and a stranger could get to a running APK.

**Reorder, with reason:** device procurement moves up to Day 4, far earlier than a Week 3 placement would suggest. `docs/holistic-v2-risks.md` R2 advises escalating device access at the start rather than at the end, since the offline work does not need it. Asking on Day 4 gives the request 25 days to land instead of 5.

**Week 2, Days 8 to 14. Prove the math, then close Phase 8.** CI first so every later change is checked, then the three correctness items in dependency order: make `normalize()` testable, then test it against Python, then settle handedness. Then the threshold documentation, then Phase 8. Milestone: both hand-ported math paths are covered by tests in CI and handedness is settled with evidence either way. This is the block that protects the actual thesis contribution.

**Week 3, Days 15 to 21. Produce one real number, then attack the evidence gaps.** The accuracy re-run comes first because Days 5 and 6 have made it reproducible. Then the three evidence-integrity documents that a panel will ask for: signer leakage, gold-standard provenance, and the numerals risk. Then Phase 9, matrix first and execution second. Milestone: one measurement in `benchmark_history.json` that is not retroactive, and the three weakest claims in the thesis documented before someone else finds them.

**Week 4, Days 22 to 30. Study tooling, stats skeleton, thesis drafts, review.** Consent and the delete path first, because RA 10173 compliance gates everything downstream of it, then instruments, then scoring, then the stats skeleton, then the three drafts. Milestone: the study could start the day the handedness question and recruitment clear.

**Constraint that a reader would otherwise miss:** Days 22 to 24 build study tooling and dry-run it on synthetic data, which is safe at any time. **Recruitment, consent collection, and any real participant data must not start until Days 10 and 11 have settled `normalize()` parity and handedness.** `docs/hardening-plan.md` Gate C says it plainly: a study run against a pipeline with swapped hands produces data you throw away. Nothing in this plan schedules participant contact, and Day 22's consent form is a template, not a deployment.

---

# 4. Daily Entries

## Week 1: Truth, Requests, and a Repo That Builds

### Day 1 | 2026-09-21, Monday | PRD Phase 0 and 9a (spec 13) | PR #2 Stage A1, A2 | 3h

**Goal:** Downgrade every phase gate whose evidence the repo contradicts, and mark the two spec 13 tasks whose runs never happened.

**Dependencies:** None.

**First action, before anything else:** `docs/hardening-plan.md` is not in this branch's working tree. Materialise it read-only with `git fetch origin docs/hardening-plan && git show origin/docs/hardening-plan:docs/hardening-plan.md > /tmp/hardening-plan.md`, then read Stage A from `/tmp/`. Do not merge the branch, do not copy the file into `docs/`, and do not commit it. If the `git show` output differs from what section 1c of this plan describes, stop and take the fallback below.

**Done when:**
- `.kiro/specs/13-benchmarking-harness/tasks.md` tasks 5 and 7 stay `[x]` and each gains a `NEVER EXECUTED` note: task 5 naming the absent device or emulator, task 7 naming both the absent device and the `/sdcard/Download/` API 29+ write-path bug from `docs/hardening-plan.md` §1.8.
- `grep -c '\[x\]' .kiro/specs/13-benchmarking-harness/tasks.md` still returns **14**. The count is deliberately unchanged: per Conflict 5 both tasks are *create* tasks, `LatencyBenchmarkTest.kt` and `BenchmarkMode.kt` both exist, and `BenchmarkMode` is wired at `MainActivity.kt:56`. Unchecking would assert that code which exists does not.
- The spec's Notes section states plainly that a checked box in that file means written, not executed.
- `docs/phase-gates.md` Phase 4 and Phase 5 rows read CONDITIONAL, emulator only, real device pending, instead of a bare check.
- The Phase 6 gate cell carries UNEVIDENCED IN REPO with a pointer to the blank `docs/phase10-expert-validation-protocol.md`.
- The Phase 9a row separates accuracy (executed 2026-07-23) from latency and FPS (never executed on a device).
- No row in `docs/phase-gates.md` asserts a measurement taken on a physical device.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Documentation Agent (PRD section 7)
PHASE: PRD Phase 0 and 9a, executing docs/hardening-plan.md Stage A1 and A2
OBJECTIVE: Make docs/phase-gates.md and spec 13 tasks.md state only what the repo can evidence.
INPUT: docs/phase-gates.md, .kiro/specs/13-benchmarking-harness/tasks.md, benchmarking/benchmark_history.json, benchmarking/phase4_emulator_report.md, docs/phase10-expert-validation-protocol.md, docs/30-day-plan.md sections 1a and 1b conflict 5, and docs/hardening-plan.md Stage A obtained via: git fetch origin docs/hardening-plan && git show origin/docs/hardening-plan:docs/hardening-plan.md > /tmp/hardening-plan.md (that file is NOT in this branch's working tree)
CONSTRAINTS: Do not edit benchmark_history.json (Day 2 owns it). Do not touch spec 21 tasks.md (Day 13 owns it). Do not delete history, downgrade with a reason. Do not invent dates or device names. Change no code. Do not merge or check out the docs/hardening-plan branch, and do not commit a copy of it into docs/. Do NOT un-check spec 13 tasks 5 or 7: both files exist (LatencyBenchmarkTest.kt, BenchmarkMode.kt wired at MainActivity.kt:56) and unchecking would create a new false statement. Annotate instead.
ACCEPTANCE CRITERIA: spec 13 tasks 5 and 7 remain [x] and each carries a NEVER EXECUTED note, task 7's naming the API 29+ /sdcard/Download write-path bug; grep -c '[x]' on that file still returns 14; the spec Notes section says a checked box means written not executed; phase-gates Phase 4 and 5 rows say emulator only and real device pending; Phase 6 gate cell says UNEVIDENCED IN REPO and cites the blank protocol file; Phase 9a row splits accuracy from latency and FPS; no row claims a physical-device measurement.
OUTPUT LOCATION: docs/phase-gates.md, .kiro/specs/13-benchmarking-harness/tasks.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If PR #2 turns out to have changed since 2026-09-15, spend the 3h re-reading it via `git show origin/docs/hardening-plan:docs/hardening-plan.md` and writing a delta note into this plan's section 1c instead. Same hours, no new dependency. If `git fetch` fails for lack of network, the gate downgrades still proceed: they depend on repo artifacts already listed in section 1a, not on PR #2 itself, and PR #2 supplies only the stage vocabulary.

---

### Day 2 | 2026-09-22, Tuesday | PRD Phase 9a | PR #2 Stage A3, A4 | 3h

**Goal:** Quarantine the retroactive benchmark entries so plots show only measured data, and give the README an honest limitations section.

**Dependencies:** Day 1 (gate rows already downgraded, so the two files agree).

**Done when:**
- The two `2026-07-07T12:00:00` entries in `benchmarking/benchmark_history.json` carry `"provenance": "retroactive-estimate"` and no longer carry `gate_pass: true`.
- `python benchmarking/plot_history.py --type fps` produces output containing no retroactive point, or exits saying there is no measured FPS data.
- `README.md` has a Known Limitations section naming all five of: emulator-only performance, unevidenced expert sign-off, numerals weakness with the FIVE F1 figure, n=203 test set, and the Holistic-versus-split-model skew.
- The original two entries are still present in the file, marked, not deleted.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: QA/Benchmarking Agent (PRD section 7)
PHASE: PRD Phase 9a, executing docs/hardening-plan.md Stage A3 and A4
OBJECTIVE: Mark the retroactive benchmark entries as estimates excluded from plots, and add a Known Limitations section to README.md.
INPUT: benchmarking/benchmark_history.json, benchmarking/plot_history.py, benchmarking/phase4_emulator_report.md, README.md, docs/30-day-plan.md section 1b conflicts 6 and 8
CONSTRAINTS: Do not delete the two retroactive entries, mark them. Do not alter the two accuracy entries from 2026-07-23. Do not add any new measurement. Do not touch model or app code. Use only numbers already present in the repo.
ACCEPTANCE CRITERIA: both 2026-07-07 entries have provenance retroactive-estimate and no gate_pass true; plot_history.py excludes them or reports no measured FPS data; README Known Limitations names emulator-only perf, unevidenced expert sign-off, FIVE F1 0.333, n=203 test set, and the Holistic skew; the file still validates as JSON via python -m json.tool.
OUTPUT LOCATION: benchmarking/benchmark_history.json, README.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If `plot_history.py` cannot run for lack of matplotlib in the active venv, do the JSON marking and the README section by hand and record the plot verification as a Day 5 acceptance item. Same hours.

---

### Day 3 | 2026-09-23, Wednesday | PRD Phase 0, 1, and 3 | none | 3h

**Goal:** Send the three overdue human sign-off requests and start a tracked waiting list.

**Dependencies:** Days 1 and 2 (the requests must describe the corrected status, not the overstated one).

**Done when:**
- `docs/sign-off-requests.md` exists with three dated request sections: PM structure confirm (Phase 0 gate), PM dataset and 50-class sign-off (Phase 1 gate), adviser acknowledgment of FSL-105 provenance (open decision 3).
- Each section states what is being approved, what changes if it is refused, and carries `waiting on [role] since Day 3 (2026-09-23)`.
- The FSL-105 request links `docs/dataset-notes.md` and states plainly that the dataset is public and not team-collected.
- A blocker table at the top lists all open human dependencies with the day each was requested.
- No section records an outcome, an approval, or a signature.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Documentation Agent (PRD section 7)
PHASE: PRD Phase 0, 1, and 3 gate requests
OBJECTIVE: Produce one file containing the three outstanding approval requests for PM Cabrera and adviser Abella, each with an explicit waiting-since marker.
INPUT: docs/phase-gates.md (as corrected on Day 1), docs/PRD.md sections 5 and 6, docs/dataset-notes.md, docs/selected-50-signs.md, .kiro/specs/00-project-init/gap-reconciliation-report.md
CONSTRAINTS: Never write an approval, a signature, a date of approval, or an outcome. These are requests only. Do not name any person beyond Cabrera and Abella as given in PRD section 5. Do not change scope. Do not edit phase-gates.md gate cells today.
ACCEPTANCE CRITERIA: file contains exactly three request sections; each names what is approved, the consequence of refusal, and a waiting on X since Day 3 (2026-09-23) line; a blocker table lists all open human dependencies with request dates; the FSL-105 section states the dataset is public and cites docs/dataset-notes.md; no outcome is recorded anywhere.
OUTPUT LOCATION: docs/sign-off-requests.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** Draft the same three requests as email-ready text in the same file without the blocker table, then use the remaining time to list every other decision in `docs/phase-gates.md` Open decisions that needs a human. Same hours.

---

### Day 4 | 2026-09-24, Thursday | PRD Phase 10 precondition | PR #2 Stage D precondition | 3h

**Goal:** Turn the missing device from an unstated blocker into a dated request with named acceptable hardware.

**Dependencies:** Day 3 (the procurement ask goes to the same people, in the same tracked list).

**Done when:**
- `docs/device-procurement.md` lists at least three acceptable device classes against the `AGENTS.md` target (Helio G series or Snapdragon 6 series, 4GB RAM), with no invented prices or model availability.
- It records the three acquisition routes to try: borrow, department loan, purchase, each with who to ask.
- It states the precondition sentence that every BLOCKED day in this plan cites: one physical Android device matching the target class, with USB debugging enabled and `adb devices` listing it.
- A readiness checklist exists that can be executed in one session once a device arrives, covering all three `benchmarking/environment_protocol.md` conditions.
- `waiting on device access since Day 4 (2026-09-24), expected date unknown` appears in `docs/sign-off-requests.md`.
- No device is named as acquired and no measurement is scheduled against a specific date.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Model Optimization Agent (PRD section 7)
PHASE: PRD Phase 10 precondition, supporting docs/hardening-plan.md Stage D
OBJECTIVE: Produce a device procurement and readiness document that names the target hardware class and the one precondition every blocked measurement day depends on.
INPUT: AGENTS.md hard constraints, docs/PRD.md sections 2 and 11, benchmarking/environment_protocol.md, benchmarking/phase4_emulator_report.md, docs/sign-off-requests.md
CONSTRAINTS: Never state that a device has been obtained. Do not invent prices, stock, model availability, or an access date. Use TBD for anything unknown. Do not relabel the existing emulator figures as device results. Write no code.
ACCEPTANCE CRITERIA: at least three acceptable device classes listed against the Helio G or Snapdragon 6 and 4GB target; three acquisition routes each with who to ask; one explicit precondition sentence referencing adb devices; a one-session readiness checklist covering optimal, low_light and cluttered; a waiting-since line added to docs/sign-off-requests.md; no acquired device and no dated measurement.
OUTPUT LOCATION: docs/device-procurement.md, docs/sign-off-requests.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** Write the readiness checklist and the three environment condition setups in full detail (lux targets, background, framing, warm-up) so that zero thinking is needed on device day. Same hours, nothing new required.

---

### Day 5 | 2026-09-25, Friday | PRD Phase 9a and 13 | PR #2 Stage B1 | 3h

**Goal:** Replace the three-line `requirements.txt` with declared environments that match what the code actually imports.

**Dependencies:** Day 1 (Phase 9a row now distinguishes what ran from what did not, so this day knows which env it must unblock).

**Done when:**
- `training/requirements-mediapipe.txt`, `training/requirements-tf.txt`, and `benchmarking/requirements.txt` all exist, generated from the working environments rather than written by hand.
- `benchmarking/requirements.txt` pins TensorFlow and scikit-learn, and resolves the duplicate `ai_edge_litert` (1.4.0 and 2.2.0 are both installed) to one version.
- Each file installs clean into a fresh throwaway venv, verified by actually doing it.
- `python -c "import tensorflow, sklearn"` succeeds in the TF env and `python -c "import cv2, mediapipe"` succeeds in the mediapipe env.
- `training/requirements.txt` either points at the new files or is removed, with the reason recorded.
- A note records the version skew: runs logged in `experiments_log.json` used TensorFlow 2.19.0, the benchmarking env has 2.21.0.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Model/Training Agent (PRD section 7)
PHASE: PRD Phase 9a and 13, executing docs/hardening-plan.md Stage B1
OBJECTIVE: Declare the two real Python environments as installable requirements files so the accuracy benchmark and the training scripts can be reconstructed.
INPUT: training/requirements.txt, training/.venv, benchmarking/.venv, benchmarking/accuracy_benchmark.py, benchmarking/plot_history.py, training/models/experiments_log.json, docs/30-day-plan.md section 1b conflict 10
CONSTRAINTS: Pin exact versions from the environments that actually work, do not guess. Do not upgrade or reinstall the existing venvs. Do not change any script's imports. Record the 2.19.0 versus 2.21.0 skew rather than hiding it. Resolve the duplicate ai_edge_litert install to one version.
ACCEPTANCE CRITERIA: three requirements files exist; each installs clean in a fresh venv, demonstrated; import tensorflow and sklearn succeeds in the TF env; import cv2 and mediapipe succeeds in the mediapipe env; only one ai_edge_litert version is pinned; the TF version skew is recorded in a comment or note.
OUTPUT LOCATION: training/requirements-mediapipe.txt, training/requirements-tf.txt, benchmarking/requirements.txt
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If a fresh-venv install fails on a pin that cannot resolve, record the exact failing package and version in `docs/reproducibility.md` as a known blocker and pin the rest. A partially declared env with a named failure beats an undeclared one.

---

### Day 6 | 2026-09-26, Saturday | PRD Phase 13 | PR #2 Stage B2, B5 | 4h

**Goal:** Make the repo build from a clean clone with no out-of-repo dependency.

**Dependencies:** Day 5 (the reproducibility document describes the environments declared yesterday).

**Done when:**
- `app/fetch_assets.sh` no longer reads from `../../kumpas-data/` and instead fetches every asset from a pinned, addressable source.
- Every fetched asset has a recorded SHA-256 checksum, verified after download, with the script failing on mismatch.
- `docs/reproducibility.md` exists and contains literal commands for clone, env, assets, build, benchmark.
- The clean-clone path is actually tested: clone to a fresh temporary directory, run the script, confirm all five assets land in `app/android/app/src/main/assets/`.
- If the classifier cannot yet be fetched because no release exists, the script fails with an explicit message naming the missing release, and `docs/sign-off-requests.md` gains `waiting on model release publication since Day 6`, because publishing a GitHub Release needs repo owner rights.
- `.gitignore` lines 11 and 12 are left alone, with the reason recorded (models stay untracked by design, the fetch path is the fix).

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Mobile/Flutter Agent (PRD section 7)
PHASE: PRD Phase 13, executing docs/hardening-plan.md Stage B2 and B5
OBJECTIVE: Remove the out-of-repo dependency from app/fetch_assets.sh and document a clean-clone path to a running build.
INPUT: app/fetch_assets.sh, .gitignore, app/android/app/src/main/assets/, ../kumpas-data/tflite/, training/requirements-tf.txt, benchmarking/requirements.txt, docs/30-day-plan.md section 1b conflict 9
CONSTRAINTS: Do not commit any .tflite or .task file. Do not change .gitignore lines 11 and 12. Do not modify the trained model or the app's feature logic. If a pinned release does not exist yet, fail loudly rather than falling back to the sibling directory. Do not claim a build succeeded unless it did.
ACCEPTANCE CRITERIA: fetch_assets.sh has no ../../kumpas-data reference; every asset has a verified SHA-256 and the script exits nonzero on mismatch; docs/reproducibility.md lists literal commands for clone, env, assets, build, benchmark; a fresh clone plus the script places all five assets in the assets directory, or fails with a named missing release; any human-gated step is added to docs/sign-off-requests.md.
OUTPUT LOCATION: app/fetch_assets.sh, docs/reproducibility.md, docs/sign-off-requests.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If no release can be published without owner action, write `docs/reproducibility.md` in full and change the script to take a `--classifier-path` argument with a clear error when it is absent. The clean-clone gate stays open with a named single blocker. Same hours.

---

### Day 7 | 2026-09-27, Sunday | buffer | none | 4h

**Goal:** Absorb Week 1 overrun and carry nothing new.

**Dependencies:** Days 1 to 6.

**Done when:**
- Every Day 1 to 6 acceptance criterion is either met or listed in `docs/30-day-plan-log.md` with the reason and the day it moves to.
- No new scope was added.

**What this day absorbs if the week ran clean, in priority order:** first, the Day 6 clean-clone test if it was not completed end to end, because Days 15 and 20 depend on it. Second, the Day 5 fresh-venv verification if it was skipped. Third, a reconciliation note if the branch moved to `main` mid-week. If all of Week 1 is genuinely clean, write the Week 1 section of `docs/30-day-plan-log.md` and stop. Do not pull Day 8 forward.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Documentation Agent (PRD section 7)
PHASE: buffer day, no PRD phase advances
OBJECTIVE: Record Week 1 actual versus planned and close out any unmet acceptance criterion from Days 1 to 6.
INPUT: docs/30-day-plan.md Days 1 to 6, docs/phase-gates.md, .kiro/specs/13-benchmarking-harness/tasks.md, benchmarking/benchmark_history.json, README.md, training/requirements-tf.txt, benchmarking/requirements.txt, app/fetch_assets.sh, docs/reproducibility.md, docs/sign-off-requests.md
CONSTRAINTS: Add no new scope. Do not start Day 8 work. Do not mark any gate closed that a human has not signed. Do not create new features or tests.
ACCEPTANCE CRITERIA: docs/30-day-plan-log.md has a Week 1 section listing each Day 1 to 6 criterion as met or deferred with a reason and a target day; no file outside the Day 1 to 6 output list was modified; open human blockers are still listed with their waiting-since dates.
OUTPUT LOCATION: docs/30-day-plan-log.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If Week 1 is fully clean and the log takes under an hour, use the remainder to expand `docs/reproducibility.md` with a troubleshooting section for failures you actually hit this week. No new dependency.

---

## Week 2: Prove the Math, Then Close Phase 8

### Day 8 | 2026-09-28, Monday | PRD Phase 13 | PR #2 Stage B4 | 3h

**Goal:** Add CI so every change from here on is checked, starting with the feedback parity test.

**Dependencies:** Day 5 (CI installs from the declared requirements files), Day 6 (CI cannot build the app without the asset path fixed, so the Python and Kotlin jobs run even if the APK job is gated).

**Done when:**
- `.github/workflows/ci.yml` exists, where before Day 8 `.github/` did not exist at all.
- The workflow runs four things: `flutter analyze`, `flutter test`, `./gradlew testDebugUnitTest`, and `python -m compileall training benchmarking`.
- A run is green, and `FeedbackEngineParityTest` appears by name in the job log.
- If the APK build cannot run in CI for lack of a fetchable classifier, that job is present but explicitly skipped with a named reason, not silently omitted.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: QA/Benchmarking Agent (PRD section 7)
PHASE: PRD Phase 13, executing docs/hardening-plan.md Stage B4
OBJECTIVE: Create a CI workflow that runs Flutter analysis and tests, the Kotlin unit tests including the feedback parity test, and a Python compile check.
INPUT: app/, app/android/app/src/test/kotlin/com/kumpas/kumpas_app/, training/requirements-tf.txt, benchmarking/requirements.txt, docs/reproducibility.md, app/pubspec.yaml, app/android/app/build.gradle.kts
CONSTRAINTS: Do not weaken or skip any existing test to make CI pass. Do not commit secrets or a keystore. Do not add a job that downloads the classifier from a sibling directory. If the APK job cannot run, mark it skipped with a reason rather than deleting it. Change no application code.
ACCEPTANCE CRITERIA: .github/workflows/ci.yml exists and runs flutter analyze, flutter test, gradlew testDebugUnitTest, and python -m compileall training benchmarking; one run is green; FeedbackEngineParityTest is visible by name in the log; any skipped job states why.
OUTPUT LOCATION: .github/workflows/ci.yml
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the Flutter or Gradle action cannot be made green in 3h, commit the Python-only job green and open the Flutter and Kotlin jobs as a named TODO in `docs/reproducibility.md`. Partial CI that runs beats a red workflow.

---

### Day 9 | 2026-09-29, Tuesday | PRD Phase 5 | PR #2 Stage C3 | 3h

**Goal:** Make `VisionEngine.normalize()` testable without a camera, so Day 10 can test it.

**Dependencies:** Day 8 (CI exists, so the new class is covered from the moment it lands).

**Done when:**
- The normalization logic lives in its own class or object, constructible in a unit test with no Android camera and no MediaPipe session.
- A headless test instantiates it and calls it, proving no camera is needed.
- The hardcoded class count in `VisionEngine.kt` is read from `label_map.json` instead, and no literal `50` remains in that path.
- `./gradlew testDebugUnitTest` passes and the new headless test appears in the output.
- Behaviour is unchanged: this is an extraction, not a rewrite of the math.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Mobile/Flutter Agent (PRD section 7)
PHASE: PRD Phase 5, executing docs/hardening-plan.md Stage C3
OBJECTIVE: Extract the normalization math from VisionEngine into a headlessly testable unit and read the class count from label_map.json.
INPUT: app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt, app/android/app/src/main/assets/label_map.json, training/preprocessing/build_sequences.py, app/android/app/src/test/kotlin/com/kumpas/kumpas_app/
CONSTRAINTS: Do not change the normalization arithmetic, only its location and testability. Do not touch the feedback comparison math. Do not switch the landmarker from PoseLandmarker plus HandLandmarker to Holistic, that is unapproved spec 22 work. Keep the 258-feature layout exactly as is.
ACCEPTANCE CRITERIA: normalization is callable from a unit test with no camera and no MediaPipe session; a headless test constructs it and runs; no literal 50 remains in the class-count path and the value comes from label_map.json; gradlew testDebugUnitTest passes with the new test listed; the feature count is still 258.
OUTPUT LOCATION: app/android/app/src/main/kotlin/com/kumpas/kumpas_app/, app/android/app/src/test/kotlin/com/kumpas/kumpas_app/
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the extraction fights the existing structure, write the headless test against the current `VisionEngine` surface with the camera parts stubbed, and record the extraction as a Day 14 buffer item. Day 10 needs a callable normalization path, however it is reached.

---

### Day 10 | 2026-09-30, Wednesday | PRD Phase 5 | PR #2 Stage C2 | 3h

**Goal:** Prove the Kotlin normalization matches the Python reference, closing one of the two untested hand-ported math paths.

**Dependencies:** Day 9 (normalization is callable headlessly), Day 5 (the mediapipe env can run `build_sequences.py` to export fixtures), Day 8 (CI runs it).

**Done when:**
- At least 5 fixtures are exported from `training/preprocessing/build_sequences.py` as committed test data, landmark values only, no video.
- A Kotlin unit test asserts the Kotlin normalization output matches each fixture within a stated tolerance, following the pattern `FeedbackEngineParityTest.kt` already established.
- The test runs in CI and is visible in the Day 8 workflow log.
- The tolerance value is stated in the test with a one-line reason, not left as a bare number.
- If the two paths disagree, the test fails and the disagreement is recorded in `docs/normalization-parity.md` rather than the tolerance being widened to force a pass.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Mobile/Flutter Agent (PRD section 7)
PHASE: PRD Phase 5, executing docs/hardening-plan.md Stage C2
OBJECTIVE: Add a parity test proving the Kotlin normalization matches build_sequences.py on exported fixtures.
INPUT: training/preprocessing/build_sequences.py, ../kumpas-data/sequences/X_test.npy, app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt, app/android/app/src/test/kotlin/com/kumpas/kumpas_app/FeedbackEngineParityTest.kt, training/requirements-mediapipe.txt
CONSTRAINTS: Commit landmark fixtures only, never raw video, per PRD section 9. Do not widen the tolerance to force a pass. If the paths disagree, report it and stop. Do not change the Python reference to match Kotlin. Do not alter the feedback engine.
ACCEPTANCE CRITERIA: at least 5 fixtures committed as test data; a Kotlin unit test asserts per-value agreement within a stated and justified tolerance; the test runs in CI and appears in the workflow log; on disagreement, docs/normalization-parity.md records the exact mismatching indices and magnitudes.
OUTPUT LOCATION: app/android/app/src/test/kotlin/com/kumpas/kumpas_app/, app/android/app/src/test/resources/, docs/normalization-parity.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If fixture export fails, hand-build three small synthetic landmark frames with known expected output, assert against those, and record that real-data fixtures are still needed. A weaker passing test plus a named gap beats no test.

---

### Day 11 | 2026-10-01, Thursday | PRD Phase 5 and 6 | PR #2 Stage C1 | 3h

**Goal:** Settle whether the app's left and right hand assignment matches the training data. This is the highest-risk correctness item in the repo.

**Dependencies:** Day 10 (normalization parity established, so a handedness mismatch cannot be confused with a normalization bug), Day 9 (headless test path).

**Done when:**
- `docs/handedness-calibration.md` records, with evidence, whether the serving convention matches training: the app assigns hand blocks from MediaPipe `categoryName()` into fixed offsets 132 and 195, while `CameraPreviewView` feeds the raw front-camera bitmap with no mirroring.
- A test takes one known sequence and asserts the left and right feature blocks land at the same offsets in both the Kotlin and Python paths.
- The document states the outcome either way. A confirmed match is as valuable as a found bug and must be recorded, not left implicit.
- If they disagree, the mismatch is documented with the affected offsets and a fix is proposed but **not** applied today, because per `docs/holistic-v2-risks.md` R1 a fix in the split-model path may be discarded by spec 22.
- The document notes that a naive parity test passes when both sides are mirrored the same way, so the assertion is about anatomical correctness on a real signer, not just agreement.
- The blocker line is recorded: study recruitment cannot start until this day's outcome is documented.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Mobile/Flutter Agent (PRD section 7)
PHASE: PRD Phase 5 and 6, executing docs/hardening-plan.md Stage C1
OBJECTIVE: Determine and document whether the app's left and right hand feature assignment matches the training convention, and assert it in a test.
INPUT: app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt, app/android/app/src/main/kotlin/com/kumpas/kumpas_app/CameraPreviewView.kt, training/preprocessing/build_sequences.py, ../kumpas-data/sequences/, benchmarking/phase4_emulator_report.md, docs/holistic-v2-risks.md R1
CONSTRAINTS: Do not apply a mirroring fix today, document the finding and propose the fix. Do not switch to HolisticLandmarker, that is unapproved spec 22 work. Do not assume the conventions agree, prove it. State clearly that agreement between two identically mirrored implementations is not anatomical correctness. Never claim a real signer was tested if none was.
ACCEPTANCE CRITERIA: docs/handedness-calibration.md states match or mismatch with the evidence that decided it; a test asserts left and right blocks at offsets 132 and 195 land identically across the Kotlin and Python paths; the limitation about mirrored-but-agreeing implementations is written down; if mismatched, affected offsets and a proposed fix are recorded without being applied.
OUTPUT LOCATION: docs/handedness-calibration.md, app/android/app/src/test/kotlin/com/kumpas/kumpas_app/
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If a definitive answer needs a real signer in front of a real camera, which it may, document the desk-verifiable half (offset mapping, mirroring path, training convention) and record the anatomical confirmation as BLOCKED on device access from Day 4. Name it as blocking study recruitment.

---

### Day 12 | 2026-10-02, Friday | PRD Phase 6 | PR #2 Stage C5, C4 partial | 3h

**Goal:** Document every feedback threshold and divisor, and state plainly which of the four promised feedback dimensions the shipped 258-dim feature set can actually support.

**Dependencies:** Day 11 (per-hand prompt validity depends on the handedness finding), Day 10 (normalization is trustworthy).

**Done when:**
- `docs/feedback-thresholds.md` has an entry for each of the four thresholds (timing 0.30, motion 0.25, handshape 0.22, orientation 0.25) and each of the three divisors, recording value, meaning, how it was chosen, and sensitivity.
- Every value whose origin cannot be traced is marked **arbitrary, origin not recorded**, rather than given a plausible-sounding justification.
- A four-dimension coverage section states, with the numbers from section 1b conflict 8: timing and motion rest on pose wrists detected in essentially every frame; handshape and orientation rest on hand landmarks with mean `any_hand_rate` 0.3516 aggregate and 0.954 in-span, and a wrist-relative fingertip amplitude roughly 7.5x smaller than the pose block.
- Both hand-rate numbers appear, aggregate and in-span, with the explanation that the aggregate is inflated by rest padding.
- The corroborating result is cited: the four handshape-only signs are the four weakest classes (FIVE F1 0.333, FOUR 0.600, THREE 0.667, TWO 0.800).
- The document does not claim the feedback is invalid, and does not claim it is fine. It states what is evidenced and hands the open question to Day 17.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Feedback Algorithm Agent (PRD section 7)
PHASE: PRD Phase 6, executing docs/hardening-plan.md Stage C5
OBJECTIVE: Document every feedback threshold and divisor, and state which of the four promised feedback dimensions the 258-dim feature set actually supports.
INPUT: app/android/app/src/main/kotlin/com/kumpas/kumpas_app/FeedbackEngine.kt, training/feedback/feedback_engine.py, training/preprocessing/extraction_log.csv, training/models/reports/20260705_194813_no_face_eval.md, docs/PRD.md sections 1 and 2, docs/holistic-v2-diagnosis.md, docs/30-day-plan.md section 1b conflict 8
CONSTRAINTS: Do not change any threshold value. Do not invent a justification for an untraceable constant, mark it arbitrary. Report both the aggregate and the in-span hand rates, never the aggregate alone. Do not declare the feedback engine valid or invalid, that is the FSL Expert's call. Do not modify the engine code.
ACCEPTANCE CRITERIA: all four thresholds and three divisors each have value, meaning, origin, and sensitivity; untraceable values are marked arbitrary origin not recorded; the coverage section gives mean lh_rate 0.0803, rh_rate 0.3445, any_hand_rate 0.3516 aggregate and 0.954 in-span; it names timing and motion as pose-backed and handshape and orientation as hand-dependent; the numerals F1 figures are cited as corroboration.
OUTPUT LOCATION: docs/feedback-thresholds.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If tracing constant origins stalls, write the four-dimension coverage section first since it is the defense-critical half, and list each untraceable constant as an open question for the threshold calibration discussion. Same hours.

---

### Day 13 | 2026-10-03, Saturday | PRD Phase 8 (spec 21) | PR #2 Stage E1 | 4h

**Goal:** Confirm the recorded local-only decision, reconcile the Phase 8 status conflict, and run the one remaining spec 21 verification.

**Dependencies:** Day 1 (gate rows corrected), Day 8 (CI runs the session-logging unit tests), Day 12 (nothing in Phase 8 depends on feedback, but Week 2's math work must land before a gate closes).

**Done when:**
- `docs/decisions/2026-10-03-session-logging-local-only.md` exists, confirming from `.kiro/specs/00-project-init/gap-reconciliation-report.md` §3.3 that the backend is OUT and storage is local-only, and noting that the `docs/PRD.md` §6 Phase 8 gate text asking the PM to decide is stale.
- The decision record states that the keep-or-delete question in `docs/hardening-plan.md` Stage E1 is already answered by the code, since `MainActivity.kt` constructs `SessionManager` and `DataExporter`, and cites the grep.
- Spec 21 task 16 is executed on the emulator: a practice flow creates a session and attempts in SQLite, export produces parseable JSON, clear wipes the data, and JSONL migration handles an existing file.
- Task 16 is checked only if all four of those actually pass. If any fails, it stays unchecked with the failure recorded.
- `docs/phase-gates.md` Phase 8 row and spec 21 `tasks.md` agree with each other after the edit.
- The Phase 8 row states the verification was done on an emulator, not a device.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Mobile/Flutter Agent (PRD section 7)
PHASE: PRD Phase 8 (spec 21), confirming docs/hardening-plan.md Stage E1
OBJECTIVE: Record the local-only storage decision as confirmed, execute spec 21 task 16 on the emulator, and make the Phase 8 gate row and spec 21 tasks file agree.
INPUT: .kiro/specs/00-project-init/gap-reconciliation-report.md section 3.3, .kiro/specs/21-session-logging/tasks.md, docs/PRD.md section 6 Phase 8, app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt, app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionManager.kt, app/android/app/src/main/kotlin/com/kumpas/kumpas_app/DataExporter.kt, benchmarking/verify_session_logging.sh, docs/phase-gates.md
CONSTRAINTS: Do not reopen the backend decision, confirm it. Do not delete the session-logging classes, they are wired. Do not check task 16 unless all four checks pass. Do not describe emulator verification as device verification. Add no cloud or network code.
ACCEPTANCE CRITERIA: a dated decision record confirms backend OUT and local-only and notes the stale PRD gate text; it cites MainActivity constructing SessionManager and DataExporter; the four task 16 checks are each reported pass or fail; task 16 is checked only if all four pass; the Phase 8 gate row and spec 21 tasks.md agree and the row says emulator.
OUTPUT LOCATION: docs/decisions/2026-10-03-session-logging-local-only.md, .kiro/specs/21-session-logging/tasks.md, docs/phase-gates.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the emulator will not cooperate, write the decision record and reconcile the status conflict, then leave task 16 unchecked with the emulator failure recorded. The status reconciliation is the part that matters for honesty and it needs no emulator.

---

### Day 14 | 2026-10-04, Sunday | buffer | none | 4h

**Goal:** Absorb Week 2 overrun and carry nothing new.

**Dependencies:** Days 8 to 13.

**Done when:**
- Every Day 8 to 13 acceptance criterion is met or recorded in `docs/30-day-plan-log.md` with a reason and a target day.
- No new scope was added.

**What this day absorbs if the week ran clean, in priority order:** first, Day 11 handedness if it ran long, since it is the highest-risk item in the plan and Week 4's study tooling is gated on its outcome. Second, the Day 9 extraction if Day 10 used a stubbed fallback. Third, the Day 8 Flutter or Kotlin CI jobs if only the Python job went green. If Week 2 is clean, write the Week 2 log section and stop. Do not pull Day 15 forward, because Day 15 produces the first citable number of the month and should start fresh.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Documentation Agent (PRD section 7)
PHASE: buffer day, no PRD phase advances
OBJECTIVE: Record Week 2 actual versus planned and close out any unmet acceptance criterion from Days 8 to 13.
INPUT: docs/30-day-plan.md Days 8 to 13, docs/30-day-plan-log.md, .github/workflows/ci.yml, docs/normalization-parity.md, docs/handedness-calibration.md, docs/feedback-thresholds.md, docs/decisions/, .kiro/specs/21-session-logging/tasks.md, docs/phase-gates.md
CONSTRAINTS: Add no new scope. Do not start Day 15 work. Do not close any gate a human has not signed. Do not widen a test tolerance to turn a Week 2 failure into a pass.
ACCEPTANCE CRITERIA: docs/30-day-plan-log.md has a Week 2 section listing each Day 8 to 13 criterion as met or deferred with a reason and target day; the handedness outcome is recorded as settled or still open; no file outside the Day 8 to 13 output list was modified.
OUTPUT LOCATION: docs/30-day-plan-log.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If Week 2 is clean, use the time to add more fixtures to the Day 10 parity test. More fixtures on an existing test introduces no new dependency and directly strengthens the thesis-critical claim.

---

## Week 3: Produce One Real Number, Then Attack the Evidence Gaps

### Day 15 | 2026-10-05, Monday | PRD Phase 9a (spec 13) | PR #2 Stage B gate consequence | 3h

**Goal:** Teach the accuracy benchmark to record its own environment, then re-run it and record the first non-retroactive entry of the month.

**Dependencies:** Day 5 (declared TF environment), Day 6 (reproducible asset path), Day 2 (retroactive entries already quarantined so the new entry is not mixed with estimates). Scheduling rule satisfied: this is the first day that produces a number, and it comes after both the env day and the clean-clone day.

**Script change comes first, and it is not optional.** Per Conflict 10, `accuracy_benchmark.py` builds its entry with `"device": "offline/python"` and `"condition": "n/a"` hardcoded and writes no library versions anywhere. Running it as-is produces a third unattributable entry and leaves the 2.19.0-versus-2.21.0 question exactly where it was. Add an `environment` block to the `entry` dict in `main()` first: `tensorflow.__version__`, `sys.version`, `platform.platform()`, and the resolved model filename. Keep it additive so `log_utils.validate_entry` and the existing four entries stay valid. Budget roughly 45m of the 3h for this.

**Done when:**
- `benchmarking/accuracy_benchmark.py` appends an `environment` block containing at minimum the TensorFlow version, the Python version, and the platform string, read at runtime rather than hardcoded, and `python -m json.tool benchmarking/benchmark_history.json` still passes.
- The script runs to completion from `benchmarking/requirements.txt`, against `../kumpas-data/sequences/X_test.npy` and `y_test.npy`. Expect the `Feature mismatch` line on stdout: `X_test.npy` is 1662-dim and the deployed model takes 258, and `run_tflite_inference()` slices correctly. That message is normal output, not an error.
- A new entry appears in `benchmarking/benchmark_history.json` with a real timestamp, no `provenance: retroactive-estimate`, and that environment block populated.
- `"device"` and `"condition"` on the new entry are honest for an offline host run, and the entry does not borrow a device name from anywhere.
- The result is compared against the two 2026-07-23 entries and the 0.9507 in the eval report, and the comparison is recorded whether it matches or not.
- If the number differs from 0.9507, the difference is recorded as a finding with the TensorFlow 2.19.0 versus 2.21.0 skew named as a candidate cause. It is not adjusted, hidden, or averaged away.
- `docs/phase-gates.md` Phase 9a accuracy line cites this new entry.
- The entry does **not** claim the number is a defensible final accuracy. Per `docs/holistic-v2-risks.md` R4, the Stage G2 test-set fix will change the baseline, and n=203 at about 4 clips per class cannot support a tight claim.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: QA/Benchmarking Agent (PRD section 7)
PHASE: PRD Phase 9a (spec 13), accuracy execution
OBJECTIVE: Add a runtime environment block to accuracy_benchmark.py, then re-run it and log one real, non-retroactive entry that records the environment it ran in.
INPUT: benchmarking/accuracy_benchmark.py (note: main() currently hardcodes device offline/python and condition n/a and records no library versions), benchmarking/log_utils.py, benchmarking/requirements.txt, ../kumpas-data/sequences/X_test.npy, ../kumpas-data/sequences/y_test.npy, ../kumpas-data/tflite/kumpas_50sign_builtins_dynamic.tflite, benchmarking/benchmark_history.json, training/models/reports/20260705_194813_no_face_eval.md, docs/30-day-plan.md section 1b conflict 10
CONSTRAINTS: Do not modify the model or the test split. Do not retrain. Do not touch run_tflite_inference's 1662 to 258 slicing logic, it is correct. Do not edit the two 2026-07-23 entries or the two retroactive ones. Make the environment block additive so existing entries still validate. If the result differs from 0.9507, record the difference, do not reconcile it by changing anything. Do not describe this as a defensible final accuracy. Do not claim latency or FPS, this day measures accuracy only. Do not invent a device name for a host-side run.
ACCEPTANCE CRITERIA: accuracy_benchmark.py reads the TensorFlow version, Python version, and platform at runtime and writes them into the appended entry; the script completes and appends exactly one entry with a real timestamp and that block populated; benchmark_history.json still parses via python -m json.tool and the four prior entries are byte-identical; the entry has no retroactive-estimate provenance; the result is compared in writing against 0.9507 and the two prior runs; any difference is recorded with the TF 2.19.0 versus 2.21.0 skew named; phase-gates Phase 9a accuracy line cites the new entry; no tight-accuracy claim is made.
OUTPUT LOCATION: benchmarking/accuracy_benchmark.py, benchmarking/benchmark_history.json, docs/phase-gates.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the benchmark will not run, capture the exact traceback into `docs/reproducibility.md` as a named environment blocker and fix the requirements pin that caused it. A reproducible failure with a cause is real progress on Phase 9a.

---

### Day 16 | 2026-10-06, Tuesday | PRD Phase 1 and 3 | PR #2 Stage G2 precursor | 3h

**Goal:** Determine whether the same signer appears in both train and test, and state honestly what can and cannot be known.

**Dependencies:** Day 15 (the accuracy number this leakage question qualifies now exists and is reproducible).

**Done when:**
- `docs/signer-leakage-check.md` reports whether clip indices overlap between the train and test splits, computed from the actual split files.
- It states the hard limit up front: `docs/dataset-notes.md` records that FSL-105 CSVs carry no signer IDs, so signer-level disjointness **cannot** be established from metadata at all.
- It reports what the clip-index analysis can and cannot imply, without overclaiming either way.
- It specifies the only two routes to a real answer: manual review of clips for recurring signers, or the FSL-105 dataset paper, and sizes the manual route in hours.
- It states the consequence for the thesis: if signer disjointness cannot be shown, the accuracy claim must be scoped as signer-dependent rather than presented as generalization.
- No signer count, signer identity, or disjointness conclusion is asserted without evidence.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Data/Preprocessing Agent (PRD section 7)
PHASE: PRD Phase 1 and 3, supporting docs/hardening-plan.md Stage G2
OBJECTIVE: Report whether train and test clip indices overlap and state the limits of what signer-level leakage analysis can conclude for FSL-105.
INPUT: ../FSL-105 A dataset for recognizing 105 Filipino sign language videos/train.csv, ../FSL-105 A dataset for recognizing 105 Filipino sign language videos/test.csv, training/preprocessing/selected_classes.json, ../kumpas-data/sequences/clips_test.json, docs/dataset-notes.md, training/preprocessing/extraction_log.csv
CONSTRAINTS: Do not claim a signer count or any signer identity, the CSVs have no signer IDs. Do not assert disjointness or leakage without evidence. Do not re-split the data or retrain, this is analysis only. Do not modify the dataset, it stays outside the repo. Do not contradict docs/dataset-notes.md.
ACCEPTANCE CRITERIA: the document reports clip-index overlap between splits as a computed result; it states that signer IDs do not exist in the metadata; it names the two routes to a real answer and estimates the manual review in hours; it states the consequence that accuracy may need scoping as signer-dependent; no unevidenced disjointness conclusion appears.
OUTPUT LOCATION: docs/signer-leakage-check.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the split files are harder to align than expected because of the Windows backslash paths and BOM recorded in `docs/dataset-notes.md`, document the path-normalization problem itself as a reproducibility finding and report overlap for the subset that does parse.

---

### Day 17 | 2026-10-07, Wednesday | PRD Phase 6 | none | 3h

**Goal:** Document where all 50 gold standards came from, what validation is on file, and draft the question to you about the unevidenced expert sign-off.

**Dependencies:** Day 12 (the four-dimension coverage finding is what makes part of the sign-off worth revisiting), Day 3 (the human-request pattern and the waiting list already exist).

**Done when:**
- `docs/gold-standard-provenance.md` lists all 50 signs with their source clip, taken from the existing manifest and the protocol table, not reconstructed from memory.
- It records the selection method as medoid, the most statistically typical clip per class, and states explicitly that this is not the same as a linguistically ideal reference.
- It records the `status` field currently in `training/feedback/gold_standards_manifest.json` verbatim, whether that is provisional or otherwise.
- It states the gap: `docs/phase-gates.md` claims expert approval on 2026-07-23 while `docs/phase10-expert-validation-protocol.md` is blank, and no filled record was found in the repo.
- It **asks** you three questions without answering them: does an offline record of the 2026-07-23 session exist, if so where should it be filed, and if not should a scoped re-validation be scheduled.
- It scopes the possible re-validation using the `docs/holistic-v2-diagnosis.md` finding: timing and motion align on pose wrists and retain their sign-off, so only handshape and orientation would need fresh review. This makes the ask much smaller than a full 50-sign session.
- `waiting on FSL Expert record clarification since Day 17` is added to `docs/sign-off-requests.md`.
- No expert name, no date, and no rating is written anywhere.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Feedback Algorithm Agent (PRD section 7)
PHASE: PRD Phase 6 (spec 10-feedback-logic)
OBJECTIVE: Document gold-standard provenance for all 50 signs and draft the open question about the unevidenced 2026-07-23 expert sign-off.
INPUT: training/feedback/gold_standards_manifest.json, docs/phase10-expert-validation-protocol.md, docs/phase-gates.md Phase 6 row, docs/selected-50-signs.md, docs/feedback-thresholds.md, docs/holistic-v2-diagnosis.md, docs/sign-off-requests.md
CONSTRAINTS: Never write an expert name, a validation date, or a rating. Never state the sign-off happened or did not happen, state that the repo cannot evidence it. Do not change the manifest status field. Do not select or replace any gold standard clip. Ask the questions, do not answer them.
ACCEPTANCE CRITERIA: all 50 signs listed with source clip and selection method; medoid is distinguished from linguistically ideal; the manifest status field is quoted verbatim; the phase-gates versus blank-protocol gap is stated; exactly three questions are posed to the author unanswered; the possible re-validation is scoped to handshape and orientation only with the pose-wrist reason given; a waiting-since line is added.
OUTPUT LOCATION: docs/gold-standard-provenance.md, docs/sign-off-requests.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the manifest does not cover all 50 clips, build the table from the 50 rows in `docs/phase10-expert-validation-protocol.md` Block B, mark which entries could not be cross-checked against the manifest, and treat that mismatch as a provenance finding in its own right.

---

### Day 18 | 2026-10-08, Thursday | PRD Phase 3 | PR #2 Stage G1 documentation only | 3h

**Goal:** Name the two weakest claims in the thesis before a panelist does: the numerals and the test-set size.

**Dependencies:** Day 15 (a reproduced accuracy number exists), Day 16 (the leakage limits are documented and feed the same argument).

**Done when:**
- `docs/defense-risks.md` records the numerals weakness with the actual per-class figures: FIVE F1 0.333 and recall 0.250, FOUR 0.600, THREE 0.667, TWO 0.800, each on support 4.
- It records that the aggregate 95.07% passes the 90% gate while a whole semantic family, the numbers, is near-unusable, and that this is the predictable first question at defense.
- It records the test-set problem: n=203 across 50 classes, about 4 clips per class, so one additional error moves a per-class recall by 25 points, and no confidence interval is reported anywhere.
- It records that the winning run logged `best_val_accuracy` 1.0, which gives no model-selection signal and makes the reported test figure partly a selection artifact.
- It connects the numerals to Day 12: the four worst classes are exactly the signs that differ only by handshape, and handshape is the dimension the 258-dim representation supports least well.
- It states what would fix each item (stratified re-split or cross-validation for the test set, and the representation work for the numerals) and marks both as **out of 30-day scope**, with the reason.
- No fix is attempted and no model is retrained.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: QA/Benchmarking Agent (PRD section 7)
PHASE: PRD Phase 3, documenting docs/hardening-plan.md Stage G1 and G2 without executing them
OBJECTIVE: Write the defense-risk record for the numerals weakness and the n=203 test set, connecting both to the handshape representation finding.
INPUT: training/models/reports/20260705_194813_no_face_eval.md, benchmarking/benchmark_history.json, training/models/experiments_log.json, docs/feedback-thresholds.md, docs/signer-leakage-check.md, docs/holistic-v2-diagnosis.md
CONSTRAINTS: Do not retrain, re-split, or change any model. Use only per-class numbers already in the repo. Do not propose a fix as if it were scheduled, mark both as out of 30-day scope with the reason. Do not soften the numbers. Do not claim the 90 percent gate is invalid, state precisely what it does and does not cover.
ACCEPTANCE CRITERIA: FIVE, FOUR, THREE and TWO F1 figures recorded with support 4; the aggregate-passes-while-family-fails point stated; n=203 and the 25-point-per-error sensitivity stated; best_val_accuracy 1.0 recorded as no selection signal; the link to the handshape dimension from docs/feedback-thresholds.md is explicit; each fix named and marked out of scope; nothing retrained.
OUTPUT LOCATION: docs/defense-risks.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If time runs short, write the numerals section in full and defer the test-set section to Day 21 buffer. The numerals are the more likely opening question because the per-class table is published in the eval report.

---

### Day 19 | 2026-10-09, Friday | PRD Phase 9 | none | 3h

**Goal:** Define the full Phase 9 integration test matrix and mark honestly which rows can run now and which need a device.

**Dependencies:** Day 13 (Phase 8 closed, so session logging is part of the flow under test), Day 11 (the handedness finding determines whether per-hand feedback rows are trustworthy), Day 4 (the device precondition sentence this matrix cites).

**Done when:**
- `benchmarking/integration_test_matrix.md` enumerates all 50 gestures against the three `benchmarking/environment_protocol.md` conditions, with the per-row pass criteria.
- Each row is marked runnable-now (emulator) or device-blocked, citing the Day 4 precondition for the blocked ones.
- The matrix includes the Phase 7 open item explicitly: the success-path feedback sheet check that the Phase 7 gate row deferred to Phase 9.
- It states the PRD Phase 9 gate condition, no open blocking bugs, and defines what counts as blocking.
- It records that emulator rows cannot substitute for device rows, and that passing every emulator row does **not** close Phase 9.
- No result is recorded today. This is the matrix, not the run.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: QA/Benchmarking Agent (PRD section 7)
PHASE: PRD Phase 9, integration testing
OBJECTIVE: Define the 50-gesture by 3-condition integration test matrix with per-row pass criteria and an honest runnable-now versus device-blocked marking.
INPUT: benchmarking/environment_protocol.md, docs/selected-50-signs.md, docs/phase-gates.md Phase 7 and 9 rows, docs/device-procurement.md, docs/handedness-calibration.md, app/lib/ui/, docs/PRD.md section 6 Phase 9
CONSTRAINTS: Record no test results today, this is the matrix only. Do not mark an emulator row as satisfying a device row. Do not reduce the gesture count below 50 or change the three conditions. Do not claim Phase 9 can close on emulator evidence. Cite the Day 4 precondition for every blocked row.
ACCEPTANCE CRITERIA: all 50 gestures appear against all three conditions with per-row pass criteria; every row is marked runnable-now or device-blocked with the precondition cited; the Phase 7 success-path feedback sheet item is present as a named row; blocking-bug is defined; an explicit statement says emulator rows do not close Phase 9; no results recorded.
OUTPUT LOCATION: benchmarking/integration_test_matrix.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If enumerating 50 by 3 runs long, complete the optimal-condition column for all 50 and template the other two, since optimal is the only condition an emulator can reasonably approximate anyway.

---

### Day 20 | 2026-10-10, Saturday | PRD Phase 9 and 7 | none | 4h

**Goal:** Execute the emulator-runnable part of the Phase 9 matrix, including the Phase 7 success-path feedback item.

**Dependencies:** Day 19 (the matrix exists), Day 13 (session logging verified so attempts persist during the run), Day 6 (the build path works), Day 8 (CI green so the build under test is the checked one).

**Done when:**
- Every row marked runnable-now in `benchmarking/integration_test_matrix.md` has a recorded result: pass, fail, or not-run with a reason.
- The Phase 7 success-path feedback sheet item has a recorded emulator outcome, and the row still shows the device check as outstanding.
- Any failure is written up as a numbered bug with reproduction steps, not summarized as a count.
- The results state the environment as emulator and name the AVD, and nowhere describe it as a mid-range device.
- `docs/phase-gates.md` Phase 9 row is updated to in-progress with the fraction of rows executed, and **not** to closed.
- If the Day 11 handedness question came out as a mismatch or is still open, every per-hand feedback row is marked provisional with that reason.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: QA/Benchmarking Agent (PRD section 7)
PHASE: PRD Phase 9 and the PRD Phase 7 deferred item
OBJECTIVE: Run every emulator-runnable row of the integration matrix and record results, including the deferred Phase 7 success-path feedback check.
INPUT: benchmarking/integration_test_matrix.md, app/, benchmarking/verify_session_logging.sh, docs/handedness-calibration.md, docs/phase-gates.md, benchmarking/phase4_emulator_report.md
CONSTRAINTS: Never label emulator output as a mid-range device result. Do not close the Phase 9 gate. Do not skip a failing row, record it. Do not record a device-blocked row as passed. If handedness is unresolved, mark per-hand feedback rows provisional. Record no latency or FPS numbers, this day is functional testing only.
ACCEPTANCE CRITERIA: every runnable-now row has pass, fail, or not-run with a reason; the Phase 7 success-path item has an emulator outcome and its device check remains open; each failure is a numbered bug with reproduction steps; the environment is named as the emulator AVD; phase-gates Phase 9 row reads in-progress with the executed fraction, not closed.
OUTPUT LOCATION: benchmarking/integration_test_matrix.md, benchmarking/integration_test_results.md, docs/phase-gates.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the emulator cannot sustain a 50-gesture pass in 4h, run a stratified subset of 15 covering the weak numerals, the confusion pairs from the eval report, and one sign per category, and record exactly which rows were not attempted.

---

### Day 21 | 2026-10-11, Sunday | buffer | none | 4h

**Goal:** Absorb Week 3 overrun and carry nothing new.

**Dependencies:** Days 15 to 20.

**Done when:**
- Every Day 15 to 20 acceptance criterion is met or recorded in `docs/30-day-plan-log.md` with a reason and a target day.
- No new scope was added.

**What this day absorbs if the week ran clean, in priority order:** first, any unexecuted Day 20 matrix rows, since Phase 9 progress is the week's headline. Second, the Day 18 test-set section if it was deferred. Third, the Day 16 manual clip review if the clip-index analysis was inconclusive and a few hours of review would settle it. If Week 3 is clean, write the Week 3 log section and stop. Do not pull Week 4 forward.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Documentation Agent (PRD section 7)
PHASE: buffer day, no PRD phase advances
OBJECTIVE: Record Week 3 actual versus planned and close out any unmet acceptance criterion from Days 15 to 20.
INPUT: docs/30-day-plan.md Days 15 to 20, docs/30-day-plan-log.md, benchmarking/benchmark_history.json, docs/signer-leakage-check.md, docs/gold-standard-provenance.md, docs/defense-risks.md, benchmarking/integration_test_matrix.md, benchmarking/integration_test_results.md, docs/phase-gates.md
CONSTRAINTS: Add no new scope. Do not start Day 22 work. Do not close the Phase 9 gate. Do not record any device measurement. Do not adjust the Day 15 accuracy result.
ACCEPTANCE CRITERIA: docs/30-day-plan-log.md has a Week 3 section listing each Day 15 to 20 criterion as met or deferred with a reason and target day; the count of integration rows executed versus device-blocked is stated; no file outside the Day 15 to 20 output list was modified.
OUTPUT LOCATION: docs/30-day-plan-log.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If Week 3 is clean, extend `docs/defense-risks.md` with the Holistic-versus-split-model skew from conflict 7, which is a third likely defense question and needs no new measurement.

---

## Week 4: Study Tooling, Stats Skeleton, Thesis Drafts, Review

> **Constraint for the whole week.** Days 22 to 25 build and dry-run study tooling on synthetic data, which is safe to do now. **No recruitment, no consent collection, and no real participant data may begin until the Day 10 normalization parity and the Day 11 handedness outcomes are documented and settled.** `docs/hardening-plan.md` Gate C states the reason: a study run against a pipeline with swapped hands produces data you throw away. Nothing this week contacts a participant.

### Day 22 | 2026-10-12, Monday | PRD Phase 11 | PR #2 Stage F1, F3 | 3h

**Goal:** Produce the RA 10173 consent template and verify the data deletion path actually deletes.

**Dependencies:** Day 13 (session logging closed and local-only confirmed, so consent describes real storage), Day 11 (the handedness outcome determines whether recruitment may follow at all).

**Done when:**
- `evaluation/consent-form-template.md` exists, covering RA 10173 informed consent for landmark data, what is stored, where it is stored, retention, and the participant's right to withdraw and have data deleted.
- It states local-only storage with no cloud sync, consistent with the Day 13 decision record.
- The delete path is actually exercised on the emulator: `clearAllData` runs and a subsequent query returns no participant, session, attempt, or assessment rows.
- The verification result is recorded, and if deletion leaves residue that is written up as a compliance bug, because RA 10173 requires the delete path to work.
- The template has no participant name, no real ID, and no signature.
- A note states that consent collection must not begin before the Day 11 handedness outcome is settled, naming this plan's Week 4 constraint.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Security/Privacy Agent (PRD section 7)
PHASE: PRD Phase 11, executing docs/hardening-plan.md Stage F1 and F3
OBJECTIVE: Write the RA 10173 consent template for the evaluation study and verify on the emulator that the clear-all-data path leaves no residue.
INPUT: docs/PRD.md section 9, docs/decisions/2026-10-03-session-logging-local-only.md, app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionDatabase.kt, app/android/app/src/main/kotlin/com/kumpas/kumpas_app/DataExporter.kt, app/lib/ui/profile_screen.dart, docs/dataset-notes.md, docs/handedness-calibration.md
CONSTRAINTS: Never fill in a participant name, ID, or signature, this is a template. Do not state a participant count as recruited. Do not schedule recruitment. Do not add any network or cloud storage. Do not claim deletion works unless the emulator check proves it. Keep the 40-participant figure as the PRD target, not as enrolled.
ACCEPTANCE CRITERIA: the template covers landmark data, storage location, retention, withdrawal, and deletion rights under RA 10173; it states local-only with no cloud sync; clearAllData is executed on the emulator and a follow-up query returns zero rows across all four tables, with the result recorded; any residue is filed as a compliance bug; a note states consent collection is gated on the handedness outcome.
OUTPUT LOCATION: evaluation/consent-form-template.md, evaluation/delete-path-verification.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the emulator is unavailable, write the consent template and read the deletion code path statically, recording which tables `clearAllData` touches and flagging any the schema defines but the delete misses. That static check has real value and needs no emulator.

---

### Day 23 | 2026-10-13, Tuesday | PRD Phase 11 | PR #2 Stage F1 | 3h

**Goal:** Draft the pre-test and post-test instruments and the scoring rubric.

**Dependencies:** Day 22 (consent must exist before the instruments it governs), Day 13 (the in-app assessment screen from spec 21 task 11 already exists and the paper instruments must match its fields).

**Done when:**
- `evaluation/pre-test-instrument.md` and `evaluation/post-test-instrument.md` exist and their items match the fields the existing `app/lib/ui/assessment_screen.dart` already collects, so the app and the paper forms do not diverge.
- `evaluation/scoring-rubric.md` defines the standardized rubric the PRD Phase 11 deliverable requires, with explicit point allocations and what counts as correct for a signed gesture.
- The rubric states who scores, and that inter-rater agreement is unaddressed if only one rater exists.
- The post-test includes the SUS items the assessment screen already implements, and the item count matches.
- Group assignment (experimental versus control) is described as a procedure, with no participant assigned.
- No instrument contains fabricated normative data, cut scores borrowed from nowhere, or a citation that was not read.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Research/Evaluation Agent (PRD section 7)
PHASE: PRD Phase 11, executing docs/hardening-plan.md Stage F1
OBJECTIVE: Draft pre-test and post-test instruments matching the existing in-app assessment fields, plus the standardized scoring rubric.
INPUT: app/lib/ui/assessment_screen.dart, .kiro/specs/16-evaluation-study-design/, docs/PRD.md section 6 Phase 11 and section 5, evaluation/consent-form-template.md, docs/selected-50-signs.md
CONSTRAINTS: Read-only on the app codebase per the persona definition. Do not invent normative data, cut scores, or citations. Do not assign or recruit any participant. Keep the PRD 40-participant figure as a target, not as enrolled. Do not change the 50-sign scope. Match the existing SUS item count in the app rather than inventing one.
ACCEPTANCE CRITERIA: both instruments exist and their items map one to one onto the fields in assessment_screen.dart, with the mapping shown; the rubric gives explicit point allocations and a correctness definition per gesture; it names who scores and flags the single-rater limitation; the post-test SUS item count matches the app; group assignment is a procedure with no participant named.
OUTPUT LOCATION: evaluation/pre-test-instrument.md, evaluation/post-test-instrument.md, evaluation/scoring-rubric.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If `.kiro/specs/16-evaluation-study-design/` turns out to be thinner than expected, build the instruments from the app fields alone and record the spec gap as an open item for adviser input.

---

### Day 24 | 2026-10-14, Wednesday | PRD Phase 11 | PR #2 Stage F4 | 3h

**Goal:** Build the rubric scoring script and prove it works on synthetic data with known answers.

**Dependencies:** Day 23 (the rubric it implements), Day 22 (the export format it consumes), Day 5 (a declared Python environment to run in).

**Done when:**
- `evaluation/score_sessions.py` reads an export file in the format `DataExporter` actually produces and applies the Day 23 rubric.
- `evaluation/synthetic_fixtures/` contains generated input with **known** expected scores, including edge cases: a perfect participant, a zero-score participant, a partial session, and a participant who withdrew mid-session.
- The script produces the known expected score for every fixture, verified by an assertion that fails loudly if not.
- The synthetic data is clearly labelled synthetic in both filename and file content, so it can never be mistaken for participant data.
- The script refuses to run on an export whose schema does not match, with a clear error rather than a silent wrong number.
- No real participant data is created, referenced, or implied.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Research/Evaluation Agent (PRD section 7)
PHASE: PRD Phase 11, executing docs/hardening-plan.md Stage F4
OBJECTIVE: Write the rubric scoring script and validate it against synthetic fixtures with known expected scores.
INPUT: evaluation/scoring-rubric.md, app/android/app/src/main/kotlin/com/kumpas/kumpas_app/DataExporter.kt, evaluation/delete-path-verification.md, benchmarking/requirements.txt, app/android/app/src/test/kotlin/com/kumpas/kumpas_app/DataExporterTest.kt
CONSTRAINTS: Generate synthetic data only, never real participant data. Label every fixture synthetic in both the filename and the contents. Do not modify the app or the exporter. Fail loudly on a schema mismatch rather than guessing. Do not report any score as a study result.
ACCEPTANCE CRITERIA: the script parses the real DataExporter JSON structure; at least four synthetic fixtures exist covering perfect, zero, partial, and withdrawn cases; every fixture produces its known expected score under an assertion that fails on mismatch; a schema mismatch produces a clear nonzero-exit error; every fixture is labelled synthetic in filename and contents.
OUTPUT LOCATION: evaluation/score_sessions.py, evaluation/synthetic_fixtures/
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the export schema is hard to reproduce by hand, generate a real export from the emulator with synthetic practice attempts and use that as the fixture base, noting it came from emulator input and not from a participant.

---

### Day 25 | 2026-10-15, Thursday | PRD Phase 12 | none | 3h

**Goal:** Build the statistics skeleton and prove it runs end to end on dummy data.

**Dependencies:** Day 24 (the scored output it consumes), Day 23 (the instruments that define the variables), Day 5 (declared environment).

**Done when:**
- `evaluation/analyze_prepost.py` computes descriptives, a paired pre-versus-post comparison, and an effect size, taking the Day 24 scoring output as input.
- It runs end to end on dummy data whose answer is known in advance, and the computed result matches that known answer.
- The dummy dataset includes a deliberate null case (no pre-post difference) and a deliberate strong-effect case, and the script reports each correctly.
- The script states its assumptions in output or comments: which test it runs, what distributional assumption that test makes, and what to do if the assumption fails.
- The script does **not** hardcode a participant count and works with whatever n the input contains, since no participant has been recruited.
- Nothing in the output is presented as a study finding, and the dummy origin is labelled in the output itself.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Research/Evaluation Agent (PRD section 7)
PHASE: PRD Phase 12, stats and analysis skeleton
OBJECTIVE: Build the pre-post analysis skeleton and verify it on dummy data with a known answer, including a null case and a strong-effect case.
INPUT: evaluation/score_sessions.py, evaluation/synthetic_fixtures/, evaluation/pre-test-instrument.md, evaluation/post-test-instrument.md, evaluation/scoring-rubric.md, benchmarking/requirements.txt
CONSTRAINTS: Read-only on the app codebase. Do not hardcode n equals 40 or any participant count. Never present dummy output as a study finding, label it dummy in the output. Do not invent a p-value or an effect size outside a computed run. State the test's distributional assumption rather than leaving it implicit. Create no real participant data.
ACCEPTANCE CRITERIA: the script computes descriptives, a paired pre-post comparison, and an effect size from the Day 24 output format; it runs end to end on dummy input and reproduces the known expected result; the null case reports no effect and the strong case reports one; the chosen test and its assumption are stated; no participant count is hardcoded; output is labelled dummy.
OUTPUT LOCATION: evaluation/analyze_prepost.py, evaluation/dummy_data/
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the paired test needs a library not in the declared environment, implement descriptives and effect size only, add the dependency to `benchmarking/requirements.txt`, and record the paired test as the remaining step.

---

### Day 26 | 2026-10-16, Friday | PRD Phase 13 precursor | none | 3h

**Goal:** Draft thesis objectives that match what the repo actually does.

**Dependencies:** Day 18 (the defense risks that bound what can be claimed), Day 15 (the one reproduced number), Day 12 (which feedback dimensions are supported), Day 16 (how the accuracy claim must be scoped).

**Done when:**
- `docs/thesis-drafts/objectives.md` states objectives traceable to artifacts in this repo, with each objective citing the file that evidences it or marked as not yet evidenced.
- Any objective that the current evidence cannot support is marked so, rather than being reworded until it sounds supported.
- The accuracy objective is scoped per Day 16: if signer disjointness cannot be shown, it reads as signer-dependent performance on a held-out clip split, not as generalization.
- The feedback objective distinguishes the four promised dimensions by evidential strength per Day 12, rather than claiming all four equally.
- The latency and FPS objectives are marked **not yet measured**, since no device measurement exists.
- Scope is unchanged: 50 gestures, Android only, on-device inference, closed vocabulary.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Documentation Agent (PRD section 7)
PHASE: PRD Phase 13 precursor, thesis drafting support
OBJECTIVE: Draft thesis objectives aligned to what the repo can actually evidence, each with a citation or a not-yet-evidenced marker.
INPUT: docs/PRD.md sections 1 and 2, docs/defense-risks.md, docs/feedback-thresholds.md, docs/signer-leakage-check.md, benchmarking/benchmark_history.json, docs/phase-gates.md, training/models/reports/20260705_194813_no_face_eval.md
CONSTRAINTS: Do not change project scope, it stays 50 gestures, Android only, on-device inference, closed vocabulary. Do not claim a latency or FPS result, none has been measured on a device. Do not reword an unsupported objective to sound supported, mark it. Cite only files that exist. Invent no citation to external literature.
ACCEPTANCE CRITERIA: every objective either cites an evidencing file or is marked not yet evidenced; the accuracy objective is scoped per docs/signer-leakage-check.md; the feedback objective separates the four dimensions by evidential strength per docs/feedback-thresholds.md; latency and FPS objectives are marked not yet measured; scope statements are unchanged from PRD section 2.
OUTPUT LOCATION: docs/thesis-drafts/objectives.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** Draft the objectives that are fully evidenced and list the rest as an evidence-gap table mapping each unsupported objective to the measurement that would support it. That table is useful to the adviser on its own.

---

### Day 27 | 2026-10-17, Saturday | PRD Phase 13 precursor | none | 4h

**Goal:** Draft Scope and Limitations, and the FSL-105 provenance note.

**Dependencies:** Day 26 (objectives set the frame that limitations qualify), Day 16, Day 17, Day 18 (the three evidence-gap documents this draws on).

**Done when:**
- `docs/thesis-drafts/scope-and-limitations.md` records the in-scope and out-of-scope lists from `docs/PRD.md` §2 unchanged, plus the limitations this month actually established.
- The limitations include, each with its source document: emulator-only performance with no device measurement, n=203 at about 4 clips per class, numerals weakness, signer disjointness unestablished, handshape and orientation feedback resting on sparse hand data, gold standards selected by medoid rather than expert design, and the Holistic-versus-split-model deviation from the locked stack.
- `docs/thesis-drafts/fsl105-provenance-note.md` states plainly that FSL-105 is a public dataset (Tupal and Villaverde, Mendeley Data, 2023, as recorded in `docs/dataset-notes.md`) and **not** team-collected, and that the methodology chapter must not claim original data collection for training.
- The provenance note distinguishes what was original: the 50-class selection, preprocessing, augmentation, model, app, and the future evaluation study.
- It records that the dataset licence terms must be verified on the Mendeley record and cited, marking this as an open item rather than asserting a licence.
- No citation is fabricated. The dataset attribution comes from `docs/dataset-notes.md` and is marked as needing verification against the original record.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Documentation Agent (PRD section 7)
PHASE: PRD Phase 13 precursor, thesis drafting support
OBJECTIVE: Draft Scope and Limitations and the FSL-105 provenance note, grounded in the evidence documents produced this month.
INPUT: docs/PRD.md section 2, docs/dataset-notes.md, docs/defense-risks.md, docs/signer-leakage-check.md, docs/gold-standard-provenance.md, docs/feedback-thresholds.md, docs/thesis-drafts/objectives.md, docs/30-day-plan.md section 1b conflict 7
CONSTRAINTS: Do not change the in-scope or out-of-scope lists from PRD section 2. Do not assert the dataset licence, mark it as needing verification on the Mendeley record. Do not fabricate any citation. Do not claim original data collection for the training set. Every limitation must cite the document that established it.
ACCEPTANCE CRITERIA: scope lists match PRD section 2 verbatim; at least the seven named limitations appear, each citing its source document; the provenance note states FSL-105 is public and not team-collected and names the recorded attribution; it separates what was original to this project; the licence verification is an open item, not an assertion.
OUTPUT LOCATION: docs/thesis-drafts/scope-and-limitations.md, docs/thesis-drafts/fsl105-provenance-note.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** Write the provenance note first, since it is the shorter document and it resolves `docs/phase-gates.md` Open decision 3 which has been waiting since Day 3, then carry Scope and Limitations into Day 28 buffer.

---

### Day 28 | 2026-10-18, Sunday | buffer | none | 4h

**Goal:** Absorb Week 4 overrun and carry nothing new.

**Dependencies:** Days 22 to 27.

**Done when:**
- Every Day 22 to 27 acceptance criterion is met or recorded in `docs/30-day-plan-log.md` with a reason and a target day.
- No new scope was added.

**What this day absorbs if the week ran clean, in priority order:** first, Day 27 Scope and Limitations if the provenance note took the day. Second, the Day 25 paired test if a dependency blocked it. Third, a dry run of Day 24 and Day 25 chained together, export through scoring through analysis, on synthetic data end to end, which is the single most useful rehearsal before a real study. If Week 4 is clean, write the Week 4 log section and stop. Do not pull Day 29 forward.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Documentation Agent (PRD section 7)
PHASE: buffer day, no PRD phase advances
OBJECTIVE: Record Week 4 actual versus planned and close out any unmet acceptance criterion from Days 22 to 27.
INPUT: docs/30-day-plan.md Days 22 to 27, docs/30-day-plan-log.md, evaluation/, docs/thesis-drafts/, docs/phase-gates.md
CONSTRAINTS: Add no new scope. Do not start Day 29 work. Do not create real participant data. Do not schedule recruitment. Do not present any synthetic or dummy output as a study result.
ACCEPTANCE CRITERIA: docs/30-day-plan-log.md has a Week 4 section listing each Day 22 to 27 criterion as met or deferred with a reason and target day; if the chained synthetic dry run was performed, its result is recorded; no file outside the Day 22 to 27 output list was modified.
OUTPUT LOCATION: docs/30-day-plan-log.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If Week 4 is clean, add more synthetic fixtures to Day 24, particularly a participant with missing post-test data, which is the most likely real-world messiness and the most likely thing to crash the analysis.

---

### Day 29 | 2026-10-19, Monday | PRD Phase 10 preparation | PR #2 Stage D4 design only | 3h

**Goal:** Specify the end-to-end latency and FPS measurement so the eventual device session is one sitting, and record why it cannot run yet.

**Dependencies:** Day 4 (the device precondition), Day 19 (the matrix conditions), Day 6 and Day 5 (satisfying the rule that no hardware-measurement work precedes the clean-clone and environment days).

**Done when:**
- `docs/e2e-latency-protocol.md` specifies measurement from camera frame in to feedback out, covering MediaPipe landmarking plus TFLite inference plus feedback computation, with the per-stage breakdown named.
- It states explicitly that the existing 0 to 2ms figure is interpreter-only and excludes the 35 to 63ms MediaPipe cost recorded in `benchmarking/phase4_emulator_report.md`, so it is not the number the 150ms gate is about.
- It records the three known harness defects to fix before the run, from `docs/hardening-plan.md` §1.8 and Stage D1 to D3: the `BenchmarkMode` write path failing on API 29+ given `maxSdkVersion="28"`, the counting of emitted events instead of camera frames, and the absence of any UI trigger.
- The FPS protocol requires a window of at least 60s, satisfying `collect_fps.py`'s own validation, and names all three `environment_protocol.md` conditions.
- The document is marked **BLOCKED** with the Day 4 precondition quoted.
- It records the `docs/holistic-v2-risks.md` R2 warning: the 258-dim baseline must be measured on the same device as any future Holistic pipeline for the comparison to be fair, so plan for two runs, not one.
- No measurement is recorded and no device is named as available.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Model Optimization Agent (PRD section 7)
PHASE: PRD Phase 10 preparation, designing docs/hardening-plan.md Stage D4 without executing it
OBJECTIVE: Specify the end-to-end camera-to-feedback latency and sustained FPS protocol, and record it as blocked on device access.
INPUT: benchmarking/phase4_emulator_report.md, benchmarking/collect_latency.py, benchmarking/collect_fps.py, benchmarking/environment_protocol.md, app/android/app/src/main/kotlin/com/kumpas/kumpas_app/BenchmarkMode.kt, app/android/app/src/main/AndroidManifest.xml, docs/device-procurement.md, docs/hardening-plan.md section 1.8, docs/holistic-v2-risks.md R2
CONSTRAINTS: Record no measurement, this is a protocol only. Never present the interpreter-only 0 to 2ms as an end-to-end result. Do not name a device as available. Do not modify BenchmarkMode today, list the fixes. Require a 60s minimum FPS window. Do not claim the 150ms gate is met or unmet, state that it is unmeasured end to end.
ACCEPTANCE CRITERIA: the protocol covers camera frame in to feedback out with a per-stage breakdown including MediaPipe; it states the interpreter-only figure excludes the 35 to 63ms landmarking cost; the three harness defects are listed as prerequisites; FPS requires at least 60s across all three named conditions; the document is marked BLOCKED quoting the Day 4 precondition; the R2 two-run fairness requirement is recorded; no measurement appears.
OUTPUT LOCATION: docs/e2e-latency-protocol.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** Write the protocol for the optimal condition only in full detail, and template the other two. Optimal is the condition to run first when a device arrives, so the detailed half is the half that gets used soonest.

---

### Day 30 | 2026-10-20, Tuesday | review only | none | 3h

**Goal:** Report what closed, what did not, and what carries forward. No new work.

**Dependencies:** All of Days 1 to 29.

**Done when:**
- `docs/30-day-review.md` contains a per-phase before-and-after table for PRD Phases 0 to 13, using the section 1a ledger as the before state.
- Every gate that changed status names the artifact that justified the change.
- Every gate that did not change names the blocker and the day it was last touched.
- A gap report lists what the target asked for and did not get: Phase 10 entirely, Phase 9a latency and FPS, Phase 9 closure, with the precondition for each.
- The human-blocker list shows every outstanding item with its waiting-since day, including PM structure confirm, PM dataset sign-off, adviser FSL-105 acknowledgment, device access, the FSL Expert record question, and the model release publication.
- The Day 31+ list is carried forward from section 9 of this plan with any new items added.
- No gate is marked closed that a human has not signed, and no measurement is claimed that was not taken.

~~~
Read AGENTS.md and docs/phase-gates.md first
AGENT: Documentation Agent (PRD section 7)
PHASE: review only, no PRD phase advances
OBJECTIVE: Produce the 30-day review and gap report comparing the Day 1 ledger against the Day 30 repo state.
INPUT: docs/30-day-plan.md sections 1a and 9, docs/30-day-plan-log.md, docs/phase-gates.md, benchmarking/benchmark_history.json, docs/sign-off-requests.md, docs/defense-risks.md, benchmarking/integration_test_results.md, evaluation/, docs/thesis-drafts/, docs/e2e-latency-protocol.md
CONSTRAINTS: Add no new scope and start no new work. Do not close any gate a human has not signed. Do not claim a measurement that was not taken. Do not relabel emulator results as device results. Use the section 1a ledger as the before state, not the original phase-gates table.
ACCEPTANCE CRITERIA: a before-and-after table covers PRD Phases 0 to 13; every changed gate cites its justifying artifact; every unchanged gate names its blocker and last-touched day; the gap report lists Phase 10, Phase 9a latency and FPS, and Phase 9 closure with preconditions; the human-blocker list shows all items with waiting-since days; the Day 31+ list is carried forward.
OUTPUT LOCATION: docs/30-day-review.md
Update docs/phase-gates.md status only for what was actually completed
~~~

**Fallback if blocked:** If the review runs long, produce the before-and-after table and the human-blocker list first. Those two are what the PM and adviser need in order to act, and the Day 31+ list already exists in section 9 of this plan.

---

# 5. Human-Only Task List

None of these can be completed by an agent. Each has a request artifact produced on the day shown, and an explicit waiting state. No day in this plan consumes an answer earlier than one buffer day after the request.

| # | Task | Who | Requested on | Request artifact | Blocks | Earliest consuming day |
|---|---|---|---|---|---|---|
| H1 | Confirm repo structure, Phase 0 gate | PM Cabrera | Day 3 | `docs/sign-off-requests.md` | Phase 0 gate closure, and strictly Rule #0 for all code work | Day 8 or later |
| H2 | Sign off dataset and the 50-class pick, Phase 1 gate | PM Cabrera | Day 3 | `docs/sign-off-requests.md` | Phase 1 gate closure | Day 8 or later |
| H3 | Acknowledge FSL-105 provenance for the methodology chapter | Adviser Abella | Day 3 | `docs/sign-off-requests.md`, `docs/dataset-notes.md` | `docs/phase-gates.md` Open decision 3, Day 27 provenance note | Day 27 |
| H4 | Obtain one physical low-mid-range Android device | Author, plus whoever lends or funds it | Day 4 | `docs/device-procurement.md` | Phase 10 entirely, Phase 9a latency and FPS, Phase 9 closure, Day 29 protocol execution | Day 31+ |
| H5 | Clarify whether an offline record of the 2026-07-23 FSL Expert session exists | Author, then FSL Expert | Day 17 | `docs/gold-standard-provenance.md` | Phase 6 gate evidence | Day 31+ |
| H6 | Publish the model and gold standards as a versioned release | Author, needs repo owner rights | Day 6 | `docs/sign-off-requests.md` | Full clean-clone build without a local classifier path | Day 31+ |
| H7 | Scoped FSL Expert re-validation of handshape and orientation prompts | FSL Expert | drafted Day 17 | `docs/gold-standard-provenance.md` | Phase 6 re-closure if H5 finds no record | Day 31+ |
| H8 | Recruit the 40 participants and collect consent | Author | not scheduled | `evaluation/consent-form-template.md` (Day 22) | Phase 11 execution | Day 31+, and gated on Day 11 |
| H9 | Rule #0 approval for the architecture and phase gates | PM Cabrera and Adviser Abella | Day 3 (via H1 and H2) | `docs/sign-off-requests.md` | Formally, every implementation day in this plan | Day 8 or later |

**Gating note on H8.** Recruitment and consent collection must not begin until the Day 10 normalization parity and Day 11 handedness outcomes are documented. If handedness is wrong, per-hand feedback prompts are wrong, and study data collected against that build has to be discarded. This plan schedules no participant contact.

**Note on H9.** As recorded at the top of this file, implementation code already exists in the repo ahead of this approval. That is a pre-existing condition, not something this plan creates. Days 1 to 30 are mostly verification, documentation, and repair of existing code, which I read as inside Rule #0. No day retrains a model or adds a feature.

---

# 6. Path Manifest

Each path appears once, with its state at the time this plan was written.

## Exists, read as evidence for this plan

| Path | State |
|---|---|
| `AGENTS.md` | EXISTS |
| `README.md` | EXISTS |
| `docs/PRD.md` | EXISTS |
| `docs/phase-gates.md` | EXISTS |
| `docs/dataset-notes.md` | EXISTS |
| `docs/selected-50-signs.md` | EXISTS |
| `docs/phase10-expert-validation-protocol.md` | EXISTS, blank template |
| `docs/holistic-v2-kiro-prompt.md` | EXISTS on `main`, planning input |
| `docs/holistic-v2-diagnosis.md` | EXISTS on `main`, planning input |
| `docs/holistic-v2-risks.md` | EXISTS on `main`, planning input |
| `docs/design/` | EXISTS |
| `training/requirements.txt` | EXISTS, incomplete (3 packages) |
| `training/preprocessing/extraction_log.csv` | EXISTS, 1016 ok rows |
| `training/preprocessing/build_sequences.py` | EXISTS |
| `training/preprocessing/selected_classes.json` | EXISTS |
| `training/models/experiments_log.json` | EXISTS, 4 runs |
| `training/models/reports/20260705_194813_no_face_eval.md` | EXISTS |
| `training/feedback/gold_standards_manifest.json` | EXISTS |
| `training/feedback/feedback_engine.py` | EXISTS |
| `training/.venv` | EXISTS, mediapipe and cv2, no TensorFlow |
| `benchmarking/benchmark_history.json` | EXISTS, 4 entries, 2 retroactive |
| `benchmarking/phase4_emulator_report.md` | EXISTS |
| `benchmarking/environment_protocol.md` | EXISTS |
| `benchmarking/accuracy_benchmark.py` | EXISTS. Handles the 1662 to 258 slice correctly, but hardcodes `device` and `condition` and records no library versions. MODIFIED ON DAY 15 to add a runtime `environment` block |
| `benchmarking/collect_latency.py` | EXISTS |
| `benchmarking/collect_fps.py` | EXISTS |
| `benchmarking/plot_history.py` | EXISTS |
| `benchmarking/log_utils.py` | EXISTS |
| `benchmarking/verify_session_logging.sh` | EXISTS |
| `benchmarking/.venv` | EXISTS, TensorFlow 2.21.0 and sklearn, no cv2 |
| `app/fetch_assets.sh` | EXISTS, depends on out-of-repo sibling |
| `app/lib/main.dart` | EXISTS |
| `app/lib/ui/` | EXISTS |
| `app/lib/ui/assessment_screen.dart` | EXISTS |
| `app/lib/ui/profile_screen.dart` | EXISTS |
| `app/lib/session/session_repository.dart` | EXISTS |
| `app/lib/session/session_lifecycle.dart` | EXISTS |
| `app/lib/feedback_engine/kumpas_channel.dart` | EXISTS |
| `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt` | EXISTS |
| `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt` | EXISTS |
| `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionManager.kt` | EXISTS, wired |
| `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionDatabase.kt` | EXISTS, wired |
| `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/DataExporter.kt` | EXISTS, wired |
| `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/BenchmarkMode.kt` | EXISTS, wired at `MainActivity.kt:56`, never executed (spec 13 task 7) |
| `app/android/app/src/androidTest/kotlin/com/kumpas/kumpas_app/benchmark/LatencyBenchmarkTest.kt` | EXISTS, never executed (spec 13 task 5) |
| `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/FeedbackEngine.kt` | EXISTS |
| `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/CameraPreviewView.kt` | EXISTS |
| `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/FeedbackEngineParityTest.kt` | EXISTS |
| `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/SessionDatabaseTest.kt` | EXISTS |
| `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/SessionManagerTest.kt` | EXISTS |
| `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/DataExporterTest.kt` | EXISTS |
| `app/android/app/src/main/AndroidManifest.xml` | EXISTS |
| `app/android/app/build.gradle.kts` | EXISTS |
| `app/android/app/src/main/assets/gold_standards.bin` | EXISTS, git-tracked |
| `app/android/app/src/main/assets/label_map.json` | EXISTS, git-tracked |
| `app/android/app/src/main/assets/kumpas_50sign.tflite` | EXISTS on disk, gitignored |
| `app/android/app/src/main/assets/pose_landmarker_lite.task` | EXISTS on disk, gitignored |
| `app/android/app/src/main/assets/hand_landmarker.task` | EXISTS on disk, gitignored |
| `.gitignore` | EXISTS, lines 11 to 12 exclude the models |
| `.kiro/specs/13-benchmarking-harness/tasks.md` | EXISTS, all 14 checked. Stays 14 after Day 1, which annotates tasks 5 and 7 rather than unchecking them |
| `.kiro/specs/21-session-logging/tasks.md` | EXISTS, 1 to 15 checked, 16 unchecked |
| `.kiro/specs/00-project-init/gap-reconciliation-report.md` | EXISTS |
| `.kiro/specs/10-feedback-logic/design.md` | EXISTS |
| `.kiro/specs/16-evaluation-study-design/` | EXISTS |
| `.kiro/steering/product.md` | EXISTS |
| `.kiro/steering/tech.md` | EXISTS, locks Holistic and Colab |
| `.kiro/steering/structure.md` | EXISTS |
| `evaluation/.gitkeep` | EXISTS, only file in `evaluation/` |
| `../kumpas-data/tflite/` | EXISTS on this machine, outside the repo |
| `../kumpas-data/sequences/X_test.npy` | EXISTS on this machine, shape `(203, 30, 1662)` |
| `../kumpas-data/sequences/y_test.npy` | EXISTS on this machine, shape `(203,)` |
| `../kumpas-data/sequences/X_train.npy` | EXISTS on this machine, 162,144,848 bytes → 813 samples |
| `../kumpas-data/sequences/X_train_aug.npy` | EXISTS on this machine, 648,579,008 bytes → 3252 samples |
| `../kumpas-data/sequences/y_train.npy` | EXISTS on this machine, 6,632 bytes → 813 labels |
| `../kumpas-data/sequences/y_train_aug.npy` | EXISTS on this machine, 26,144 bytes → 3252 labels |
| `../kumpas-data/sequences/clips_test.json` | EXISTS on this machine |
| `../FSL-105 A dataset for recognizing 105 Filipino sign language videos/` | EXISTS, outside the repo |

## Absent, to be created by the days shown

| Path | State | Created on |
|---|---|---|
| `docs/30-day-plan.md` | this file | Day 0 |
| `docs/sign-off-requests.md` | TO BE CREATED | Day 3, appended Days 4, 6, 17 |
| `docs/device-procurement.md` | TO BE CREATED | Day 4 |
| `training/requirements-mediapipe.txt` | TO BE CREATED | Day 5 |
| `training/requirements-tf.txt` | TO BE CREATED | Day 5 |
| `benchmarking/requirements.txt` | TO BE CREATED | Day 5 |
| `docs/reproducibility.md` | TO BE CREATED | Day 6 |
| `docs/30-day-plan-log.md` | TO BE CREATED | Day 7, appended Days 14, 21, 28 |
| `.github/workflows/ci.yml` | TO BE CREATED | Day 8 |
| `docs/normalization-parity.md` | TO BE CREATED | Day 10, only if the paths disagree |
| `app/android/app/src/test/resources/` | TO BE CREATED | Day 10 |
| `docs/handedness-calibration.md` | TO BE CREATED | Day 11 |
| `docs/feedback-thresholds.md` | TO BE CREATED | Day 12 |
| `docs/decisions/2026-10-03-session-logging-local-only.md` | TO BE CREATED | Day 13 |
| `docs/signer-leakage-check.md` | TO BE CREATED | Day 16 |
| `docs/gold-standard-provenance.md` | TO BE CREATED | Day 17 |
| `docs/defense-risks.md` | TO BE CREATED | Day 18 |
| `benchmarking/integration_test_matrix.md` | TO BE CREATED | Day 19 |
| `benchmarking/integration_test_results.md` | TO BE CREATED | Day 20 |
| `evaluation/consent-form-template.md` | TO BE CREATED | Day 22 |
| `evaluation/delete-path-verification.md` | TO BE CREATED | Day 22 |
| `evaluation/pre-test-instrument.md` | TO BE CREATED | Day 23 |
| `evaluation/post-test-instrument.md` | TO BE CREATED | Day 23 |
| `evaluation/scoring-rubric.md` | TO BE CREATED | Day 23 |
| `evaluation/score_sessions.py` | TO BE CREATED | Day 24 |
| `evaluation/synthetic_fixtures/` | TO BE CREATED | Day 24 |
| `evaluation/analyze_prepost.py` | TO BE CREATED | Day 25 |
| `evaluation/dummy_data/` | TO BE CREATED | Day 25 |
| `docs/thesis-drafts/objectives.md` | TO BE CREATED | Day 26 |
| `docs/thesis-drafts/scope-and-limitations.md` | TO BE CREATED | Day 27 |
| `docs/thesis-drafts/fsl105-provenance-note.md` | TO BE CREATED | Day 27 |
| `docs/e2e-latency-protocol.md` | TO BE CREATED | Day 29 |
| `docs/30-day-review.md` | TO BE CREATED | Day 30 |

## Referenced but not on this branch

| Path | State |
|---|---|
| `docs/hardening-plan.md` | PR #2, NOT ON MAIN AND NOT IN THIS WORKING TREE. Exists only as `remotes/origin/docs/hardening-plan`, dated 2026-09-15. Read it with `git show origin/docs/hardening-plan:docs/hardening-plan.md`, per Day 1's first action. Every reference to this path in this plan is a reference to that object, not to a local file |
| `.kiro/specs/22-holistic-v2/` | DOES NOT EXIST. Proposed by `docs/holistic-v2-kiro-prompt.md`, needs PM approval, out of 30-day scope |
| `.github/` | ABSENT at the time of writing, created Day 8 |

---

# 7. Hours Ledger

Capacity model: weekdays 3h, weekend days 4h. Buffer days carry no new scope. Day 30 is review only.

| Day | Date | Weekday | Capacity | Planned | Type |
|---|---|---|---|---|---|
| 1 | 2026-09-21 | Monday | 3 | 3 | delivery |
| 2 | 2026-09-22 | Tuesday | 3 | 3 | delivery |
| 3 | 2026-09-23 | Wednesday | 3 | 3 | delivery |
| 4 | 2026-09-24 | Thursday | 3 | 3 | delivery |
| 5 | 2026-09-25 | Friday | 3 | 3 | delivery |
| 6 | 2026-09-26 | Saturday | 4 | 4 | delivery |
| 7 | 2026-09-27 | Sunday | 4 | 4 | buffer |
| 8 | 2026-09-28 | Monday | 3 | 3 | delivery |
| 9 | 2026-09-29 | Tuesday | 3 | 3 | delivery |
| 10 | 2026-09-30 | Wednesday | 3 | 3 | delivery |
| 11 | 2026-10-01 | Thursday | 3 | 3 | delivery |
| 12 | 2026-10-02 | Friday | 3 | 3 | delivery |
| 13 | 2026-10-03 | Saturday | 4 | 4 | delivery |
| 14 | 2026-10-04 | Sunday | 4 | 4 | buffer |
| 15 | 2026-10-05 | Monday | 3 | 3 | delivery |
| 16 | 2026-10-06 | Tuesday | 3 | 3 | delivery |
| 17 | 2026-10-07 | Wednesday | 3 | 3 | delivery |
| 18 | 2026-10-08 | Thursday | 3 | 3 | delivery |
| 19 | 2026-10-09 | Friday | 3 | 3 | delivery |
| 20 | 2026-10-10 | Saturday | 4 | 4 | delivery |
| 21 | 2026-10-11 | Sunday | 4 | 4 | buffer |
| 22 | 2026-10-12 | Monday | 3 | 3 | delivery |
| 23 | 2026-10-13 | Tuesday | 3 | 3 | delivery |
| 24 | 2026-10-14 | Wednesday | 3 | 3 | delivery |
| 25 | 2026-10-15 | Thursday | 3 | 3 | delivery |
| 26 | 2026-10-16 | Friday | 3 | 3 | delivery |
| 27 | 2026-10-17 | Saturday | 4 | 4 | delivery |
| 28 | 2026-10-18 | Sunday | 4 | 4 | buffer |
| 29 | 2026-10-19 | Monday | 3 | 3 | delivery |
| 30 | 2026-10-20 | Tuesday | 3 | 3 | review |

## Weekly totals, arithmetic shown

| Week | Days | Weekday hours | Weekend hours | Total |
|---|---|---|---|---|
| 1 | 1 to 7 | 5 x 3 = 15 | 2 x 4 = 8 | **23** |
| 2 | 8 to 14 | 5 x 3 = 15 | 2 x 4 = 8 | **23** |
| 3 | 15 to 21 | 5 x 3 = 15 | 2 x 4 = 8 | **23** |
| 4 | 22 to 28 | 5 x 3 = 15 | 2 x 4 = 8 | **23** |
| tail | 29 to 30 | 2 x 3 = 6 | 0 | **6** |

Grand total: 23 + 23 + 23 + 23 + 6 = **98h**.

Cross-check by day type: 22 weekdays x 3h = 66h, 8 weekend days x 4h = 32h, 66 + 32 = **98h**. The two methods agree.

Calendar cross-check: 2026-09-21 to 2026-09-30 is 10 days, 2026-10-01 to 2026-10-20 is 20 days, 10 + 20 = **30 days**.

## Allocation

| Category | Hours | Arithmetic |
|---|---|---|
| Buffer, Days 7, 14, 21, 28 | 16 | 4 x 4h |
| Review, Day 30 | 3 | 1 x 3h |
| **Delivery, 25 days** | **79** | 98 − 16 − 3 |

Planned never exceeds capacity on any day: every row above has Planned equal to Capacity, and no row exceeds it.

Feasibility check against PR #2 estimates: `docs/hardening-plan.md` §2 sizes Stage A at about 0.5 day, B at 1 to 2, C at 2 to 3, E at 1 to 2, F at 3 to 5. Taking midpoints gives roughly 0.5 + 1.5 + 2.5 + 1.5 + 4 = 10 full days, which at 8h is about 80h against the 79h available. That is why Stages D, G, and H are cut rather than squeezed, and why the Day 30 target had to shrink.

---

# 8. Final Self-Check

| # | Check | Result | How checked |
|---|---|---|---|
| 1 | 30 daily entries present | PASS | Days 1 to 30 each have a heading block in section 4 |
| 2 | Dates consecutive from 2026-09-21 | PASS | Section 7 table runs 2026-09-21 to 2026-10-20 with no gap or repeat |
| 3 | Weekday names correct | PASS | 2026-09-21 is Monday as given. September has 30 days, so Day 10 is 2026-09-30 Wednesday and Day 11 is 2026-10-01 Thursday. All four buffer days land on Sunday, consistent with a Monday start and a 7-day cycle |
| 4 | Day 30 is 2026-10-20 | PASS | 10 days in September plus 20 in October equals 30 |
| 5 | Buffers on Days 7, 14, 21, 28 | PASS | Each is typed buffer in section 7 and each states what it absorbs |
| 6 | Buffer days carry no new scope | PASS | Each buffer prompt constrains against starting the next day's work |
| 7 | Day 30 is review only | PASS | Its objective is the review and gap report, and its constraints forbid new scope |
| 8 | Every day has all required fields in order | PASS | Each entry has the header line, Goal, Dependencies, Done when, Kiro prompt, Fallback if blocked |
| 9 | Every prompt has exactly the 7 required fields in order | PASS | 30 prompts, each with AGENT, PHASE, OBJECTIVE, INPUT, CONSTRAINTS, ACCEPTANCE CRITERIA, OUTPUT LOCATION on its own line in that order |
| 10 | Every prompt opens with the required first line | PASS | 30 of 30 begin with "Read AGENTS.md and docs/phase-gates.md first" |
| 11 | Every prompt closes with the required last line | PASS | 30 of 30 end with "Update docs/phase-gates.md status only for what was actually completed" |
| 12 | Every prompt uses `~~~` fences | PASS | 30 fenced blocks, all `~~~`, so backticks inside would render |
| 13 | AGENT names a PRD §7 persona | PASS | Personas used: Documentation (12), QA/Benchmarking (6), Mobile/Flutter (4), Research/Evaluation (3), Model Optimization (2), Feedback Algorithm (2), Model/Training (1), Data/Preprocessing (1), Security/Privacy (1). All nine appear in PRD §7 |
| 14 | Dependencies point backward only | PASS | Only Day 1 states None. Every other day cites strictly lower day numbers. No forward reference appears |
| 15 | No day consumes a same-day human response | PASS | Requests are made on Days 3, 4, 6, 17. The earliest day that would consume one is Day 8, five days after the Day 3 request, with Day 7 buffer between |
| 16 | No hardware-measurement day precedes the clean-clone and env days | PASS | Env is Day 5, clean clone is Day 6. The only hardware-adjacent days are 13 and 20 (emulator, not hardware) and 29 (design only, no measurement). No device measurement is scheduled at all |
| 17 | No day cites a number an earlier day has not produced | PASS | Day 15 produces the first new number. Days 12, 18 cite figures already in the repo (`extraction_log.csv`, the eval report, `benchmark_history.json`), which is existing evidence, not a future result. Day 18 still depends on Day 15 |
| 18 | Study tooling gated correctly | PASS | Days 22 to 25 use synthetic and dummy data only. The Week 4 header and Day 22 both state that recruitment and consent collection are gated on Days 10 and 11. H8 in section 5 repeats it |
| 19 | Human-dependent days produce an artifact plus a waiting state | PASS | Days 3, 4, 6, 17 each produce a request document and add a "waiting on X since Day N" line |
| 20 | Path manifest complete, each path once | PASS, re-checked after the 2026-09-23 amendments | Section 6 has three tables: exists, to be created, not on this branch. Every path named in a prompt INPUT or OUTPUT appears in exactly one. Six rows were added on 2026-09-23 (`LatencyBenchmarkTest.kt`, and the four train arrays under `../kumpas-data/sequences/`). One path, `benchmarking/accuracy_benchmark.py`, is now both a Day 15 INPUT and a Day 15 OUTPUT; it stays in the exists table with the modification noted, so the once-only rule holds |
| 21 | Hours ledger arithmetic shown and within capacity | PASS | Section 7 shows per-day, weekly, two independent grand-total methods that agree at 98h, and the 98 − 16 − 3 = 79 allocation. No day exceeds capacity |
| 22 | All 15 must-covers mapped to day numbers | PASS | The table in section 2 maps each to at least one day. Items 4 and 11 are mapped with their device-blocked portions named |
| 23 | Assumptions listed | PASS | Seven assumptions in section 2 |
| 24 | Could-not-verify list present | PASS, contents changed 2026-09-23 | Below this table. Old item 1 (augmentation counts) was **resolved** by the byte-count arithmetic now in the section 1a augmentation row and is struck, so the list renumbered from 10 entries to 9. The line-numbers entry, now item 5, was narrowed: `BenchmarkMode.kt` came off it because `MainActivity.kt:56` is directly confirmed |
| 25 | Only one file created | PASS | This plan writes `docs/30-day-plan.md` and nothing else. No gate was flipped, no spec task checkbox changed, `benchmark_history.json` untouched. Still true after the 2026-09-23 amendments: the verification pass ran read-only commands (`git rev-parse`, `stat`, `grep`, and `.npy` header reads) and changed no file but this one |
| 26 | No fabricated results, dates, devices, or citations | **FAIL as written 2026-09-21, PASS after correction 2026-09-23** | **This row flipped.** No measurement, expert name, validation date, participant, or device was ever asserted, and that part held. But the Repo state line named `kiro-sdlc-framework` as the checked-out branch when `git rev-parse --abbrev-ref HEAD` returns `docs/30-day-plan-2026-09-21`, and it described `docs/hardening-plan.md` as merely "not on `main`" when it is not in this working tree at all. Both were unverified citations about repo state, which is exactly what this row forbids. Corrected in the header, Assumptions 5 and 6, section 6, and Day 1 |
| 27 | Scope unchanged | PASS | 50 gestures, Android only, on-device inference, closed vocabulary preserved throughout. No day proposes a scope change |
| 28 | No em dashes | PASS | Written without em dashes throughout, per instruction. Re-checked across the 2026-09-23 amendments |
| 29 | No status downgrade asserts that existing code is absent | **PASS after correction 2026-09-23** | **This row is new and it caught a real defect.** The 2026-09-21 draft had Day 1 un-check spec 13 tasks 5 and 7 and had DoD item 2 require `grep -c '[x]'` to return 12. Both tasks are worded as create tasks and both artifacts exist: `app/android/app/src/androidTest/kotlin/com/kumpas/kumpas_app/benchmark/LatencyBenchmarkTest.kt`, and `BenchmarkMode.kt` wired at `MainActivity.kt:56`. Unchecking would have replaced an overstatement with an understatement. Day 1, DoD item 2, Conflict 5, and section 6 now annotate instead, and the count stays 14 |
| 30 | Every acceptance criterion is achievable by the tool the day actually calls | **PASS after correction 2026-09-23** | **This row is new and it caught a second defect.** DoD item 12 and Day 15 required the new accuracy entry to carry "a recorded environment", but `benchmarking/accuracy_benchmark.py` hardcodes `"device": "offline/python"` and `"condition": "n/a"` and writes no library versions, so no run of it could satisfy that criterion. Day 15 now budgets 45m to add a runtime `environment` block first, and lists the script as an OUTPUT. The other 19 DoD items were re-walked against the tool or file each one names; no further mismatch found |
| 31 | Every number in section 1a and 1b traceable to a command or file read | PASS, spot-checked 2026-09-23 | Re-verified directly: 1016 `ok` rows and all five landmark rates including 733 and 962; the four accuracies 0.8571 / 0.9507 / 0.9409 / 0.8325 with `best_val_accuracy` 1.0 on the winner and `local M1 (tensorflow 2.19.0)` on all four; `benchmark_history.json` at exactly 4 entries with `duration_s: 55` and `condition: "n/a"` on the retroactive pair; `VisionEngine.kt` importing `HandLandmarker` and `PoseLandmarker` with no Holistic and `N_FEATURES = 258`; `MainActivity.kt` lines 22 to 23 declaring and 54 to 55 constructing `SessionManager` and `DataExporter`; `.github/` absent; `evaluation/` holding only `.gitkeep`; `benchmarking/requirements.txt` absent; both venv inventories; `git ls-files` on the assets dir returning two files. Items that remain unverified are listed below, and the count of them dropped by one |

## Amendment log

**2026-09-23, verification pass against artifacts.** Five changes, each traceable to a command or file read:

1. **Repo state, header plus Assumptions 5 and 6.** Branch corrected from `kiro-sdlc-framework` to `docs/30-day-plan-2026-09-21` per `git rev-parse --abbrev-ref HEAD`. `docs/hardening-plan.md` reclassified from "not on `main`" to "not in this working tree", since `git branch -a` shows it only as `remotes/origin/docs/hardening-plan`.
2. **Section 1a augmentation row, UNVERIFIABLE to MATCHES.** Settled by `.npy` header arithmetic on file sizes from `stat -f %z`, shown in the row itself. No array load was needed and none was done.
3. **Conflict 5, Day 1, DoD item 2, section 6.** Stopped Day 1 from unchecking spec 13 tasks 5 and 7. Evidence: both files exist, and `BenchmarkMode` is constructed at `MainActivity.kt:56`. Annotation replaces unchecking; the checked count stays 14.
4. **Conflict 10, Day 15, DoD item 12.** Recorded that `accuracy_benchmark.py` hardcodes `device` and `condition` and logs no versions, so Day 15 must patch the script before running it. Also recorded the good news that `run_tflite_inference()` already slices 1662 to 258 via `np.r_[0:132, 1536:1662]`, so the shape will not block the run.
5. **Day 1 first action.** Added the `git show origin/docs/hardening-plan:docs/hardening-plan.md` step, because every PR #2 reference in this plan previously pointed at a path that does not resolve on this branch.

Self-check rows 26, 29, and 30 record the two defects this pass found. Rows 29, 30, and 31 are new. Rows 20, 24, 25, and 28 were re-checked and held.

## Could not verify

These are stated as unverified rather than assumed:

1. **Whether an offline FSL Expert record exists.** The repo has none. Commit `3205220` suggests a session occurred. Day 17 asks.
2. **Whether `docs/hardening-plan.md` has changed since 2026-09-15.** Read from `origin/docs/hardening-plan` as it stands now, and not present in this working tree. Day 1's first action fetches it and its fallback covers a change.
3. **Whether the Phase 7 UI matches the approved Figma.** Not checkable from the repo. Ledger verdict UNVERIFIABLE.
4. **Whether `docs/reproducibility.md` will actually get a stranger to a build.** Depends on H6, which needs repo owner rights.
5. **Exact line numbers in `VisionEngine.kt`, `CameraPreviewView.kt`, and `FeedbackEngine.kt`.** Cited behaviour comes from `docs/hardening-plan.md` and `docs/holistic-v2-diagnosis.md`, which name specific lines. Confirmed directly: the `VisionEngine.kt` imports and `N_FEATURES = 258`, the `MainActivity.kt` lines 22 to 23 and 54 to 55 wiring of `SessionManager` and `DataExporter`, and `BenchmarkMode` construction at `MainActivity.kt:56`. `BenchmarkMode.kt` is therefore off this list. Line numbers inside the other three files were not re-verified.
6. **Whether the Day 15 re-run will reproduce 0.9507.** The logged runs used TensorFlow 2.19.0 and `benchmarking/.venv` has 2.21.0. Note that the two existing accuracy entries agree with each other to four decimals, so the harness is internally reproducible within one environment; the open question is only across versions.
7. **`.kiro/steering/product.md` and `structure.md` contents.** Listed as existing. Only `tech.md` claims are asserted, via the two holistic-v2 documents that quote it.
8. **`.kiro/specs/16-evaluation-study-design/` contents.** Directory exists. Day 23's fallback covers it being thin.
9. **Whether an Android emulator is currently working.** Inferred from `benchmarking/phase4_emulator_report.md`. Days 13, 20, 22 have non-emulator fallbacks.

---

# 9. Day 31+ Deferred List

In dependency order. Each names what unblocks it.

1. **Execute the Phase 10 device run.** Unblocked by H4. Run `docs/e2e-latency-protocol.md` across optimal, low_light, and cluttered, producing at least 9 real entries in `benchmark_history.json` with `condition` never `"n/a"`. Per `docs/holistic-v2-risks.md` R2, measure the 258-dim baseline on that same device so a future comparison is fair.
2. **Fix the benchmark harness defects first.** PR #2 Stage D1 to D3: the `BenchmarkMode` API 29+ write path, counting camera frames instead of emitted events with a thread-safe structure, and a UI trigger. These must land before item 1 or the run produces nothing usable.
3. **Phase 9a latency and FPS closure.** Follows item 1. Then clear the `NEVER EXECUTED` notes that Day 1 added to spec 13 tasks 5 and 7, replacing each with the date and device of the run that finally executed it.
4. **Phase 9 closure.** Execute the device-blocked rows of `benchmarking/integration_test_matrix.md`, including the Phase 7 success-path feedback sheet check.
5. **Cold start fix.** PR #2 Stage D6: the three models load synchronously. Measure before and after.
6. **Resolve the FSL Expert record question.** H5, then H7 if needed, scoped to handshape and orientation only.
7. **Apply the handedness fix if Day 11 found a mismatch.** Deferred deliberately per `docs/holistic-v2-risks.md` R1, since a fix in the split-model path may be discarded by spec 22.
8. **Grow the test set.** PR #2 Stage G2, and a prerequisite for any further accuracy claim per R4. Stratified re-split or cross-validation so accuracy carries a confidence interval. This changes the baseline away from 95.07%.
9. **Diagnose and address the numerals.** PR #2 Stage G1 and G3, after item 8 so an improvement can be distinguished from noise. Currently a 1-of-4 to 3-of-4 change is two clips.
10. **PR #2 Stage E3 to E5.** `SessionLog` unbounded growth and full-file reads, substring-based channel routing, the `!!` assertions, and tests for what survives.
11. **Study execution.** H8, gated on item 7 and the Day 11 outcome. Pilot with 2 or 3 people first, per PR #2 Stage F5, before the full cohort.
12. **PR #2 Stage H, release readiness.** Real signing config with the keystore outside the repo, the zero-network-call privacy verification, camera permission denial handling, the UI honesty pass, and the camera `unbindAll()` fix.
13. **Resolve the two stack deviations.** The Holistic lock in `.kiro/steering/tech.md` versus the shipped PoseLandmarker plus HandLandmarker, and the Colab lock versus the `local M1` training environment in all four logged runs. Either amend steering with PM approval or record the deviations.
14. **Decide on spec 22, Holistic v2.** Needs PM approval per Rule #0. If approved it re-opens Phases 2, 3, 4, 5, and 6 per `docs/holistic-v2-kiro-prompt.md` WS7. Note the sequencing advice in `docs/holistic-v2-risks.md` §4: stopping after Wave 3 delivers the accuracy result without depending on hardware or expert availability.
15. **Phase 13.** Final polish, reproducibility notes, defense readiness. Not started, by design.

---

*End of plan. Written by the Documentation Agent. This file created nothing else and changed no gate status.*
