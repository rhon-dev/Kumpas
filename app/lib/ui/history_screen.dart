import 'package:flutter/material.dart';

import '../feedback_engine/kumpas_channel.dart';
import '../feedback_engine/models.dart';
import 'feedback_sheet.dart';

/// Session history: past attempts from local storage, newest first.
class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  late Future<List<AttemptResult>> _history;

  @override
  void initState() {
    super.initState();
    _history = KumpasChannel.getHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Session history')),
      body: FutureBuilder<List<AttemptResult>>(
        future: _history,
        builder: (context, snap) {
          if (!snap.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final attempts = snap.data!;
          if (attempts.isEmpty) {
            return const Center(child: Text('No attempts yet — go practice!'));
          }
          return ListView.separated(
            itemCount: attempts.length,
            separatorBuilder: (_, index) => const Divider(height: 1),
            itemBuilder: (context, i) {
              final a = attempts[i];
              final pct = (a.overallMatch * 100).toStringAsFixed(0);
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor:
                      a.overallMatch >= 0.8 ? Colors.green : Colors.amber,
                  child: Text(pct, style: const TextStyle(fontSize: 12)),
                ),
                title: Text(a.targetLabel),
                subtitle: Text(
                    '${a.recognizedAsTarget ? "recognized" : "read as ${a.predictedLabel}"}'
                    '${a.timestamp != null ? " · ${_fmt(a.timestamp!)}" : ""}'),
                trailing: Text('${a.items.length} tip${a.items.length == 1 ? "" : "s"}'),
                onTap: () => showModalBottomSheet(
                  context: context,
                  isScrollControlled: true,
                  builder: (_) => FeedbackSheet(result: a),
                ),
              );
            },
          );
        },
      ),
    );
  }

  static String _fmt(DateTime t) =>
      '${t.year}-${t.month.toString().padLeft(2, "0")}-${t.day.toString().padLeft(2, "0")} '
      '${t.hour.toString().padLeft(2, "0")}:${t.minute.toString().padLeft(2, "0")}';
}
