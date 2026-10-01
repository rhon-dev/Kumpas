
import 'package:flutter_test/flutter_test.dart';
import 'package:kumpas_app/session/session_repository.dart';
import 'package:kumpas_app/feedback_engine/kumpas_channel.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  test(
    'clear resets cached identity/session and invalidates visible data',
    () async {
      var cleared = false;
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(KumpasChannel.control, (call) async {
            switch (call.method) {
              case 'getParticipantId':
                return cleared ? 'new' : 'old';
              case 'startSession':
                return 'session';
              case 'clearAllData':
                cleared = true;
                return null;
              default:
                return null;
            }
          });
      final repo = SessionRepository.instance;
      expect(await repo.participantId, 'old');
      await repo.startSession();
      final revision = repo.dataRevision.value;
      await repo.clearAllData();
      expect(repo.activeSessionId, isNull);
      expect(await repo.participantId, 'new');
      expect(repo.dataRevision.value, revision + 1);
    },
  );
}
