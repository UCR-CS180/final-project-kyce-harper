import 'package:flutter/material.dart';
import 'screens/team_screen.dart';
import 'screens/main_screen.dart';

void main() {
  runApp(const CoachNotesApp());
}

class CoachNotesApp extends StatelessWidget {
  const CoachNotesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Coach Notes',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.dark(
          primary: const Color(0xFF4FC3F7),
          surface: const Color(0xFF1C2E3F),
        ),
        useMaterial3: true,
      ),
      initialRoute: '/',
      routes: {
        '/': (_) => const TeamScreen(),
        '/chat': (_) => const MainScreen(),
      },
    );
  }
}
