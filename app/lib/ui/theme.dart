import 'package:flutter/material.dart';

/// KUMPAS design tokens — from the approved Figma (docs/design/*.png):
/// light surfaces, green primary with gradient headers, orange lesson accent.
/// Screens read semantic colors from [KumpasColors]; no raw hex in widgets.
abstract final class KumpasTheme {
  static const seed = Color(0xFF00A550);

  /// Settings → Hitsura → Dark Mode toggle drives this.
  static final themeMode = ValueNotifier<ThemeMode>(ThemeMode.light);

  static ThemeData light() {
    final scheme = ColorScheme.fromSeed(seedColor: seed);
    return _base(
      scheme.copyWith(
        primary: const Color(0xFF00A550),
        onPrimary: Colors.white,
        surface: const Color(0xFFF7FAF8),
        surfaceContainerLowest: Colors.white,
      ),
      const KumpasColors(
        success: Color(0xFF16A34A),
        warn: Color(0xFFD97706),
        accent: Color(0xFFF59E0B),
        gradientTop: Color(0xFF00B25A),
        gradientBottom: Color(0xFF008F4C),
        greenTint: Color(0xFFE8F7EE),
        amberTint: Color(0xFFFEF6E7),
        purple: Color(0xFF8B5CF6),
        live: Color(0xFFEF4444),
        cameraPanel: Color(0xFF1A2230),
      ),
    );
  }

  static ThemeData dark() {
    final scheme =
        ColorScheme.fromSeed(seedColor: seed, brightness: Brightness.dark);
    return _base(
      scheme,
      const KumpasColors(
        success: Color(0xFF4ADE80),
        warn: Color(0xFFFBBF24),
        accent: Color(0xFFFBBF24),
        gradientTop: Color(0xFF14532D),
        gradientBottom: Color(0xFF052E16),
        greenTint: Color(0xFF14351F),
        amberTint: Color(0xFF3A2E12),
        purple: Color(0xFFA78BFA),
        live: Color(0xFFF87171),
        cameraPanel: Color(0xFF10161F),
      ),
    );
  }

  static ThemeData _base(ColorScheme scheme, KumpasColors colors) {
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: scheme.surface,
      extensions: [colors],
      cardTheme: CardThemeData(
        color: scheme.surfaceContainerLowest,
        elevation: 1,
        shadowColor: Colors.black26,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        margin: EdgeInsets.zero,
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: scheme.surfaceContainerLowest,
        showDragHandle: true,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size(64, 48),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: scheme.surfaceContainerLowest,
        indicatorColor: colors.greenTint,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        height: 68,
      ),
      snackBarTheme:
          const SnackBarThemeData(behavior: SnackBarBehavior.floating),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }
}

/// Motion tokens: micro-interactions 150–300ms, ease-out entrances.
/// Callers must zero these out when `MediaQuery.disableAnimations` is set.
abstract final class KumpasMotion {
  static const fast = Duration(milliseconds: 150);
  static const base = Duration(milliseconds: 220);
  static const gauge = Duration(milliseconds: 550);
}

/// Semantic colors beyond [ColorScheme], matched to the Figma frames.
class KumpasColors extends ThemeExtension<KumpasColors> {
  final Color success;
  final Color warn;
  final Color accent; // orange lesson/streak accent
  final Color gradientTop; // header gradient
  final Color gradientBottom;
  final Color greenTint; // pale green card fill
  final Color amberTint; // pale amber card fill
  final Color purple; // achievements accent
  final Color live; // LIVE badge red
  final Color cameraPanel; // dark rounded camera panel

  const KumpasColors({
    required this.success,
    required this.warn,
    required this.accent,
    required this.gradientTop,
    required this.gradientBottom,
    required this.greenTint,
    required this.amberTint,
    required this.purple,
    required this.live,
    required this.cameraPanel,
  });

  static KumpasColors of(BuildContext context) =>
      Theme.of(context).extension<KumpasColors>()!;

  LinearGradient get headerGradient => LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [gradientTop, gradientBottom],
      );

  @override
  KumpasColors copyWith({
    Color? success,
    Color? warn,
    Color? accent,
    Color? gradientTop,
    Color? gradientBottom,
    Color? greenTint,
    Color? amberTint,
    Color? purple,
    Color? live,
    Color? cameraPanel,
  }) =>
      KumpasColors(
        success: success ?? this.success,
        warn: warn ?? this.warn,
        accent: accent ?? this.accent,
        gradientTop: gradientTop ?? this.gradientTop,
        gradientBottom: gradientBottom ?? this.gradientBottom,
        greenTint: greenTint ?? this.greenTint,
        amberTint: amberTint ?? this.amberTint,
        purple: purple ?? this.purple,
        live: live ?? this.live,
        cameraPanel: cameraPanel ?? this.cameraPanel,
      );

  @override
  KumpasColors lerp(KumpasColors? other, double t) {
    if (other == null) return this;
    Color l(Color a, Color b) => Color.lerp(a, b, t)!;
    return KumpasColors(
      success: l(success, other.success),
      warn: l(warn, other.warn),
      accent: l(accent, other.accent),
      gradientTop: l(gradientTop, other.gradientTop),
      gradientBottom: l(gradientBottom, other.gradientBottom),
      greenTint: l(greenTint, other.greenTint),
      amberTint: l(amberTint, other.amberTint),
      purple: l(purple, other.purple),
      live: l(live, other.live),
      cameraPanel: l(cameraPanel, other.cameraPanel),
    );
  }
}
