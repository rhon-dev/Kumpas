import 'package:flutter_test/flutter_test.dart';

import 'package:kumpas_app/main.dart';

void main() {
  testWidgets('app shell builds with library screen', (WidgetTester tester) async {
    await tester.pumpWidget(const KumpasApp());
    // Native channels are absent in the test env; the library screen shows
    // its loading state. We only assert the shell builds.
    expect(find.text('KUMPAS'), findsOneWidget);
  });
}
