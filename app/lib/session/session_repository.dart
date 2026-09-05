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
  String? _participantId;

  /// Whether a practice session is currently active.
  bool get hasActiveSession => _activeSessionId != null;

  /// The current active session ID, or null.
  String? get activeSessionId => _activeSessionId;

  /// The device-generated participant UUID (cached after first call).
  Future<String> get participantId async {
    _participantId ??= await KumpasChannel.getParticipantId();
    return _participantId!;
  }

  /// Start a new practice session. Safe to call if one is already active
  /// (the native side closes the old one first).
  Future<String> startSession() async {
    _activeSessionId = await KumpasChannel.startSession();
    return _activeSessionId!;
  }

  /// End the active session. No-op if none is active.
  Future<void> endSession() async {
    if (_activeSessionId == null) return;
    await KumpasChannel.endSession();
    _activeSessionId = null;
  }

  /// Sync the cached session state with native (e.g. after app resume
  /// when native may have auto-closed the session).
  Future<void> sync() async {
    _activeSessionId = await KumpasChannel.getActiveSession();
  }

  /// Get the attempt history (newest first), backed by SQLite.
  Future<List<AttemptResult>> getHistory() => KumpasChannel.getHistory();

  /// Save a pre or post assessment.
  Future<void> saveAssessment({
    required String type,
    required Map<String, dynamic> responses,
  }) =>
      KumpasChannel.saveAssessment(type: type, responses: responses);

  /// Get all saved assessments for the current participant.
  Future<List<Map<String, dynamic>>> getAssessments() =>
      KumpasChannel.getAssessments();

  /// Export all data to a JSON file. Returns the absolute file path.
  Future<String> exportData() => KumpasChannel.exportData();

  /// Permanently clear all session data and reset the participant ID.
  Future<void> clearAllData() async {
    await KumpasChannel.clearAllData();
    _activeSessionId = null;
    _participantId = null;
  }
}
