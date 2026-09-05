import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../feedback_engine/kumpas_channel.dart';
import '../feedback_engine/models.dart';
import '../session/session_lifecycle.dart';
import 'feedback_sheet.dart';
import 'theme.dart';

/// Practice mode (Figma camera-panel style, Translate.png): rounded dark
/// camera card on a light screen, LIVE badge, one-tap attempt capture
/// (~4s window), then corrective feedback from the native engine.
class PracticeScreen extends StatefulWidget {
  final Sign sign;

  const PracticeScreen({super.key, required this.sign});

  @override
  State<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends State<PracticeScreen> {
  StreamSubscription<Map<String, dynamic>>? _sub;
  bool _warmingUp = true;
  bool _attemptRunning = false;
  int _collected = 0;
  int _needed = 30;
  String _liveLabel = '';
  bool _signerVisible = true;
  late SessionLifecycleObserver _lifecycleObserver;

  @override
  void initState() {
    super.initState();
    _lifecycleObserver = SessionLifecycleObserver();
    WidgetsBinding.instance.addObserver(_lifecycleObserver);
    _lifecycleObserver.setPracticeActive(true);
    _sub = KumpasChannel.eventStream().listen(_onEvent);
  }

  void _onEvent(Map<String, dynamic> m) {
    if (!mounted) return;
    switch (m['state']) {
      case 'attempt_progress':
        setState(() {
          _warmingUp = false;
          _attemptRunning = true;
          _collected = m['collected'] as int;
          _needed = m['needed'] as int;
        });
      case 'attempt_result':
        setState(() => _attemptRunning = false);
        HapticFeedback.mediumImpact();
        final result = AttemptResult.fromJson(m);
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          builder: (_) => FeedbackSheet(result: result),
        );
      case 'attempt_failed':
        setState(() => _attemptRunning = false);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(m['reason'] as String),
          action: SnackBarAction(label: 'Ulitin', onPressed: _startAttempt),
        ));
      case 'prediction':
        setState(() {
          _warmingUp = false;
          _liveLabel = m['label'] as String;
          _signerVisible = true;
        });
      case 'no_signer':
        setState(() {
          _warmingUp = false;
          _liveLabel = '';
          _signerVisible = false;
        });
    }
  }

  Future<void> _startAttempt() async {
    HapticFeedback.lightImpact();
    setState(() {
      _attemptRunning = true;
      _collected = 0;
    });
    await KumpasChannel.startAttempt(widget.sign.id);
  }

  Future<void> _cancelAttempt() async {
    await KumpasChannel.cancelAttempt();
    if (mounted) setState(() => _attemptRunning = false);
  }

  @override
  void dispose() {
    _lifecycleObserver.setPracticeActive(false);
    WidgetsBinding.instance.removeObserver(_lifecycleObserver);
    _sub?.cancel();
    KumpasChannel.cancelAttempt();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final reduceMotion = MediaQuery.of(context).disableAnimations;
    final hint = _warmingUp
        ? 'Sinisimulan ang camera…'
        : !_signerVisible
            ? 'Ilagay ang iyong mga kamay sa view'
            : null;

    return Scaffold(
      body: Column(
        children: [
          Container(
            decoration: BoxDecoration(gradient: colors.headerGradient),
            child: SafeArea(
              bottom: false,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(4, 4, 20, 12),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                      tooltip: 'Bumalik',
                    ),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(widget.sign.label,
                              style: Theme.of(context)
                                  .textTheme
                                  .titleLarge
                                  ?.copyWith(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold)),
                          Text('Pagsasanay • ${widget.sign.category}',
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(color: Colors.white70)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: Container(
                    height: 380,
                    color: colors.cameraPanel,
                    child: Stack(
                      fit: StackFit.expand,
                      children: [
                        const AndroidView(
                            viewType: 'kumpas/camera_preview'),
                        Positioned(
                          top: 12,
                          right: 12,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: colors.live,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.circle,
                                    size: 8, color: Colors.white),
                                SizedBox(width: 4),
                                Text('LIVE',
                                    style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold)),
                              ],
                            ),
                          ),
                        ),
                        Align(
                          alignment: Alignment.topCenter,
                          child: AnimatedSwitcher(
                            duration: reduceMotion
                                ? Duration.zero
                                : KumpasMotion.base,
                            child: hint == null
                                ? const SizedBox.shrink()
                                : Container(
                                    key: ValueKey(hint),
                                    // Below the LIVE badge row to avoid overlap.
                                    margin: const EdgeInsets.only(top: 52),
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 14, vertical: 8),
                                    decoration: BoxDecoration(
                                      color: Colors.black
                                          .withValues(alpha: 0.55),
                                      borderRadius:
                                          BorderRadius.circular(20),
                                    ),
                                    child: Text(hint,
                                        style: const TextStyle(
                                            color: Colors.white)),
                                  ),
                          ),
                        ),
                        if (_liveLabel.isNotEmpty)
                          Align(
                            alignment: Alignment.bottomCenter,
                            child: Container(
                              margin: const EdgeInsets.only(bottom: 12),
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 14, vertical: 8),
                              decoration: BoxDecoration(
                                color:
                                    Colors.black.withValues(alpha: 0.55),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.visibility,
                                      size: 16, color: Colors.white70),
                                  const SizedBox(width: 6),
                                  Text('nakikita: $_liveLabel',
                                      style: const TextStyle(
                                          color: Colors.white)),
                                ],
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  _attemptRunning
                      ? 'Hawakan ang senyas hanggang matapos ang capture'
                      : 'Isenyas ang "${widget.sign.label}" kapag nagsimula ang capture',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 16),
                _attemptRunning
                    ? _CaptureProgress(
                        collected: _collected,
                        needed: _needed,
                        reduceMotion: reduceMotion,
                        onCancel: _cancelAttempt,
                      )
                    : FilledButton.icon(
                        style: FilledButton.styleFrom(
                          backgroundColor: colors.success,
                          minimumSize: const Size.fromHeight(52),
                        ),
                        icon: const Icon(Icons.sign_language),
                        label: const Text('Subukan ang Senyas'),
                        onPressed: _startAttempt,
                      ),
                SizedBox(
                    height:
                        MediaQuery.of(context).padding.bottom + 8),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Capture-in-progress state: progress ring with frame count + cancel.
class _CaptureProgress extends StatelessWidget {
  final int collected;
  final int needed;
  final bool reduceMotion;
  final VoidCallback onCancel;

  const _CaptureProgress({
    required this.collected,
    required this.needed,
    required this.reduceMotion,
    required this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final success = KumpasColors.of(context).success;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: 84,
          height: 84,
          child: Stack(
            fit: StackFit.expand,
            alignment: Alignment.center,
            children: [
              TweenAnimationBuilder<double>(
                tween: Tween(end: collected / needed),
                duration: reduceMotion ? Duration.zero : KumpasMotion.fast,
                builder: (_, value, child) => CircularProgressIndicator(
                  value: value,
                  strokeWidth: 6,
                  strokeCap: StrokeCap.round,
                  color: success,
                  backgroundColor: scheme.surfaceContainerHighest,
                ),
              ),
              Center(
                child: Text(
                  '$collected/$needed',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 4),
        TextButton.icon(
          onPressed: onCancel,
          icon: const Icon(Icons.close, size: 18),
          label: const Text('Kanselahin'),
          style: TextButton.styleFrom(
            foregroundColor: scheme.onSurfaceVariant,
            minimumSize: const Size(64, 44),
          ),
        ),
      ],
    );
  }
}
