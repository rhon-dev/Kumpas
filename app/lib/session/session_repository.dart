import 'package:flutter/foundation.dart';
import '../feedback_engine/kumpas_channel.dart';
import '../feedback_engine/models.dart';

/// Dart-side session repository (Phase 8).
///
/// Wraps [KumpasChannel] session methods and caches the active session state
/// to avoid redundant platform channel calls. UI components should use this
/// instead of calling KumpasChannel session methods directly.
class SessionRepository {
  SessionRepository._();
  static final instance = SessionRepository._();

  String? _activeSessionId;
  String? _endingSessionId;
  String? _participantId;
  // Clear fences reads at entry and completion. Only the newest issued session
  // command may update its cache, regardless of response order. These guards
  // protect only Dart state: no native effects are cancelled or IDs altered.
  int _cacheEpoch = 0;
  int _sessionCommand = 0;
  final dataRevision = ValueNotifier<int>(0);
  Future<void> _lifecycleTail = Future<void>.value();

  /// Coordinate screen observers across dispose/recreate, including pending
  /// replies. Direct repository callers are not serialized by this queue.
  Future<void> reconcileLifecycle(Future<void> Function() operation) {
    final next = _lifecycleTail.then((_) => operation());
    // A failed old screen must not poison a replacement screen's turn.
    _lifecycleTail = next.then<void>(
      (_) {},
      onError: (Object _, StackTrace _) {},
    );
    return next;
  }

  /// Whether a practice session is currently active.
  bool get hasActiveSession => _activeSessionId != null;

  /// The current active session ID, or null.
  String? get activeSessionId => _activeSessionId;

  /// An end error may follow a native effect. Keep its ID for safe retry, but
  /// never let a new screen adopt that uncertain/ending session.
  String? get adoptableSessionId =>
      _activeSessionId == _endingSessionId ? null : _activeSessionId;

  /// The device-generated participant UUID (cached after first call).
  Future<String> get participantId async {
    final cached = _participantId;
    if (cached != null) return cached;
    final epoch = _cacheEpoch;
    final id = await KumpasChannel.getParticipantId();
    if (epoch == _cacheEpoch) _participantId = id;
    return id;
  }

  /// Start a new practice session. Safe to call if one is already active
  /// (the native side closes the old one first).
  Future<String> startSession() async {
    final epoch = _cacheEpoch;
    final command = ++_sessionCommand;
    final id = await KumpasChannel.startSession();
    if (epoch == _cacheEpoch && command == _sessionCommand) {
      _activeSessionId = id;
      _endingSessionId = null;
    }
    return id;
  }

  /// End the active session. No-op if none is active.
  Future<void> endSession() async {
    if (_activeSessionId == null) return;
    _endingSessionId = _activeSessionId;
    final epoch = _cacheEpoch;
    final command = ++_sessionCommand;
    await KumpasChannel.endSession();
    if (epoch == _cacheEpoch && command == _sessionCommand) {
      _activeSessionId = null;
      _endingSessionId = null;
    }
  }

  /// Sync the cached session state with native (e.g. after app resume
  /// when native may have auto-closed the session).
  Future<void> sync() async {
    final epoch = _cacheEpoch;
    final command = ++_sessionCommand;
    final id = await KumpasChannel.getActiveSession();
    if (epoch == _cacheEpoch && command == _sessionCommand) {
      _activeSessionId = id;
      _endingSessionId = null;
    }
  }

  /// Get the attempt history (newest first), backed by SQLite.
  Future<List<AttemptResult>> getHistory() => KumpasChannel.getHistory();

  /// Save a pre or post assessment.
  Future<void> saveAssessment({
    required String type,
    required Map<String, dynamic> responses,
  }) => KumpasChannel.saveAssessment(type: type, responses: responses);

  /// Get all saved assessments for the current participant.
  Future<List<Map<String, dynamic>>> getAssessments() =>
      KumpasChannel.getAssessments();

  /// Export all data to a JSON file. Returns the absolute file path.
  Future<String> exportData() => KumpasChannel.exportData();

  /// Permanently clear all session data and reset the participant ID.
  Future<void> clearAllData() async {
    _invalidateCaches();
    try {
      await KumpasChannel.clearAllData();
    } finally {
      // Fence both pre-clear requests and requests made during the purge.
      // Native filesystem/SQLite/preferences purge is not an atomic rollback.
      _invalidateCaches();
      dataRevision.value++;
    }
  }

  void _invalidateCaches() {
    _cacheEpoch++;
    _activeSessionId = null;
    _endingSessionId = null;
    _participantId = null;
  }
}
