import 'package:flutter_test/flutter_test.dart';

import 'package:kumpas_app/main.dart';

void main() {
  testWidgets('recognition screen builds', (WidgetTester tester) async {
    await tester.pumpWidget(const KumpasApp());
    // Platform view + event channel are Android-only; in the test env we just
    // assert the widget tree builds and shows the warm-up state.
    expect(find.textContaining('Warming up'), findsOneWidget);
  });
}
