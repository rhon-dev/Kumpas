import 'dart:async';

import 'package:flutter/material.dart';

import '../feedback_engine/kumpas_channel.dart';
import 'theme.dart';
import 'widgets.dart';

/// Isalin tab (Figma: Translate.png / T2.png) — live sign→text translation.
/// Camera starts only after the CTA so the camera is never held while the
/// user is on another tab. "Boses sa Senyas" mode is a visual stub: the MVP
/// pipeline only recognizes signs (PRD scope).
class TranslateScreen extends StatefulWidget {
  const TranslateScreen({super.key});

  @override
  State<TranslateScreen> createState() => _TranslateScreenState();
}

class _TranslateScreenState extends State<TranslateScreen> {
  StreamSubscription<Map<String, dynamic>>? _sub;
  bool _signToVoice = true;
  bool _cameraOn = false;
  bool _signerVisible = true;
  String _label = '';

  @override
  void initState() {
    super.initState();
    _sub = KumpasChannel.eventStream().listen(_onEvent);
  }

  void _onEvent(Map<String, dynamic> m) {
    if (!mounted) return;
    switch (m['state']) {
      case 'prediction':
        setState(() {
          _label = m['label'] as String;
          _signerVisible = true;
        });
      case 'no_signer':
        setState(() {
          _label = '';
          _signerVisible = false;
        });
    }
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final scheme = Theme.of(context).colorScheme;
    return Column(
      children: [
        const GradientHeader(
          title: 'Tagapagsalin',
          subtitle: 'FSL • Real-time na pagsasalin',
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _ModeToggle(
                signToVoice: _signToVoice,
                onChanged: (v) => setState(() => _signToVoice = v),
              ),
              const SizedBox(height: 16),
              ClipRRect(
                borderRadius: BorderRadius.circular(20),
                child: Container(
                  height: 340,
                  color: colors.cameraPanel,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      if (_cameraOn && _signToVoice)
                        const AndroidView(
                            viewType: 'kumpas/camera_preview'),
                      if (!_cameraOn || !_signToVoice)
                        Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                width: 96,
                                height: 96,
                                decoration: BoxDecoration(
                                  color:
                                      Colors.white.withValues(alpha: 0.08),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(Icons.photo_camera,
                                    size: 40, color: Colors.white70),
                              ),
                              const SizedBox(height: 16),
                              Text(
                                _signToVoice
                                    ? 'Ilagay ang iyong mga kamay sa view'
                                    : 'Handa na ang camera',
                                style: const TextStyle(color: Colors.white70),
                              ),
                            ],
                          ),
                        ),
                      if (_cameraOn && _signToVoice && !_signerVisible)
                        const Center(
                          child: Text('Ilagay ang iyong mga kamay sa view',
                              style: TextStyle(color: Colors.white70)),
                        ),
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
                              Icon(Icons.circle, size: 8, color: Colors.white),
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
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SectionCard(
                color: scheme.surfaceContainerLow,
                child: Text(
                  _label.isEmpty ? 'Lalabas dito ang salin…' : _label,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: _label.isEmpty
                            ? scheme.onSurfaceVariant
                            : scheme.onSurface,
                        fontWeight:
                            _label.isEmpty ? null : FontWeight.bold,
                      ),
                ),
              ),
              const SizedBox(height: 16),
              if (_signToVoice)
                FilledButton.icon(
                  style: FilledButton.styleFrom(
                    backgroundColor: colors.success,
                    minimumSize: const Size.fromHeight(52),
                  ),
                  icon: Icon(_cameraOn ? Icons.stop : Icons.sign_language),
                  label: Text(_cameraOn
                      ? 'Ihinto ang Pagtuklas'
                      : 'Simulan ang Pagtuklas ng Senyas'),
                  onPressed: () => setState(() => _cameraOn = !_cameraOn),
                )
              else
                SectionCard(
                  color: scheme.surfaceContainerLow,
                  child: Text(
                    'Boses sa Senyas: hindi pa available sa MVP — '
                    'senyas → teksto lamang ang sinusuportahan.',
                    style: Theme.of(context)
                        .textTheme
                        .bodyMedium
                        ?.copyWith(color: scheme.onSurfaceVariant),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ModeToggle extends StatelessWidget {
  final bool signToVoice;
  final ValueChanged<bool> onChanged;

  const _ModeToggle({required this.signToVoice, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final colors = KumpasColors.of(context);
    final scheme = Theme.of(context).colorScheme;
    Widget pill(String text, IconData icon, bool selected, bool value) {
      return Expanded(
        child: Material(
          color: selected ? colors.success : Colors.transparent,
          borderRadius: BorderRadius.circular(24),
          child: InkWell(
            borderRadius: BorderRadius.circular(24),
            onTap: () => onChanged(value),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(icon,
                      size: 16,
                      color: selected ? Colors.white : scheme.onSurface),
                  const SizedBox(width: 6),
                  Text(text,
                      style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color:
                              selected ? Colors.white : scheme.onSurface)),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: scheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: scheme.outlineVariant),
      ),
      child: Row(
        children: [
          pill('Senyas sa Boses', Icons.back_hand, signToVoice, true),
          pill('Boses sa Senyas', Icons.volume_up, !signToVoice, false),
        ],
      ),
    );
  }
}
