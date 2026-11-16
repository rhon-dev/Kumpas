# Task B — visible built-in MacBook Holistic preview

AGENT: Host capture / Data integration implementer.
PHASE: Mac tracking preparation before expensive full-dataset extraction. This is not classifier recognition or owner-performed acceptance.
OBJECTIVE: A bounded visible preview using the accepted Task A detector/packer and an explicitly bound built-in MacBook camera, never iPhone/Continuity/default-index capture.
PREREQUISITE: Parent must accept Task A's specification and quality review before dispatching this task. This brief does not grant that acceptance.

## Inputs and ownership

Read `AGENTS.md`, the root `HOLISTIC_MIGRATION_PLAN.md`, `docs/holistic-migration/FEATURES.md`, and the actual Task A detector/features interfaces. Preserve every existing file and all Task A source bytes.

Create only:
- `training/holistic_migration/camera.swift`
- `training/holistic_migration/camera.py`
- `training/holistic_migration/webcam.py`
- `training/holistic_migration/tests/test_camera.py`
- `training/holistic_migration/tests/test_webcam.py`
- Incremental `docs/holistic-migration/task-b-report.md`

No dataset extraction/training, app/phone operations, live frame/video/landmark persistence, installed-package edits, dependencies, commits or pushes. The parent owns actual live preview launch and acceptance. Native compilation with the existing Apple SDK is allowed; outputs/cache must be outside Git in owned data/scratch paths, not the original cloud folders.

## Required design

1. Use a new native AVFoundation helper. Discover only `.builtInWideAngleCamera` video devices, reject `isContinuityCamera`, require exactly one eligible device, and build `AVCaptureDeviceInput` from that exact discovered object. Do not use `AVCaptureDevice.default` or OpenCV integer camera selection. No fallback. Model selection and anatomy are separate claims.
2. Metadata-only discovery must not open a capture session. Expose a pure descriptor-selection function or native self-test path so invalid types/Continuity/zero/multiple devices can be tested without camera access.
3. The helper streams owned BGRA frames through a binary pipe, not disk. Publish one JSON handshake containing actual buffer dimensions/format, structured device type, Continuity=false and SHA-256 native identity. Define bounded framing (e.g. big-endian timestamp + payload length + tightly row-packed BGRA); account for CVPixelBuffer row padding. Frame dimensions come from the actual buffer, not a requested preset. Use a fixed requested 1280×720 preset only if supported, and report actual dimensions. Reconfiguration/malformed packets must fail closed.
4. Python must compile the exact owned Swift source with `/usr/bin/swiftc` into an explicit external build directory, retain source/binary digest receipt, and recheck that binding before launch. Never trust an arbitrary executable selected only by filename. Use subprocess argument arrays, not a shell. Set module cache/TMPDIR under the runtime scratch directory. Do not reuse another worktree's helper as if current.
5. Validate the handshake before detector work; require exact built-in type, false Continuity, nonempty identity digest, supported actual dimensions and BGRA size. Validate framing, finite/strict timestamps, exact lengths and EOF. Add bounded startup/frame deadlines and child-exit diagnostics. Release only the specifically owned child on exit/error; use terminate then bounded kill if needed. Preserve useful stderr separately from frame stdout without unbounded memory growth.
6. A latest-only in-memory capture queue must avoid accumulating stale frames. Convert actual BGRA to RGB and explicitly resize to640×360 for this preview; report both source and processing dimensions. Do not silently relabel resized frames as sensor output. No raw frames/videos/landmark arrays may be written.
7. `python -m training.holistic_migration.webcam --model <official.task> --build-dir <external-dir> --duration 60` opens a visible OpenCV window. Validate finite positive bounded duration and paths before compilation, model/camera metadata access or capture. The actual Tasks HolisticDetector and pack_frame are imported, not copied. There is no sign-classifier loading in this stage.
8. Draw observed pose and hand connections; face outline/points are optional but their real count/status must be shown. Mirror display only; keep overlay text readable. Label SDK left/right until independently validated. Show elapsed time, processed FPS, detector/packing time, component presence and candidate feature masks. Keys: q/Escape quit; m toggles display mirroring. Window close, error and deadline must release detector, native child and GUI resources.
9. Allow an explicitly requested operational JSON report path, refusing overwrite; store only run/source/detector/native-binding identities, timing/count summaries and terminal disposition. No recognized strings, raw frames or landmark arrays. A running heartbeat or zero-human session is not passed live acceptance. Keep no report on default path unless requested. Do not hide failed attempts or claim target FPS without measuring it.

## Tests and execution

Use strict vertical TDD. Run each behavioral RED then GREEN using the existing combined Python environment and `-E -B`; append exact commands/results to the report after each cohesive slice. Unit tests cannot open a real camera, create GUI windows or load MediaPipe by default. Test selection/handshake rejection, invalid duration before dependencies, short/partial/oversized packets, timestamp regression, EOF, ownership/cleanup on failures, latest-only queue, BGRA/RGB/no-input-mirror behavior, actual dimensions, overlay missing components and quit/timeout paths. Tests must exercise production code, not copied parsers.

Compile/exercise native pure self-tests without camera access and record their actual output. Run the full new package test suite and the neighboring original training suite. Parent separately launches the visible built-in preview and checks real frames, bounded exit and owner readiness. No anatomical, gesture-accuracy, offline/live-recognition or phone claims follow from this implementation.

## Previously measured context (not this task's verification)

Native discovery found one built-in FaceTime HD Camera, Continuity=false; actual exact-name FFmpeg capture produced1280×720 data successfully, explicitly resized to640×360. The single observed frame had no detected person and established no human tracking. The official bundle is at `~/KumpasBuilds/holistic-migration-data/holistic_landmarker.task`; SHA-256 `e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8`. MediaPipe1.2.0 uses public ctypes Tasks APIs; do not install the old empty-packet private decoder workaround.

Return a short status, modified files, actual test/compile results, report path and concerns. Do not launch a live preview from the child.
