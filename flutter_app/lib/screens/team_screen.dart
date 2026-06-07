import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/api_service.dart';

class TeamScreen extends StatefulWidget {
  const TeamScreen({super.key});

  @override
  State<TeamScreen> createState() => _TeamScreenState();
}

class _TeamScreenState extends State<TeamScreen> {
  final _controller = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  String? _selectedCategory;
  bool _isLoading = false;

  static const _sports = [
    {'key': 'football',          'label': 'Football',          'emoji': '🏈'},
    {'key': 'basketball',        'label': 'Basketball',        'emoji': '🏀'},
    {'key': 'soccer',            'label': 'Soccer',            'emoji': '⚽'},
    {'key': 'baseball',          'label': 'Baseball',          'emoji': '⚾'},
    {'key': 'personal_training', 'label': 'Personal Training', 'emoji': '💪'},
    {'key': 'volleyball',        'label': 'Volleyball',        'emoji': '🏐'},
    {'key': 'track',             'label': 'Track & Field',     'emoji': '🏃'},
    {'key': 'general',           'label': 'Other',             'emoji': '🎯'},
  ];

  Future<void> _startSession() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedCategory == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pick a sport first.')),
      );
      return;
    }
    setState(() => _isLoading = true);
    final teamName = _controller.text.trim();
    final uid = FirebaseAuth.instance.currentUser?.uid ?? '';
    final sportCategory =
        await ApiService.createOrGetTeam(teamName, _selectedCategory!, uid);
    if (!mounted) return;
    setState(() => _isLoading = false);
    Navigator.pushNamed(
      context,
      '/chat',
      arguments: {'teamName': teamName, 'sportCategory': sportCategory},
    );
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
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Center(
                  child: Icon(Icons.sports, color: Color(0xFF4FC3F7), size: 60),
                ),
                const SizedBox(height: 12),
                const Center(
                  child: Text('Coach Notes',
                      style: TextStyle(
                          color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
                ),
                const SizedBox(height: 4),
                const Center(
                  child: Text('AI-powered practice notes',
                      style: TextStyle(color: Color(0xFF90A4AE), fontSize: 13)),
                ),
                const SizedBox(height: 36),

                const Text('Team name',
                    style: TextStyle(color: Color(0xFF90A4AE), fontSize: 13)),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _controller,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'e.g. Varsity Hawks',
                    hintStyle: const TextStyle(color: Color(0xFF546E7A)),
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
                  textInputAction: TextInputAction.next,
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? 'Enter a team name' : null,
                ),
                const SizedBox(height: 28),

                const Text('Sport / Category',
                    style: TextStyle(color: Color(0xFF90A4AE), fontSize: 13)),
                const SizedBox(height: 10),
                GridView.count(
                  crossAxisCount: 4,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: 10,
                  crossAxisSpacing: 10,
                  children: _sports.map((s) {
                    final key = s['key']!;
                    final selected = _selectedCategory == key;
                    return GestureDetector(
                      onTap: () => setState(() => _selectedCategory = key),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 150),
                        decoration: BoxDecoration(
                          color: selected
                              ? const Color(0xFF4FC3F7).withOpacity(0.15)
                              : const Color(0xFF1C2E3F),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: selected
                                ? const Color(0xFF4FC3F7)
                                : Colors.transparent,
                            width: 2,
                          ),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(s['emoji']!, style: const TextStyle(fontSize: 22)),
                            const SizedBox(height: 4),
                            Text(
                              s['label']!,
                              style: TextStyle(
                                color: selected
                                    ? const Color(0xFF4FC3F7)
                                    : const Color(0xFF90A4AE),
                                fontSize: 9,
                                fontWeight: selected
                                    ? FontWeight.bold
                                    : FontWeight.normal,
                              ),
                              textAlign: TextAlign.center,
                              maxLines: 2,
                            ),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
                ),
                const SizedBox(height: 32),

                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _startSession,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4FC3F7),
                      foregroundColor: const Color(0xFF0D1B2A),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            width: 20, height: 20,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Color(0xFF0D1B2A)))
                        : const Text('Start Session',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
