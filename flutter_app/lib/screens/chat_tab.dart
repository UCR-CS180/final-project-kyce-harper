import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../services/api_service.dart';

class ChatTab extends StatefulWidget {
  final String teamName;
  final List<String> roster;
  final VoidCallback onRosterChanged;

  const ChatTab({
    super.key,
    required this.teamName,
    required this.roster,
    required this.onRosterChanged,
  });

  @override
  State<ChatTab> createState() => _ChatTabState();
}

class _ChatTabState extends State<ChatTab> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();

  final List<ChatMessage> _messages = [];
  bool _isLoading = false;
  bool _seeded = false;
  final Set<int> _resolvedMessages = {};

  static const _statusColors = {
    'success':    Color(0xFF4CAF50),
    'exists':     Color(0xFF64B5F6),
    'incomplete': Color(0xFFFFA726),
    'error':      Color(0xFFEF5350),
    'unknown':    Color(0xFF78909C),
  };

  @override
  void didUpdateWidget(ChatTab old) {
    super.didUpdateWidget(old);
    // Seed the welcome message once the roster arrives
    if (!_seeded && widget.roster.isNotEmpty) {
      _seeded = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        setState(() {
          _messages.add(ChatMessage(
            text: 'Roster loaded: ${widget.roster.join(', ')}.',
            isCoach: false,
            status: 'success',
          ));
        });
      });
    }
  }

  @override
  void initState() {
    super.initState();
    if (widget.roster.isNotEmpty) {
      _seeded = true;
      _messages.add(ChatMessage(
        text: 'Roster loaded: ${widget.roster.join(', ')}.',
        isCoach: false,
        status: 'success',
      ));
    } else {
      _messages.add(const ChatMessage(
        text: 'Roster is empty — add players in the Roster tab.',
        isCoach: false,
        status: 'success',
      ));
    }
  }

  Future<void> _send() async {
    final input = _controller.text.trim();
    if (input.isEmpty || _isLoading) return;
    _controller.clear();
    setState(() {
      _messages.add(ChatMessage(text: input, isCoach: true));
      _isLoading = true;
    });
    _scrollToBottom();
    final result = await ApiService.sendMessage(widget.teamName, input, widget.roster);
    if (!mounted) return;
    await _applyResult(result, originalInput: input);
  }

  Future<void> _sendSilent(String input) async {
    setState(() => _isLoading = true);
    final result = await ApiService.sendMessage(widget.teamName, input, widget.roster);
    if (!mounted) return;
    await _applyResult(result, originalInput: input);
  }

  Future<void> _applyResult(Map<String, dynamic> result, {required String originalInput}) async {
    final reply = ChatMessage.fromEngine(result, originalInput: originalInput);
    final message = result['message'] as String? ?? '';
    if (result['status'] == 'success' && message.contains('Added:')) {
      widget.onRosterChanged();
    }
    if (!mounted) return;
    setState(() {
      _messages.add(reply);
      _isLoading = false;
    });
    _scrollToBottom();
  }

  void _resolveAndSend(int index, String input) {
    setState(() => _resolvedMessages.add(index));
    _sendSilent(input);
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            controller: _scrollController,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            itemCount: _messages.length + (_isLoading ? 1 : 0),
            itemBuilder: (context, index) {
              if (index == _messages.length) return _buildTypingIndicator();
              return _buildBubble(_messages[index], index);
            },
          ),
        ),
        _buildInputBar(),
      ],
    );
  }

  Widget _buildBubble(ChatMessage msg, int index) {
    if (msg.isCoach) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(bottom: 10, left: 48),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: const BoxDecoration(
            color: Color(0xFF1565C0),
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(18),
              topRight: Radius.circular(18),
              bottomLeft: Radius.circular(18),
              bottomRight: Radius.circular(4),
            ),
          ),
          child: Text(msg.text, style: const TextStyle(color: Colors.white, fontSize: 15)),
        ),
      );
    }

    final borderColor = _statusColors[msg.status] ?? const Color(0xFF78909C);
    final showActions = msg.status == 'incomplete' &&
        msg.missingNames.isNotEmpty &&
        !_resolvedMessages.contains(index);

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10, right: 48),
        decoration: BoxDecoration(
          color: const Color(0xFF1C2E3F),
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(4),
            topRight: Radius.circular(18),
            bottomLeft: Radius.circular(18),
            bottomRight: Radius.circular(18),
          ),
          border: Border(left: BorderSide(color: borderColor, width: 3)),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(msg.text, style: const TextStyle(color: Colors.white, fontSize: 15)),
              if (msg.missingNames.isNotEmpty) ...[
                const SizedBox(height: 8),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: msg.missingNames.map((name) => Chip(
                    label: Text(name, style: const TextStyle(fontSize: 12, color: Colors.white)),
                    backgroundColor: const Color(0xFFFFA726),
                    padding: EdgeInsets.zero,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  )).toList(),
                ),
              ],
              if (showActions) ...[
                const SizedBox(height: 12),
                const Divider(color: Color(0xFF37474F), height: 1),
                const SizedBox(height: 10),
                ...msg.missingNames.expand((name) {
                  final suggestion = msg.suggestions[name];
                  return [
                    if (suggestion != null)
                      _ActionButton(
                        label: 'Did you mean "$suggestion"?',
                        icon: Icons.swap_horiz_rounded,
                        color: const Color(0xFF4FC3F7),
                        onTap: () => _resolveAndSend(
                            index, msg.originalInput.replaceAll(name, suggestion)),
                      ),
                    _ActionButton(
                      label: 'Add "$name" to roster',
                      icon: Icons.person_add_rounded,
                      color: const Color(0xFF4CAF50),
                      onTap: () => _resolveAndSend(index, 'Add $name'),
                    ),
                  ];
                }),
                const SizedBox(height: 2),
                GestureDetector(
                  onTap: () => setState(() => _resolvedMessages.add(index)),
                  child: const Text('Dismiss',
                      style: TextStyle(color: Color(0xFF546E7A), fontSize: 12)),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF1C2E3F),
          borderRadius: BorderRadius.circular(18),
        ),
        child: const SizedBox(
          width: 40,
          height: 16,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [_Dot(delay: 0), _Dot(delay: 150), _Dot(delay: 300)],
          ),
        ),
      ),
    );
  }

  Widget _buildInputBar() {
    return Container(
      color: const Color(0xFF1C2E3F),
      padding: EdgeInsets.only(
        left: 16, right: 8, top: 10,
        bottom: MediaQuery.of(context).padding.bottom + 10,
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Type a message...',
                hintStyle: const TextStyle(color: Color(0xFF546E7A)),
                filled: true,
                fillColor: const Color(0xFF0D1B2A),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
              ),
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _send(),
              maxLines: null,
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: _send,
            child: Container(
              width: 44, height: 44,
              decoration: const BoxDecoration(
                color: Color(0xFF4FC3F7),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.send_rounded, color: Color(0xFF0D1B2A), size: 20),
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({required this.label, required this.icon, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.12),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.4)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(width: 6),
            Flexible(child: Text(label,
                style: TextStyle(color: color, fontSize: 13, fontWeight: FontWeight.w500))),
          ],
        ),
      ),
    );
  }
}

class _Dot extends StatefulWidget {
  final int delay;
  const _Dot({required this.delay});

  @override
  State<_Dot> createState() => _DotState();
}

class _DotState extends State<_Dot> with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 600))
      ..repeat(reverse: true);
    _anim = Tween(begin: 0.3, end: 1.0).animate(
      CurvedAnimation(parent: _ctrl,
          curve: Interval(delay / 600, 1.0, curve: Curves.easeInOut)),
    );
  }

  @override
  void dispose() { _ctrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _anim,
      child: const CircleAvatar(radius: 4, backgroundColor: Color(0xFF4FC3F7)),
    );
  }
}
