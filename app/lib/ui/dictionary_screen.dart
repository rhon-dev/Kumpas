import 'package:flutter/material.dart';

import '../feedback_engine/kumpas_channel.dart';
import '../feedback_engine/models.dart';
import 'practice_screen.dart';
import 'theme.dart';

/// Diksyunaryo tab (Figma: Dictionary.png / D2 / D3) — searchable 50-sign
/// browser with category chips and favorites. Tap a card to practice.
/// Favorites are session-local (no backend in MVP); "Mga Parirala" shows
/// multi-word signs from the label set.
class DictionaryScreen extends StatefulWidget {
  const DictionaryScreen({super.key});

  @override
  State<DictionaryScreen> createState() => _DictionaryScreenState();
}

class _DictionaryScreenState extends State<DictionaryScreen>
    with SingleTickerProviderStateMixin {
  late Future<List<Sign>> _signs;
  late final TabController _tabs = TabController(length: 3, vsync: this);
  final _favorites = <int>{};
  String _query = '';
  String _category = 'Lahat';

  @override
  void initState() {
    super.initState();
    _signs = KumpasChannel.getSigns();
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  void _openPractice(Sign s) {
    Navigator.push(
        context, MaterialPageRoute(builder: (_) => PracticeScreen(sign: s)));
  }

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final scheme = Theme.of(context).colorScheme;
    return FutureBuilder<List<Sign>>(
      future: _signs,
      builder: (context, snap) {
        if (!snap.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final signs = snap.data!;
        final categories = ['Lahat', ...{for (final s in signs) s.category}];
        return Column(
          children: [
            Container(
              width: double.infinity,
              decoration: BoxDecoration(gradient: colors.headerGradient),
              child: SafeArea(
                bottom: false,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Diksyunaryo',
                          style: Theme.of(context)
                              .textTheme
                              .headlineSmall
                              ?.copyWith(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold)),
                      Text('FSL • ${signs.length} senyas na magagamit',
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall
                              ?.copyWith(color: Colors.white70)),
                    ],
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
              child: TextField(
                onChanged: (v) => setState(() => _query = v),
                decoration: InputDecoration(
                  hintText: 'Maghanap ng senyas...',
                  prefixIcon: const Icon(Icons.search),
                  filled: true,
                  fillColor: scheme.surfaceContainerLow,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: EdgeInsets.zero,
                ),
              ),
            ),
            TabBar(
              controller: _tabs,
              labelColor: colors.success,
              indicatorColor: colors.success,
              tabs: const [
                Tab(text: 'Lahat ng Senyas'),
                Tab(text: 'Paborito'),
                Tab(text: 'Mga Parirala'),
              ],
              onTap: (_) => setState(() {}),
            ),
            SizedBox(
              height: 52,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                children: categories
                    .map((c) => Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: ChoiceChip(
                            label: Text(c),
                            selected: _category == c,
                            onSelected: (_) =>
                                setState(() => _category = c),
                          ),
                        ))
                    .toList(),
              ),
            ),
            Expanded(
              child: AnimatedBuilder(
                animation: _tabs,
                builder: (context, _) {
                  var filtered = signs.where((s) {
                    if (_category != 'Lahat' && s.category != _category) {
                      return false;
                    }
                    if (_query.isNotEmpty &&
                        !s.label
                            .toLowerCase()
                            .contains(_query.toLowerCase())) {
                      return false;
                    }
                    return switch (_tabs.index) {
                      1 => _favorites.contains(s.id),
                      2 => s.label.contains(' '),
                      _ => true,
                    };
                  }).toList();
                  if (filtered.isEmpty) {
                    return Center(
                      child: Text(
                        _tabs.index == 1
                            ? 'Wala pang paborito — i-tap ang bituin sa senyas.'
                            : 'Walang nahanap na senyas.',
                        style: Theme.of(context)
                            .textTheme
                            .bodyMedium
                            ?.copyWith(color: scheme.onSurfaceVariant),
                      ),
                    );
                  }
                  return ListView.separated(
                    padding: const EdgeInsets.all(16),
                    itemCount: filtered.length,
                    separatorBuilder: (_, i) => const SizedBox(height: 12),
                    itemBuilder: (context, i) =>
                        _SignCard(
                      sign: filtered[i],
                      favorite: _favorites.contains(filtered[i].id),
                      onTap: () => _openPractice(filtered[i]),
                      onFavorite: () => setState(() {
                        _favorites.contains(filtered[i].id)
                            ? _favorites.remove(filtered[i].id)
                            : _favorites.add(filtered[i].id);
                      }),
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }
}

class _SignCard extends StatelessWidget {
  final Sign sign;
  final bool favorite;
  final VoidCallback onTap;
  final VoidCallback onFavorite;

  const _SignCard({
    required this.sign,
    required this.favorite,
    required this.onTap,
    required this.onFavorite,
  });

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: favorite ? colors.amberTint : colors.greenTint,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(Icons.play_arrow,
                    size: 32,
                    color: favorite ? colors.accent : colors.success),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(sign.label,
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        _Tag(text: sign.category,
                            color: scheme.surfaceContainerHighest),
                        const SizedBox(width: 6),
                        _Tag(text: 'beginner', color: colors.greenTint),
                      ],
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: onFavorite,
                icon: Icon(favorite ? Icons.star : Icons.star_border,
                    color: favorite
                        ? colors.accent
                        : scheme.onSurfaceVariant),
                tooltip: favorite
                    ? 'Alisin sa paborito'
                    : 'Idagdag sa paborito',
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Tag extends StatelessWidget {
  final String text;
  final Color color;

  const _Tag({required this.text, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(text, style: Theme.of(context).textTheme.labelSmall),
    );
  }
}
