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
}
