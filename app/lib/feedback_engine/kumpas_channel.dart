import 'dart:convert';

import 'package:flutter/services.dart';

import 'models.dart';

/// Thin wrapper over the platform channels to the native vision pipeline.
class KumpasChannel {
  static const control = MethodChannel('kumpas/control');
  static const events = EventChannel('kumpas/predictions');

  static Stream<Map<String, dynamic>>? _stream;

  /// Broadcast stream of pipeline events (warmup / no_signer / prediction /
  /// attempt_progress / attempt_result / attempt_failed).
  static Stream<Map<String, dynamic>> eventStream() {
    _stream ??= events
        .receiveBroadcastStream()
        .map((e) => jsonDecode(e as String) as Map<String, dynamic>);
    return _stream!;
  }

  static Future<List<Sign>> getSigns() async {
    final raw = await control.invokeMethod<String>('getLabels');
    final map = jsonDecode(raw!) as Map<String, dynamic>;
    final signs = map.entries
        .map((e) => Sign.fromLabelMapEntry(e.key, e.value as Map<String, dynamic>))
        .toList();
    signs.sort((a, b) => a.id.compareTo(b.id));
    return signs;
  }

  static Future<void> startAttempt(int classId) =>
      control.invokeMethod('startAttempt', {'classId': classId});

  static Future<void> cancelAttempt() => control.invokeMethod('cancelAttempt');

  /// Start FPS benchmark for the given duration.
  static Future<void> startBenchmark({int durationSeconds = 60}) =>
      control.invokeMethod('startBenchmark', {'durationSeconds': durationSeconds});

  /// Stop a running benchmark early and get results.
  static Future<String> stopBenchmark() async {
    final raw = await control.invokeMethod<String>('stopBenchmark');
    return raw ?? '{}';
  }

  /// Check if benchmark mode is currently active.
  static Future<bool> isBenchmarkActive() async {
    final active = await control.invokeMethod<bool>('isBenchmarkActive');
    return active ?? false;
  }

  static Future<List<AttemptResult>> getHistory() async {
    final raw = await control.invokeMethod<String>('getHistory');
    final list = jsonDecode(raw!) as List<dynamic>;
    return list
        .map((e) => AttemptResult.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  // ─── Session lifecycle (Phase 8) ─────────────────────────────────

  /// Start a new practice session. Returns the session UUID.
  static Future<String> startSession() async {
    final id = await control.invokeMethod<String>('startSession');
    return id!;
  }

  /// End the active practice session.
  static Future<void> endSession() => control.invokeMethod('endSession');

  /// Get the active session ID, or null if none.
  static Future<String?> getActiveSession() =>
      control.invokeMethod<String?>('getActiveSession');

  // ─── Assessments (Phase 8) ───────────────────────────────────────

  /// Save a pre or post assessment.
  /// [type] is 'pre' or 'post'.
  /// [responses] is a JSON-encoded map of questionnaire answers.
  static Future<void> saveAssessment({
    required String type,
    required Map<String, dynamic> responses,
  }) =>
      control.invokeMethod('saveAssessment', {
        'type': type,
        'responses': jsonEncode(responses),
      });

  /// Get all assessments for the current participant.
  static Future<List<Map<String, dynamic>>> getAssessments() async {
    final raw = await control.invokeMethod<String>('getAssessments');
    final list = jsonDecode(raw!) as List<dynamic>;
    return list.cast<Map<String, dynamic>>();
  }

  // ─── Data export / management (Phase 8) ──────────────────────────

  /// Export all session data to a JSON file. Returns the file path on device.
  static Future<String> exportData() async {
    final path = await control.invokeMethod<String>('exportData');
    return path!;
  }

  /// Permanently delete all local session data and reset stats.
  static Future<void> clearAllData() => control.invokeMethod('clearAllData');

  /// Get the device-generated participant UUID.
  static Future<String> getParticipantId() async {
    final id = await control.invokeMethod<String>('getParticipantId');
    return id!;
  }
}
