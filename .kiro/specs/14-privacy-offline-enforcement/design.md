# Phase 14 — Privacy & Offline Enforcement Design

## 1. Offline Enforcement Strategy

### Principle: No Network Calls During Normal App Operation

| Layer | Enforcement |
|-------|-------------|
| Architecture | No backend, no API endpoints, no cloud services |
| Dependencies | Every library audited for network behavior (see §2) |
| Build | No analytics/crash-reporting SDK included |
| Testing | Airplane-mode test on release build (see §3) |

### Airplane-Mode Test Protocol

1. Enable airplane mode on device
2. Install release APK (not debug)
3. Complete full flow: launch → browse dictionary → start practice → perform sign → receive feedback → view history
4. Verify: no error, no hang, no "no connection" message
5. **Pass criterion:** All features work identically to connected mode

## 2. Dependency Network Audit

| Dependency | Network Calls? | Evidence |
|------------|---------------|----------|
| Flutter SDK | No (core framework) | Well-documented |
| CameraX | No | Local hardware access only |
| MediaPipe Holistic | No (model bundled in APK) | Confirmed: model files in assets, no download |
| TFLite runtime | No | Local inference only |
| TFLite Flex delegate | No | Static library, no network |
| material_design_icons | No | Static asset package |
| **Total third-party network calls:** | **0** | |

### What Is NOT Included (By Design)

- No Firebase (Analytics, Crashlytics, Auth, or Firestore)
- No Sentry / Bugsnag / crash reporting
- No Google Analytics
- No ad SDKs
- No update-checking mechanism
- No telemetry of any kind

## 3. Camera Permission Handling

| State | Behavior |
|-------|----------|
| Not yet requested | Show explanation screen: "Kumpas needs camera access to see your signs and provide feedback. No video is stored or sent anywhere." |
| Granted | Proceed to camera features |
| Denied | Show: "Camera access is needed for sign practice. You can enable it in Settings." + "Open Settings" button |
| Revoked mid-session | Gracefully return to non-camera screen; show permission explanation |

## 4. Data Handling

### Session Data (Practice Attempts)
- **Stored:** Attempt count, timestamp, sign attempted, overall match score, feedback items
- **NOT stored:** Raw frames, landmark sequences, video
- **Location:** Local app storage only (SharedPreferences or local SQLite)
- **Retention:** Indefinite (user's practice history) — no automatic deletion
- **Export:** Not implemented for MVP (no sync, no share)

### Evaluation Study Data (Phase 16+ Only)
- **Requires:** Separate explicit consent per participant
- **Stored:** Pre/post assessment scores, session logs during study period
- **NOT stored:** Raw video of participants
- **Separation rule:** Study data NEVER merges into FSL-105 training corpus
- **Retention:** Defined in consent form (recommended: delete after thesis publication + 1 year)
- **Location:** Local device only; researcher extracts via USB/adb

## 5. RA 10173 (Data Privacy Act) Applicability

| Data Processing Activity | RA 10173 Applies? | Action Required |
|-------------------------|-------------------|-----------------|
| Using FSL-105 public dataset for training | No (public data, CC BY license) | Cite properly |
| Bundling gold-standard landmarks in app | No (derived from public data, no PII) | — |
| Storing user's practice history locally | Minimal (no PII beyond device storage) | — |
| Evaluation study participant data | **YES** | Informed consent, data minimization, retention limits, right to withdraw |
| Recording participant signing sessions (if done) | **YES** (biometric-adjacent) | Explicit consent for landmark extraction; no raw video retained |

## 6. Consent Form Requirements (Evaluation Study)

Must cover:
1. What is collected (assessment scores, session logs, possibly landmark data)
2. What is NOT collected (video, audio, personal identifiers beyond participant ID)
3. How data is stored (locally, encrypted if platform supports)
4. How long data is retained (specific window, e.g., 2 years post-defense)
5. Right to withdraw at any time (data deleted upon request)
6. Who has access (researcher, adviser only)
7. How results are reported (aggregate only, no individual identification)

## Status

**Design complete.** Formal verification (airplane-mode test on release build) pending Phase 19.
