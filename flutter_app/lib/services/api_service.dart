import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // iOS simulator → localhost, Android emulator → 10.0.2.2
  static const String baseUrl = 'http://localhost:8000';

  /// Create a team. Returns the sport_category (may come back from an existing team).
  static Future<String> createOrGetTeam(String teamName, String sportCategory) async {
    final uri = Uri.parse('$baseUrl/teams');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'team_name': teamName, 'sport_category': sportCategory}),
    );
    if (response.statusCode == 200) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      return body['sport_category'] as String? ?? sportCategory;
    }
    return sportCategory;
  }

  /// Returns full player rows including position field.
  static Future<List<Map<String, dynamic>>> getRosterFull(String teamName) async {
    final uri = Uri.parse('$baseUrl/roster/${Uri.encodeComponent(teamName)}');
    final response = await http.get(uri);
    if (response.statusCode == 200) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      return List<Map<String, dynamic>>.from(body['players'] as List);
    }
    return [];
  }

  /// Convenience: just player names, for the engine roster validation.
  static Future<List<String>> getRosterNames(String teamName) async {
    final rows = await getRosterFull(teamName);
    return rows.map((r) => r['player_name'] as String? ?? '').where((n) => n.isNotEmpty).toList();
  }

  static Future<List<Map<String, dynamic>>> getAllObservations(String teamName) async {
    final uri = Uri.parse('$baseUrl/observations/${Uri.encodeComponent(teamName)}');
    final response = await http.get(uri);
    if (response.statusCode == 200) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      return List<Map<String, dynamic>>.from(body['observations'] as List);
    }
    return [];
  }

  static Future<Map<String, dynamic>> sendMessage(
    String teamName,
    String userInput,
    List<String> roster, {
    String sportCategory = 'general',
  }) async {
    final uri = Uri.parse('$baseUrl/chat');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'team_name': teamName,
        'user_input': userInput,
        'roster': roster,
        'sport_category': sportCategory,
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    return {'status': 'error', 'message': 'Server error ${response.statusCode}', 'data': null};
  }
}
