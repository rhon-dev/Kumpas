# Phase 9 — Mobile App Architecture: Design

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  Flutter UI Layer (Dart)                        │
│  - AppShell (5-tab navigation)                  │
│  - Practice screen, Dictionary, Learn, Profile  │
│  - Feedback sheet (bottom sheet overlay)        │
│  - ThemeMode (light/dark via ValueNotifier)     │
└─────────────┬───────────────────────────────────┘
              │ Platform Channel (MethodChannel)
              ▼
┌─────────────────────────────────────────────────┐
│  Native Pipeline (Kotlin/Android)               │
│  - CameraX capture (24-30 FPS)                  │
│  - MediaPipe Holistic (landmark extraction)     │
│  - TFLite Interpreter (sign classification)     │
│  - Feedback Engine (gold-standard comparison)   │
└─────────────────────────────────────────────────┘
```

## 2. Module Boundaries

| Module | Language | Responsibility | Does NOT Touch |
|--------|----------|---------------|----------------|
| `app/lib/ui/` | Dart | All screens, widgets, navigation, theming | Native pipeline, model artifacts |
| `app/lib/feedback_engine/` | Dart | Platform channel interface, feedback data models | Native implementation details |
| `app/android/.../KumpasChannel.kt` | Kotlin | CameraX, MediaPipe, TFLite, feedback engine | UI rendering, Flutter state |
| `app/assets/models/` | — | TFLite model + label map + gold standards (bundled) | — |

## 3. State Management

**Approach:** ValueNotifier + InheritedWidget (lightweight, no external packages)

**Justification:**
- App state is simple: current screen, theme mode, session history, practice state
- No complex reactive flows requiring Bloc/Riverpod
- Fewer dependencies = fewer potential network-calling libraries to audit
- Matches thesis scope (functional, not production-scale complexity)

## 4. Threading / Pipeline Architecture

### Camera Pipeline (Native, Kotlin)

```
Camera Frame (30 FPS) ──→ MediaPipe Holistic ──→ Landmark Buffer
                                                        │
                          TFLite Interpreter ←──────────┘
                                │
                          Prediction + Confidence
                                │
                          Feedback Engine (if practice mode)
                                │
                          MethodChannel → Dart UI
```

### Thread Model

| Component | Thread | Rationale |
|-----------|--------|-----------|
| CameraX preview | Camera thread (managed by CameraX) | Standard Android pattern |
| MediaPipe processing | Background thread (Executor) | Keeps UI thread free |
| TFLite inference | Same background thread | Sequential dependency on landmarks |
| Feedback computation | Same background thread | Sequential dependency on prediction |
| UI update | Main/UI thread (via MethodChannel callback) | Flutter requirement |

### Frame Management Strategy

**Policy:** Process latest frame, skip if pipeline is busy.

- Camera delivers frames at 30 FPS
- If inference pipeline hasn't finished processing the previous frame, the new frame is **dropped** (not queued)
- This ensures the UI always shows the most recent result, never stale predictions from a backed-up queue
- FPS counter measures frames that complete the full pipeline, not camera frames delivered

## 5. Latency Budget Allocation

| Stage | Budget | Measured (Emulator) | Notes |
|-------|--------|-------------------|-------|
| Frame capture | ~5 ms | ~3 ms | CameraX callback |
| MediaPipe Holistic | ~80 ms | TBD real device | Most expensive step |
| Landmark normalization | ~1 ms | <1 ms | Simple math on 258 values |
| TFLite inference | ~10 ms | 0-2 ms (emulator) | 270K param model, quantized |
| Feedback engine | ~5 ms | TBD | DTW on 30-frame sequences |
| Channel transfer + UI | ~5 ms | <5 ms | MethodChannel serialization |
| **Total** | **<150 ms** | **~30 ms (emulator)** | Emulator is not representative |

**Risk:** MediaPipe Holistic is the dominant cost. If it exceeds budget on real hardware, options: (a) reduce model_complexity to 0, (b) process every other frame, (c) use Hands-only (not full Holistic).

## 6. Dependencies (Offline Audit)

| Dependency | Purpose | Network Calls? | Size Impact |
|------------|---------|---------------|-------------|
| Flutter SDK | Framework | No | Base |
| CameraX | Camera capture | No | ~1 MB |
| MediaPipe Holistic | Landmark extraction | No (model bundled) | ~15 MB |
| TFLite + Flex delegate | Model inference | No | ~8 MB |
| No analytics SDK | — | — | — |
| No crash reporting | — | — | — |
| No Firebase | — | — | — |

**Total APK size estimate:** ~40-50 MB (dominated by MediaPipe model + TFLite Flex)

## 7. Platform Channel Interface

```kotlin
// KumpasChannel.kt
class KumpasChannel(private val messenger: BinaryMessenger) {
    // Methods called from Dart:
    fun startCamera(textureId: Long)
    fun stopCamera()
    fun startPractice(signLabel: String)  // loads gold standard
    fun stopPractice()
    
    // Callbacks to Dart:
    fun onPrediction(label: String, confidence: Float, fps: Float)
    fun onFeedback(report: FeedbackReport)
    fun onLandmarks(detected: Boolean)  // for UI "no hand detected" state
}
```

## 8. App Asset Structure

```
app/assets/
├── models/
│   ├── kumpas_50sign_no_face_dynamic.tflite  (0.32 MB)
│   └── label_map.json
└── gold_standards/
    └── gold_standards.json  (50 entries, per-sign reference landmarks)
```

## Status

**Complete.** Architecture documented; implementation exists and is running on emulator. Real-device validation pending (Phase 18).
