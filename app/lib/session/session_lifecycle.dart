import 'package:flutter/material.dart';
import 'session_repository.dart';

/// Observer for app lifecycle state transitions to manage session start/end.
///
/// When the app enters the practice screen (resumed while in practice),
/// starts a new session. When the app enters background or the user
/// navigates away from practice, ends the session.
///
/// Phase 8, Task 9.
class SessionLifecycleObserver extends WidgetsBindingObserver {
  bool _inPracticeScreen = false;
  AppLifecycleState? _lastLifecycleState;

  /// Mark that the user is on the practice screen.
  void setPracticeActive(bool active) {
    _inPracticeScreen = active;
    if (active && _lastLifecycleState == AppLifecycleState.resumed) {
      _ensureSessionStarted();
    } else if (!active) {
      _ensureSessionEnded();
    }
  }

  @override
  Future<void> didChangeAppLifecycleState(AppLifecycleState state) async {
    _lastLifecycleState = state;

    switch (state) {
      case AppLifecycleState.resumed:
        if (_inPracticeScreen) {
          await _ensureSessionStarted();
        }
        break;

      case AppLifecycleState.paused:
      case AppLifecycleState.detached:
      case AppLifecycleState.hidden:
        // App entered background or is about to be destroyed.
        // End the session to allow native auto-timeout to take effect.
        await _ensureSessionEnded();
        break;

      case AppLifecycleState.inactive:
        // Transitional state; no action needed.
        break;
    }
  }

  /// Ensure a session is active. Safe to call multiple times.
  Future<void> _ensureSessionStarted() async {
    if (!SessionRepository.instance.hasActiveSession) {
      await SessionRepository.instance.startSession();
    }
  }

  /// Ensure no session is active. Safe to call multiple times.
  Future<void> _ensureSessionEnded() async {
    if (SessionRepository.instance.hasActiveSession) {
      await SessionRepository.instance.endSession();
    }
  }
}
