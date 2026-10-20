import 'package:flutter/material.dart';
import 'session_repository.dart';

/// Serializes this practice screen's lifecycle intent around channel replies.
/// Native commands are not cancelled or rolled back when intent changes.
class SessionLifecycleObserver extends WidgetsBindingObserver {
  bool _inPracticeScreen = false;
  bool _foreground = false;
  int _departure = 0;
  int _intent = 0;
  String? _ownedSessionId;
  Future<void>? _pending;

  void setPracticeActive(bool active) {
    _inPracticeScreen = active;
    if (!active) _departure++;
    _schedule();
  }

  @override
  Future<void> didChangeAppLifecycleState(AppLifecycleState state) async {
    switch (state) {
      case AppLifecycleState.resumed:
        _foreground = true;
        break;
      case AppLifecycleState.paused:
      case AppLifecycleState.detached:
      case AppLifecycleState.hidden:
        _foreground = false;
        _departure++;
        break;
      case AppLifecycleState.inactive:
        // Transitional: keep the previous foreground/session intent.
        return;
    }
    await _schedule();
  }

  bool get _wantsSession => _inPracticeScreen && _foreground;

  Future<void> _schedule() {
    _intent++;
    return _pending ??= _drain();
  }

  Future<void> _drain() async {
    try {
      while (true) {
        final intent = _intent;
        try {
          await SessionRepository.instance.reconcileLifecycle(_reconcile);
        } catch (_) {
          // Binding and setPracticeActive callers do not await this work.
          // Avoid arbitrary channel details; a subsequent event can retry.
          debugPrint(
            'Session lifecycle operation failed; retry on next event.',
          );
        }
        if (intent == _intent) return;
      }
    } finally {
      // Release in the same continuation that checks intent, not in a later
      // whenComplete callback which could swallow a new event in between.
      _pending = null;
    }
  }

  Future<void> _reconcile() async {
    final repo = SessionRepository.instance;
    while (true) {
      if (!_wantsSession) {
        await _endOwnedSession();
        if (!_wantsSession) return;
        continue;
      }
      final adoptable = repo.adoptableSessionId;
      if (adoptable != null) {
        _ownedSessionId = adoptable;
        return;
      }
      final departure = _departure;
      final id = await repo.startSession();
      // Clear or an external replacement may have superseded our reply.
      if (repo.activeSessionId != id) return;
      _ownedSessionId = id;
      if (departure == _departure && _wantsSession) return;
      await _endOwnedSession();
      // Re-entry during a pending start/end gets a fresh session only after
      // the departed session's end command has completed.
    }
  }

  Future<void> _endOwnedSession() async {
    final repo = SessionRepository.instance;
    final owned = _ownedSessionId;
    if (owned != null && repo.activeSessionId == owned) {
      await repo.endSession();
    }
    _ownedSessionId = null;
  }
}
