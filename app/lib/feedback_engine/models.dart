/// Dart-side models for the native pipeline's events and the gesture library.
/// The comparison math lives in Kotlin (FeedbackEngine.kt) mirrored from the
/// Python reference — Flutter only displays results (PRD: Mobile Agent does
/// not modify feedback math).
library;

class Sign {
  final int id;
  final String label;
  final String category;

  const Sign({required this.id, required this.label, required this.category});

  factory Sign.fromLabelMapEntry(String key, Map<String, dynamic> v) =>
      Sign(id: int.parse(key), label: v['label'] as String, category: v['category'] as String);
}

class FeedbackItem {
  final String dimension;
  final double severity;
  final String hand;
  final String prompt;

  const FeedbackItem(
      {required this.dimension, required this.severity, required this.hand, required this.prompt});

  factory FeedbackItem.fromJson(Map<String, dynamic> m) => FeedbackItem(
        dimension: m['dimension'] as String,
        severity: (m['severity'] as num).toDouble(),
        hand: m['hand'] as String,
        prompt: m['prompt'] as String,
      );
}

class AttemptResult {
  final int targetClass;
  final String targetLabel;
  final String predictedLabel;
  final double predictedConfidence;
  final bool recognizedAsTarget;
  final double overallMatch;
  final List<FeedbackItem> items;
  final DateTime? timestamp;

  const AttemptResult({
    required this.targetClass,
    required this.targetLabel,
    required this.predictedLabel,
    required this.predictedConfidence,
    required this.recognizedAsTarget,
    required this.overallMatch,
    required this.items,
    this.timestamp,
  });

  factory AttemptResult.fromJson(Map<String, dynamic> m) => AttemptResult(
        targetClass: m['targetClass'] as int,
        targetLabel: m['targetLabel'] as String,
        predictedLabel: m['predictedLabel'] as String,
        predictedConfidence: (m['predictedConfidence'] as num).toDouble(),
        recognizedAsTarget: m['recognizedAsTarget'] as bool,
        overallMatch: (m['overallMatch'] as num).toDouble(),
        items: (m['items'] as List<dynamic>)
            .map((e) => FeedbackItem.fromJson(e as Map<String, dynamic>))
            .toList(),
        timestamp: m['timestamp'] != null
            ? DateTime.fromMillisecondsSinceEpoch(m['timestamp'] as int)
            : null,
      );
}
