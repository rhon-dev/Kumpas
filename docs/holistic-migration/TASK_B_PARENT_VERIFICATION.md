# Task B parent verification and first built-in preview

## Software execution

Parent independently ran the actual current suites:
- New migration package: **61 tests passed**, exit0 (18.102seconds).
- Neighboring original training suite: **51 tests passed**, exit0 (8.903seconds); existing runtime/deprecation warnings are retained.
- All six accepted Task A source hashes remain unchanged; original tracked diff and diff whitespace checks pass.

Logs and exact hashes: `~/KumpasBuilds/holistic-migration-data/evidence/task-b-parent-9e87d9dd61ec4433bf5f8663dc9687fa/verification.json`.

The full five-source-file Task B review package/manifest is retained at `~/KumpasBuilds/holistic-migration-data/evidence/task-b-review-35995bb4181049d98ac1dcec6240f713/`. Independent specification and quality review is pending; tests/live execution do not replace it.

## Actual camera/GUI execution

Parent executed the real module CLI with duration60seconds and an explicitly requested external operational report. It compiled the current owned Swift helper and used that helper's built-in-only AVFoundation capture. No default-index, iPhone or Continuity fallback was used.

Exact evidence directory:
`~/KumpasBuilds/holistic-migration-data/task-b-live-parent-a3143ff84049433ba446d6f8f61ed0e7/`

- Python process handle: `proc_78818a81b9fc`; PID39079; actual exit0.
- Operational report run UUID: `ea4ff993-16be-44f7-915b-b3e5cb60728d`; terminal `deadline`; elapsed60.003486083995085seconds.
- Native handshake: `AVCaptureDeviceTypeBuiltInWideAngleCamera`, Continuity=false, device identity SHA-256 `a67c141c9d25ffdda3950d21b7c9aaf74de980a581b26fc86a2397024bde8a15`.
- Actual source1280×720 BGRA; explicitly processed640×360 RGB.
- Native frames received1,649; processed1,279; latest-slot overwrites369. One last pending observation need not be processed at deadline. These are distinct counters, not camera/display FPS.
- Measured processed rate21.315428210447788FPS. This was a **zero-detection session**, not representative human tracking throughput.
- **Pose, face, left hand, right hand and usable-pose observations were all zero.** Do not infer the reason or classify this as performed-sign failure.
- Cleanup errors0. The specifically owned native child exited with SIGTERM(-15) during normal parent deadline cleanup; no matching owned camera child remained afterward.
- Launcher stderr retains MediaPipe feedback-manager warnings. No raw frames, video or landmark arrays were written by this preview.

## Window evidence without saving camera pixels

During the actual session, CoreGraphics reported the same owned Python PID39079 with an on-screen640×392 window at(0,30), window ID1900. Window title was unavailable through the OS metadata API. This verifies an on-screen owned window, not human observation of its overlay. No screenshot or focus change was performed.

## Bounded conclusion

The actual native built-in camera, binary framing, latest-only transport, detector/packer, GUI loop and bounded cleanup executed without a reported error. **Human tracking, anatomical handedness, gesture recognition and live acceptance remain unverified.** The report correctly retains `live_acceptance:false` and `mode:tracking_only`.

Next: finish independent software review, then obtain owner readiness for a bounded human tracking check or an explicit deferral while independent offline work continues. No classifier was loaded or trained; no phone work occurred.
