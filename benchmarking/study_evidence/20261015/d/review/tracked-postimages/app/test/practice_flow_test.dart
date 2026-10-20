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
  var returnedBenchmarkId = '11111111-1111-4111-8111-111111111111';
  var failBenchmark = false;
  var failStop = false;
  Completer<String>? pendingBenchmark;
  final stoppedRuns = <String>[];
  final confirmedRuns = <String>[];
  Completer<String>? pendingStop;
  Completer<bool>? pendingConfirmation;
  setUp(() {
    failStart = false;
    pendingStart = null;
    cancelledIds.clear();
    cancelOutcomes.clear();
    cancelCalls = 0;
    presentedCalls = 0;
    sequence = 0;
    benchmarkCalls = 0;
    returnedBenchmarkId = '11111111-1111-4111-8111-111111111111';
    failBenchmark = false;
    failStop = false;
    pendingBenchmark = null;
    stoppedRuns.clear();
    confirmedRuns.clear();
    pendingStop = null;
    pendingConfirmation = null;
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
          if (pendingBenchmark != null) return pendingBenchmark!.future;
          return returnedBenchmarkId;
        case 'confirmBenchmarkStart':
          confirmedRuns.add(call.arguments['runId'] as String);
          if (pendingConfirmation != null) return pendingConfirmation!.future;
          return true;
        case 'stopBenchmark':
          stoppedRuns.add(call.arguments['runId'] as String);
          if (pendingStop != null) return pendingStop!.future;
          if (failStop) throw PlatformException(code: 'STOP_FAILED');
          return '{"complete":false}';
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
  for (final lateError in [false, true]) {
    testWidgets('owned completion while confirmation pending preserves replacement lateError=$lateError', (tester) async {
      final old = pendingConfirmation = Completer<bool>();
      await open(tester, benchmarkDurationSeconds: 60);
      await tester.pump(const Duration(seconds: 3));
      await tester.pump();
      const a = '11111111-1111-4111-8111-111111111111';
      await event(tester, {'state': 'benchmark_complete', 'results': {'run_id': a}});
      expect(find.textContaining('Benchmark complete'), findsOneWidget);
      expect(find.textContaining('confirmation pending'), findsOneWidget);
      await tester.pump(const Duration(milliseconds: 29499));
      expect(find.textContaining('confirmation uncertain'), findsNothing);
      await tester.pump(const Duration(milliseconds: 1));
      expect(find.textContaining('confirmation uncertain'), findsOneWidget);
      expect(find.textContaining('Benchmark complete'), findsOneWidget);
      await tester.pumpWidget(const MaterialApp(home: SizedBox()));
      pendingConfirmation = null;
      returnedBenchmarkId = '22222222-2222-4222-8222-222222222222';
      await open(tester, benchmarkDurationSeconds: 60);
      await tester.pump(const Duration(seconds: 3));
      await tester.pump();
      if (lateError) {
        old.completeError(PlatformException(code: 'CONTROL_FAILED', message: 'PRIVATE_patient_text'));
      } else {
        old.complete(true);
      }
      await tester.pump();
      expect(find.textContaining('Benchmark running: 22222222'), findsOneWidget);
      expect(find.textContaining(a), findsNothing);
      expect(stoppedRuns, isEmpty);
      expect(benchmarkCalls, 2);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const MaterialApp(home: SizedBox()));
    });
  }
  for (final response in ['pending', 'error', 'false', 'lateSuccess', 'lateError', 'dispose']) {
    testWidgets('receipt ownership survives uncertain confirmation $response', (tester) async {
      final start = Completer<String>();
      final confirmation = Completer<bool>();
      pendingBenchmark = start;
      pendingConfirmation = confirmation;
      await open(tester, benchmarkDurationSeconds: 60);
      await tester.pump(const Duration(seconds: 3));
      await tester.pump(const Duration(milliseconds: 29999));
      const id = '11111111-1111-4111-8111-111111111111';
      start.complete(id);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 500));
      expect(find.textContaining(id), findsOneWidget);
      expect(find.text('Copy ID'), findsOneWidget);
      expect(find.text('Retry'), findsNothing);
      expect(confirmedRuns, [id]);
      if (response == 'error') confirmation.completeError(PlatformException(code: 'CONTROL_FAILED', message: 'PRIVATE_patient_text'));
      if (response == 'false') confirmation.complete(false);
      if (response == 'dispose') {
        await tester.pumpWidget(const MaterialApp(home: SizedBox()));
        confirmation.completeError(PlatformException(code: 'CONTROL_FAILED', message: 'PRIVATE_patient_text'));
        await tester.pump();
        expect(stoppedRuns, isEmpty);
        expect(tester.takeException(), isNull);
        return;
      }
      await tester.pump(const Duration(seconds: 30));
      await tester.pump(const Duration(milliseconds: 500));
      expect(find.textContaining('Benchmark could not start'), findsNothing);
      expect(find.textContaining('PRIVATE_patient_text'), findsNothing);
      expect(find.textContaining(id), findsOneWidget);
      expect(find.text('Retry'), findsNothing);
      await event(tester, {'state': 'benchmark_complete', 'results': {'run_id': id}});
      await tester.pump(const Duration(seconds: 1));
      expect(find.textContaining('Benchmark complete'), findsOneWidget);
      if (response == 'lateSuccess') confirmation.complete(true);
      if (response == 'lateError') confirmation.completeError(PlatformException(code: 'CONTROL_FAILED', message: 'PRIVATE_patient_text'));
      await tester.pump();
      await event(tester, {'state': 'prediction', 'label': 'ONE'});
      expect(benchmarkCalls, 1);
      expect(stoppedRuns, isEmpty);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const MaterialApp(home: SizedBox()));
    });
  }

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
  testWidgets('hung benchmark control response recovers and late run cannot stop replacement', (tester) async {
    final old = pendingBenchmark = Completer<String>();
    await open(tester, benchmarkDurationSeconds: 60);
    await tester.pump(const Duration(seconds: 4));
    await tester.pump(const Duration(seconds: 31));
    await tester.pump(const Duration(milliseconds: 500));
    expect(find.text('Retry'), findsOneWidget);
    pendingBenchmark = null;
    await tester.tap(find.text('Retry'));
    await tester.pump();
    expect(benchmarkCalls, 2);
    expect(confirmedRuns, ['11111111-1111-4111-8111-111111111111']);
    old.complete('22222222-2222-4222-8222-222222222222');
    await tester.pump();
    expect(stoppedRuns, ['22222222-2222-4222-8222-222222222222']);
    await tester.pump(const Duration(milliseconds: 500));
    expect(find.textContaining('Benchmark running: 11111111'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox());
  });
  for (final disposed in [false, true]) {
    for (final completion in ['pending', 'success', 'error']) {
      testWidgets('hung late stop deadline disposed=$disposed completion=$completion', (tester) async {
        final messages = <String?>[];
        final priorPrint = debugPrint;
        debugPrint = (String? message, {int? wrapWidth}) => messages.add(message);
        try {
          final old = pendingBenchmark = Completer<String>();
          final stop = pendingStop = Completer<String>();
          await open(tester, benchmarkDurationSeconds: 60);
          await tester.pump(const Duration(seconds: 4));
          await tester.pump(const Duration(seconds: 31));
          await tester.pump(const Duration(milliseconds: 500));
          if (disposed) {
            await tester.pumpWidget(const SizedBox());
          } else {
            pendingBenchmark = null;
            await tester.tap(find.text('Retry'));
            await tester.pump();
          }
          old.complete('22222222-2222-4222-8222-222222222222');
          await tester.pump();
          expect(stoppedRuns, ['22222222-2222-4222-8222-222222222222']);
          await tester.pump(const Duration(milliseconds: 29999));
          expect(messages, isEmpty);
          await tester.pump(const Duration(milliseconds: 1));
          expect(messages.where((m) => m?.contains('Late run cleanup failed') == true), hasLength(1));
          await tester.pump(const Duration(milliseconds: 1));
          if (completion == 'success') stop.complete('{"complete":true}');
          if (completion == 'error') stop.completeError(PlatformException(code: 'PRIVATE_ERROR', message: 'PRIVATE patient text'));
          await tester.pump();
          expect(messages.where((m) => m?.contains('Late run cleanup failed') == true), hasLength(1));
          expect(messages.join(), isNot(contains('PRIVATE')));
          expect(tester.takeException(), isNull);
          expect(stoppedRuns, ['22222222-2222-4222-8222-222222222222']);
          if (!disposed) {
            await tester.pump(const Duration(milliseconds: 500));
            expect(find.textContaining('Benchmark running: 11111111'), findsOneWidget);
          }
          await tester.pumpWidget(const SizedBox());
        } finally { debugPrint = priorPrint; }
      });
    }
  }
  testWidgets('late benchmark cleanup failure after disposal retains coded diagnostics' , (tester) async {
    final messages = <String?>[];
    final priorPrint = debugPrint;
    debugPrint = (String? message, {int? wrapWidth}) => messages.add(message);
    try {
      pendingBenchmark = Completer<String>();
      failStop = true;
      await open(tester, benchmarkDurationSeconds: 60);
      await tester.pump(const Duration(seconds: 4));
      await tester.pumpWidget(const SizedBox());
      pendingBenchmark!.complete('22222222-2222-4222-8222-222222222222');
      await tester.pump();
      expect(stoppedRuns, ['22222222-2222-4222-8222-222222222222']);
      expect(messages.any((message) => message?.contains('Late run cleanup failed') == true), isTrue);
      expect(tester.takeException(), isNull);
    } finally {
      // Binding invariants run before addTearDown callbacks.
      debugPrint = priorPrint;
    }
  });

  testWidgets('late benchmark identity after disposal is stopped by its own run ID', (tester) async {
    final old = pendingBenchmark = Completer<String>();
    await open(tester, benchmarkDurationSeconds: 60);
    await tester.pump(const Duration(seconds: 4));
    await tester.pumpWidget(const SizedBox());
    old.complete('22222222-2222-4222-8222-222222222222');
    await tester.pump();
    expect(stoppedRuns, ['22222222-2222-4222-8222-222222222222']);
    expect(tester.takeException(), isNull);
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
    expect(cancelOutcomes, ['timeout']);
    await event(tester, result());
    expect(find.byType(FeedbackSheet), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
  });
  testWidgets('pending identity preserves timeout without replacement and cancel on disposal', (tester) async {
    for (final terminal in ['timeout', 'cancelled', 'dispose']) {
      await open(tester);
      final old = pendingStart = Completer<String>();
      await tester.tap(find.text('Subukan ang Senyas'));
      await tester.pump();
      if (terminal == 'timeout') {
        await tester.pump(const Duration(seconds: 31));
      } else if (terminal == 'cancelled') {
        await tester.tap(find.text('Kanselahin'));
        await tester.pump();
      } else {
        await tester.pumpWidget(const SizedBox());
      }
      old.complete('old-$terminal');
      await tester.pump();
      expect(cancelledIds.last, 'old-$terminal');
      expect(cancelOutcomes.last, terminal == 'timeout' ? 'timeout' : 'cancelled');
      pendingStart = null;
      await tester.pumpWidget(const SizedBox());
    }
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
