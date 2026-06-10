class ChatMessage {
  final String text;
  final bool isCoach;
  final String status;
  final List<String> missingNames;
  final Map<String, String> suggestions;
  final String originalInput;

  const ChatMessage({
    required this.text,
    required this.isCoach,
    this.status = 'success',
    this.missingNames = const [],
    this.suggestions = const {},
    this.originalInput = '',
  });

  factory ChatMessage.fromEngine(
    Map<String, dynamic> result, {
    String originalInput = '',
  }) {
    final status = result['status'] as String? ?? 'error';
    final message = result['message'] as String? ?? 'No response.';
    final data = result['data'] as List<dynamic>?;
    final missing = (result['missing'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        [];
    final suggestionsRaw =
        (result['suggestions'] as Map<String, dynamic>?) ?? {};
    final suggestions =
        suggestionsRaw.map((k, v) => MapEntry(k, v.toString()));

    String text = message;
    if (status == 'success' && data != null && data.isNotEmpty) {
      final rows = data.map((r) {
        final name = r['player_name'] ?? '';
        final notes = r['notes'] ?? '';
        final date = r['session_date'] ?? '';
        return notes.isNotEmpty ? '  • $name [$date]: $notes' : '  • $name';
      }).join('\n');
      text = '$message\n$rows';
    }

    return ChatMessage(
      text: text,
      isCoach: false,
      status: status,
      missingNames: missing,
      suggestions: suggestions,
      originalInput: originalInput,
    );
  }
}
