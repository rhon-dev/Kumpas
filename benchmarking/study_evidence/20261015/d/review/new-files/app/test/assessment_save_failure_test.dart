import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kumpas_app/ui/assessment_screen.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('post required responses submit with empty optional feedback', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1000, 4000));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    final saves = <MethodCall>[];
    final messenger = TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
    messenger.setMockMethodCallHandler(const MethodChannel('kumpas/control'), (call) async {
      if (call.method == 'saveAssessment') saves.add(call);
      return null;
    });
    addTearDown(() => messenger.setMockMethodCallHandler(const MethodChannel('kumpas/control'), null));
    await tester.pumpWidget(MaterialApp(home: Builder(builder: (context) => Scaffold(
      body: TextButton(onPressed: () => Navigator.of(context).push(MaterialPageRoute<void>(
        builder: (_) => const AssessmentScreen(isPost: true))), child: const Text('Open post')),
    ))));
    await tester.tap(find.text('Open post'));
    await tester.pumpAndSettle();
    expect(tester.widget<TextButton>(find.widgetWithText(TextButton, 'Susunod')).onPressed, isNull);
    await tester.tap(find.text('3').first);
    await tester.pump();
    expect(tester.widget<TextButton>(find.widgetWithText(TextButton, 'Susunod')).onPressed, isNull);
    await tester.tap(find.text('3').last);
    await tester.pump();
    await tester.tap(find.text('Susunod'));
    await tester.pumpAndSettle();
    expect(find.text('3'), findsNWidgets(10));
    for (var i = 0; i < 9; i++) {
      await tester.tap(find.text('3').at(i));
      await tester.pump();
    }
    expect(tester.widget<FilledButton>(find.widgetWithText(FilledButton, 'Ipon')).onPressed, isNull);
    await tester.tap(find.text('Ipon'));
    await tester.pump();
    expect(saves, isEmpty);
    await tester.tap(find.text('3').last);
    await tester.pump();
    expect(tester.widget<TextField>(find.byType(TextField)).controller!.text, isEmpty);
    expect(tester.widget<FilledButton>(find.widgetWithText(FilledButton, 'Ipon')).onPressed, isNotNull);
    await tester.tap(find.text('Ipon'));
    await tester.pumpAndSettle();
    expect(saves, hasLength(1));
    expect((saves.single.arguments as Map)['type'], 'post');
    final responses = jsonDecode((saves.single.arguments as Map)['responses'] as String) as Map;
    expect(responses['openFeedback'], '');
    expect(responses['fslConfidence'], 3);
    expect(responses['signsKnown'], 3);
    expect(responses['susScores'], List.filled(10, 3));
    expect(find.byType(AssessmentScreen), findsNothing);
  });
  testWidgets('assessment save failure stays on form and safe retry navigates', (tester) async {
    var failSave = true;
    var saves = 0;
    final messenger = TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
    messenger.setMockMethodCallHandler(const MethodChannel('kumpas/control'), (call) async {
      if (call.method == 'saveAssessment') {
        saves++;
        if (failSave) throw PlatformException(code: 'PERSISTENCE_FAILED');
      }
      return null;
    });
    addTearDown(() => messenger.setMockMethodCallHandler(const MethodChannel('kumpas/control'), null));
    await tester.pumpWidget(MaterialApp(home: Builder(builder: (context) => Scaffold(
      body: TextButton(onPressed: () => Navigator.of(context).push(MaterialPageRoute<void>(
        builder: (_) => const AssessmentScreen())), child: const Text('Open synthetic form')),
    ))));
    await tester.tap(find.text('Open synthetic form'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('3').first);
    await tester.tap(find.text('3').last);
    await tester.pump();
    await tester.tap(find.text('Ipon'));
    await tester.pumpAndSettle();
    expect(saves, 1);
    expect(find.byType(AssessmentScreen), findsOneWidget);
    expect(find.textContaining('Error saving assessment:'), findsOneWidget);
    expect(find.textContaining('Salamat sa pagkumpleto'), findsNothing);
    failSave = false;
    await tester.tap(find.text('Ipon'));
    await tester.pumpAndSettle();
    expect(saves, 2);
    expect(find.byType(AssessmentScreen), findsNothing);
  });
}
