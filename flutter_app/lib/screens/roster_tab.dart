import 'package:flutter/material.dart';
import '../services/api_service.dart';

class RosterTab extends StatefulWidget {
  final String teamName;
  final List<Map<String, dynamic>> rosterRows;
  final List<String> roster;
  final VoidCallback onRosterChanged;

  const RosterTab({
    super.key,
    required this.teamName,
    required this.rosterRows,
    required this.roster,
    required this.onRosterChanged,
  });

  @override
  State<RosterTab> createState() => _RosterTabState();
}

class _RosterTabState extends State<RosterTab> {
  final _controller = TextEditingController();
  bool _isAdding = false;
  String? _feedback;

  Future<void> _addPlayer() async {
    final name = _controller.text.trim();
    if (name.isEmpty) return;
    setState(() { _isAdding = true; _feedback = null; });

    final result = await ApiService.sendMessage(
      widget.teamName, 'Add $name', widget.roster);
    final status  = result['status']  as String? ?? 'error';
    final message = result['message'] as String? ?? '';

    if (!mounted) return;
    setState(() {
      _isAdding = false;
      _feedback = message;
    });

    if (status == 'success') {
      _controller.clear();
      widget.onRosterChanged();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Add player bar
        Container(
          color: const Color(0xFF1C2E3F),
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText: 'Player name',
                        hintStyle: const TextStyle(color: Color(0xFF546E7A)),
                        filled: true,
                        fillColor: const Color(0xFF0D1B2A),
                        contentPadding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 10),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10),
                          borderSide: BorderSide.none,
                        ),
                      ),
                      textInputAction: TextInputAction.done,
                      onSubmitted: (_) => _addPlayer(),
                    ),
                  ),
                  const SizedBox(width: 10),
                  ElevatedButton(
                    onPressed: _isAdding ? null : _addPlayer,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4FC3F7),
                      foregroundColor: const Color(0xFF0D1B2A),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 12),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                    child: _isAdding
                        ? const SizedBox(
                            width: 16, height: 16,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Color(0xFF0D1B2A)))
                        : const Text('Add',
                            style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              if (_feedback != null) ...[
                const SizedBox(height: 6),
                Text(_feedback!,
                    style: const TextStyle(
                        color: Color(0xFF90A4AE), fontSize: 12)),
              ],
            ],
          ),
        ),

        // Player list
        Expanded(
          child: widget.rosterRows.isEmpty
              ? const Center(
                  child: Text('No players yet. Add your first player above.',
                      style: TextStyle(color: Color(0xFF546E7A))),
                )
              : ListView.separated(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: widget.rosterRows.length,
                  separatorBuilder: (_, __) =>
                      const Divider(height: 1, color: Color(0xFF1C2E3F)),
                  itemBuilder: (context, index) {
                    final player = widget.rosterRows[index];
                    final name     = player['player_name'] as String? ?? '';
                    final position = player['position']    as String? ?? 'Player';
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundColor: const Color(0xFF1C2E3F),
                        child: Text(
                          name.isNotEmpty ? name[0].toUpperCase() : '?',
                          style: const TextStyle(
                              color: Color(0xFF4FC3F7),
                              fontWeight: FontWeight.bold),
                        ),
                      ),
                      title: Text(name,
                          style: const TextStyle(
                              color: Colors.white, fontSize: 15)),
                      subtitle: Text(position,
                          style: const TextStyle(
                              color: Color(0xFF4FC3F7), fontSize: 12)),
                      trailing: Text('#${index + 1}',
                          style: const TextStyle(
                              color: Color(0xFF546E7A), fontSize: 12)),
                    );
                  },
                ),
        ),
      ],
    );
  }
}
