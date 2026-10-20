import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kumpas_app/session/session_repository.dart';
import 'package:kumpas_app/feedback_engine/kumpas_channel.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final messenger =
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
  final repo = SessionRepository.instance;

  setUp(() async {
    messenger.setMockMethodCallHandler(
      KumpasChannel.control,
      (_) async => null,
    );
    await repo.clearAllData();
  });
  tearDown(() async {
    messenger.setMockMethodCallHandler(
      KumpasChannel.control,
      (_) async => null,
    );
    await repo.clearAllData();
    messenger.setMockMethodCallHandler(KumpasChannel.control, null);
  });

  for (final partialFailure in [false, true]) {
    test(
      'clear resets cached identity/session and revision; partialFailure=$partialFailure',
      () async {
        var cleared = false;
        messenger.setMockMethodCallHandler(KumpasChannel.control, (call) async {
          switch (call.method) {
            case 'getParticipantId':
              return cleared ? 'new' : 'old';
            case 'startSession':
              return cleared ? 'new-session' : 'session';
            case 'clearAllData':
              cleared = true;
              if (partialFailure) throw PlatformException(code: 'CLEAR_FAILED');
              return null;
            default:
              return null;
          }
        });
        expect(await repo.participantId, 'old');
        await repo.startSession();
        final revision = repo.dataRevision.value;
        if (partialFailure) {
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
        expect(repo.activeSessionId, isNull);
        expect(await repo.participantId, 'new');
        expect(repo.dataRevision.value, revision + 1);
        expect(await repo.startSession(), 'new-session');
        expect(repo.activeSessionId, 'new-session');
      },
    );
  }
}
