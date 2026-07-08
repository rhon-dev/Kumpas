import 'package:flutter/material.dart';

import '../feedback_engine/models.dart';

/// Displays one attempt's corrective feedback: overall match, recognition
/// result, and per-dimension prompts (worst first).
class FeedbackSheet extends StatelessWidget {
  final AttemptResult result;

  const FeedbackSheet({super.key, required this.result});

  static const _dimensionIcons = {
    'timing': Icons.speed,
    'motion': Icons.open_with,
    'handshape': Icons.back_hand,
    'orientation': Icons.threesixty,
  };

  @override
  Widget build(BuildContext context) {
    final good = result.overallMatch >= 0.8;
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(good ? Icons.check_circle : Icons.tips_and_updates,
                    size: 40, color: good ? Colors.green : Colors.amber),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(result.targetLabel,
                          style: Theme.of(context)
                              .textTheme
                              .headlineSmall
                              ?.copyWith(fontWeight: FontWeight.bold)),
                      Text('match ${(result.overallMatch * 100).toStringAsFixed(0)}% · '
                          'recognized as ${result.predictedLabel} '
                          '(${(result.predictedConfidence * 100).toStringAsFixed(0)}%)'),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (result.items.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: Text('Great! Your sign matches the model. 🎉'),
              )
            else
              ...result.items.map((it) => ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: Icon(_dimensionIcons[it.dimension] ?? Icons.info),
                    title: Text(it.prompt),
                    subtitle: Text(
                        '${it.dimension} · ${it.hand} · severity ${(it.severity * 100).toStringAsFixed(0)}%'),
                  )),
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerRight,
              child: FilledButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Try again'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
