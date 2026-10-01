import 'package:flutter_test/flutter_test.dart';
import 'package:kumpas_app/feedback_engine/models.dart';
import 'package:kumpas_app/ui/stats.dart';

AttemptResult attempt(double score, bool recognized, {int target = 0}) =>
    AttemptResult(
      targetClass: target,
      targetLabel: 'ONE',
      predictedLabel: recognized ? 'ONE' : 'TWO',
      predictedConfidence: .9,
      recognizedAsTarget: recognized,
      overallMatch: score,
      items: const [],
    );

void main() {
  const signs = [
    Sign(id: 0, label: 'ONE', category: 'Numbers'),
    Sign(id: 1, label: 'TWO', category: 'Numbers'),
  ];
  test('high geometric match with wrong recognition is not mastery', () {
    final history = [attempt(.99, false)];
    expect(LearnerStats.fromHistory(history).signsMastered, 0);
    expect(LearnerStats.categoryProgress(history, signs, 'Numbers'), (0, 2));
  });
  test('both conditions must occur on the same attempt', () {
    expect(
      LearnerStats.fromHistory([
        attempt(.99, false),
        attempt(.79, true),
      ]).signsMastered,
      0,
    );
  });
  test('exact threshold qualifies once; later failure does not revoke', () {
    final history = [attempt(.8, true), attempt(.95, true), attempt(.1, false)];
    expect(LearnerStats.fromHistory(history).signsMastered, 1);
    expect(LearnerStats.categoryProgress(history, signs, 'Numbers'), (1, 2));
  });
  test(
    'next sign and category use the same predicate including empty history',
    () {
      expect(nextPracticeSign(signs, [attempt(.99, false)])!.id, 0);
      expect(nextPracticeSign(signs, [attempt(.8, true)])!.id, 1);
      expect(nextPracticeSign(signs, [])!.id, 0);
      expect(nextPracticeSign([], []), isNull);
      final complete = [attempt(.8, true), attempt(.8, true, target: 1)];
      expect(LearnerStats.categoryProgress(complete, signs, 'Numbers'), (2, 2));
      expect(nextPracticeSign(signs, complete)!.id, 0);
    },
  );
}
