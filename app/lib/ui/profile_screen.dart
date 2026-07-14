import 'package:flutter/material.dart';

import '../feedback_engine/kumpas_channel.dart';
import 'feedback_sheet.dart';
import 'stats.dart';
import 'theme.dart';
import 'widgets.dart';

/// Profile tab (Figma: Profile.png / P2 / P3) — local learner profile,
/// usage stats from attempt history, and settings. No accounts in the MVP:
/// name is a static placeholder, level = mastered signs.
class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen>
    with SingleTickerProviderStateMixin {
  late Future<(LearnerStats, int)> _data;
  late final TabController _tabs = TabController(length: 3, vsync: this);

  @override
  void initState() {
    super.initState();
    _data = _load();
  }

  Future<(LearnerStats, int)> _load() async {
    final history = await KumpasChannel.getHistory();
    final signs = await KumpasChannel.getSigns();
    return (LearnerStats.fromHistory(history), signs.length);
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    return FutureBuilder<(LearnerStats, int)>(
      future: _data,
      builder: (context, snap) {
        if (!snap.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final (stats, totalSigns) = snap.data!;
        return Column(
          children: [
            const GradientHeader(
              title: 'Profile',
              subtitle: 'Pamahalaan ang iyong account at settings',
            ),
            TabBar(
              controller: _tabs,
              labelColor: colors.success,
              indicatorColor: colors.success,
              tabs: const [
                Tab(text: 'Profile'),
                Tab(text: 'Estadistika'),
                Tab(text: 'Mga Setting'),
              ],
            ),
            Expanded(
              child: TabBarView(
                controller: _tabs,
                children: [
                  _ProfileTab(stats: stats, totalSigns: totalSigns),
                  _StatsTab(stats: stats),
                  const _SettingsTab(),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

class _ProfileTab extends StatelessWidget {
  final LearnerStats stats;
  final int totalSigns;

  const _ProfileTab({required this.stats, required this.totalSigns});

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final scheme = Theme.of(context).colorScheme;
    final level = 1 + stats.signsMastered ~/ 10;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        SectionCard(
          color: colors.greenTint,
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              CircleAvatar(
                radius: 40,
                backgroundColor: colors.success,
                child: const Text('KL',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold)),
              ),
              const SizedBox(height: 12),
              Text('KUMPAS Learner',
                  style: Theme.of(context)
                      .textTheme
                      .titleLarge
                      ?.copyWith(fontWeight: FontWeight.bold)),
              Text('Lokal na profile — walang account sa MVP',
                  style: Theme.of(context)
                      .textTheme
                      .bodySmall
                      ?.copyWith(color: scheme.onSurfaceVariant)),
              const SizedBox(height: 16),
              SectionCard(
                child: LabeledProgress(
                  label: 'Antas $level',
                  trailing: '${stats.signsMastered}/$totalSigns',
                  value:
                      totalSigns == 0 ? 0 : stats.signsMastered / totalSigns,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        SectionCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.workspace_premium, color: colors.purple),
                  const SizedBox(width: 8),
                  Text('Mga Kamakailang Tagumpay',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 12),
              _Achievement(
                icon: Icons.military_tech,
                tint: colors.amberTint,
                iconColor: colors.accent,
                title: 'Mandirigma ng Linggo',
                subtitle:
                    '${stats.streakDays}-araw na sunod-sunod na gawain',
              ),
              const SizedBox(height: 8),
              _Achievement(
                icon: Icons.school,
                tint: colors.greenTint,
                iconColor: colors.success,
                title: 'Mabilis na Mag-aaral',
                subtitle: '${stats.signsTried} senyas na nasubukan',
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _Achievement extends StatelessWidget {
  final IconData icon;
  final Color tint;
  final Color iconColor;
  final String title;
  final String subtitle;

  const _Achievement({
    required this.icon,
    required this.tint,
    required this.iconColor,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: tint,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: iconColor,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, size: 20, color: Colors.white),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: Theme.of(context)
                        .textTheme
                        .bodyMedium
                        ?.copyWith(fontWeight: FontWeight.w600)),
                Text(subtitle,
                    style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatsTab extends StatelessWidget {
  final LearnerStats stats;

  const _StatsTab({required this.stats});

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final scheme = Theme.of(context).colorScheme;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        SectionCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.bar_chart, color: colors.success),
                  const SizedBox(width: 8),
                  Text('Pangkalahatang Paggamit',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: StatCard(
                        icon: Icons.swap_horiz,
                        iconColor: colors.success,
                        value: '${stats.totalAttempts}',
                        label: 'Pagsasanay',
                        fill: colors.greenTint),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: StatCard(
                        icon: Icons.sign_language,
                        iconColor: colors.purple,
                        value: '${stats.signsMastered}',
                        label: 'Senyas na Natutunan',
                        fill: scheme.surfaceContainerLow),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: StatCard(
                        icon: Icons.local_fire_department,
                        iconColor: colors.success,
                        value: '${stats.streakDays}',
                        label: 'Sunod-sunod na Araw',
                        fill: colors.greenTint),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: StatCard(
                        icon: Icons.track_changes,
                        iconColor: colors.accent,
                        value: '${(stats.avgMatch * 100).round()}%',
                        label: 'Avg na Tugma',
                        fill: colors.amberTint),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        SectionCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Kamakailang Aktibidad',
                  style: Theme.of(context)
                      .textTheme
                      .titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              if (stats.recent.isEmpty)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: Text('Wala pang aktibidad — magsanay na!',
                      style: Theme.of(context)
                          .textTheme
                          .bodyMedium
                          ?.copyWith(color: scheme.onSurfaceVariant)),
                )
              else
                ...stats.recent.map((a) => ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: CircleAvatar(
                        backgroundColor: a.overallMatch >= 0.8
                            ? colors.greenTint
                            : colors.amberTint,
                        child: Text('${(a.overallMatch * 100).round()}',
                            style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: a.overallMatch >= 0.8
                                    ? colors.success
                                    : colors.warn)),
                      ),
                      title: Text(a.targetLabel),
                      subtitle: Text(a.recognizedAsTarget
                          ? 'nakilala'
                          : 'nabasa bilang ${a.predictedLabel}'),
                      trailing: Text(
                          '${a.items.length} tip${a.items.length == 1 ? '' : 's'}'),
                      onTap: () => showModalBottomSheet(
                        context: context,
                        isScrollControlled: true,
                        builder: (_) => FeedbackSheet(result: a),
                      ),
                    )),
            ],
          ),
        ),
      ],
    );
  }
}

class _SettingsTab extends StatefulWidget {
  const _SettingsTab();

  @override
  State<_SettingsTab> createState() => _SettingsTabState();
}

class _SettingsTabState extends State<_SettingsTab> {
  bool _notifications = true;
  bool _sounds = true;

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final scheme = Theme.of(context).colorScheme;
    final dark = KumpasTheme.themeMode.value == ThemeMode.dark;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        SectionCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.language, color: colors.success),
                  const SizedBox(width: 8),
                  Text('Mga Setting ng Wika',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 12),
              Text('Piniling Wikang Senyas',
                  style: Theme.of(context).textTheme.bodyMedium),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
                decoration: BoxDecoration(
                  color: scheme.surfaceContainerLow,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text('Filipino Sign Language (FSL)',
                    style: Theme.of(context).textTheme.bodyMedium),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        SectionCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.notifications_outlined, color: colors.purple),
                  const SizedBox(width: 8),
                  Text('Mga Notipikasyon',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold)),
                ],
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Push Notifications'),
                subtitle:
                    const Text('Makatanggap ng pang-araw-araw na paalala'),
                value: _notifications,
                onChanged: (v) => setState(() => _notifications = v),
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Mga Tunog'),
                subtitle: const Text('I-play ang tunog para sa mga aksyon'),
                value: _sounds,
                onChanged: (v) => setState(() => _sounds = v),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        SectionCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.dark_mode_outlined, color: colors.purple),
                  const SizedBox(width: 8),
                  Text('Hitsura',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold)),
                ],
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Dark Mode'),
                subtitle: const Text('Gumamit ng madilim na tema'),
                value: dark,
                onChanged: (v) => setState(() => KumpasTheme.themeMode.value =
                    v ? ThemeMode.dark : ThemeMode.light),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
