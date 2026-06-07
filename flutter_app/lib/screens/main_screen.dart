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
  List<String> _roster = [];
  int _currentTab = 0;
  bool _initialized = false;

  static const _tabs = ['Chat', 'Roster', 'Notes'];
  static const _icons = [Icons.chat_bubble_outline, Icons.group_outlined, Icons.notes_outlined];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_initialized) {
      _teamName = ModalRoute.of(context)!.settings.arguments as String;
      _initialized = true;
      _loadRoster();
    }
  }

  Future<void> _loadRoster() async {
    final players = await ApiService.getRoster(_teamName);
    if (!mounted) return;
    setState(() => _roster = players);
  }

  @override
  Widget build(BuildContext context) {
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
              '${_roster.length} player${_roster.length == 1 ? '' : 's'} · ${_tabs[_currentTab]}',
              style: const TextStyle(fontSize: 12, color: Color(0xFF90A4AE)),
            ),
          ],
        ),
      ),
      // IndexedStack keeps all three tabs alive so chat history isn't lost on tab switch
      body: IndexedStack(
        index: _currentTab,
        children: [
          ChatTab(
            teamName: _teamName,
            roster: _roster,
            onRosterChanged: _loadRoster,
          ),
          RosterTab(
            teamName: _teamName,
            roster: _roster,
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
