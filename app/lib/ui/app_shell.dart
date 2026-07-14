import 'package:flutter/material.dart';

import 'dictionary_screen.dart';
import 'home_screen.dart';
import 'learn_screen.dart';
import 'profile_screen.dart';
import 'translate_screen.dart';

/// 5-tab shell per the approved Figma: Home, Isalin, Diksyunaryo, Mag-aral,
/// Profile. Tabs are rebuilt on switch (no IndexedStack) so the camera in
/// Isalin is released whenever the user leaves the tab — only one CameraX
/// client may hold the camera at a time.
class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _index = 0;

  void _goTo(int i) => setState(() => _index = i);

  @override
  Widget build(BuildContext context) {
    final body = switch (_index) {
      0 => HomeScreen(onQuickAction: _goTo),
      1 => const TranslateScreen(),
      2 => const DictionaryScreen(),
      3 => const LearnScreen(),
      _ => const ProfileScreen(),
    };
    return Scaffold(
      body: body,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: _goTo,
        destinations: const [
          NavigationDestination(
              icon: Icon(Icons.home_outlined),
              selectedIcon: Icon(Icons.home),
              label: 'Home'),
          NavigationDestination(
              icon: Icon(Icons.translate_outlined),
              selectedIcon: Icon(Icons.translate),
              label: 'Isalin'),
          NavigationDestination(
              icon: Icon(Icons.menu_book_outlined),
              selectedIcon: Icon(Icons.menu_book),
              label: 'Diksyunaryo'),
          NavigationDestination(
              icon: Icon(Icons.school_outlined),
              selectedIcon: Icon(Icons.school),
              label: 'Mag-aral'),
          NavigationDestination(
              icon: Icon(Icons.person_outline),
              selectedIcon: Icon(Icons.person),
              label: 'Profile'),
        ],
      ),
    );
  }
}
