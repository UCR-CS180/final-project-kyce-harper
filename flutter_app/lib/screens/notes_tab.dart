import 'package:flutter/material.dart';
import '../services/api_service.dart';

class NotesTab extends StatefulWidget {
  final String teamName;

  const NotesTab({super.key, required this.teamName});

  @override
  State<NotesTab> createState() => _NotesTabState();
}

class _NotesTabState extends State<NotesTab> {
  List<Map<String, dynamic>> _observations = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final obs = await ApiService.getAllObservations(widget.teamName);
    if (!mounted) return;
    setState(() {
      _observations = obs;
      _loading = false;
    });
  }

  // Group observations by player name, preserving date-desc order within each group
  Map<String, List<Map<String, dynamic>>> _grouped() {
    final map = <String, List<Map<String, dynamic>>>{};
    for (final obs in _observations) {
      final name = obs['player_name'] as String? ?? 'Unknown';
      map.putIfAbsent(name, () => []).add(obs);
    }
    return map;
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF4FC3F7)));
    }

    if (_observations.isEmpty) {
      return const Center(
        child: Text('No notes logged yet.',
            style: TextStyle(color: Color(0xFF546E7A))),
      );
    }

    final grouped = _grouped();
    final players = grouped.keys.toList()..sort();

    return RefreshIndicator(
      onRefresh: _load,
      color: const Color(0xFF4FC3F7),
      backgroundColor: const Color(0xFF1C2E3F),
      child: ListView(
        padding: const EdgeInsets.symmetric(vertical: 8),
        children: players.map((player) {
          final notes = grouped[player]!;
          return _PlayerSection(player: player, notes: notes);
        }).toList(),
      ),
    );
  }
}

class _PlayerSection extends StatefulWidget {
  final String player;
  final List<Map<String, dynamic>> notes;

  const _PlayerSection({required this.player, required this.notes});

  @override
  State<_PlayerSection> createState() => _PlayerSectionState();
}

class _PlayerSectionState extends State<_PlayerSection> {
  bool _expanded = true;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF1C2E3F),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          // Player header — tap to collapse/expand
          InkWell(
            onTap: () => setState(() => _expanded = !_expanded),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 12, 12),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 18,
                    backgroundColor: const Color(0xFF0D1B2A),
                    child: Text(
                      widget.player[0].toUpperCase(),
                      style: const TextStyle(
                          color: Color(0xFF4FC3F7), fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(widget.player,
                        style: const TextStyle(
                            color: Colors.white, fontSize: 15, fontWeight: FontWeight.w600)),
                  ),
                  Text('${widget.notes.length} note${widget.notes.length == 1 ? '' : 's'}',
                      style: const TextStyle(color: Color(0xFF546E7A), fontSize: 12)),
                  const SizedBox(width: 4),
                  Icon(_expanded ? Icons.expand_less : Icons.expand_more,
                      color: const Color(0xFF546E7A), size: 20),
                ],
              ),
            ),
          ),

          if (_expanded) ...[
            const Divider(height: 1, color: Color(0xFF0D1B2A)),
            ...widget.notes.asMap().entries.map((entry) {
              final i = entry.key;
              final obs = entry.value;
              final date = obs['session_date'] as String? ?? '';
              final notes = obs['notes'] as String? ?? '';
              return Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(date,
                            style: const TextStyle(
                                color: Color(0xFF4FC3F7), fontSize: 11,
                                fontWeight: FontWeight.w500)),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(notes,
                              style: const TextStyle(color: Color(0xFFCFD8DC), fontSize: 14)),
                        ),
                      ],
                    ),
                  ),
                  if (i < widget.notes.length - 1)
                    const Divider(height: 1, indent: 16, color: Color(0xFF0D1B2A)),
                ],
              );
            }),
          ],
        ],
      ),
    );
  }
}
