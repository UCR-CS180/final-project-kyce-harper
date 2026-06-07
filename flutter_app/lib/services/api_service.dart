import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // iOS simulator → localhost, Android emulator → 10.0.2.2
  static const String baseUrl = 'http://localhost:8000';

  static Future<List<String>> getRoster(String teamName) async {
    final uri = Uri.parse('$baseUrl/roster/${Uri.encodeComponent(teamName)}');
    final response = await http.get(uri);
    if (response.statusCode == 200) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      return List<String>.from(body['players'] as List);
    }
    return [];
  }

  static Future<Map<String, dynamic>> sendMessage(
    String teamName,
    String userInput,
    List<String> roster,
  ) async {
    final uri = Uri.parse('$baseUrl/chat');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'team_name': teamName,
        'user_input': userInput,
        'roster': roster,
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    return {'status': 'error', 'message': 'Server error ${response.statusCode}', 'data': null};
  }
}
