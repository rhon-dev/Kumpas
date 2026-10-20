import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kumpas_app/feedback_engine/kumpas_channel.dart';
import 'package:kumpas_app/feedback_engine/models.dart';
import 'package:kumpas_app/session/session_repository.dart';
import 'package:kumpas_app/ui/practice_screen.dart';
import 'package:kumpas_app/ui/feedback_sheet.dart';
import 'package:kumpas_app/ui/stats.dart';
import 'package:kumpas_app/ui/theme.dart';
import 'support/host_fixture.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late HostFixture fixture;
  setUp(() {
    fixture = HostFixture.load();
  });

  testWidgets(
    'exact Handler bytes through mocked EventChannel open one sheet and ACK native identity',
    (tester) async {
      final event = fixture.event;
      final acks = <String>[];
      final calls = <MethodCall>[];
      final messenger = tester.binding.defaultBinaryMessenger;
      messenger.setMockMethodCallHandler(KumpasChannel.control, (call) async {
        calls.add(call);
        switch (call.method) {
          case 'startAttempt':
            expect(call.arguments['classId'], event['targetClass']);
            // Native attempt was direct AttemptBoundary setup, not startAttempt RPC.
            // Only this transport identity response is constructed from its envelope.
            return fixture.study['primary']['attempt_id'];
          case 'startSession':
            return fixture.control('initialized', 'startSession')['response'];
          case 'feedbackPresented':
            final native = fixture.control('one-terminal', 'feedbackPresented');
            expect(call.arguments, native['arguments']);
            acks.add(call.arguments['attemptId'] as String);
            return native['response'];
          case 'getActiveSession':
            return fixture.control(
              'initialized',
              'getActiveSession',
            )['response'];
          case 'endSession':
          case 'cancelAttempt':
            return null; // Synthetic UI lifecycle transport, not a captured native stage.
          default:
            fail('unexpected mocked control method: ${call.method}');
        }
      });
      messenger.setMockMethodCallHandler(
        const MethodChannel('kumpas/predictions'),
        (_) async => null,
      );
      messenger.setMockMethodCallHandler(SystemChannels.platform_views, (
        call,
      ) async {
        if (call.method == 'create') return 0;
        if (call.method == 'resize') return {'width': 400.0, 'height': 380.0};
        return null;
      });
      addTearDown(() {
        messenger.setMockMethodCallHandler(KumpasChannel.control, null);
        messenger.setMockMethodCallHandler(
          const MethodChannel('kumpas/predictions'),
          null,
        );
        messenger.setMockMethodCallHandler(SystemChannels.platform_views, null);
      });
      await tester.binding.setSurfaceSize(const Size(800, 1000));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      await tester.pumpWidget(
        MaterialApp(
          theme: KumpasTheme.light(),
          home: PracticeScreen(
            sign: Sign(
              id: event['targetClass'] as int,
              label: event['targetLabel'] as String,
              category: 'Synthetic',
            ),
          ),
        ),
      );
      await tester.pump();
      await tester.tap(find.text('Subukan ang Senyas'));
      await tester.pump();
      Future<void> send(String raw) async {
        tester.binding.defaultBinaryMessenger.handlePlatformMessage(
          'kumpas/predictions',
          const StandardMethodCodec().encodeSuccessEnvelope(raw),
          (_) {},
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 600));
      }

      // Unowned native replacement identity is a stale consumer-negative event.
      final stale = Map<String, dynamic>.from(event)
        ..['attemptId'] =
            fixture.study['queued_persistence']['replacement_attempt_id'];
      await send(jsonEncode(stale));
      expect(find.byType(FeedbackSheet), findsNothing);
      expect(acks, isEmpty);
      final raw = fixture.text('attempt-event.json');
      expect(raw, fixture.study['primary']['delivered_event']);
      await send(raw);
      expect(find.byType(FeedbackSheet), findsOneWidget);
      final sheet = tester.widget<FeedbackSheet>(find.byType(FeedbackSheet));
      expect(sheet.result.recognizedAsTarget, event['recognizedAsTarget']);
      expect(sheet.result.overallMatch, event['overallMatch']);
      expect(sheet.result.targetClass, event['targetClass']);
      expect(sheet.result.items, hasLength(1));
      final item = sheet.result.items.single;
      expect(item.dimension, 'handshape');
      expect(item.severity, .25);
      expect(item.hand, 'right');
      expect(item.prompt, 'SYNTHETIC feedback');
      expect(find.text('SYNTHETIC feedback'), findsOneWidget);
      await tester.pumpAndSettle();
      expect(find.text('80%'), findsOneWidget);
      expect(acks, [fixture.study['primary']['attempt_id']]);
      await send(raw);
      await send(jsonEncode(stale));
      expect(find.byType(FeedbackSheet), findsOneWidget);
      expect(acks, hasLength(1));
      await tester.tap(find.text('Try again'));
      await tester.pumpAndSettle();
      await send(raw);
      expect(find.byType(FeedbackSheet), findsNothing);
      expect(acks, hasLength(1));
      expect(calls.where((c) => c.method == 'startAttempt'), hasLength(1));
      await tester.pumpWidget(const MaterialApp(home: SizedBox()));
      await tester.pump();
      expect(tester.takeException(), isNull);
    },
  );

  test(
    'captured controls exercise repository, failed clear invalidation and reopened identity',
    () async {
      final repo = SessionRepository.instance;
      final messenger =
          TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
      var stage = 'initialized';
      Map<String, dynamic>? selected;
      final invoked = <MethodCall>[];
      messenger.setMockMethodCallHandler(KumpasChannel.control, (call) async {
        invoked.add(call);
        final record = selected ?? fixture.control(stage, call.method);
        expect(call.method, record['method']);
        if (record['arguments'] != null) {
          expect(call.arguments, record['arguments']);
        }
        if (record['error_code'] != null) {
          throw PlatformException(code: record['error_code'] as String);
        }
        return record['response'];
      });
      addTearDown(
        () => messenger.setMockMethodCallHandler(KumpasChannel.control, null),
      );
      final original = fixture.control(
        'initialized',
        'getParticipantId',
      )['response'];
      expect(await repo.participantId, original);
      expect(
        await repo.startSession(),
        fixture.control('initialized', 'startSession')['response'],
      );
      await repo.sync();
      expect(
        repo.activeSessionId,
        fixture.control('initialized', 'getActiveSession')['response'],
      );
      selected = fixture.control('initialized', 'saveAssessment', index: 0);
      await repo.saveAssessment(
        type: 'pre',
        responses:
            jsonDecode(selected['arguments']['responses'] as String)
                as Map<String, dynamic>,
      );
      selected = fixture.control('initialized', 'saveAssessment', index: 1);
      await expectLater(
        repo.saveAssessment(
          type: 'post',
          responses:
              jsonDecode(selected['arguments']['responses'] as String)
                  as Map<String, dynamic>,
        ),
        throwsA(
          isA<PlatformException>().having(
            (e) => e.code,
            'code',
            'CONTROL_FAILED',
          ),
        ),
      );
      selected = fixture.control('initialized', 'saveAssessment', index: 2);
      await repo.saveAssessment(
        type: 'post',
        responses:
            jsonDecode(selected['arguments']['responses'] as String)
                as Map<String, dynamic>,
      );
      selected = null;
      final assessments = await repo.getAssessments();
      expect(assessments, hasLength(2));
      expect(
        assessments,
        fixture.study['primary']['independent_rows']['assessments'],
      );
      expect(assessments.map((r) => r['type']), ['pre', 'post']);
      stage = 'one-terminal';
      final history = await repo.getHistory();
      expect(history, hasLength(1));
      expect(history.single.targetLabel, fixture.event['targetLabel']);
      expect(
        history.single.items.single.prompt,
        fixture.event['items'][0]['prompt'],
      );
      expect(
        history.single.timestamp!.millisecondsSinceEpoch,
        fixture
            .study['primary']['independent_rows']['attempts'][0]['timestamp'],
      );
      final stats = LearnerStats.fromHistory(history);
      expect(stats.totalAttempts, 1);
      expect(stats.signsTried, 1);
      expect(stats.signsMastered, 1);
      expect(stats.avgMatch, .8);
      expect(isMasteryAttempt(history.single), isTrue);
      selected = fixture.control(
        'export-before-queued-terminal',
        'exportData',
        index: 2,
      );
      await expectLater(
        repo.exportData(),
        throwsA(
          isA<PlatformException>().having(
            (e) => e.code,
            'code',
            'EXPORT_FAILED',
          ),
        ),
      );
      selected = fixture.control(
        'export-before-queued-terminal',
        'exportData',
        index: 0,
      );
      expect(
        await repo.exportData(),
        selected['response'],
      ); // Never dereference historical native path.
      selected = null;
      final revision = repo.dataRevision.value;
      stage = 'partial-purge-failure';
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
      expect(repo.activeSessionId, isNull);
      expect(repo.dataRevision.value, revision + 1);
      expect(
        fixture.study['partial_clear']['independent_rows']['attempts'],
        hasLength(3),
      );
      // Failed purge kept native SQL; explicit ordered snapshot, not live persistence.
      stage = 'initialized';
      expect(await repo.participantId, original);
      final readsAfterFailure = invoked
          .where((c) => c.method == 'getParticipantId')
          .length;
      expect(readsAfterFailure, 2);
      stage = 'clear-retry';
      await repo.clearAllData();
      expect(repo.dataRevision.value, revision + 2);
      final replacement = await repo.participantId;
      expect(replacement, fixture.study['clear']['participant_id']);
      expect(replacement, isNot(original));
      expect(await repo.getHistory(), isEmpty);
      expect(await repo.getAssessments(), isEmpty);
      await repo.sync();
      expect(repo.activeSessionId, isNull);
      final clearedStats = LearnerStats.fromHistory(await repo.getHistory());
      expect(clearedStats.totalAttempts, 0);
      expect(clearedStats.signsMastered, 0);
      expect(clearedStats.avgMatch, 0);
      stage = 'reopened';
      expect(
        await KumpasChannel.getParticipantId(),
        replacement,
      ); // bypass cache: real reopen response
      expect(await repo.getHistory(), isEmpty);
      expect(await repo.getAssessments(), isEmpty);
      expect(
        await repo.exportData(),
        fixture.control('reopened', 'exportData')['response'],
      );
      expect(fixture.study['reopen']['independent_rows']['attempts'], isEmpty);
    },
  );

  test(
    'retained exports match independent scoped SQLite rows and reopened empty export',
    () {
      final rows =
          fixture.study['export_stage_independent_rows']
              as Map<String, dynamic>;
      expect(rows['participants'], hasLength(2));
      expect(
        rows['attempts'],
        hasLength(2),
      ); // foreign participant has actual data.
      expect(
        fixture.text('external-export.json'),
        fixture.text('internal-export.json'),
      );
      for (final name in ['external-export.json', 'internal-export.json']) {
        final export = fixture.json(name) as Map<String, dynamic>;
        final participant = export['metadata']['participant_id'];
        final sessions = (rows['sessions'] as List)
            .where((r) => r['participant_id'] == participant)
            .toList();
        final sessionIds = sessions.map((r) => r['id']).toSet();
        final attempts = (rows['attempts'] as List)
            .where((r) => sessionIds.contains(r['session_id']))
            .toList();
        final assessments = (rows['assessments'] as List)
            .where((r) => r['participant_id'] == participant)
            .toList();
        expect(export['summary'], {
          'total_sessions': sessions.length,
          'total_attempts': attempts.length,
          'total_assessments': assessments.length,
        });
        expect(export['assessments'], assessments);
        expect(export['sessions'], hasLength(1));
        expect(export['sessions'][0]['attempts'], attempts);
        for (final session in export['sessions'] as List) {
          final withoutAttempts = Map<String, dynamic>.from(session as Map)
            ..remove('attempts');
          expect(sessions, contains(equals(withoutAttempts)));
        }
        expect(attempts.single['target_label'], fixture.event['targetLabel']);
        expect(attempts.single['overall_match'], fixture.event['overallMatch']);
      }
      final reopened =
          fixture.json('reopened-export.json') as Map<String, dynamic>;
      expect(
        reopened['metadata']['participant_id'],
        fixture.study['reopen']['participant_id'],
      );
      expect(reopened['summary'], {
        'total_sessions': 0,
        'total_attempts': 0,
        'total_assessments': 0,
      });
      expect(reopened['sessions'], isEmpty);
      expect(reopened['assessments'], isEmpty);
      expect(fixture.study['clear']['both_export_roots_purged'], isTrue);
      expect(fixture.study['clear']['unrelated_sentinels_survived'], isTrue);
    },
  );
  test('current execution loads pinned verified native fixture without skip', () {
    expect(() => HostFixture.load(), returnsNormally);
    expect(fixture.receipt['artifacts'], hasLength(11));
    expect(fixture.calls, hasLength(25));
    // Retained in the actual Flutter test stdout; no native rerun is implied.
    // ignore: avoid_print
    print(
      'HOST_CONSUMER_BINDING ${fixture.receipt['run_id']} '
      '${fixture.receipt['manifest_sha256']} sources=42 artifacts=11 producer_tests=5',
    );
  });
}
