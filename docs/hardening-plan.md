# KUMPAS — Hardening & Verification Plan

**Status:** proposal for author review · **Date:** 2026-09-15
**Supersedes for execution purposes:** nothing. This plan sequences the remaining work in `docs/phase-gates.md` Phases 8–13 (= `.kiro/specs/` 13–20) and adds the repairs that must land before them.

---

## 0. The reframe: you are not in the build phase anymore

The standard vibe-coding sequence — *frontend → backend → database → auth → payments*, validating at each step — does not map onto this project, and following it now would be a mistake. Kumpas is an on-device ML app, and its risk-ordered sequence is:

> dataset → preprocessing → model → export → native pipeline → feedback math → UI → study → defense

**You have already been through that sequence once, and it worked.** Phases 0–7 are delivered: 95.07% test accuracy, a working Flutter shell, a Kotlin feedback engine with a real parity test, an approved Figma UI. That is genuinely further than most projects get.

So the highest-leverage thing left is not *building the next feature*. It is **verifying that what you claim is true, and making it reproducible by a stranger** — because this is a thesis, and the panel's job is to attack exactly the claims that are currently unverified.

That changes the priority order. What follows is ordered by *thesis risk*, not by feature appeal.

---

## 1. What is actually wrong (evidence, not vibes)

Ranked. Each item was verified against the repo, with the file that proves it.

### 🔴 P0 — Blocks reproducibility and defense credibility

**1.1 The repo does not build from a clean clone.**
`.gitignore:11-12` blocks `*.tflite` and `*.task`. `app/android/app/src/main/assets/` contains only `gold_standards.bin` and `label_map.json` — the three models the app loads (`pose_landmarker_lite.task`, `hand_landmarker.task`, `kumpas_50sign.tflite`) are absent. `app/fetch_assets.sh` downloads the two MediaPipe files but copies the classifier from `../../kumpas-data/`, a sibling directory that does not exist in a fresh clone.

*Consequence:* nobody — not your adviser, not a panelist, not future-you on a new laptop — can run this app. `LatencyBenchmarkTest` also cannot run, because it opens the missing `.tflite`.

**1.2 Phase gates claim PASS on evidence that self-labels as invalid.**
`benchmarking/benchmark_history.json` has 4 entries. Two are genuine accuracy runs. The latency and FPS entries are **hand-written retroactively**, carrying `note: "Retroactive from phase4_emulator_report.md; M1 proxy, not real device"`, with `n_inferences: null` and `cold_start_ms: null`. The FPS entry covers 55s, which fails `collect_fps.py`'s own ≥60s validation. Meanwhile `.kiro/specs/13-benchmarking-harness/tasks.md` marks **all 14 tasks `[x]`**, including on-device tasks 5 and 7 that were never executed on a device.

*Consequence:* your `<150ms` and `24–30 FPS` gates are, on paper, unmet. Worse, the p95 = 2ms figure measures **the TFLite interpreter in isolation** while `benchmarking/phase4_emulator_report.md` records MediaPipe landmarking at **35–63ms/frame** — the dominant cost is excluded from the only latency number you have. A panelist who reads both files will find this in five minutes.

**1.3 `training/requirements.txt` cannot reconstruct the environment.**
It is three lines (`mediapipe`, `numpy`, `opencv-python`). It contains **no `tensorflow`, no `keras`, no `scikit-learn`, no `matplotlib`** — yet `train_cnn_lstm.py`, `eval_report.py`, `export_tflite.py`, `benchmarking/accuracy_benchmark.py` (imports `tensorflow`, `sklearn.metrics`) and `plot_history.py` all require them. The actual TF environment exists only as prose in a docstring (`train_cnn_lstm.py:16-19`: `~/.kumpas-venvs/tf`, "tensorflow==2.19.0 / keras 3.10 / numpy 2.1"). The pinned versions in the file should also be re-verified against what you actually ran — I could not resolve them from this sandbox (network egress is blocked), so treat them as unconfirmed rather than correct.

*Consequence:* "reproducible" is a claim you cannot currently support. Reproducibility is an explicit Phase 13 deliverable.

### 🟠 P1 — Silent correctness risk to the thesis novelty

**1.4 Front-camera mirroring / handedness is uncalibrated.**
`VisionEngine.kt:146-147` assigns hand features by MediaPipe's `categoryName()` "Left"/"Right" into fixed offsets (left→132, right→195). `CameraPreviewView.kt` feeds the **raw front-camera bitmap** to MediaPipe without mirroring. `phase4_emulator_report.md` lists this as an open, uncalibrated issue.

*Consequence:* if the convention disagrees with the training data, left/right hand features are swapped. The classifier may absorb this, but `FeedbackEngine` emits **per-hand** corrective prompts ("your left hand…"), so a swap makes the thesis's actual contribution confidently wrong. This is the single most dangerous open bug in the repo.

**1.5 `VisionEngine.normalize()` has no parity test.**
It is a hand-port of `training/preprocessing/build_sequences.py` (mid-hip centering, torso scaling, `<1e-4` guard). `FeedbackEngineParityTest.kt` proves the *feedback* port matches Python — a genuinely good test — but nothing does this for the *normalization* port, even though every prediction depends on it.

**1.6 The 95.07% headline hides the numerals.**
Per-class data in `benchmark_history.json`: **FIVE F1 = 0.333** (recall 0.25), FOUR = 0.600, THREE = 0.667, TWO = 0.800. Test set is n=203 across 50 classes (~4 samples/class), and one logged run reports val accuracy 1.0 — both signs the test set is too small to support a tight accuracy claim.

*Consequence:* "≥90%" passes on aggregate while a whole semantic family is near-unusable. Expect this exact question at defense.

### 🟡 P2 — Accumulated AI-generated debt

**1.7 ~707 lines of dead code.** I verified this directly: a repo-wide grep for `SessionManager`, `SessionDatabase`, `DataExporter` across all `.kt` and `.dart` files returns **zero references outside the three files themselves**. A full SQLite schema (participants/sessions/attempts/assessments + 3 indexes), a JSONL→SQLite migration, and an export path are all written and completely unreachable. Production uses the 33-line `SessionLog` instead. `.kiro/specs/21-session-logging/tasks.md` confirms: tasks 1–3 `[x]`, **tasks 4–16 `[ ]`**.

*This is the textbook vibe-coding failure mode* — a subsystem generated in one pass, never wired, never validated, now sitting in the repo looking finished. It is also why "validate at every step" is rule #1 below.

**1.8 `BenchmarkMode` writes to a path that fails on modern Android.** `BenchmarkMode.kt:72` writes to `Environment.getExternalStoragePublicDirectory(DIRECTORY_DOWNLOADS)`; `AndroidManifest.xml:3-4` grants `WRITE_EXTERNAL_STORAGE` only with `maxSdkVersion="28"`. On API 29+ this write fails. It also counts *emitted events* (post-stride, ~7.5/s) rather than camera frames, contradicting the FPS gate's semantics — and no UI can trigger it, so `collect_fps.py` has nothing to pull.

**1.9 No CI, no Python tests.** There is no `.github/` directory at all. Zero Python tests exist. PR #1 merged with no automated verification. Total test inventory: one 12-line Dart smoke test, one good Kotlin parity test, one instrumented test that cannot run.

**1.10 Cosmetic UI presented as real.** Voice→sign mode (labeled unavailable — fine), dictionary demo playback (a play button with no video asset anywhere), profile identity (hardcoded `'KL'` / `'KUMPAS Learner'`), notification/sound switches (plain `bool`s, no persistence, no behavior), language selector (a static `Container`). Dark mode works but does not survive a relaunch — there is no `shared_preferences` in `pubspec.yaml`.

**1.11 Release builds sign with the debug key.** Explicit `// TODO` at `app/android/app/build.gradle.kts:37`.

**1.12 Feedback prompt copy is hardcoded English inside Kotlin** (`FeedbackEngine.kt`), while the entire UI is Filipino. The `attempt_failed` string in `VisionEngine.kt:214` has the same problem. Thresholds (0.30/0.25/0.22/0.25) and divisors (0.8/0.30/90.0) are undocumented magic numbers — every one of them is a "why that value?" question at defense.

---

## 2. The plan — discrete steps, validated

Each step is small enough to hold in one context window and ends in a **binary, checkable** gate. Do not start step N+1 until step N's gate is green. Steps within a stage marked *parallel-safe* touch disjoint files.

### Stage A — Tell the truth (½ day, no code)

The cheapest and highest-leverage stage. Do it first, because every later decision depends on knowing the real state.

| # | Task | Gate |
|---|------|------|
| A1 | Un-check the spec tasks that were never executed: `13-benchmarking-harness/tasks.md` tasks 5, 7 (and any other on-device task). Add a one-line reason each. | `grep -c '\[x\]'` drops; each un-checked task names why |
| A2 | Rewrite the Phase 4/5 rows in `docs/phase-gates.md` from ✅ to ⚠️ **CONDITIONAL — emulator only, real-device pending**. | No row claims a device measurement that `benchmark_history.json` cannot back |
| A3 | Delete the two retroactive latency/FPS entries from `benchmark_history.json`, or move them to a `provenance: "retroactive-estimate"` block excluded from plots. | `plot_history.py` output contains only measured data |
| A4 | Add a "Known Limitations" section to `README.md`: emulator-only perf, provisional gold standards, numerals weakness, n=203 test set. | Section exists and matches §1 of this doc |

> **Why first:** your adviser and panel will forgive an unmeasured gate. They will not forgive a gate marked PASS with a file in the same repo saying the evidence is invalid. Fixing the paperwork also stops *you* from planning against numbers you don't have.

### Stage B — Make it reproducible (1–2 days)

| # | Task | Gate |
|---|------|------|
| B1 | Rewrite `training/requirements.txt` as two real files: `requirements-mediapipe.txt` and `requirements-tf.txt`, generated by `pip freeze` from the environments you actually used. Verify each installs clean in a fresh venv. | `pip install -r` succeeds from scratch, both files |
| B2 | Fix `app/fetch_assets.sh` so it works with **no** out-of-repo dependency: download the two MediaPipe `.task` files, and fetch `kumpas_50sign.tflite` from a pinned release artifact (GitHub Release on this repo) with a **SHA-256 checksum** verified after download. | Fresh `git clone` + `./fetch_assets.sh` + `flutter build apk --debug` succeeds |
| B3 | Publish the model + gold standards as a versioned GitHub Release (`model-v1.0`, the `no_face` 258-feature run), with the release notes recording seed `20260705`, test accuracy, and the commit that trained it. | Release exists; B2's script pulls from it; checksum matches |
| B4 | Add `.github/workflows/ci.yml`: `flutter analyze` + `flutter test`, `./gradlew testDebugUnitTest` (runs the parity test), and `python -m compileall training benchmarking`. | CI green on a PR; parity test visibly runs in the log |
| B5 | Write `docs/reproducibility.md`: clone → env → assets → train → export → build → benchmark, as literal commands. | A person with only this file and a fresh machine reaches a running APK |

> **Gate B (hard stop):** a stranger with the repo URL and this doc gets a running app and a passing test suite. Do not proceed until true — every later measurement is worthless if it isn't reproducible.

### Stage C — Prove the math is right (2–3 days) — *the thesis-critical stage*

| # | Task | Gate |
|---|------|------|
| C1 | **Resolve handedness/mirroring (§1.4).** Write a fixture test: take one known sequence from `../kumpas-data/`, run the Kotlin path and the Python path on the same input, assert the left/right feature blocks (offsets 132 and 195) land identically. Fix `CameraPreviewView` mirroring if they disagree. | Test asserts block-level equality and passes; result documented either way |
| C2 | **Normalization parity test (§1.5).** Mirror `FeedbackEngineParityTest`'s pattern: export N fixtures from `build_sequences.py`, assert `VisionEngine.normalize()` matches within tolerance. | New Kotlin unit test, ≥5 fixtures, runs in CI |
| C3 | Extract `VisionEngine.normalize()` into its own testable class so C2 doesn't need a camera. Read the class count from `label_map.json` instead of the hardcoded `Array(50)` (`VisionEngine.kt:62-66`). | Test runs headless; no `50` literal remains |
| C4 | Move all feedback prompt copy out of `FeedbackEngine.kt` into a string resource, translated to Filipino. Same for `attempt_failed` (`VisionEngine.kt:214`). | No user-facing English literal in either Kotlin file |
| C5 | Document every threshold and divisor in `docs/feedback-thresholds.md`: value, what it means, how it was chosen, sensitivity. Where a value is arbitrary, **say so**. | Every constant in `FeedbackEngine.kt:41-43` and each divisor has an entry |

> **Gate C:** both hand-ported math paths (normalization *and* feedback) are covered by parity tests in CI, and handedness is settled with evidence. This is the stage that protects your actual contribution — do not skip it because it produces no visible feature.

### Stage D — Measure for real (2–3 days, needs a physical device)

Blocked on Gates B and C. Measuring before C means measuring a possibly-wrong pipeline.

| # | Task | Gate |
|---|------|------|
| D1 | Fix `BenchmarkMode` storage (`BenchmarkMode.kt:72`): write to `context.getExternalFilesDir(null)` (app-scoped, no permission on API 29+), and drop the now-dead `WRITE_EXTERNAL_STORAGE` entry. Update `collect_fps.py`'s `adb pull` path to match. | File lands on an API 33+ device; `collect_fps.py` pulls it |
| D2 | Make `BenchmarkMode` count **camera frames** (hook `CameraPreviewView`'s analyzer, before the `tick()` stride gate), not emitted events. Guard `frameTimestamps` with a lock or use a concurrent structure — it is currently written from the analysis thread and read from the platform thread. | FPS reading ≈ CameraX's configured rate, not ~7.5 |
| D3 | Add a hidden debug entry point (long-press the Profile header) that calls `startBenchmark`/`stopBenchmark`. | Benchmark is triggerable on a real device without a debugger |
| D4 | Add **end-to-end** latency instrumentation: camera frame in → feedback ready out, covering MediaPipe + TFLite. This, not interpreter-only p95, is the number the `<150ms` gate is about. | `LatencyBenchmarkTest` (or a new instrumented test) reports e2e p50/p95 |
| D5 | Run accuracy/latency/FPS on **real mid-range hardware** (Helio G / Snapdragon 6, 4GB) across all three `environment_protocol.md` conditions: `optimal`, `low_light`, `cluttered`. | 9 real entries in `benchmark_history.json`, `condition` never `"n/a"` |
| D6 | Fix cold start: the three models load synchronously on the calling thread (`VisionEngine.kt:83-107`). Move to a background thread with a loading state in the UI. | Measured cold start recorded before *and* after |
| D7 | Rewrite `docs/phase-gates.md` Phase 4/5/10 rows from the real numbers. If e2e latency exceeds 150ms, **report it and adjust the claim** — do not re-hide it. | Every perf claim traces to a non-retroactive entry |

> **Gate D:** every performance number in the thesis comes from a real device under a named condition, and includes MediaPipe. This is the stage that converts your weakest chapter into your strongest.

### Stage E — Decide the session-logging question (1–2 days)

Do not "finish" `SessionManager` by default. Decide first:

- **`.kiro/specs/00-project-init/gap-reconciliation-report.md` §3.3 resolved backend as OUT of scope.**
- The evaluation study (Stage F) *does* need structured local data: participant IDs, sessions, assessments, export.

| # | Task | Gate |
|---|------|------|
| E1 | **Decide, and write it down:** (a) wire up `SessionManager`/`SessionDatabase`/`DataExporter` (spec 21 tasks 4–16), or (b) delete all three and extend `SessionLog` to cover only what Stage F needs. Judge by Stage F's data requirements, nothing else. | A decision record in `docs/`, dated, with reasoning |
| E2 | Execute the decision. If (a): add lifecycle overrides in `MainActivity` (`onPause`/`onResume` — the 60s auto-close timer currently has no callers), add the missing method-channel names, run the JSONL→SQLite migration once with a backup. If (b): delete ~707 lines and note it in the spec. | No unreferenced class remains in `kumpas_app/`; `grep` for the three names returns only live call sites, or nothing |
| E3 | Either way: fix `SessionLog`'s unbounded growth + full-file read on every `getHistory()` (called on Home, Learn, *and* Profile load). Cap or index it. | History load does not read the whole file |
| E4 | Replace the fragile `contains("attempt_result")` substring routing in `MainActivity.kt:49` with a parsed `type` field. Remove the `!!` assertions on `visionEngine`/`sessionLog`/`benchmarkMode`. | Routing is field-based; no `!!` in the channel handler |
| E5 | Add unit tests for whatever survives (spec 21 tasks 14–15). | Tests in CI |

> **Gate E:** zero unreferenced production classes. Whatever logging exists is wired, tested, and bounded.

### Stage F — Evaluation study tooling (3–5 days)

`evaluation/` currently contains one empty `.gitkeep`. Everything is spec markdown.

| # | Task | Gate |
|---|------|------|
| F1 | From `.kiro/specs/16-evaluation-study-design/`, finalize: participant count (PRD says 40), assignment, pre/post instrument, consent form under RA 10173. | Protocol doc + consent form reviewed by adviser |
| F2 | Build the in-app assessment screen (spec 21 task 11) — the missing `lib/ui/assessment_screen.dart`. | Pre-test and post-test both completable on device |
| F3 | Build export + clear-data UI (spec 21 tasks 12–13) with a retention statement. RA 10173 requires the delete path to actually work. | Export produces a parseable file; clear leaves no residue |
| F4 | Write `evaluation/` analysis scripts: descriptives, paired pre/post test, effect size. Validate on **synthetic** data first. | Scripts run end-to-end on synthetic input with known answers |
| F5 | Pilot with 2–3 people before the real run. | Pilot completes; instrument problems fixed before the real cohort |

> **Gate F:** you could run the study tomorrow and the analysis would work. Piloting is non-negotiable — a broken instrument discovered at participant 40 costs you the study.

### Stage G — Model improvement (optional, 2–4 days)

Only after Stage C. If handedness was wrong, retrain anyway and these numbers change.

| # | Task | Gate |
|---|------|------|
| G1 | Diagnose the numerals confusion (FIVE F1 0.333, FOUR 0.600, THREE 0.667). Inspect the confusion matrix rows and the actual clips. | Written diagnosis: data scarcity vs. genuine visual ambiguity vs. preprocessing artifact |
| G2 | Grow the test set. ~4 samples/class cannot support a tight accuracy claim, and one run reporting val accuracy 1.0 is a red flag. Re-split with stratification, or cross-validate. | Reported accuracy has a confidence interval |
| G3 | Only if G1 says it's fixable: targeted augmentation or an architecture change, logged as a new `experiments_log.json` run. | New entry, seeded; accuracy reported with CI; no regression elsewhere |
| G4 | Generate the missing per-run eval artifacts — only the `no_face` run has `_eval.md`/`_confusion.png`/`_per_class.csv`. | All 4 logged runs have comparable reports |

### Stage H — Release readiness (1–2 days)

| # | Task | Gate |
|---|------|------|
| H1 | Real signing config (`build.gradle.kts:37`), keystore **out** of the repo, documented in `docs/reproducibility.md`. | `flutter build apk --release` produces a non-debug-signed APK |
| H2 | Execute spec 14 privacy verification: prove zero network calls during inference. Capture traffic on-device and attach the evidence. | Report in `docs/` with actual capture output |
| H3 | Handle the ignored camera-permission denial (`MainActivity.kt:30-34` never overrides `onRequestPermissionsResult` — a denial silently yields a dead camera). Show a real message. | Denying permission produces a visible explanation |
| H4 | UI honesty pass (§1.10): either implement or clearly mark the dictionary play button, profile identity, notification/sound switches, language selector. Add `shared_preferences` so dark mode and settings survive relaunch. | No control that looks functional and does nothing |
| H5 | `CameraPreviewView.dispose()` should `unbindAll()` — releasing the camera currently relies on `AppShell` rebuilding tabs. | Camera light goes off when leaving the tab |

---

## 3. How to actually vibe-code this

Adapted to *this* repo, not generic advice.

### 3.1 One task per prompt, and a gate before the next

Each numbered row above is one prompt. If a prompt won't fit in a short paragraph, it's two tasks. The dead `SessionManager` subsystem is exactly what a too-big prompt produces: plausible, complete-looking, unreachable code. Nothing caught it because nothing between "generate" and "commit" asked *is this called?*

### 3.2 Your PRD already exists — reference it, don't rewrite it

You have `docs/PRD.md`, `docs/phase-gates.md`, `.kiro/steering/`, and 21 spec folders. This puts you ahead of the article's advice. The failure mode here is the opposite one: **specs drifting from reality** (tasks marked `[x]` for work never done). So:

- Start prompts with the spec path: *"Per `.kiro/specs/21-session-logging/design.md` §3, wire…"*
- Update the spec in the **same commit** as the code. A spec that lies is worse than no spec, because you'll plan against it.
- `AGENTS.md` Rule #0 (no code before the gate) is a good rule. It was bypassed for the session-logging subsystem. Re-enforce it.

### 3.3 Validation for an ML app means four different things

"Does it work?" is not enough here. Per step, check:

1. **Does it run?** Build, launch, click the flow.
2. **Is it called?** `grep` for the new class/method from outside its own file. This one check would have caught §1.7.
3. **Does the math match the reference?** Parity tests against Python. You did this for `FeedbackEngine` and it is the best code in the repo — replicate that pattern (Stage C).
4. **Is the measurement real?** A number in a JSON file is not a measurement. It needs a device, a condition, and a timestamp from an actual run.

### 3.4 Route models by task type

| Task type | Model | Examples from this plan |
|---|---|---|
| Architecture, ambiguous debugging, judgment | Opus | C1 handedness, E1 keep-or-delete, G1 numerals diagnosis |
| Well-specified implementation | Sonnet | B4 CI, D1–D3, F2 assessment screen, H4 UI pass |
| Mechanical, verifiable edits | Haiku | A1–A4 doc corrections, C4 string extraction, F-boilerplate |

Stage A is almost entirely Haiku work. Stage C is where premium reasoning earns its cost — a wrong handedness decision invalidates the whole feedback chapter.

### 3.5 Commit and PR discipline

You have one merged PR and no CI. Going forward: one stage per branch, one task per commit, CI green before merge. This gives you a reviewable history for the methodology chapter — "here is when and why each decision was made" — which is worth real marks and costs you nothing extra.

### 3.6 Keep a decision log

Add `docs/decisions/` with one dated file per non-obvious choice: why `no_face`/258 features, why medoid gold standards, why threshold 0.22 for handshape, keep-or-delete on `SessionManager`. Every one of these is a defense question. Answering from a dated record beats reconstructing from memory in month nine.

---

## 4. Suggested sequencing

```
Week 1   Stage A (½ day)  →  Stage B  ───────────────► Gate B: stranger can build
Week 2   Stage C  ──────────────────────────────────► Gate C: math proven  ★ critical
Week 3   Stage D (needs real device)  ──────────────► Gate D: real numbers
Week 4   Stage E  ─────────┐
                            ├─ parallel-safe (disjoint files)
Week 4   Stage G (optional)─┘
Week 5-6 Stage F  ─────────────────────────────────► Gate F: study ready
Week 7   Stage H  ─────────────────────────────────► Gate H: defensible build
```

**If you only do three things:** Stage A (tell the truth), Stage B (make it reproducible), Stage C (prove the math). Those three convert Kumpas from "a demo that works on the author's laptop" into "a thesis artifact someone else can verify" — which is the actual bar.

**Do not** start Stage F or G before Gate C. A study run against a pipeline with swapped hands produces data you have to throw away.

---

## 5. The one-line version

The code is in better shape than the evidence. Spend the next two weeks making the evidence match the code, not adding features — then measure on real hardware and run the study.
