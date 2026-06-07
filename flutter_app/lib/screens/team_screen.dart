import 'package:flutter/material.dart';

class TeamScreen extends StatefulWidget {
  const TeamScreen({super.key});

  @override
  State<TeamScreen> createState() => _TeamScreenState();
}

class _TeamScreenState extends State<TeamScreen> {
  final _controller = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  void _startSession() {
    if (_formKey.currentState!.validate()) {
      final teamName = _controller.text.trim();
      Navigator.pushNamed(context, '/chat', arguments: teamName);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1B2A),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.sports, color: Color(0xFF4FC3F7), size: 72),
                  const SizedBox(height: 16),
                  const Text(
                    'Coach Notes',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'AI-powered practice notes',
                    style: TextStyle(color: Color(0xFF90A4AE), fontSize: 14),
                  ),
                  const SizedBox(height: 48),
                  TextFormField(
                    controller: _controller,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      labelText: 'Team name',
                      labelStyle: const TextStyle(color: Color(0xFF90A4AE)),
                      prefixIcon: const Icon(Icons.group, color: Color(0xFF4FC3F7)),
                      filled: true,
                      fillColor: const Color(0xFF1C2E3F),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Color(0xFF4FC3F7)),
                      ),
                    ),
                    textInputAction: TextInputAction.go,
                    onFieldSubmitted: (_) => _startSession(),
                    validator: (value) =>
                        (value == null || value.trim().isEmpty) ? 'Enter a team name' : null,
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: _startSession,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF4FC3F7),
                        foregroundColor: const Color(0xFF0D1B2A),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text(
                        'Start Session',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
