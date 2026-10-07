import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AgriVisionMobileApp());
}

class AgriVisionMobileApp extends StatefulWidget {
  const AgriVisionMobileApp({super.key});

  @override
  State<AgriVisionMobileApp> createState() => _AgriVisionMobileAppState();
}

class _AgriVisionMobileAppState extends State<AgriVisionMobileApp> {
  // Global bilingual toggle: Hindi (true) vs English (false)
  bool _isHindi = false;

  void _toggleLanguage() {
    setState(() {
      _isHindi = !_isHindi;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AgriVision AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1B5E20),
          primary: const Color(0xFF1B5E20),
          secondary: const Color(0xFF2E7D32),
          surface: const Color(0xFFF4F7F4),
        ),
        textTheme: GoogleFonts.poppinsTextTheme(Theme.of(context).textTheme),
        scaffoldBackgroundColor: const Color(0xFFF4F7F4),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1B5E20),
          foregroundColor: Colors.white,
          centerTitle: false,
        ),
      ),
      home: HomeScreen(
        isHindi: _isHindi,
        onToggleLanguage: _toggleLanguage,
      ),
    );
  }
}
