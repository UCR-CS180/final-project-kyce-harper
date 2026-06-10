import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'firebase_options.dart';
import 'screens/auth_screen.dart';
import 'screens/team_library_screen.dart';
import 'screens/team_screen.dart';
import 'screens/main_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
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
      home: StreamBuilder<User?>(
        stream: FirebaseAuth.instance.authStateChanges(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(
              backgroundColor: Color(0xFF0D1B2A),
              body: Center(
                child: CircularProgressIndicator(color: Color(0xFF4FC3F7)),
              ),
            );
          }
          return snapshot.data == null
              ? const AuthScreen()
              : const TeamLibraryScreen();
        },
      ),
      routes: {
        '/create': (_) => const TeamScreen(),
        '/chat': (_) => const MainScreen(),
      },
    );
  }
}
