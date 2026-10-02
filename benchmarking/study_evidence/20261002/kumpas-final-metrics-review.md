# Independent metrics/spec-quality review — 2026-10-02

Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`
Reviewed HEAD: `693c9852f4c476659e6f359c6e1b5055b3713b83`, with the current uncommitted working-tree repairs. Line references below refer to the actual source files read, not to line numbers in the scratch diff package. Concurrent parent work may subsequently change them.

## Verdicts

- **Spec compliance: PARTIAL; measurement/phone-handoff acceptance is not yet satisfied.** Core native clock, counter, duration, storage and host-boundary repairs substantially implement approved spec §3. However, the supported Flutter trigger discards the start-time run identity, does not initiate a run if the camera never produces a full-window event, and does not record failed/cancelled trial outcomes. Retained figures still present excluded historical estimates. The three-condition definitions/checklist exist, but the concrete named-device/per-sign handoff record is not prepared in the inspected artifacts. The physical gate remains **BLOCKED**, not passed and not a measured failure.
- **Code quality: CHANGES REQUIRED before calling the measurement/reporting path ready.** Native metric separation and host validation are materially better than the original implementation. The consequential defects are integration/evidence-presentation defects rather than incorrect basic duration/rate mathematics. Additional active-run report isolation, trace-window isolation and history-writer concurrency issues remain.
- **Evidence strength: read-only source/artifact review only.** No builds, tests, collector invocations, installation, device access, benchmark-history writes, or participant collection were performed. Reproduction steps below are static follow-ups for the parent; they were deliberately not executed. Previous resume-report test/build outcomes are attributed reports, not independently reproduced outcomes.

## Findings

### M1 — P1 / high: supported Flutter benchmark flow loses the fresh run ID required by the host

**Files/lines:** `app/lib/feedback_engine/kumpas_channel.dart:50–52`; `app/lib/ui/practice_screen.dart:164–177,116–123`; native return at `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt:116`; required host parameter at `benchmarking/collect_fps.py:232–235` and `benchmarking/collect_latency.py:92,98–100`.

Native `startBenchmark` returns the unique UUID, but the Dart wrapper remains `Future<void>`, and `_startBenchmark` retains/displays neither UUID nor any run handle. The completion branch also ignores the report object (which contains the ID). Thus the documented Settings → benchmark → retain returned run ID → collect same run workflow cannot actually provide its required `$RUN_ID` through the supported UI/API wrapper. This is a contract defect, not absence of a phone.

**Static reproduction:** follow the Settings benchmark action and inspect the start/completion snackbars: neither exposes the UUID. A caller awaiting the public Dart wrapper receives no run identity to retain. Reading `latest.json` afterwards is an alternative investigative workaround, but deriving the expected identity from the very file being validated removes the independent freshness check promised by `benchmarking/README.md:30–38`.

**Required closure:** return a validated nonempty `Future<String>` from the wrapper, retain the ID at successful start, expose/copy it without changing the approved layout, and correlate completion/get/stop requests with that ID. Extend the existing widget contract test to assert retention/correlation, not merely one method invocation (`app/test/practice_flow_test.dart:162–172`).

### M2 — P1 / high: excluded estimates remain in actual figures; schema-v2/failed reports are rendered as zeros

**Files/lines:** `benchmarking/plot_history.py:40–49,96–98,104–108,136–138,144–148`; `benchmarking/README.md:97–107`; artifacts `benchmarking/plots/latency_over_iterations.png` and `benchmarking/plots/fps_over_iterations.png` (binary images, no line numbers); source estimates `benchmarking/benchmark_history.json:2–38`.

Direct visual inspection confirms that the retained latency figure is titled “Inference Latency Across Runs,” plots the Android emulator against the 150ms target, and contains no retroactive-estimate/interpreter-only warning. The retained FPS figure is titled “Sustained FPS Across Runs,” plots the emulator above 24 FPS, and contains no 55-second/retroactive-estimate warning. The history correctly marks these estimates `provenance:retroactive-estimate` and `gate_pass:null`, and the current loader excludes them. But when the filtered latency/FPS list is empty, plotting returns without overwriting or marking the existing image. The stale apparently successful figures therefore survive a normal regeneration.

There is a second concrete schema defect in the same presentation path: new latency values live under `assessment.event_latency_ms`, and new FPS rates under `results.fps.analyzer`, whereas the plotter reads only old top-level result fields and defaults absent values to **0**. It also filters neither `measurement_type` nor rejection state. A schema-v2 latency run or rejected collection with `results:{}` becomes an apparent zero-latency result; legacy interpreter diagnostics are mixed into the same latency series. README lines 75–78 warn not to mix these, but the advertised plotting command still does so.

**Static reproduction:** use the current history with its excluded estimates: the early-return branches leave the existing PNGs untouched. Supply a new collector-shaped row to the renderer: the old-field lookups select zero instead of the native summary/rate. No rendering was run in this review.

**Required closure:** preserve originals for provenance but quarantine/label stale figures, emit an explicit no-measured-data artifact when empty, and use boundary/schema-specific readers with missing values remaining missing. Retain rejected trials with an unmistakable rejected status rather than either converting them to zeros or silently promoting them to measured success.

### M3 — P2 / medium: a camera that never produces a full-window event never starts the UI benchmark

**Files/lines:** `app/lib/ui/practice_screen.dart:57–65,164–184`; `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt:213–239`; underlying native deadline `BenchmarkMode.kt:52–57`.

The explicit UI action only calls `startBenchmark` after a `prediction` or `no_signer` event. Both are emitted only after the native ring buffer fills. A zero-frame or perpetually warming-up camera leaves the action pending indefinitely; it creates no run ID, deadline or failed/stalled report. `_benchmarkStarted` is also set before the call succeeds, so a failed/busy start cannot retry on later camera events. The native timer correctly terminates zero-frame runs **once started**; the missing behavior is in the real trigger path.

**Static reproduction:** open the benchmark screen with no subsequent camera events (or only `warmup`/`camera_error`), or make `startBenchmark` fail once. The guard never initiates/retries the timed observation. This is distinct from zero observed throughput in a successfully started native run.

**Required closure:** start an explicit timed observation independent of successful warmup, or impose a bounded camera-start phase that retains a failed-start outcome. Set success state only after native start succeeds and expose retry.

### M4 — P2 / medium: failed/cancelled trials are absent from benchmark outcomes

**Files/lines:** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt:94–99,259–265`; `MainActivity.kt:67–73,140–178`; `CameraPreviewView.kt:80–83,96–99`; `app/lib/ui/practice_screen.dart:154–155,187–204`; protocol `benchmarking/environment_protocol.md:67`.

A no-signer attempt emits `attempt_failed`, but `MainActivity` only counts that message as an event and does not record a coded failure. Cancellation and Flutter timeout similarly do not record an outcome. Benchmark failure counters are wired only to camera exceptions/bind errors and persistence failure. Consequently a run with failed/cancelled captures can report zero failures and has no trial-outcome record; successful-result-only traces do not repair the missing denominator. This undermines the approved phone checklist and interpretation of latency sample selection.

**Static reproduction:** during an active run, complete a no-signer attempt and cancel another. Follow these branches: no corresponding `recordFailure` or cancellation-outcome hook exists. The synthetic counter test invokes `recordFailure("no_signer")` directly (`BenchmarkModeTest.kt:27`), which does not demonstrate actual production wiring.

**Required closure:** preserve coded failed/cancelled/timeout outcomes separately from successful latency samples, without raw landmarks/video or participant IDs. Do not redefine an intentional cancellation as a detector crash or fabricate latency for it.

### M5 — P2 / medium: active-run report lookup can expose a prior successful run

**Files/lines:** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/BenchmarkMode.kt:51–56,154–155`; `MainActivity.kt:117–119`.

Starting run B clears in-memory `results` but leaves persisted run A's `latest.json` intact. While B is active, `latestResults()` therefore returns A. `getBenchmarkReport` exposes that object without current-run identity/status. This is an actual stale-success exposure, although the host rejects it when given B's independently retained expected ID. M1 means the normal UI currently lacks exactly that independent ID.

**Static reproduction:** finish A, start B, then call `getBenchmarkReport` before B finishes: the return path falls back to A's persisted report. If someone obtains the expected ID from that fallback instead of from B's start, the host freshness comparison is no longer an independent safeguard.

**Required closure:** distinguish active/current/historical states, require the requested run identity, and do not label a disk fallback as the active run. Preserve A rather than deleting history.

### M6 — P2 / medium: traces are not constrained to the same observation window as counters

**Files/lines:** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/BenchmarkMode.kt:77–98`; `PipelineMetrics.kt:14–23,25–36`; `MainActivity.kt:75–81,170–175`; host checks `benchmarking/collect_fps.py:138–140,153–160`.

Counters enforce the half-open fixed window even if the main-looper deadline fires late. `recordTrace`, however, only checks `isActive`, injects the current run ID regardless of when the attempt started, and records/overwrites a trace without validating its first/event/ACK timestamps against that window. An attempt begun before benchmark start is relabelled into the new run; a delayed completion/ACK after the logical deadline can be stored before the Handler gets to `finish`. Host validation correctly rejects these traces, but this turns an otherwise valid full-window FPS observation into a rejected report. It is producer-side run contamination, not a demonstrated host false pass.

**Static reproduction:** begin an attempt before starting the benchmark, or delay the main looper across the deadline so delivery/ACK runs before the finish Runnable. Follow `recordTrace` versus the timestamp guards used by `PipelineMetrics`. Also note that host trace comparisons allow equality at `end_ns` while counters exclude that endpoint.

**Required closure:** bind attempt/run identities and retain out-of-window outcomes explicitly, without overwriting a valid in-window event sample with an out-of-window ACK. Do not silently truncate a slow attempt to create a passing latency.

### M7 — P2 / medium, spec/documentation gap: three-condition handoff is generic and run metadata does not bind the condition

**Files/lines:** `benchmarking/environment_protocol.md:9–47,54–68`; `BenchmarkMode.kt:47–50,110–126`; `benchmarking/collect_fps.py:207–224,230–236,251–260`; required handoff `docs/superpowers/specs/2026-10-01-study-readiness-design.md:35`; planned evidence file `docs/superpowers/plans/2026-10-01-study-readiness.md:55–60`.

The protocol correctly defines optimal (>300 lux/plain), low light (<100 lux/plain), cluttered (>300 lux/complex), front camera, 60–90cm distance, ≥60s, target-class ≥4GB phone, hashes and thermal-state checklist. What is absent is a concrete named-device × condition handoff table and per-sign trial/confusion/outcome recording form covering all 50 signs, FIVE and multiple consenting signers. `benchmarking/study_readiness.md` was not present at review time. The approved spec itself describes the missing deliverable; it is not evidence that it has been prepared.

Native metadata includes real model SHA-256 and app version/debuggable state, but not APK SHA-256/revision, actual lens/camera ID, RAM/chip class, thermal state, or condition/lux/background/distance. Host condition is supplied only when collecting. The identical run can consequently be logged under all three condition strings without any mismatch being detected. A positive collector row therefore is **not** a completed target-phone/environment matrix cell unless accompanied by a run-ID-linked setup/device record. The camera also silently falls back to the back camera (`CameraPreviewView.kt:90–95`), so front-camera use cannot be inferred from report metadata.

**Required closure:** prepare a blank run-linked matrix/outcome form, clearly BLOCKED, with named candidate device specifications to verify locally when available. Bind the observed condition/setup and actual camera/build identity to the run or to an explicit immutable sidecar. Require manual evidence review for target hardware rather than equating “non-emulator” with “Helio G/Snapdragon 6, ≥4GB.” Do not invent devices, trials, lux readings or approvals.

### M8 — P2 / medium: concurrent FPS/latency collection can lose a retained history row

**Files/lines:** `benchmarking/log_utils.py:48–60`; collectors `benchmarking/collect_fps.py:261` and `benchmarking/collect_latency.py:103`.

The existing history utility atomically replaces the file, but does not lock its read-modify-write sequence. Two independent collectors can load the same old history, each append its own row, and replace one another's result. Atomic replacement prevents partial JSON; it does not prevent lost updates. This utility is pre-existing, not introduced by the repair, but both repaired collectors use it and failed/diagnostic row retention is part of the reviewed contract.

**Static reproduction:** interleave two processes after both execute `load_history()` and before either replaces the target. The last replace keeps only its addition. The provided real-append regression is sequential and does not exercise this interleaving (`benchmarking/test_collectors.py:116–132`).

**Required closure:** serialize append via an interprocess lock or explicitly require/enforce sequential collectors. Preserve existing rows and record append failure honestly.

## Privacy/evidence observations within this review's limited scope

- Native `BenchmarkMode.recordTrace` uses a primitive timing/attempt-ID allowlist (`BenchmarkMode.kt:80–86`). Actual `MainActivity` calls pass `PipelineTrace.toJson`, not the whole recognition/persistence event. No normal-path raw video, landmarks, prediction payload or participant UUID leak into native benchmark reports was found. Attempt UUIDs are run-event identifiers, not evidence of anonymization of arbitrary future metadata.
- **Defensive concern, not demonstrated participant leakage:** host `read_report`/`log_collection` preserve the entire received object and original raw text even when rejected (`collect_fps.py:215–227,257–258`). Unexpected `raw_video`/participant fields in a malformed/future report would therefore be copied into host history. The module docstring's “No images/landmarks are stored” is guaranteed by the current native producer, not by the host sink. Keep this limitation visible to the separate privacy reviewer; do not test it with real participant data.
- Partial persistence is distinguishable only in memory: immutable run JSON is written before the AtomicFile latest update (`BenchmarkMode.kt:131–147`). If only latest replacement fails, the already-written per-run file does not receive the later `storage_error`/false local gate annotation, while in-memory results do. This needs a stage-specific retention/readback design or an explicit limitation; no storage fault was induced here.
- App benchmarking still follows ordinary practice persistence (`MainActivity.kt:153–159`). It is not a disposable/synthetic-session mode. No human/participant exercise is authorized by this review.

## Measurement boundary and implementation strengths

1. **Latency origin:** `CameraPreviewView.kt:55` samples native `elapsedRealtimeNanos` at analyzer callback entry, before RGBA conversion/rotation. `VisionEngine.kt:195–209,242–281` propagates that timestamp and times interpreter execution separately. Sensor `ImageInfo.timestamp` is used only as MediaPipe's VIDEO input time; it is not subtracted from the native benchmark clock.
2. **Collection interval:** first/final selected analyzer times are stored separately. The whole multi-frame attempt is not misreported as last-frame processing latency.
3. **Feedback/persistence:** `MainActivity.kt:155–159` persists before the main-thread delivery stamp at line 172; therefore the final-analyzer-to-event measurement includes native extraction, classifier, feedback, persistence and main-thread queue wait. The stamp is taken just before report/JSON encoding and EventSink submission, not after Flutter rendering. It is a dispatch-start boundary, not sensor-to-display time. ACK captures a later native callback after Flutter's post-frame callback and is correctly described as an upper bound, not photons.
4. **Counter separation:** analyzer/stride-selected/completed-processed/emitted-vision-event counters are independently hooked at `CameraPreviewView.kt:60,62,77` and `MainActivity.kt:177`. `event_count` includes warmup/progress/prediction/failure messages, not only terminal successful attempts; it must not be interpreted as the attempt-success denominator. The current direct FPS analyzer recording samples its own native clock slightly after the callback-entry trace stamp; this does not mix clock epochs.
5. **Window calculation:** `PipelineMetrics.kt:14–36` uses half-open native windows, full-duration means and all one-second bins including zeros. Early finish is incomplete. `BenchmarkMode.kt:57,101–128` closes using a timer rather than waiting for a future camera event. None of this proves sensor/display FPS or full-detector throughput.
6. **Storage/validation:** unique app-internal run files and atomic latest replacement preserve normal finished/failed/stalled runs. Host explicit serial/package/run-ID checks, model/build shapes, physical-emulator checks, strict duplicate/nonfinite parsing, ordered boundaries and derived-value checks are real safeguards in source. Missing ACK remains missing; interpreter-only diagnostics always have `gate_pass:false`. Latency and sustained analyzer gates are independent; passing one does not imply the other or accuracy.
7. **Targets:** ≥90% accuracy, <150ms named latency and sustained 24–30 analyzer FPS remain stated. No 80%/20FPS relaxation was found in these current reviewed collector/protocol files. Rates above 30 are not artificially capped. The approved spec requests the literal field name `analyzer_to_feedback_ms`; current code uses the more explicit `final_analyzer_to_event_ms`. The boundary is documented, but the schema naming deviation should be acknowledged rather than claiming literal field-for-field compliance.

## Prepared versus unavailable phone evidence

| Condition | Existing protocol | Required run evidence | Current status |
|---|---|---|---|
| optimal | >300 lux, plain background | verified named target phone, actual front camera, run-linked setup/build/model/thermal metadata, ≥60s bins, latency traces and trial outcomes | BLOCKED; no authorized/available phone evidence |
| low_light | <100 lux, same plain background/framing | same evidence and hardware identity; measured lux | BLOCKED; no authorized/available phone evidence |
| cluttered | >300 lux, complex background, same framing | same evidence and hardware identity; people-free setup image if retained | BLOCKED; no authorized/available phone evidence |

Across these rows: observed trials for all 50 signs, multiple consenting signers, FIVE/confusion coverage and failed/cancelled trials remain human-gated future evidence. No sample count or success is inferred from templates. The existing emulator camera sample with no latency traces remains diagnostic only, as directed. Historical interpreter/emulator proxies and synthetic tests cannot close physical latency/FPS, accuracy, linguistic validity, or participant-readiness gates.

## Scope and files

Read AGENTS, full PRD, approved design/plan, phase gates, scratch review/resume package, actual native/Dart producer hooks, collector/history/plotter source, relevant regression-test source and environment docs. Inspected the two retained performance PNGs directly. Read-only git HEAD/status established the review baseline. No network research was needed or performed.

**Created:** only `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-final-metrics-review.md` (this requested report). **Modified:** no repository, model/reference, training/evaluation, history or figure file. No tests/builds were run; parent owns execution and closure. This report identifies defects/gaps and does not claim any were repaired.
