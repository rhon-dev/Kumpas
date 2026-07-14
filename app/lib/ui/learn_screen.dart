import 'package:flutter/material.dart';

import '../feedback_engine/kumpas_channel.dart';
import '../feedback_engine/models.dart';
import 'practice_screen.dart';
import 'stats.dart';
import 'theme.dart';
import 'widgets.dart';

/// Mag-aral tab (Figma: Learn.png / L2.png) — categories as lessons with
/// real per-category progress, plus challenges computed from history.
/// "XP" = 10 points per attempt ≥80% (documented stand-in; no backend).
class LearnScreen extends StatefulWidget {
  const LearnScreen({super.key});

  @override
  State<LearnScreen> createState() => _LearnScreenState();
}

class _LearnScreenState extends State<LearnScreen>
    with SingleTickerProviderStateMixin {
  late Future<(List<Sign>, List<AttemptResult>)> _data;
  late final TabController _tabs = TabController(length: 2, vsync: this);

  @override
  void initState() {
    super.initState();
    _data = _load();
  }

  Future<(List<Sign>, List<AttemptResult>)> _load() async =>
      (await KumpasChannel.getSigns(), await KumpasChannel.getHistory());

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  void _practice(Sign s) {
    Navigator.push(
            context, MaterialPageRoute(builder: (_) => PracticeScreen(sign: s)))
        .then((_) => setState(() => _data = _load()));
  }

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    return FutureBuilder<(List<Sign>, List<AttemptResult>)>(
      future: _data,
      builder: (context, snap) {
        if (!snap.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final (signs, history) = snap.data!;
        final stats = LearnerStats.fromHistory(history);
        final categories = {for (final s in signs) s.category}.toList();
        final done = categories.where((c) {
          final (m, t) = LearnerStats.categoryProgress(history, signs, c);
          return t > 0 && m == t;
        }).length;
        final xp = history.where((a) => a.overallMatch >= 0.8).length * 10;
        final accuracy =
            history.isEmpty ? 0 : (stats.avgMatch * 100).round();

        return Column(
          children: [
            GradientHeader(
              title: 'Sentro ng Pag-aaral',
              subtitle: 'FSL • $done/${categories.length} aralin na nakumpleto',
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
              child: Column(
                children: [
                  LabeledProgress(
                    label: 'Kabuuang Progreso',
                    trailing:
                        '${(stats.signsMastered / (signs.isEmpty ? 1 : signs.length) * 100).round()}%',
                    value: stats.signsMastered /
                        (signs.isEmpty ? 1 : signs.length),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: StatCard(
                            icon: Icons.star,
                            iconColor: colors.accent,
                            value: '$xp',
                            label: 'XP Points',
                            fill: Theme.of(context)
                                .colorScheme
                                .surfaceContainerLow),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: StatCard(
                            icon: Icons.emoji_events,
                            iconColor: colors.purple,
                            value:
                                '${stats.signsMastered}/${signs.length}',
                            label: 'Tagumpay',
                            fill: Theme.of(context)
                                .colorScheme
                                .surfaceContainerLow),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: StatCard(
                            icon: Icons.track_changes,
                            iconColor: colors.success,
                            value: '$accuracy%',
                            label: 'Katumpakan',
                            fill: Theme.of(context)
                                .colorScheme
                                .surfaceContainerLow),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            TabBar(
              controller: _tabs,
              labelColor: colors.success,
              indicatorColor: colors.success,
              tabs: const [Tab(text: 'Mga Aralin'), Tab(text: 'Mga Hamon')],
            ),
            Expanded(
              child: TabBarView(
                controller: _tabs,
                children: [
                  _LessonList(
                      signs: signs, history: history, onPractice: _practice),
                  _ChallengeList(stats: stats),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

class _LessonList extends StatelessWidget {
  final List<Sign> signs;
  final List<AttemptResult> history;
  final ValueChanged<Sign> onPractice;

  const _LessonList(
      {required this.signs, required this.history, required this.onPractice});

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final scheme = Theme.of(context).colorScheme;
    final categories = {for (final s in signs) s.category}.toList();
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: categories.length,
      separatorBuilder: (_, i) => const SizedBox(height: 12),
      itemBuilder: (context, i) {
        final cat = categories[i];
        final inCat = signs.where((s) => s.category == cat).toList();
        final (mastered, total) =
            LearnerStats.categoryProgress(history, signs, cat);
        final complete = total > 0 && mastered == total;
        final started = mastered > 0;
        final next = inCat.firstWhere(
          (s) => !history
              .any((a) => a.targetClass == s.id && a.overallMatch >= 0.8),
          orElse: () => inCat.first,
        );
        return SectionCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: colors.greenTint,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: complete
                        ? Icon(Icons.check_circle, color: colors.success)
                        : Center(
                            child: Text('${i + 1}',
                                style: TextStyle(
                                    color: colors.success,
                                    fontWeight: FontWeight.bold))),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(cat,
                                  style: Theme.of(context)
                                      .textTheme
                                      .titleMedium
                                      ?.copyWith(
                                          fontWeight: FontWeight.bold)),
                            ),
                            if (complete)
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: colors.greenTint,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text('Nakumpleto',
                                    style: TextStyle(
                                        fontSize: 11,
                                        color: colors.success,
                                        fontWeight: FontWeight.w600)),
                              ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text('$total senyas • $mastered nakamit',
                            style: Theme.of(context)
                                .textTheme
                                .bodySmall
                                ?.copyWith(color: scheme.onSurfaceVariant)),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (started && !complete) ...[
                ClipRRect(
                  borderRadius: BorderRadius.circular(3),
                  child: LinearProgressIndicator(
                    value: total == 0 ? 0 : mastered / total,
                    minHeight: 6,
                    color: colors.success,
                    backgroundColor: scheme.surfaceContainerHighest,
                  ),
                ),
                const SizedBox(height: 10),
              ],
              FilledButton.icon(
                style:
                    FilledButton.styleFrom(backgroundColor: colors.success),
                icon: const Icon(Icons.play_arrow, size: 20),
                label: Text(complete
                    ? 'Ulitin'
                    : started
                        ? 'Ituloy'
                        : 'Simulan'),
                onPressed: () => onPractice(next),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ChallengeList extends StatelessWidget {
  final LearnerStats stats;

  const _ChallengeList({required this.stats});

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final challenges = [
      (
        Icons.emoji_events,
        colors.success,
        'Daily Practice',
        'Magsanay ng 20 senyas ngayong araw',
        '50 XP',
        stats.attemptsToday,
        20,
      ),
      (
        Icons.emoji_events,
        colors.purple,
        'Week Warrior',
        'Magsanay ng 5 araw na sunod-sunod',
        '200 XP',
        stats.streakDays.clamp(0, 5),
        5,
      ),
      (
        Icons.emoji_events,
        colors.accent,
        'Perfect Score',
        'Makakuha ng 100% sa kahit anong senyas',
        '100 XP',
        stats.recent.any((a) => a.overallMatch >= 1.0) ? 1 : 0,
        1,
      ),
    ];
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: challenges.length,
      separatorBuilder: (_, i) => const SizedBox(height: 12),
      itemBuilder: (context, i) {
        final (icon, color, title, desc, xp, progress, goal) = challenges[i];
        return SectionCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(icon, size: 22, color: color),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(title,
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold)),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color:
                          Theme.of(context).colorScheme.surfaceContainerHigh,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(xp,
                        style: Theme.of(context)
                            .textTheme
                            .labelSmall
                            ?.copyWith(fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(desc, style: Theme.of(context).textTheme.bodyMedium),
              const SizedBox(height: 10),
              LabeledProgress(
                label: '',
                trailing: '$progress/$goal',
                value: goal == 0 ? 0 : progress / goal,
                color: color,
              ),
            ],
          ),
        );
      },
    );
  }
}
