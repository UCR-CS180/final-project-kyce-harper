import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'chat_tab.dart';
import 'roster_tab.dart';
import 'notes_tab.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  late String _teamName;
  late String _sportCategory;
  List<Map<String, dynamic>> _rosterRows = [];
  int _currentTab = 0;
  bool _initialized = false;

  static const _tabs  = ['Chat', 'Roster', 'Notes'];
  static const _icons = [
    Icons.chat_bubble_outline,
    Icons.group_outlined,
    Icons.notes_outlined,
  ];

  static const _sportLabels = {
    'football':          'Football 🏈',
    'basketball':        'Basketball 🏀',
    'soccer':            'Soccer ⚽',
    'baseball':          'Baseball ⚾',
    'personal_training': 'Personal Training 💪',
    'volleyball':        'Volleyball 🏐',
    'track':             'Track & Field 🏃',
    'general':           'General 🎯',
  };

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_initialized) {
      final args = ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
      _teamName     = args['teamName'] as String;
      _sportCategory = args['sportCategory'] as String? ?? 'general';
      _initialized  = true;
      _loadRoster();
    }
  }

  Future<void> _loadRoster() async {
    final rows = await ApiService.getRosterFull(_teamName);
    if (!mounted) return;
    setState(() => _rosterRows = rows);
  }

  List<String> get _rosterNames =>
      _rosterRows.map((r) => r['player_name'] as String? ?? '').where((n) => n.isNotEmpty).toList();

  @override
  Widget build(BuildContext context) {
    final sportLabel = _sportLabels[_sportCategory] ?? _sportCategory;

    return Scaffold(
      backgroundColor: const Color(0xFF0D1B2A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1C2E3F),
        foregroundColor: Colors.white,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_teamName,
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            Text(
              '$sportLabel · ${_rosterRows.length} player${_rosterRows.length == 1 ? '' : 's'}',
              style: const TextStyle(fontSize: 11, color: Color(0xFF90A4AE)),
            ),
          ],
        ),
      ),
      body: IndexedStack(
        index: _currentTab,
        children: [
          ChatTab(
            teamName: _teamName,
            roster: _rosterNames,
            sportCategory: _sportCategory,
            onRosterChanged: _loadRoster,
          ),
          RosterTab(
            teamName: _teamName,
            rosterRows: _rosterRows,
            roster: _rosterNames,
            onRosterChanged: _loadRoster,
          ),
          NotesTab(teamName: _teamName),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentTab,
        onTap: (i) => setState(() => _currentTab = i),
        backgroundColor: const Color(0xFF1C2E3F),
        selectedItemColor: const Color(0xFF4FC3F7),
        unselectedItemColor: const Color(0xFF546E7A),
        items: List.generate(
          _tabs.length,
          (i) => BottomNavigationBarItem(icon: Icon(_icons[i]), label: _tabs[i]),
        ),
      ),
    );
  }
}
