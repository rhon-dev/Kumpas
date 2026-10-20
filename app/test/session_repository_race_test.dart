import 'dart:async';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kumpas_app/feedback_engine/kumpas_channel.dart';
import 'package:kumpas_app/session/session_repository.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final messenger =
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
  final repo = SessionRepository.instance;
  late Future<Object?> Function(MethodCall) handler;
  Future<void> flush() => pumpEventQueue();

  setUp(() async {
    handler = (_) async => null;
    messenger.setMockMethodCallHandler(
      KumpasChannel.control,
      (call) => handler(call),
    );
    await repo.clearAllData();
  });
  tearDown(() async {
    handler = (_) async => null;
    await repo.clearAllData();
    messenger.setMockMethodCallHandler(KumpasChannel.control, null);
  });

  test('response order cannot undo later native session commands', () async {
    final starts = [Completer<String>(), Completer<String>()];
    final end = Completer<void>();
    final sync = Completer<String?>();
    final commands = <String>[];
    String? nativeSession;
    var startIndex = 0;
    handler = (call) async {
      commands.add(call.method);
      switch (call.method) {
        case 'startSession':
          final index = startIndex++;
          // Native side effect occurs on dispatch, not reply delivery.
          nativeSession = 'session-$index';
          if (index < starts.length) return starts[index].future;
          return nativeSession;
        case 'getActiveSession':
          return sync.future;
        case 'endSession':
          nativeSession = null;
          await end.future;
          return null;
      }
      return null;
    };
    final first = repo.startSession();
    await flush();
    final second = repo.startSession();
    await flush();
    expect(commands, ['startSession', 'startSession']);
    expect(nativeSession, 'session-1');
    starts[1].complete('session-1');
    expect(await second, 'session-1');
    starts[0].complete('session-0');
    expect(await first, 'session-0');
    expect(repo.activeSessionId, 'session-1');

    final oldSync = repo.sync();
    await flush();
    final oldEnd = repo.endSession();
    await flush();
    final replacement = await repo.startSession();
    expect(nativeSession, replacement);
    expect(commands, [
      'startSession',
      'startSession',
      'getActiveSession',
      'endSession',
      'startSession',
    ]);
    sync.complete('session-1');
    end.complete();
    await Future.wait([oldSync, oldEnd]);
    expect(repo.activeSessionId, replacement);
    expect(nativeSession, replacement);
  });

  for (final method in [
    'getParticipantId',
    'startSession',
    'getActiveSession',
  ]) {
    for (final partialFailure in [false, true]) {
      for (final duringClear in [false, true]) {
        test(
          '$method fenced at clear ${duringClear ? 'finish' : 'entry'} failure=$partialFailure',
          () async {
            final response = Completer<String>();
            final clear = Completer<void>();
            var firstRead = true;
            handler = (call) async {
              if (call.method == 'clearAllData') {
                await clear.future;
                if (partialFailure) {
                  throw PlatformException(code: 'CLEAR_FAILED');
                }
                return null;
              }
              if (call.method == method && firstRead) {
                firstRead = false;
                return response.future;
              }
              if (call.method == 'getParticipantId') return 'fresh-participant';
              if (call.method == 'startSession') return 'fresh-session';
              return null;
            };
            Future<Object?> request() async {
              switch (method) {
                case 'getParticipantId':
                  return repo.participantId;
                case 'startSession':
                  return repo.startSession();
                default:
                  await repo.sync();
                  return null;
              }
            }

            Future<Object?>? pending;
            if (!duringClear) pending = request();
            await flush();
            final purge = repo.clearAllData();
            // Install an error listener before resolving a failing channel call.
            final observedPurge = partialFailure
                ? expectLater(purge, throwsA(isA<PlatformException>()))
                : purge;
            await flush();
            if (duringClear) {
              pending = request();
              await flush();
              clear.complete();
              await observedPurge;
            }
            response.complete('removed-state');
            await pending;
            expect(repo.activeSessionId, isNull);
            // Check participant cache before clear's finally can hide a stale
            // pre-clear lookup; mock's next lookup is explicitly fresh.
            expect(await repo.participantId, 'fresh-participant');
            if (!duringClear) {
              clear.complete();
              await observedPurge;
            }
            expect(await repo.participantId, 'fresh-participant');
            expect(await repo.startSession(), 'fresh-session');
            expect(repo.activeSessionId, 'fresh-session');
          },
        );
      }
    }
  }

  for (final operation in ['endSession', 'getActiveSession']) {
    test(
      'late $operation alone cannot clear or overwrite replacement',
      () async {
        final oldResponse = Completer<Object?>();
        var starts = 0;
        final commands = <String>[];
        String? nativeSession;
        handler = (call) async {
          commands.add(call.method);
          if (call.method == 'startSession') {
            nativeSession = 'session-${starts++}';
            return nativeSession;
          }
          if (call.method == operation) {
            if (operation == 'endSession') nativeSession = null;
            return oldResponse.future;
          }
          return null;
        };
        await repo.startSession();
        final old = operation == 'endSession' ? repo.endSession() : repo.sync();
        await flush();
        final replacement = await repo.startSession();
        oldResponse.complete(operation == 'endSession' ? null : 'session-0');
        await old;
        expect(commands, ['startSession', operation, 'startSession']);
        expect(repo.activeSessionId, replacement);
        expect(nativeSession, replacement);
      },
    );
  }

  for (final fails in [false, true]) {
    test(
      'late participant/start/sync cannot restore cache after clear fails=$fails',
      () async {
        final participant = Completer<String>();
        final start = Completer<String>();
        final sync = Completer<String?>();
        var freshReads = 0;
        handler = (call) async {
          switch (call.method) {
            case 'getParticipantId':
              if (freshReads++ == 0) return participant.future;
              return 'fresh-participant';
            case 'startSession':
              return start.future;
            case 'getActiveSession':
              return sync.future;
            case 'clearAllData':
              if (fails) throw PlatformException(code: 'partial-clear');
              return null;
          }
          return null;
        };
        final oldParticipant = repo.participantId;
        final oldStart = repo.startSession();
        final oldSync = repo.sync();
        await flush();
        final revision = repo.dataRevision.value;
        if (fails) {
          await expectLater(
            repo.clearAllData(),
            throwsA(isA<PlatformException>()),
          );
        } else {
          await repo.clearAllData();
        }
        participant.complete('removed-participant');
        start.complete('removed-session');
        sync.complete('removed-session');
        await Future.wait([oldParticipant, oldStart, oldSync]);
        expect(repo.activeSessionId, isNull);
        expect(await repo.participantId, 'fresh-participant');
        expect(repo.dataRevision.value, revision + 1);
      },
    );
  }
}
