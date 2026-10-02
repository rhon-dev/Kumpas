import 'dart:convert';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kumpas_app/feedback_engine/kumpas_channel.dart';
import 'package:kumpas_app/feedback_engine/models.dart';
import 'package:kumpas_app/ui/practice_screen.dart';
import 'package:kumpas_app/ui/feedback_sheet.dart';
import 'package:kumpas_app/ui/theme.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  var failStart = false;
  Completer<String>? pendingStart;
  final cancelledIds = <String?>[];
  final cancelOutcomes = <String?>[];
  var cancelCalls = 0;
  var presentedCalls = 0;
  var sequence = 0;
  var benchmarkCalls = 0;
  var failBenchmark = false;
  setUp(() {
    failStart = false;
    pendingStart = null;
    cancelledIds.clear();
    cancelOutcomes.clear();
    cancelCalls = 0;
    presentedCalls = 0;
    sequence = 0;
    benchmarkCalls = 0;
    failBenchmark = false;
    final messenger =
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
    messenger.setMockMethodCallHandler(KumpasChannel.control, (call) async {
      switch (call.method) {
        case 'startAttempt':
          if (failStart) {
            throw PlatformException(
              code: 'CAMERA_ERROR',
              message: 'Camera unavailable',
            );
          }
          if (pendingStart != null) return pendingStart!.future;
          return 'attempt-${++sequence}';
        case 'cancelAttempt':
          cancelCalls++;
          cancelledIds.add(call.arguments['attemptId'] as String?);
          cancelOutcomes.add(call.arguments['outcome'] as String?);
          return null;
        case 'feedbackPresented':
          presentedCalls++;
          return null;
        case 'startSession':
          return 'synthetic-session';
        case 'startBenchmark':
          expect(call.arguments['durationSeconds'], 60);
          benchmarkCalls++;
          if (failBenchmark) throw PlatformException(code: 'BUSY');
          return '11111111-1111-4111-8111-111111111111';
        default:
          return null;
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
  });
  Future<void> open(
    WidgetTester tester, {
    int? benchmarkDurationSeconds,
  }) async {
    await tester.binding.setSurfaceSize(const Size(800, 1000));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(
      MaterialApp(
        theme: KumpasTheme.light(),
        home: PracticeScreen(
          sign: const Sign(id: 0, label: 'ONE', category: 'Numbers'),
          benchmarkDurationSeconds: benchmarkDurationSeconds,
        ),
      ),
    );
    await tester.pump();
  }

  Future<void> event(WidgetTester tester, Map<String, dynamic> value) async {
    tester.binding.defaultBinaryMessenger.handlePlatformMessage(
      'kumpas/predictions',
      const StandardMethodCodec().encodeSuccessEnvelope(jsonEncode(value)),
      (_) {},
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));
  }

  Map<String, dynamic> result({
    bool recognized = true,
    String id = 'attempt-1',
  }) => {
    'state': 'attempt_result',
    'attemptId': id,
    'targetClass': 0,
    'targetLabel': 'ONE',
    'predictedLabel': recognized ? 'ONE' : 'TWO',
    'predictedConfidence': .9,
    'recognizedAsTarget': recognized,
    'overallMatch': .9,
    'items': [],
  };
  testWidgets('cancelled and unsolicited results cannot open feedback', (
    tester,
  ) async {
    await open(tester);
    await tester.tap(find.text('Subukan ang Senyas'));
    await tester.pump();
    await tester.tap(find.text('Kanselahin'));
    await tester.pump();
    await event(tester, result());
    expect(find.byType(FeedbackSheet), findsNothing);
    expect(cancelCalls, greaterThan(0));
    await tester.pumpWidget(const SizedBox());
  });
  testWidgets('start errors restore retry without unhandled future', (
    tester,
  ) async {
    await open(tester);
    failStart = true;
    await tester.tap(find.text('Subukan ang Senyas'));
    await tester.pump();
    expect(tester.takeException(), isNull);
    expect(find.text('Subukan ang Senyas'), findsOneWidget);
    expect(find.textContaining('Camera unavailable'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
  });
  testWidgets(
    'matching result opens feedback once and preserves wrong recognition',
    (tester) async {
      await open(tester);
      await tester.tap(find.text('Subukan ang Senyas'));
      await tester.pump();
      await event(tester, result(recognized: false));
      expect(find.byType(FeedbackSheet), findsOneWidget);
      expect(find.textContaining('recognized as TWO'), findsOneWidget);
      await event(tester, result(recognized: false));
      expect(find.byType(FeedbackSheet), findsOneWidget);
      expect(presentedCalls, 1);
      await tester.pumpWidget(const SizedBox());
    },
  );
  testWidgets('no signer failure allows retry and rejects a late result', (
    tester,
  ) async {
    await open(tester);
    await tester.tap(find.text('Subukan ang Senyas'));
    await tester.pump();
    await event(tester, {
      'state': 'attempt_failed',
      'attemptId': 'attempt-1',
      'reason': 'No signer detected',
    });
    expect(find.text('Subukan ang Senyas'), findsOneWidget);
    await event(tester, result());
    expect(find.byType(FeedbackSheet), findsNothing);
    await tester.pumpWidget(const SizedBox());
  });
  testWidgets(
    'benchmark starts after bounded warmup without any camera events',
    (tester) async {
      await open(tester, benchmarkDurationSeconds: 60);
      expect(benchmarkCalls, 0);
      await tester.pump(const Duration(seconds: 4));
      expect(benchmarkCalls, 1);
      await event(tester, {'state': 'no_signer'});
      expect(benchmarkCalls, 1);
      await tester.pumpWidget(const SizedBox());
    },
  );
  testWidgets('benchmark run identity is visible copyable and completion correlated', (tester) async {
    String? clipboard;
    tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(SystemChannels.platform, (call) async {
      if (call.method == 'Clipboard.setData') clipboard = call.arguments['text'] as String;
      return null;
    });
    await open(tester, benchmarkDurationSeconds: 60);
    await tester.pump(const Duration(seconds: 4));
    await tester.pump();
    expect(find.textContaining('11111111-1111-4111-8111-111111111111'), findsOneWidget);
    await tester.pump(const Duration(milliseconds: 500));
    await tester.tap(find.text('Copy ID'));
    await tester.pump();
    expect(clipboard, '11111111-1111-4111-8111-111111111111');
    await event(tester, {'state': 'benchmark_complete', 'results': {'run_id': 'stale'}});
    expect(find.textContaining('Benchmark complete:'), findsNothing);
    await event(tester, {'state': 'benchmark_complete', 'results': {'run_id': '11111111-1111-4111-8111-111111111111'}});
    await tester.pump(const Duration(seconds: 5));
    expect(find.textContaining('Benchmark complete: 11111111-1111-4111-8111-111111111111'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
  });
  test('benchmark channel requires valid UUID and binds report and stop', () async {
    var returned = '';
    final calls = <MethodCall>[];
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(KumpasChannel.control, (call) async {
      calls.add(call);
      if (call.method == 'startBenchmark') return returned;
      return '{}';
    });
    await expectLater(KumpasChannel.startBenchmark(), throwsStateError);
    returned = '11111111-1111-4111-8111-111111111111';
    final id = await KumpasChannel.startBenchmark();
    await KumpasChannel.stopBenchmark(runId: id);
    await KumpasChannel.getBenchmarkReport(runId: id);
    expect(calls.last.arguments['runId'], id);
    expect(calls[calls.length - 2].arguments['runId'], id);
  });
  testWidgets('failed benchmark can retry on existing snackbar', (tester) async {
    failBenchmark = true;
    await open(tester, benchmarkDurationSeconds: 60);
    await tester.pump(const Duration(seconds: 4));
    await tester.pump();
    expect(benchmarkCalls, 1);
    failBenchmark = false;
    await tester.pump(const Duration(milliseconds: 500));
    expect(find.text('Retry'), findsOneWidget);
    await tester.tap(find.text('Retry'));
    await tester.pump();
    expect(benchmarkCalls, 2);
    await tester.pumpWidget(const SizedBox());
  });
  testWidgets('pending start times out and late identity cannot cancel replacement', (tester) async {
    await open(tester);
    final old = pendingStart = Completer<String>();
    await tester.tap(find.text('Subukan ang Senyas'));
    await tester.pump();
    await tester.pump(const Duration(seconds: 31));
    expect(find.text('Subukan ang Senyas'), findsOneWidget);
    pendingStart = null;
    await tester.tap(find.text('Subukan ang Senyas'));
    await tester.pump();
    old.complete('late-old');
    await tester.pump();
    expect(cancelledIds, ['late-old']);
    await event(tester, result());
    expect(find.byType(FeedbackSheet), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
  });
  testWidgets('timeout cancels identity and restores capture' , (tester) async {
    await open(tester);
    await tester.tap(find.text('Subukan ang Senyas'));
    await tester.pump();
    await tester.pump(const Duration(seconds: 31));
    await tester.pump();
    expect(find.text('Subukan ang Senyas'), findsOneWidget);
    expect(cancelCalls, 1);
    expect(cancelOutcomes, ['timeout']);
    await event(tester, result());
    expect(find.byType(FeedbackSheet), findsNothing);
    await tester.pumpWidget(const SizedBox());
  });
}
