import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();

  late String _teamName;
  List<String> _roster = [];
  List<ChatMessage> _messages = [];
  bool _isLoading = false;
  bool _initialized = false;

  static const _statusColors = {
    'success':    Color(0xFF4CAF50),
    'exists':     Color(0xFF64B5F6),
    'incomplete': Color(0xFFFFA726),
    'error':      Color(0xFFEF5350),
    'unknown':    Color(0xFF78909C),
  };

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
    setState(() {
      _roster = players;
      _messages.add(ChatMessage(
        text: players.isEmpty
            ? 'Roster is empty — add your first player to get started.'
            : 'Roster loaded: ${players.join(', ')}.',
        isCoach: false,
        status: 'success',
      ));
    });
    _scrollToBottom();
  }

  Future<void> _send() async {
    final input = _controller.text.trim();
    if (input.isEmpty || _isLoading) return;

    _controller.clear();
    setState(() {
      _messages.add(ChatMessage(text: input, isCoach: true, status: 'success'));
      _isLoading = true;
    });
    _scrollToBottom();

    final result = await ApiService.sendMessage(_teamName, input, _roster);
    if (!mounted) return;

    final reply = ChatMessage.fromEngine(result);

    // Refresh roster after a successful add_player
    List<String> updatedRoster = _roster;
    if (result['status'] == 'success' &&
        (result['message'] as String? ?? '').contains('Added:')) {
      updatedRoster = await ApiService.getRoster(_teamName);
    }

    setState(() {
      _messages.add(reply);
      _roster = updatedRoster;
      _isLoading = false;
    });
    _scrollToBottom();
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
    return Scaffold(
      backgroundColor: const Color(0xFF0D1B2A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1C2E3F),
        foregroundColor: Colors.white,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_teamName, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            Text(
              '${_roster.length} player${_roster.length == 1 ? '' : 's'}',
              style: const TextStyle(fontSize: 12, color: Color(0xFF90A4AE)),
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length) return _buildTypingIndicator();
                return _buildBubble(_messages[index]);
              },
            ),
          ),
          _buildInputBar(),
        ],
      ),
    );
  }

  Widget _buildBubble(ChatMessage msg) {
    if (msg.isCoach) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(bottom: 10, left: 48),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: const Color(0xFF1565C0),
            borderRadius: const BorderRadius.only(
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
                const SizedBox(height: 6),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: msg.missingNames
                      .map((name) => Chip(
                            label: Text(name,
                                style: const TextStyle(fontSize: 12, color: Colors.white)),
                            backgroundColor: const Color(0xFFFFA726),
                            padding: EdgeInsets.zero,
                            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                          ))
                      .toList(),
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
            children: [
              _Dot(delay: 0),
              _Dot(delay: 150),
              _Dot(delay: 300),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInputBar() {
    return Container(
      color: const Color(0xFF1C2E3F),
      padding: EdgeInsets.only(
        left: 16,
        right: 8,
        top: 10,
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
              width: 44,
              height: 44,
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
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat(reverse: true);
    _anim = Tween(begin: 0.3, end: 1.0).animate(
      CurvedAnimation(
        parent: _ctrl,
        curve: Interval(widget.delay / 600, 1.0, curve: Curves.easeInOut),
      ),
    );
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _anim,
      child: const CircleAvatar(radius: 4, backgroundColor: Color(0xFF4FC3F7)),
    );
  }
}
