import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kumpas_app/feedback_engine/kumpas_channel.dart';
import 'package:kumpas_app/session/session_lifecycle.dart';
import 'package:kumpas_app/session/session_repository.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final messenger =
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
  final repo = SessionRepository.instance;
  late Future<Object?> Function(MethodCall) handler;
  late SessionLifecycleObserver observer;
  Future<void> flush() => pumpEventQueue();

  setUp(() async {
    handler = (_) async => null;
    messenger.setMockMethodCallHandler(
      KumpasChannel.control,
      (call) => handler(call),
    );
    await repo.clearAllData();
    observer = SessionLifecycleObserver();
  });
  tearDown(() async {
    handler = (_) async => null;
    await repo.clearAllData();
    messenger.setMockMethodCallHandler(KumpasChannel.control, null);
  });

  test('replacement screen waits for prior screen end reply', () async {
    final endReply = Completer<void>();
    final commands = <String>[];
    String? nativeSession;
    var starts = 0;
    handler = (call) async {
      commands.add(call.method);
      if (call.method == 'startSession') {
        nativeSession = 'session-${++starts}';
        return nativeSession;
      }
      if (call.method == 'endSession') {
        nativeSession = null; // Native effect precedes withheld reply.
        await endReply.future;
      }
      return null;
    };
    observer.setPracticeActive(true);
    await observer.didChangeAppLifecycleState(AppLifecycleState.resumed);
    observer.setPracticeActive(false); // PracticeScreen.dispose does not await.
    await flush();
    final replacement = SessionLifecycleObserver();
    replacement.setPracticeActive(true);
    final resume = replacement.didChangeAppLifecycleState(
      AppLifecycleState.resumed,
    );
    await flush();
    final beforeReply = List<String>.of(commands);
    endReply.complete(); // Release prerequisite before awaiting replacement.
    await resume;
    await flush();
    expect(beforeReply, ['startSession', 'endSession']);
    expect(commands, ['startSession', 'endSession', 'startSession']);
    expect(nativeSession, 'session-2');
    expect(repo.activeSessionId, nativeSession);
    replacement.setPracticeActive(false);
    await flush();
    expect(nativeSession, isNull);
  });

  for (final effectBeforeFailure in [false, true]) {
    test('replacement after failed end effect=$effectBeforeFailure', () async {
      final endReply = Completer<void>();
      final commands = <String>[];
      String? nativeSession;
      var starts = 0;
      var ends = 0;
      handler = (call) async {
        commands.add(call.method);
        if (call.method == 'startSession') {
          nativeSession = 'session-${++starts}';
          return nativeSession;
        }
        if (call.method == 'endSession') {
          if (++ends == 1) {
            if (effectBeforeFailure) nativeSession = null;
            await endReply.future;
            throw PlatformException(code: 'synthetic-end-failure');
          }
          nativeSession = null;
        }
        return null;
      };
      observer.setPracticeActive(true);
      await observer.didChangeAppLifecycleState(AppLifecycleState.resumed);
      observer.setPracticeActive(false);
      await flush();
      final replacement = SessionLifecycleObserver();
      replacement.setPracticeActive(true);
      final resume = replacement.didChangeAppLifecycleState(
        AppLifecycleState.resumed,
      );
      await flush();
      endReply.complete();
      await resume;
      await flush();
      expect(commands, ['startSession', 'endSession', 'startSession']);
      expect(nativeSession, 'session-2');
      expect(repo.activeSessionId, nativeSession);
      // Even if an obsolete observer receives another event, it cannot close
      // the new screen's successfully committed replacement.
      observer.setPracticeActive(false);
      await flush();
      expect(ends, 1);
      replacement.setPracticeActive(false);
      await flush();
      expect(ends, 2);
      expect(nativeSession, isNull);
    });
  }

  for (final action in ['depart', 'reenter', 'clear', 'failed-clear']) {
    test('replacement $action while prior screen end is pending', () async {
      final endReply = Completer<void>();
      final commands = <String>[];
      String? nativeSession;
      var starts = 0;
      handler = (call) async {
        commands.add(call.method);
        if (call.method == 'startSession') {
          nativeSession = 'session-${++starts}';
          return nativeSession;
        }
        if (call.method == 'endSession') {
          nativeSession = null;
          await endReply.future;
        }
        if (call.method == 'clearAllData') {
          nativeSession = null;
          if (action == 'failed-clear') {
            throw PlatformException(code: 'CLEAR_FAILED');
          }
        }
        return null;
      };
      observer.setPracticeActive(true);
      await observer.didChangeAppLifecycleState(AppLifecycleState.resumed);
      observer.setPracticeActive(false);
      await flush();
      final replacement = SessionLifecycleObserver();
      replacement.setPracticeActive(true);
      final resume = replacement.didChangeAppLifecycleState(
        AppLifecycleState.resumed,
      );
      await flush();
      if (action == 'depart' || action == 'reenter') {
        replacement.setPracticeActive(false);
        if (action == 'reenter') replacement.setPracticeActive(true);
      } else {
        final revision = repo.dataRevision.value;
        if (action == 'failed-clear') {
          await expectLater(
            repo.clearAllData(),
            throwsA(
              isA<PlatformException>().having(
                (e) => e.code,
                'code',
                'CLEAR_FAILED',
              ),
            ),
          );
        } else {
          await repo.clearAllData();
        }
        expect(repo.dataRevision.value, revision + 1);
        expect(repo.activeSessionId, isNull);
      }
      final beforeReply = List<String>.of(commands);
      endReply.complete();
      await resume;
      await flush();
      expect(beforeReply, [
        'startSession',
        'endSession',
        if (action.contains('clear')) 'clearAllData',
      ]);
      expect(starts, action == 'depart' ? 1 : 2);
      expect(repo.activeSessionId, action == 'depart' ? null : 'session-2');
      expect(nativeSession, repo.activeSessionId);
      if (action == 'depart') {
        // A later entry remains usable after choosing not to start while gone.
        replacement.setPracticeActive(true);
        await flush();
        expect(repo.activeSessionId, 'session-2');
      }
      replacement.setPracticeActive(false);
      await flush();
      expect(commands.where((c) => c == 'endSession'), hasLength(2));
      expect(nativeSession, isNull);
    });
  }

  test('pending external start retains B1 non-atomic boundary', () async {
    final replacementReply = Completer<String>();
    final commands = <String>[];
    String? nativeSession;
    var starts = 0;
    handler = (call) async {
      commands.add(call.method);
      if (call.method == 'startSession') {
        nativeSession = 'session-${++starts}';
        if (starts == 2) return replacementReply.future;
        return nativeSession;
      }
      if (call.method == 'endSession') nativeSession = null;
      return null;
    };
    observer.setPracticeActive(true);
    await observer.didChangeAppLifecycleState(AppLifecycleState.resumed);
    final external = repo.startSession();
    await flush();
    observer.setPracticeActive(false);
    await flush();
    replacementReply.complete('session-2');
    await external;
    // Characterization only: direct concurrent callers are not coordinated.
    // Cache equality does not make the native end identity-scoped.
    expect(commands, ['startSession', 'startSession', 'endSession']);
    expect(nativeSession, isNull);
    expect(repo.activeSessionId, isNull);
  });

  test('practice entry and duplicate resume share one pending start', () async {
    final start = Completer<String>();
    var starts = 0;
    handler = (call) async {
      if (call.method == 'startSession') {
        starts++;
        return start.future;
      }
      return null;
    };
    await observer.didChangeAppLifecycleState(AppLifecycleState.resumed);
    observer.setPracticeActive(true);
    final resume = observer.didChangeAppLifecycleState(
      AppLifecycleState.resumed,
    );
    observer.setPracticeActive(true);
    await flush();
    // Complete before asserting so failed baseline does not strand futures.
    start.complete('owned');
    await resume;
    await flush();
    expect(starts, 1);
    expect(repo.activeSessionId, 'owned');
  });

  test(
    'leave immediately after cached resume is not lost behind completed work',
    () async {
      final commands = <String>[];
      handler = (call) async {
        commands.add(call.method);
        if (call.method == 'startSession') return 'owned';
        return null;
      };
      observer.setPracticeActive(true);
      await observer.didChangeAppLifecycleState(AppLifecycleState.resumed);
      // Cached reconciliation returns synchronously, but its Future has not
      // cleared _pending when the next actual observer method runs.
      observer.setPracticeActive(true);
      observer.setPracticeActive(false);
      await flush();
      expect(commands, ['startSession', 'endSession']);
      expect(repo.activeSessionId, isNull);
    },
  );

  for (final operation in ['startSession', 'endSession']) {
    test(
      'fire-and-forget $operation failure is handled and next event retries',
      () async {
        var failures = 0;
        var starts = 0;
        var ends = 0;
        handler = (call) async {
          if (call.method == 'startSession') starts++;
          if (call.method == 'endSession') ends++;
          if (call.method == operation && failures++ == 0) {
            throw PlatformException(code: 'synthetic-lifecycle-failure');
          }
          if (call.method == 'startSession') return 'retry-session';
          return null;
        };
        await observer.didChangeAppLifecycleState(AppLifecycleState.resumed);
        observer.setPracticeActive(true);
        await flush();
        if (operation == 'startSession') {
          expect(repo.activeSessionId, isNull);
          observer.setPracticeActive(true);
          await flush();
          expect(starts, 2);
          expect(repo.activeSessionId, 'retry-session');
        } else {
          observer.setPracticeActive(false);
          await flush();
          expect(repo.activeSessionId, 'retry-session');
          observer.setPracticeActive(false);
          await flush();
          expect(ends, 2);
          expect(repo.activeSessionId, isNull);
        }
      },
    );
  }

  test('inactive is transitional during pending and active session', () async {
    final start = Completer<String>();
    final commands = <String>[];
    handler = (call) async {
      commands.add(call.method);
      if (call.method == 'startSession') return start.future;
      return null;
    };
    observer.setPracticeActive(true);
    final resume = observer.didChangeAppLifecycleState(
      AppLifecycleState.resumed,
    );
    await flush();
    await observer.didChangeAppLifecycleState(AppLifecycleState.inactive);
    start.complete('owned');
    await resume;
    await observer.didChangeAppLifecycleState(AppLifecycleState.inactive);
    expect(commands, ['startSession']);
    expect(repo.activeSessionId, 'owned');
  });

  test(
    'departure and re-entry serialize old end before replacement start',
    () async {
      final start = Completer<String>();
      final end = Completer<void>();
      final commands = <String>[];
      var starts = 0;
      handler = (call) async {
        commands.add(call.method);
        if (call.method == 'startSession') {
          if (starts++ == 0) return start.future;
          return 'replacement';
        }
        if (call.method == 'endSession') await end.future;
        return null;
      };
      observer.setPracticeActive(true);
      final resume = observer.didChangeAppLifecycleState(
        AppLifecycleState.resumed,
      );
      await flush();
      observer.setPracticeActive(false);
      observer.setPracticeActive(true);
      start.complete('departed');
      await flush();
      expect(commands, ['startSession', 'endSession']);
      end.complete();
      await resume;
      expect(commands, ['startSession', 'endSession', 'startSession']);
      expect(repo.activeSessionId, 'replacement');
    },
  );

  test(
    'obsolete pending start does not end external replacement on leave',
    () async {
      final start = Completer<String>();
      final commands = <String>[];
      var starts = 0;
      String? nativeSession;
      handler = (call) async {
        commands.add(call.method);
        if (call.method == 'startSession') {
          nativeSession = starts++ == 0 ? 'departed' : 'external-replacement';
          if (starts == 1) return start.future;
          return nativeSession;
        }
        if (call.method == 'endSession') nativeSession = null;
        return null;
      };
      observer.setPracticeActive(true);
      final resume = observer.didChangeAppLifecycleState(
        AppLifecycleState.resumed,
      );
      await flush();
      observer.setPracticeActive(false);
      await repo.startSession();
      start.complete('departed');
      await resume;
      expect(commands, ['startSession', 'startSession']);
      expect(repo.activeSessionId, 'external-replacement');
      expect(nativeSession, 'external-replacement');
    },
  );

  test(
    'late owned end cannot clear external replacement or send another end',
    () async {
      final end = Completer<void>();
      final commands = <String>[];
      var starts = 0;
      handler = (call) async {
        commands.add(call.method);
        if (call.method == 'startSession') return 'session-${starts++}';
        if (call.method == 'endSession') await end.future;
        return null;
      };
      observer.setPracticeActive(true);
      await observer.didChangeAppLifecycleState(AppLifecycleState.resumed);
      final pause = observer.didChangeAppLifecycleState(
        AppLifecycleState.paused,
      );
      await flush();
      await repo.startSession();
      observer.setPracticeActive(false);
      end.complete();
      await pause;
      expect(commands, ['startSession', 'endSession', 'startSession']);
      expect(repo.activeSessionId, 'session-1');
    },
  );

  test(
    'clear supersedes observer pending start without obsolete cleanup',
    () async {
      final start = Completer<String>();
      final commands = <String>[];
      var starts = 0;
      handler = (call) async {
        commands.add(call.method);
        if (call.method == 'startSession') {
          if (starts++ == 0) return start.future;
          return 'post-clear';
        }
        return null;
      };
      observer.setPracticeActive(true);
      final resume = observer.didChangeAppLifecycleState(
        AppLifecycleState.resumed,
      );
      await flush();
      observer.setPracticeActive(false);
      await repo.clearAllData();
      start.complete('removed');
      await resume;
      expect(commands, ['startSession', 'clearAllData']);
      expect(repo.activeSessionId, isNull);
      observer.setPracticeActive(true);
      await flush();
      expect(repo.activeSessionId, 'post-clear');
    },
  );

  for (final terminal in ['leave', 'paused', 'hidden', 'detached']) {
    test(
      '$terminal while start pending eventually ends owned session',
      () async {
        final start = Completer<String>();
        final commands = <String>[];
        String? nativeSession;
        handler = (call) async {
          commands.add(call.method);
          if (call.method == 'startSession') {
            nativeSession = 'owned';
            return start.future;
          }
          if (call.method == 'endSession') nativeSession = null;
          return null;
        };
        observer.setPracticeActive(true);
        final resume = observer.didChangeAppLifecycleState(
          AppLifecycleState.resumed,
        );
        await flush();
        Future<void>? departure;
        if (terminal == 'leave') {
          observer.setPracticeActive(false);
        } else {
          departure = observer.didChangeAppLifecycleState(
            AppLifecycleState.values.byName(terminal),
          );
        }
        await flush();
        start.complete('owned');
        await resume;
        await departure;
        await flush();
        expect(commands, ['startSession', 'endSession']);
        expect(nativeSession, isNull);
        expect(repo.activeSessionId, isNull);
      },
    );
  }
}
