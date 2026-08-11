# Phase 9 — Mobile App Architecture

## Objective

Design the Flutter/Android app structure with explicit attention to threading, FPS targets, and offline enforcement.

## Requirements

WHEN the mobile architecture is designed,
the system SHALL specify: state management approach, module boundaries, dependency injection strategy, and the threading/isolate model for camera + inference.

WHEN the camera pipeline is designed,
the system SHALL allocate a latency budget across: frame capture → landmark extraction → model inference → feedback generation → UI render.

WHEN TFLite integration is specified,
the system SHALL document: how the model is loaded (asset vs. downloaded), interpreter lifecycle, input/output tensor handling, and warm-up strategy.

WHEN MediaPipe Holistic is integrated,
the system SHALL document: which platform channel or plugin is used, how landmarks are passed to the Dart layer, and fallback behavior if landmarks are not detected.

WHEN offline enforcement is considered,
the system SHALL ensure no dependency (library, plugin, analytics SDK) makes network calls at runtime.

## Acceptance Criteria

1. Architecture spec includes a module diagram with clear boundaries.
2. Latency budget table shows how 150ms is allocated across the pipeline.
3. Threading strategy ensures camera pipeline runs at 24–30 FPS without blocking UI.
4. Every third-party dependency is listed with confirmation of no network behavior.
5. ADRs justify state management and plugin choices.

## Status

Implementation exists (Flutter app running with camera + inference). Spec formalizes the architecture decisions.
