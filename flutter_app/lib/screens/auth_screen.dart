import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isSignUp = false;
  bool _isLoading = false;
  String? _error;

  Future<void> _submit() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();
    if (email.isEmpty || password.isEmpty) {
      setState(() => _error = 'Email and password are required.');
      return;
    }
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      if (_isSignUp) {
        await FirebaseAuth.instance.createUserWithEmailAndPassword(
          email: email,
          password: password,
        );
      } else {
        await FirebaseAuth.instance.signInWithEmailAndPassword(
          email: email,
          password: password,
        );
      }
      // Auth state change is handled by the StreamBuilder in main.dart.
    } on FirebaseAuthException catch (e) {
      // ignore: avoid_print
      print('FirebaseAuthException — code: ${e.code} | message: ${e.message}');
      final msg = switch (e.code) {
        'user-not-found'      => 'No account found for that email.',
        'wrong-password'      => 'Incorrect password.',
        'email-already-in-use'=> 'An account already exists with that email.',
        'invalid-email'       => 'Please enter a valid email address.',
        'weak-password'       => 'Password must be at least 6 characters.',
        'invalid-credential'  => 'Email or password is incorrect.',
        'operation-not-allowed' =>
            'Email/password sign-in is not enabled.\nGo to Firebase Console → Authentication → Sign-in methods and enable Email/Password.',
        _                     => '${e.message ?? 'Authentication failed.'} (${e.code})',
      };
      if (mounted) setState(() => _error = msg);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1B2A),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.sports, color: Color(0xFF4FC3F7), size: 64),
                const SizedBox(height: 12),
                const Text(
                  'Coach Notes',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                const Text(
                  'AI-powered practice notes',
                  style: TextStyle(color: Color(0xFF90A4AE), fontSize: 13),
                ),
                const SizedBox(height: 44),
                _buildField(
                    _emailController, 'Email', Icons.email_outlined, false),
                const SizedBox(height: 14),
                _buildField(
                    _passwordController, 'Password', Icons.lock_outline, true),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    _error!,
                    style:
                        const TextStyle(color: Color(0xFFEF5350), fontSize: 13),
                    textAlign: TextAlign.center,
                  ),
                ],
                const SizedBox(height: 28),
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _submit,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4FC3F7),
                      foregroundColor: const Color(0xFF0D1B2A),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Color(0xFF0D1B2A)),
                          )
                        : Text(
                            _isSignUp ? 'Create Account' : 'Sign In',
                            style: const TextStyle(
                                fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                  ),
                ),
                const SizedBox(height: 18),
                GestureDetector(
                  onTap: () =>
                      setState(() {
                        _isSignUp = !_isSignUp;
                        _error = null;
                      }),
                  child: Text(
                    _isSignUp
                        ? 'Already have an account? Sign in'
                        : "Don't have an account? Sign up",
                    style: const TextStyle(
                        color: Color(0xFF4FC3F7), fontSize: 14),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildField(TextEditingController ctrl, String hint, IconData icon,
      bool obscure) {
    return TextField(
      controller: ctrl,
      obscureText: obscure,
      style: const TextStyle(color: Colors.white),
      keyboardType:
          obscure ? TextInputType.visiblePassword : TextInputType.emailAddress,
      textInputAction:
          obscure ? TextInputAction.done : TextInputAction.next,
      onSubmitted: obscure ? (_) => _submit() : null,
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: Color(0xFF546E7A)),
        prefixIcon: Icon(icon, color: const Color(0xFF4FC3F7)),
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
    );
  }
}
