import 'dart:async';

import 'package:flutter/material.dart';

import '../feedback_engine/kumpas_channel.dart';
import '../feedback_engine/models.dart';
import 'feedback_sheet.dart';

/// Practice mode: camera preview + one-tap attempt capture (~4s window),
/// then corrective feedback from the native engine.
class PracticeScreen extends StatefulWidget {
  final Sign sign;

  const PracticeScreen({super.key, required this.sign});

  @override
  State<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends State<PracticeScreen> {
  StreamSubscription<Map<String, dynamic>>? _sub;
  bool _attemptRunning = false;
  int _collected = 0;
  int _needed = 30;
  String _liveLabel = '';
  bool _signerVisible = true;

  @override
  void initState() {
    super.initState();
    _sub = KumpasChannel.eventStream().listen(_onEvent);
  }

  void _onEvent(Map<String, dynamic> m) {
    if (!mounted) return;
    switch (m['state']) {
      case 'attempt_progress':
        setState(() {
          _attemptRunning = true;
          _collected = m['collected'] as int;
          _needed = m['needed'] as int;
        });
      case 'attempt_result':
        setState(() => _attemptRunning = false);
        final result = AttemptResult.fromJson(m);
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          builder: (_) => FeedbackSheet(result: result),
        );
      case 'attempt_failed':
        setState(() => _attemptRunning = false);
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(m['reason'] as String)));
      case 'prediction':
        setState(() {
          _liveLabel = m['label'] as String;
          _signerVisible = true;
        });
      case 'no_signer':
        setState(() {
          _liveLabel = '';
          _signerVisible = false;
        });
    }
  }

  Future<void> _startAttempt() async {
    setState(() {
      _attemptRunning = true;
      _collected = 0;
    });
    await KumpasChannel.startAttempt(widget.sign.id);
  }

  @override
  void dispose() {
    _sub?.cancel();
    KumpasChannel.cancelAttempt();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Practice: ${widget.sign.label}')),
      body: Stack(
        fit: StackFit.expand,
        children: [
          const AndroidView(viewType: 'kumpas/camera_preview'),
          if (!_signerVisible)
            const Align(
              alignment: Alignment.topCenter,
              child: Padding(
                padding: EdgeInsets.only(top: 16),
                child: Chip(label: Text('Step in front of the camera')),
              ),
            ),
          Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
              color: Colors.black.withValues(alpha: 0.65),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Sign "${widget.sign.label}" when the capture starts',
                      style: Theme.of(context).textTheme.bodyMedium),
                  if (_liveLabel.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text('recognizing: $_liveLabel',
                          style: Theme.of(context).textTheme.bodySmall),
                    ),
                  const SizedBox(height: 12),
                  _attemptRunning
                      ? Column(children: [
                          LinearProgressIndicator(value: _collected / _needed),
                          const SizedBox(height: 8),
                          Text('Capturing… $_collected/$_needed'),
                        ])
                      : FilledButton.icon(
                          icon: const Icon(Icons.sign_language),
                          label: const Text('Try the sign'),
                          onPressed: _startAttempt,
                        ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
