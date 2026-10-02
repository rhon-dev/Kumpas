# Final review remediation brief

## Scope and authority

Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`, current HEAD `693c9852f4c476659e6f359c6e1b5055b3713b83`. The owner approved the full focused privacy/build/flow/measurement repair and subsequently authorized final integrated verification. Preserve unrelated working changes. No commits, physical-phone claims, participant collection, raw participant video/landmarks, or default installed participant-store access. Preserve historical model/reference bytes, training/evaluation work, feedback math, XP, and approved layout. Use existing stack/dependencies.

Read AGENTS.md, PRD, approved design and plan, then both full review reports:
- `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-final-flow-review.md`
- `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-final-metrics-review.md`

This is ONE cohesive remediation wave for all final-review findings, not separate independent implementers. Verify each finding against current source before editing. Strict vertical RED/GREEN cycles; actual regression failure before behavior changes. Fix critical/important findings, then rerun covering suites. Parent does independent builds/instrumentation and final acceptance later.

## Parent adjudication and required repairs

1. **F1 persistence false success:** verified insert results discarded in SessionManager. Cover session/attempt/assessment failures, including silent SQLite RAISE(IGNORE), without caching a failed session or acknowledging unsaved records. MainActivity must translate failures correctly. Inspect migration/participant consumers to avoid creating a new false-success path when hardening shared insertion APIs. Existing managed deletion and rollback semantics must remain intact.
2. **F2/M3 bounded benchmark startup:** the full-window warmup gate currently makes a zero-frame run invisible. Preserve the intent of normal camera warmup without allowing indefinite startup. Either separate a bounded warmup from a guaranteed timed run or retain an explicit bounded startup-failure run. An explicit request with no events must terminate with honest retained failure/zero evidence; failed/busy start must be retryable. Do not merely remove the no-frame assertion. No new screens or broad visual changes.
3. **F3/M1 run identity:** return a validated nonempty benchmark UUID through Dart, retain/expose/copy it with existing UI surfaces, correlate completion/stop/report requests, and do not derive expected ID from the report being validated. Collectors keep strict expected-run-ID checks.
4. **F4 stale camera errors:** reproduce ordering at the production scheduling boundary, not only helper state. Carry a camera/request generation or equivalent identity through conversion/errors and re-check posted delivery, so a stale error cannot cancel a replacement capture; legitimate current camera errors still reach UI.
5. **F5 bounded attempt startup:** deadline covers the pending channel Future as well as collection. Preserve request generation and ID-specific cancellation of a late returned identity without cancelling a newer attempt. Test never-completing and late-response starts.
6. **M2 plot evidence:** inspect actual PNGs/source. Preserve original excluded figures as clearly quarantined historical artifacts; replace current published latency/FPS outputs with explicit no-measured-data results when history contains only excluded estimates. Support schema-v2 and rejected rows without missing-data-to-zero conversion or mixing interpreter diagnostics with camera latency. Do not alter historical benchmark rows or accuracy results/figures. Exercise real empty regeneration and malformed/schema-v2/rejected inputs in isolated fixtures.
7. **M4 outcomes:** record coded no-signer/failure/cancellation/timeout outcomes separately from successful latency samples. Wire actual production hooks; intentional cancellation is not a detector crash. Do not fabricate latency for unsuccessful trials or include participant identities/payloads.
8. **M5 active/current report isolation:** never return prior run A as current B while B is active. Preserve historical A and require or explicitly bind report/stop requests to their intended run. Cover previous success plus new active/no-frame run.
9. **M6 run/trace window:** enforce the same half-open native window as counters. Exclude or explicitly retain out-of-window outcomes separately; do not overwrite a valid in-window trace with an out-of-window ACK, relabel pre-run attempts, or silently truncate slow latency. Host and producer endpoint rules must agree.
10. **M7 setup/handoff:** bind condition/setup/camera/build/device identity to the run or immutable validated sidecar, rather than accepting arbitrary collection-time condition labels. Require manual verification of target chip/RAM/front camera and setup. Prepare a blank all-50-sign × condition run/outcome/confusion form and named candidate-device table, prominently BLOCKED; no invented availability, measured lux, attempts, signers or approvals. Parent will provide manufacturer-sourced candidate specs if needed. The actual chosen camera (including back-camera fallback) must be explicit. Optional fields remain absent/unverified, never guessed.
11. **M8 history concurrency:** serialize read-modify-write appends with an interprocess lock (or enforce sequential collection). Use deterministic concurrent subprocess fixtures and preserve legacy row schema; never exercise against repository history. Atomic replacement alone is insufficient.
12. **F6 naming:** add compatible `analyzer_to_feedback_ms` alias for the existing explicit final-analyzer-to-event boundary, or record an explicit non-claim of literal schema compliance. Prefer a tested alias without breaking readers.
13. **F7 helper lifetime:** add tested safe teardown closure of SessionManager-owned helper and update activity lifecycle if narrowly safe. Do not let teardown persistence exceptions prevent remaining engine/benchmark cleanup.
14. **Additional metrics privacy/storage observations:** assess rejected-report raw payload retention and immutable/latest write failure divergence. Harden the host sink against untrusted participant/raw-image fields using synthetic fixtures; preserve safe rejected evidence and reasons. Ensure partial report storage cannot expose an apparently successful file inconsistent with the returned error, or document and enforce stage-specific fail-closed readback. Do not fabricate a filesystem-fault result.

## File ownership

You may modify only focused relevant files and their tests:
- SessionManager.kt, SessionDatabase.kt; corresponding tests.
- MainActivity.kt, VisionEngine.kt, CameraPreviewView.kt, AttemptBoundary/PipelineTrace helpers if necessary; production-boundary/regression JVM or isolated instrumentation tests.
- BenchmarkMode.kt, PipelineMetrics.kt and tests.
- app/lib/feedback_engine/kumpas_channel.dart, app/lib/ui/practice_screen.dart (profile only for a narrow existing-settings handoff), existing/new focused Dart tests.
- benchmarking/collect_fps.py, collect_latency.py, plot_history.py, log_utils.py, tests, README/environment_protocol and blank handoff templates; latency/FPS figure quarantine/replacement only.
- Append remediation evidence to your scratch report; parent owns `benchmarking/study_readiness.md`, `docs/phase-gates.md`, final evidence directory and consolidated acceptance.

No bulk formatting, arbitrary file deletion, new gamification, model/geometry/math changes, installations, default-store clears, or Git commits. Capture start-time snapshots for owned files so unrelated changes are not overwritten. Parent will not edit your owned production/test files concurrently.

## Candidate-device source status (planning only)

Full manufacturer pages were blocked with Access Denied. A manufacturer search-index excerpt was retrieved for Xiaomi's global Redmi Note 11 specs: Snapdragon 680; 4GB/64GB, 4GB/128GB and 6GB/128GB variants. Source: `https://www.mi.com/global/product/redmi-note-11/specs`. Record this provenance as an indexed manufacturer excerpt, not a successful direct page fetch.

Redmi Note 11 is a named planning candidate only, not acquired/available hardware, a purchasing recommendation, or evidence of app compatibility/performance. The earlier proposed Redmi 10 qualification remains UNVERIFIED; omit it from qualified targets or leave all qualification fields pending without asserting its SoC/RAM.

Region/device variants must be verified on actual loaned hardware; names alone do not establish SoC/RAM/Android version. No price/availability/security-support claim. Any generated per-sign blank matrix must load actual dense IDs/labels from app label_map.json, programmatically verify 50 unique classes, and bind candidate/condition cells without fabricated observations.

## Verification and report

Use `/opt/homebrew/bin/python3.11` for host tests. Flutter from app/. Gradle must acquire existing scratch `kumpas-gradle.lock` via the inspected `kumpas-privacy-gradle.py` wrapper. Covering tests first per repair; final full native/Flutter/Python test suites after changes. Distinguish Gradle UP-TO-DATE from execution; force the native test task with `--rerun` when necessary. Parse XML counts; do not infer counts from tasks. Do not install APKs or run Android instrumentation; parent owns that isolated verification.

Write full report to `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-final-remediation-report.md`, with each F/M finding mapped to disposition, exact source/tests, real RED/GREEN commands/results, API/schema contracts and remaining issues. If scope/ambiguity prevents any required repair, report BLOCKED or DONE_WITH_CONCERNS rather than silently skipping. Return short summary plus absolute report path and test counts only after actual execution.
