import 'package:flutter/material.dart';

import 'ui/app_shell.dart';
import 'ui/theme.dart';

/// KUMPAS — FSL practice app (thesis MVP).
/// UI from the approved Figma (docs/design/): 5-tab shell, light green theme,
/// dark mode via Profile → Mga Setting. Native MediaPipe/TFLite pipeline +
/// corrective feedback engine behind kumpas/* platform channels.
void main() => runApp(const KumpasApp());

class KumpasApp extends StatelessWidget {
  const KumpasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: KumpasTheme.themeMode,
      builder: (context, mode, _) => MaterialApp(
        title: 'KUMPAS',
        theme: KumpasTheme.light(),
        darkTheme: KumpasTheme.dark(),
        themeMode: mode,
        home: const AppShell(),
      ),
    );
  }
}
