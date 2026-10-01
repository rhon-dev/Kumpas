import 'dart:convert';
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
  var cancelCalls = 0;
  var presentedCalls = 0;
  var sequence = 0;
  setUp(() {
    failStart = false;
    cancelCalls = 0;
    presentedCalls = 0;
    sequence = 0;
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
          return 'attempt-${++sequence}';
        case 'cancelAttempt':
          cancelCalls++;
          return null;
        case 'feedbackPresented':
          presentedCalls++;
          return null;
        case 'startSession':
          return 'synthetic-session';
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
  Future<void> open(WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 1000));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(
      MaterialApp(
        theme: KumpasTheme.light(),
        home: const PracticeScreen(
          sign: Sign(id: 0, label: 'ONE', category: 'Numbers'),
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
}
