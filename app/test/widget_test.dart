import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:kumpas_app/main.dart';

void main() {
  testWidgets('app shell builds the approved five-tab navigation', (
    WidgetTester tester,
  ) async {
    tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
      const MethodChannel('kumpas/control'),
      (call) async {
        if (call.method == 'getLabels') return '{}';
        if (call.method == 'getHistory') return '[]';
        return null;
      },
    );
    await tester.pumpWidget(const KumpasApp());
    await tester.pumpAndSettle();
    expect(find.byType(NavigationDestination), findsNWidgets(5));
    for (final label in [
      'Home',
      'Isalin',
      'Diksyunaryo',
      'Mag-aral',
      'Profile',
    ]) {
      expect(find.text(label), findsWidgets);
    }
    expect(tester.takeException(), isNull);
  });
}
