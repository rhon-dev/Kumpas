import 'package:flutter/material.dart';

import '../feedback_engine/kumpas_channel.dart';
import '../feedback_engine/models.dart';
import 'history_screen.dart';
import 'practice_screen.dart';

/// Gesture library: the 50 approved signs grouped by category.
/// Tap a sign to open practice mode.
class LibraryScreen extends StatefulWidget {
  const LibraryScreen({super.key});

  @override
  State<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends State<LibraryScreen> {
  late Future<List<Sign>> _signs;

  @override
  void initState() {
    super.initState();
    _signs = KumpasChannel.getSigns();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('KUMPAS'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'Session history',
            onPressed: () => Navigator.push(
                context, MaterialPageRoute(builder: (_) => const HistoryScreen())),
          ),
        ],
      ),
      body: FutureBuilder<List<Sign>>(
        future: _signs,
        builder: (context, snap) {
          if (!snap.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final byCategory = <String, List<Sign>>{};
          for (final s in snap.data!) {
            byCategory.putIfAbsent(s.category, () => []).add(s);
          }
          final categories = byCategory.keys.toList();
          return ListView.builder(
            itemCount: categories.length,
            itemBuilder: (context, i) {
              final cat = categories[i];
              final signs = byCategory[cat]!;
              return ExpansionTile(
                initiallyExpanded: i == 0,
                title: Text(cat,
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold)),
                subtitle: Text('${signs.length} signs'),
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: signs
                          .map((s) => ActionChip(
                                label: Text(s.label),
                                onPressed: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                      builder: (_) => PracticeScreen(sign: s)),
                                ),
                              ))
                          .toList(),
                    ),
                  ),
                ],
              );
            },
          );
        },
      ),
    );
  }
}
