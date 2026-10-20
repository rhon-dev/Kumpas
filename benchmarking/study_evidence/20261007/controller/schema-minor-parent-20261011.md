# Schema minor follow-up and isolated ownership verification

Observed: 2026-10-11T23:25:27.360381+08:00

Genuine regression-first RED: float schema_version2.0 passed report validation and FPS/latency reader-to-history qualification; interpreter diagnostics lacked rejection. Preserved schema-minor-red-1.log and schema-minor-red-sink-1.log, both exit1. Minimal fix: exact integer report validation and strict integer schema primitive in raw-reader/sink sanitization; malformed types omitted with rejection while numeric measurements remain.

Full benchmarking discovery: **43 tests passed**, exit0 (schema-minor-green-full-1.log). Valid integer2 FPS/latency passes; bool/float/string/null/wrong-version cases fail. Sink regressions exercise all3 ingestion paths, preserving1800 analyzer count,100ms trace and trusted device names.

Fresh forced offline JVM: **137 tests,0 failures/errors/skips**; includes39 SessionManager,9 MainActivityBoundary,5 CameraViewOwnership and3 ResourceCleanup (isolated-ownership-jvm-20261011.log). All82 protected originals unchanged. Existing3 APK hashes match prior manifest; no fresh APK build/installation claimed. Source delta among package4 reviewed files: .superpowers/sdd/progress.md, benchmarking/collect_fps.py, benchmarking/study_readiness.md, benchmarking/test_collectors.py, docs/phase-gates.md.

Independent review deleg_36a911af pending. ADB reported no connected device. Isolated emulator approval request timed out; no boot/install/default-store operation performed.

Managed deletion/ownership has renewed host/JVM evidence only; installed isolated instrumentation pending. Full uninterrupted CameraX/channel/UI/persistence/export/delete/reopen open. Physical-phone, expert/model/human, consent and participant-study gates remain blocked/unapproved.
