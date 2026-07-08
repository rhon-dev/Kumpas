import 'package:flutter/material.dart';

import 'ui/library_screen.dart';

/// KUMPAS — FSL practice app (thesis MVP).
/// Home is the 50-sign library; each sign opens practice mode (camera +
/// native MediaPipe/TFLite pipeline + corrective feedback engine).
void main() => runApp(const KumpasApp());

class KumpasApp extends StatelessWidget {
  const KumpasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KUMPAS',
      theme: ThemeData.dark(useMaterial3: true),
      home: const LibraryScreen(),
    );
  }
}
