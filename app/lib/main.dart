import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// KUMPAS Phase 5 skeleton: native camera preview (CameraX platform view) +
/// live prediction stream from the Kotlin VisionEngine
/// (MediaPipe pose+hands -> 258-dim features -> TFLite CNN-LSTM).
///
/// No feedback logic yet — this screen only proves the end-to-end pipeline:
/// "predicted: gesture X" at target FPS (PRD Phase 5 gate).
void main() => runApp(const KumpasApp());

class KumpasApp extends StatelessWidget {
  const KumpasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KUMPAS',
      theme: ThemeData.dark(useMaterial3: true),
      home: const RecognitionScreen(),
    );
  }
}

class RecognitionScreen extends StatefulWidget {
  const RecognitionScreen({super.key});

  @override
  State<RecognitionScreen> createState() => _RecognitionScreenState();
}

class _RecognitionScreenState extends State<RecognitionScreen> {
  static const _events = EventChannel('kumpas/predictions');

  String _label = '—';
  double _confidence = 0;
  List<dynamic> _top3 = const [];
  double _fps = 0;
  num _landmarkMs = 0;
  num _inferMs = 0;
  int _hands = 0;
  int _bufferFill = 0;
  bool _warmedUp = false;

  @override
  void initState() {
    super.initState();
    _events.receiveBroadcastStream().listen((event) {
      final m = jsonDecode(event as String) as Map<String, dynamic>;
      setState(() {
        _fps = (m['cameraFps'] as num?)?.toDouble() ?? _fps;
        _landmarkMs = m['landmarkMs'] as num? ?? _landmarkMs;
        _hands = m['handsVisible'] as int? ?? _hands;
        if (m['state'] == 'prediction') {
          _warmedUp = true;
          _label = m['label'] as String;
          _confidence = (m['confidence'] as num).toDouble();
          _top3 = m['top3'] as List<dynamic>? ?? const [];
          _inferMs = m['inferMs'] as num? ?? _inferMs;
        } else {
          _bufferFill = m['bufferFill'] as int? ?? 0;
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          const AndroidView(viewType: 'kumpas/camera_preview'),
          Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
              color: Colors.black.withValues(alpha: 0.65),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (!_warmedUp)
                    Text('Warming up… $_bufferFill/30',
                        style: Theme.of(context).textTheme.titleLarge)
                  else ...[
                    Text(_label,
                        style: Theme.of(context)
                            .textTheme
                            .displaySmall
                            ?.copyWith(fontWeight: FontWeight.bold)),
                    Text('confidence ${(_confidence * 100).toStringAsFixed(1)}%'),
                    const SizedBox(height: 4),
                    Text(
                      _top3
                          .map((e) =>
                              '${e['label']} ${((e['p'] as num) * 100).toStringAsFixed(0)}%')
                          .join('   '),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                  const Divider(height: 16),
                  Text(
                    'camera ${_fps.toStringAsFixed(1)} fps · landmarks ${_landmarkMs}ms · '
                    'inference ${_inferMs}ms · hands: $_hands',
                    style: Theme.of(context).textTheme.bodySmall,
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
