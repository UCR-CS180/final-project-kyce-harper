import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/api_service.dart';

class TeamLibraryScreen extends StatefulWidget {
  const TeamLibraryScreen({super.key});

  @override
  State<TeamLibraryScreen> createState() => _TeamLibraryScreenState();
}

class _TeamLibraryScreenState extends State<TeamLibraryScreen> {
  List<Map<String, dynamic>> _teams = [];
  bool _isLoading = true;

  static const _sportEmojis = {
    'football': '🏈',
    'basketball': '🏀',
    'soccer': '⚽',
    'baseball': '⚾',
    'personal_training': '💪',
    'volleyball': '🏐',
    'track': '🏃',
    'general': '🎯',
  };

  @override
  void initState() {
    super.initState();
    _loadTeams();
  }

  Future<void> _loadTeams() async {
    setState(() => _isLoading = true);
    final uid = FirebaseAuth.instance.currentUser!.uid;
    final teams = await ApiService.getTeamsForUser(uid);
    if (!mounted) return;
    setState(() {
      _teams = teams;
      _isLoading = false;
    });
  }

  Future<void> _signOut() async {
    await FirebaseAuth.instance.signOut();
    // StreamBuilder in main.dart handles routing back to AuthScreen.
  }

  @override
  Widget build(BuildContext context) {
    final email = FirebaseAuth.instance.currentUser?.email ?? '';

    return Scaffold(
      backgroundColor: const Color(0xFF0D1B2A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1C2E3F),
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('My Teams',
                style:
                    TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            Text(email,
                style: const TextStyle(
                    fontSize: 11, color: Color(0xFF90A4AE))),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Sign out',
            onPressed: _signOut,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          await Navigator.pushNamed(context, '/create');
          _loadTeams();
        },
        backgroundColor: const Color(0xFF4FC3F7),
        foregroundColor: const Color(0xFF0D1B2A),
        icon: const Icon(Icons.add),
        label: const Text('New Team',
            style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: _isLoading
          ? const Center(
              child:
                  CircularProgressIndicator(color: Color(0xFF4FC3F7)))
          : _teams.isEmpty
              ? _buildEmpty()
              : RefreshIndicator(
                  onRefresh: _loadTeams,
                  color: const Color(0xFF4FC3F7),
                  child: ListView.separated(
                    padding:
                        const EdgeInsets.fromLTRB(16, 16, 16, 90),
                    itemCount: _teams.length,
                    separatorBuilder: (_, __) =>
                        const SizedBox(height: 10),
                    itemBuilder: (context, index) =>
                        _buildTeamCard(_teams[index]),
                  ),
                ),
    );
  }

  Widget _buildEmpty() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.sports,
              color: Color(0xFF1C2E3F), size: 72),
          const SizedBox(height: 16),
          const Text('No teams yet',
              style: TextStyle(
                  color: Color(0xFF546E7A), fontSize: 18)),
          const SizedBox(height: 8),
          const Text('Tap + New Team to get started.',
              style: TextStyle(
                  color: Color(0xFF37474F), fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildTeamCard(Map<String, dynamic> team) {
    final name = team['team_name'] as String? ?? '';
    final sport = team['sport_category'] as String? ?? 'general';
    final emoji = _sportEmojis[sport] ?? '🎯';
    final sportLabel = sport.replaceAll('_', ' ');

    return GestureDetector(
      onTap: () => Navigator.pushNamed(
        context,
        '/chat',
        arguments: {'teamName': name, 'sportCategory': sport},
      ),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        decoration: BoxDecoration(
          color: const Color(0xFF1C2E3F),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Row(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 32)),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(name,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold)),
                  const SizedBox(height: 3),
                  Text(
                    sportLabel.toUpperCase(),
                    style: const TextStyle(
                        color: Color(0xFF546E7A),
                        fontSize: 11,
                        letterSpacing: 0.8),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios,
                color: Color(0xFF37474F), size: 14),
          ],
        ),
      ),
    );
  }
}
