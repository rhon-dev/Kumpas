import 'package:flutter/material.dart';

import '../feedback_engine/models.dart';
import 'theme.dart';

/// Displays one attempt's corrective feedback: animated match gauge,
/// recognition result, and per-dimension prompts (worst first).
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
    final scheme = Theme.of(context).colorScheme;
    final colors = KumpasColors.of(context);
    final reduceMotion = MediaQuery.of(context).disableAnimations;
    final good = result.overallMatch >= 0.8;
    final statusColor = good ? colors.success : colors.warn;

    return SafeArea(
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxHeight: MediaQuery.of(context).size.height * 0.75,
        ),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 8, 24, 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  _MatchGauge(
                    match: result.overallMatch,
                    color: statusColor,
                    reduceMotion: reduceMotion,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(result.targetLabel,
                            style: Theme.of(context)
                                .textTheme
                                .headlineSmall
                                ?.copyWith(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Icon(
                              result.recognizedAsTarget
                                  ? Icons.check_circle
                                  : Icons.swap_horiz,
                              size: 16,
                              color: result.recognizedAsTarget
                                  ? colors.success
                                  : scheme.onSurfaceVariant,
                            ),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                'recognized as ${result.predictedLabel} '
                                '(${(result.predictedConfidence * 100).toStringAsFixed(0)}%)',
                                style: Theme.of(context)
                                    .textTheme
                                    .bodySmall
                                    ?.copyWith(
                                        color: scheme.onSurfaceVariant),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (result.items.isEmpty)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: Row(
                    children: [
                      Icon(Icons.celebration, color: colors.success),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Great! Your sign matches the model.',
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ),
                    ],
                  ),
                )
              else
                Flexible(
                  child: SingleChildScrollView(
                    child: Column(
                      children: result.items
                          .map((it) => _FeedbackTile(
                                item: it,
                                icon: _dimensionIcons[it.dimension] ??
                                    Icons.info_outline,
                              ))
                          .toList(),
                    ),
                  ),
                ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  icon: const Icon(Icons.replay),
                  label: const Text('Try again'),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Circular gauge that fills to the overall match percentage.
class _MatchGauge extends StatelessWidget {
  final double match;
  final Color color;
  final bool reduceMotion;

  const _MatchGauge({
    required this.match,
    required this.color,
    required this.reduceMotion,
  });

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return SizedBox(
      width: 72,
      height: 72,
      child: TweenAnimationBuilder<double>(
        tween: Tween(begin: 0, end: match),
        duration: reduceMotion ? Duration.zero : KumpasMotion.gauge,
        curve: Curves.easeOutCubic,
        builder: (context, value, _) => Stack(
          fit: StackFit.expand,
          children: [
            CircularProgressIndicator(
              value: value,
              strokeWidth: 7,
              strokeCap: StrokeCap.round,
              color: color,
              backgroundColor: scheme.surfaceContainerHighest,
            ),
            Center(
              child: Text(
                '${(value * 100).toStringAsFixed(0)}%',
                style: Theme.of(context)
                    .textTheme
                    .titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// One corrective prompt: tinted dimension icon, prompt text, severity bar.
class _FeedbackTile extends StatelessWidget {
  final FeedbackItem item;
  final IconData icon;

  const _FeedbackTile({required this.item, required this.icon});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final warn = KumpasColors.of(context).warn;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: scheme.primaryContainer,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, size: 22, color: scheme.onPrimaryContainer),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.prompt,
                    style: Theme.of(context).textTheme.bodyLarge),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Expanded(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(2),
                        child: LinearProgressIndicator(
                          value: item.severity,
                          minHeight: 4,
                          color: warn,
                          backgroundColor: scheme.surfaceContainerHighest,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '${item.dimension} · ${item.hand}',
                      style: Theme.of(context)
                          .textTheme
                          .labelSmall
                          ?.copyWith(color: scheme.onSurfaceVariant),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
