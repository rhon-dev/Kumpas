import '../feedback_engine/models.dart';

/// Both conditions must hold on the same attempt; XP remains score-based.
bool isMasteryAttempt(AttemptResult attempt) =>
    attempt.overallMatch >= 0.8 && attempt.recognizedAsTarget;

Sign? nextPracticeSign(List<Sign> signs, List<AttemptResult> history) {
  if (signs.isEmpty) return null;
  return signs.firstWhere(
    (sign) => !history.any(
      (attempt) => attempt.targetClass == sign.id && isMasteryAttempt(attempt),
    ),
    orElse: () => signs.first,
  );
}

/// Learner stats derived from local attempt history. All values are computed
/// from real attempts — no fake numbers; screens show zeros on first run.
class LearnerStats {
  final int totalAttempts;
  final int signsTried; // distinct target signs attempted
  final int signsMastered; // distinct targets with a qualifying mastery attempt
  final int streakDays; // consecutive practice days ending today
  final int attemptsToday;
  final double avgMatch; // 0..1 over all attempts
  final List<AttemptResult> recent; // newest first

  const LearnerStats({
    required this.totalAttempts,
    required this.signsTried,
    required this.signsMastered,
    required this.streakDays,
    required this.attemptsToday,
    required this.avgMatch,
    required this.recent,
  });

  /// Signs in [category] mastered / tried, given the full sign list.
  static (int mastered, int total) categoryProgress(
    List<AttemptResult> history,
    List<Sign> signs,
    String category,
  ) {
    final inCat = signs.where((s) => s.category == category).toList();
    final mastered = inCat
        .where(
          (s) =>
              history.any((a) => a.targetClass == s.id && isMasteryAttempt(a)),
        )
        .length;
    return (mastered, inCat.length);
  }

  factory LearnerStats.fromHistory(List<AttemptResult> history) {
    final sorted = [...history]
      ..sort(
        (a, b) => (b.timestamp ?? DateTime(2000)).compareTo(
          a.timestamp ?? DateTime(2000),
        ),
      );

    final tried = <int>{};
    final mastered = <int>{};
    final days = <DateTime>{};
    var matchSum = 0.0;
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    var attemptsToday = 0;

    for (final a in history) {
      tried.add(a.targetClass);
      if (isMasteryAttempt(a)) mastered.add(a.targetClass);
      matchSum += a.overallMatch;
      final t = a.timestamp;
      if (t != null) {
        final d = DateTime(t.year, t.month, t.day);
        days.add(d);
        if (d == today) attemptsToday++;
      }
    }

    var streak = 0;
    var cursor = today;
    while (days.contains(cursor)) {
      streak++;
      cursor = cursor.subtract(const Duration(days: 1));
    }

    return LearnerStats(
      totalAttempts: history.length,
      signsTried: tried.length,
      signsMastered: mastered.length,
      streakDays: streak,
      attemptsToday: attemptsToday,
      avgMatch: history.isEmpty ? 0 : matchSum / history.length,
      recent: sorted.take(10).toList(),
    );
  }
}
