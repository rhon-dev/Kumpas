import 'package:flutter/material.dart';

import '../feedback_engine/kumpas_channel.dart';
import '../feedback_engine/models.dart';
import 'practice_screen.dart';
import 'stats.dart';
import 'theme.dart';
import 'widgets.dart';

/// Home tab (Figma: Home.png) — streak/sign/achievement chips on a gradient
/// header, daily goal, quick actions, today's lesson. All numbers computed
/// from the local attempt history.
class HomeScreen extends StatefulWidget {
  /// Switches the shell tab (1 = Isalin, 2 = Diksyunaryo).
  final ValueChanged<int> onQuickAction;

  const HomeScreen({super.key, required this.onQuickAction});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late Future<(LearnerStats, List<Sign>)> _data;

  @override
  void initState() {
    super.initState();
    _data = _load();
  }

  Future<(LearnerStats, List<Sign>)> _load() async {
    final history = await KumpasChannel.getHistory();
    final signs = await KumpasChannel.getSigns();
    return (LearnerStats.fromHistory(history), signs);
  }

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final scheme = Theme.of(context).colorScheme;
    return FutureBuilder<(LearnerStats, List<Sign>)>(
      future: _data,
      builder: (context, snap) {
        if (!snap.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final (stats, signs) = snap.data!;
        const dailyGoal = 50;
        final firstCategory = signs.isEmpty ? null : signs.first.category;
        return ListView(
          padding: EdgeInsets.zero,
          children: [
            GradientHeader(
              title: 'Kumpas',
              subtitle: 'Maligayang pagbabalik!',
              trailing: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.18),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Kasalukuyang Wika',
                        style: TextStyle(color: Colors.white70, fontSize: 10)),
                    Text('FSL',
                        style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 14)),
                  ],
                ),
              ),
              bottom: Row(
                children: [
                  Expanded(
                    child: StatCard(
                        icon: Icons.local_fire_department,
                        iconColor: colors.accent,
                        value: '${stats.streakDays}',
                        label: 'Araw'),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: StatCard(
                        icon: Icons.sign_language,
                        iconColor: colors.success,
                        value: '${stats.signsTried}',
                        label: 'Senyas'),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: StatCard(
                        icon: Icons.emoji_events,
                        iconColor: colors.accent,
                        value: '${stats.signsMastered}',
                        label: 'Nakamit'),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SectionCard(
                    child: Row(
                      children: [
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: colors.greenTint,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(Icons.bolt, color: colors.success),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: LabeledProgress(
                            label: 'Pang-araw-araw na Layunin',
                            trailing:
                                '${(stats.attemptsToday / dailyGoal * 100).round()}%',
                            value: stats.attemptsToday / dailyGoal,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text('Mabilis na Aksyon',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _QuickAction(
                          icon: Icons.videocam,
                          label: 'Magsimulang Magsalin',
                          onTap: () => widget.onQuickAction(1),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _QuickAction(
                          icon: Icons.menu_book,
                          label: 'Magsanay ng Senyas',
                          onTap: () => widget.onQuickAction(2),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  SectionCard(
                    color: colors.amberTint,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                color: colors.accent,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Icon(Icons.schedule,
                                  color: Colors.white),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('Aralin para Ngayong Araw',
                                      style: Theme.of(context)
                                          .textTheme
                                          .titleSmall
                                          ?.copyWith(
                                              fontWeight: FontWeight.bold)),
                                  Text(
                                      'Matutunan ang mga pangunahing pagbati at pagpapakilala',
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodySmall
                                          ?.copyWith(
                                              color:
                                                  scheme.onSurfaceVariant)),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        FilledButton(
                          style: FilledButton.styleFrom(
                              backgroundColor: colors.accent),
                          onPressed: firstCategory == null
                              ? null
                              : () => _startLesson(signs, firstCategory),
                          child: const Text('Simulan ang Aralin'),
                        ),
                      ],
                    ),
                  ),
                  if (stats.recent.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    SectionCard(
                      color: colors.greenTint,
                      child: Row(
                        children: [
                          Icon(Icons.celebration, color: colors.success),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Nakamit ang Tagumpay! Huling senyas: '
                              '${stats.recent.first.targetLabel} '
                              '(${(stats.recent.first.overallMatch * 100).round()}%)',
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  void _startLesson(List<Sign> signs, String category) {
    final first = signs.firstWhere((s) => s.category == category);
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => PracticeScreen(sign: first)),
    ).then((_) => setState(() => _data = _load()));
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _QuickAction(
      {required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    return Material(
      color: colors.success,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: Colors.white),
              ),
              const SizedBox(height: 10),
              Text(label,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                      color: Colors.white, fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      ),
    );
  }
}
