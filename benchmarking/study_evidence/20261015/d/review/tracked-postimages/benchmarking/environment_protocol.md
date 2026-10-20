# Benchmarking Environment Conditions Protocol

This document defines the three environmental conditions under which
on-device benchmarks (latency, FPS) are run. Consistent reproduction
is critical for thesis validity.

## Condition Definitions

### 1. Optimal (`optimal`)

| Parameter | Requirement |
|-----------|-------------|
| Lighting | Well-lit room, >300 lux at signer's hands |
| Background | Plain, single-color wall (white/gray/cream) |
| Signer position | Centered in frame, arms-length from camera |
| Measurement | Lux meter reading or phone lux-sensor app screenshot |

**How to reproduce:** Standard indoor overhead fluorescent/LED lighting,
signer facing the light source, plain wall behind. Verify ≥300 lux with
a meter at hand level.

### 2. Low Light (`low_light`)

| Parameter | Requirement |
|-----------|-------------|
| Lighting | Dim, <100 lux at signer's hands |
| Background | Same as optimal (plain wall) |
| Signer position | Same framing as optimal |
| Measurement | Lux meter confirming <100 lux |

**How to reproduce:** Single desk lamp angled away from signer (indirect
bounce light), or evening natural light with no overhead. Turn off
overhead fixtures. Background stays plain so that only illumination
changes as a variable.

### 3. Cluttered Background (`cluttered`)

| Parameter | Requirement |
|-----------|-------------|
| Lighting | Same as optimal (>300 lux) |
| Background | Complex visual scene: bookshelf, other people, varied objects |
| Signer position | Same framing as optimal |
| Measurement | Photo of the setup for reproducibility |

**How to reproduce:** Signer stands in front of a bookshelf or in a room
with multiple objects and/or other people visible. Lighting remains
optimal so that only background complexity changes as a variable.

## Pre-Run Checklist

Before each benchmark run, the tester fills this checklist and records
the condition label in the benchmark log entry:

- [ ] Condition label selected: `optimal` / `low_light` / `cluttered`
- [ ] Lux reading at signer's hand level: ______ lux
- [ ] Background description: _______________
- [ ] Device positioned on tripod / stable surface: yes / no
- [ ] Camera distance to signer: ~_____ cm (target: 60–90 cm)
- [ ] Setup photo taken and saved to `benchmarking/setup_photos/`
- [ ] Duration planned: ≥60 seconds continuous; note returned unique run ID
- [ ] Explicit ADB serial and package `com.kumpas.kumpas_app` recorded
- [ ] Physical phone with supported fixed chip option (Helio G80 / Snapdragon 680, ≥4GB RAM); emulator/unsupported chips are diagnostic only; verify actual hardware manually
- [ ] Front camera selected; maintain 60–90cm distance for the complete run
- [ ] APK/model SHA-256, app build/version, device/chip/RAM and thermal state recorded
- [ ] Analyzer/selected/processed/event counters and all second bins retained, including stalls
- [ ] Native latency attempts include first/final analyzer, native result and event boundaries
- [ ] Failure/cancellation trials recorded separately; no fabricated attempts/counts
- [ ] No participant video/landmarks stored in benchmark reports or committed; setup photos exclude people

## Labeling Convention

Use the exact string for the `condition` field in `benchmark_history.json`:
- `"optimal"` — well-lit, plain background
- `"low_light"` — dim (<100 lux), plain background
- `"cluttered"` — well-lit, complex background
- `"n/a"` — offline benchmarks (accuracy) where condition is irrelevant

## Notes

- Only one variable should change per condition (light OR background, not both).
- "Low light + cluttered" is NOT a defined condition — if needed for the thesis,
  add a new condition string and document it here before running.
- Record ambient temperature if device thermal throttling is a concern.

## Provisioning the next run (device-owner handoff; not executed here)

The native producer reads internal `files/benchmarks/next_setup.json` once at
`startBenchmark`, before its monotonic timed window. Later edits do not alter the
run snapshot. Missing, malformed, oversized (>8192 bytes), duplicate-key or
unverified setup remains collectable as diagnostic/non-gating evidence.

Blank diagnostic template only (NOT observed data; replace every blank with an
independently verified value before qualification):

```json
{
  "setup_id": "",
  "condition": "",
  "lux": null,
  "background": "",
  "distance_cm": null,
  "device_fingerprint": "",
  "chip": "",
  "ram_gb": null,
  "apk_sha256": "",
  "revision": "",
  "thermal_state": "",
  "setup_verified": false,
  "device_verified": false,
  "front_camera_verified": false
}
```

Schema: setup_id is a freshly generated lowercase UUID (exact 8-4-4-4-12
lowercase hex; provision using a UUID generator, not a free-form operator alias).
Supplied malformed identities are rejected/dropped, never repaired into acceptance.
Other strings are 1–256 characters with no newline and the fixed vocabularies below.
condition is optimal/low_light/cluttered. Finite numeric lux is <100 for low_light,
>300 otherwise; background is plain except complex for cluttered; distance_cm is
60–90; ram_gb is 4–64. Current fixed chip options are exactly `Snapdragon 680` and
`Helio G80`, the already documented candidate/example options, not an arbitrary
family/suffix regex. Other hardware stays diagnostic; adding a supported option
requires an explicit producer/consumer vocabulary revision with provenance.
These labels do not verify the actual SoC: OEM/local hardware verification remains
manual and must precede the device_verified flag. device_fingerprint must match Android
Build.FINGERPRINT. apk_sha256 is lowercase 64-hex; revision is lowercase
40/64-hex. thermal_state is nominal/fair/serious/critical. All three verification
flags must be true only after checks; a manual boolean does not measure hardware,
lighting, distance or camera binding. Nulls in this blank template deliberately
produce invalid-field diagnostics; they are not numeric measurements.

Verification sources: lux meter at hand level, measured tape distance,
background/setup record excluding people, OEM/spec or device hardware/RAM
verification, current device build fingerprint, researcher build revision,
installed APK streaming SHA-256 and contemporaneous thermal observation. The
producer hashes ApplicationInfo.sourceDir before timing and compares the declared
digest; unavailable/unreadable or split APK installs are diagnostic (split identity
is unsupported). The host independently verifies installed APK, fingerprint and
condition; producer acceptance does not replace those checks.

Only on an explicitly authorized study-free device and debuggable build, the
owner may provision a researcher-prepared local file with the following template
commands. Set SERIAL explicitly; do not run on an installed participant store:

```bash
PACKAGE=com.kumpas.kumpas_app
adb -s "$SERIAL" shell run-as "$PACKAGE" mkdir -p files/benchmarks
adb -s "$SERIAL" shell "run-as $PACKAGE sh -c 'cat > files/benchmarks/next_setup.json.new'" < /path/to/verified-setup.json
adb -s "$SERIAL" shell run-as "$PACKAGE" mv files/benchmarks/next_setup.json.new files/benchmarks/next_setup.json
adb -s "$SERIAL" shell run-as "$PACKAGE" cat files/benchmarks/next_setup.json
```

Read back and compare the exact target to the prepared file before starting;
never print participant payloads, raw landmarks or private diagnostics. Keep all
setup strings strictly within the schema and avoid names/free-form notes. Denied
run-as is a provisioning failure, not permission to clear app data or switch to
an old report. Do not mutate retained RUN_ID.json or latest.json manually.

The actual CameraX selector/lens/bound camera identity are captured at start.
The producer uses Camera2CameraInfo.cameraId from the bound camera and retains
only `camera2-sha256:` plus SHA256 of its exact UTF-8 bytes (64 lowercase hex),
not a free-form cleartext camera label. Arbitrary legitimate OEM Camera2 strings
are supported without normalizing/discarding their identity; changing the API ID
changes the representation and invalidates qualification. The host accepts only
this bounded structured representation, with trusted app producer provenance;
it does not independently enumerate/cryptographically attest camera hardware.
No unsupported host camera command is promised. Selector/lens/bind changes also
invalidate qualification: default_front/front/bound, unchanged for the window,
is required. front_camera_verified alone is insufficient. Retain returned run ID,
setup_errors and storage_state, including partial/failed runs. Retry by correcting
next_setup.json then starting a new run; never relabel an old snapshot. A 30-second
control timeout is not a >=60-second completed observation. Analyzer/event/ACK
boundaries remain software boundaries, not sensor exposure/physical display.

### Start-control ownership and retention

At native start, `RUN_ID.control.json` is atomically published/read back with
`{"schema_version":1,"run_id":"RETURNED_UUID","status":"unconfirmed"}`.
Current owners explicitly call `confirmBenchmarkStart(runId)` only after their
valid current-generation response; the producer accepts confirmation only while
that same run is active and before30s elapsed. Confirmation writes/readbacks
status confirmed. This is a control deadline, separate from observation duration.
A late identity, closed run or stale owner never upgrades; no immutable measured
report is rewritten. Thus an unreturned start response or hung late stop cannot
qualify the retained full-window diagnostics. Missing control publication or
confirmation is non-gating. Both host camera collectors require this independent
scoped companion plus report control_status confirmed. Direct-native diagnostic
runs have no implied owner confirmation. The screen commits ownership and keeps
its copyable ID immediately when a valid current start UUID is received, before
awaiting confirmation. Confirmation pending/timeout/error means an owned run with
uncertain producer confirmation, NOT failed start or Retry. An explicit false
reply means owned but unconfirmed/diagnostic; only a true reply permits the screen
to claim confirmed/running. Completion is correlated even while confirmation is
pending, and late replies cannot erase completion or change replacement B.
Navigation/disposal after receipt uses the same policy as any owned run: it does
not revoke ownership or issue a late-start stop. Errors are consumed; the native
run ID/report/scoped disposition remain available for USB recovery. Navigation
before original receipt keeps the original unowned/late-scoped-stop policy.
The original start watchdog and separate confirmation/late-stop awaits each stay
bounded30s. A producer-confirmed report is not rejected solely for a lost
confirmation reply to an already receipt-committed owner. Conversely sent RPCs,
uncertain UI state, unconfirmed/missing/faulted companions never establish a pass.
Collectors require exact integer schema1 (not bool/float), exactly the three
companion keys, exact matching lowercase UUID and fixed confirmed status;
malformed/duplicate/unreadable/private-extra companions are rejected without
retaining raw values. Never manually edit a control record.

### Recognized metadata privacy/trust boundary

Malformed SHA/revision/chip/UUID/structured-camera values and unsupported fixed labels are
omitted (never normalized into acceptance). Native rejected setup strips invalid
text and mismatched fingerprints while retaining numbers/fixed codes. Host report
device names/hardware/fingerprint and setup fingerprint are compared with the
explicit selected serial's independently acquired getprop values; trusted values,
not mismatched report copies, are retained. Build version text requires matching
installed-package dumpsys metadata; unavailable/unsupported text is omitted and
qualification fails closed. This verifies selected-device/package identity, not
physical RAM/chip/lux or general hardware attestation. Setup identities use generated
UUIDs, chips a fixed vocabulary, cameras only a producer-bound structured digest;
free-form cleartext aliases are not retained, including rejected interpreter rows.
Package acquisition/parse failure preserves already-read sanitized measured
numbers/traces and trusted selected device names, appends a fixed unavailable
code and rejects qualification independently of report-field presence. Unsupported
source device keys are detected before rebuilding trusted names; values are
omitted and rejection survives reader and repeated sink binding. Do not put names
or notes in identifiers. Error/counter categories use a fixed shared vocabulary:
no_signer, persistence_failed, failure, IOException, FileNotFoundException,
IllegalStateException, IllegalArgumentException, RuntimeException,
SecurityException; unknown native exception class names map to failure and raw
exception text is never retained in benchmark diagnostics.
