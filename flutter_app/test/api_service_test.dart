// Unit tests for new ApiService methods using MockClient injection (Lab 7 pattern).
//
// No Firebase, no real server — MockClient from package:http/testing.dart
// intercepts every request and returns a controlled response.
//
// Run:
//     flutter test test/api_service_test.dart

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:coach_notes/services/api_service.dart';

const _uid   = 'user-abc-123';
const _team  = 'Hawks';
const _sport = 'football';

void main() {

  // ── ApiService.getTeamsForUser ───────────────────────────────────────────────

  group('ApiService.getTeamsForUser', () {

    test('returns parsed list on 200', () async {
      final mockClient = MockClient((_) async => http.Response(
        jsonEncode({
          'teams': [
            {'team_name': _team, 'sport_category': _sport, 'user_id': _uid},
          ],
        }),
        200,
      ));

      final result = await ApiService.getTeamsForUser(_uid, client: mockClient);

      expect(result.length, 1);
      expect(result[0]['team_name'], _team);
    });

    test('returns empty list on http error', () async {
      final mockClient = MockClient(
          (_) async => http.Response('Internal Server Error', 500));

      final result = await ApiService.getTeamsForUser(_uid, client: mockClient);

      expect(result, isEmpty);
    });
  });

  // ── ApiService.createOrGetTeam ───────────────────────────────────────────────

  group('ApiService.createOrGetTeam', () {

    test('returns sport_category from response', () async {
      final mockClient = MockClient((_) async => http.Response(
        jsonEncode({'status': 'success', 'sport_category': 'basketball'}),
        200,
      ));

      final result = await ApiService.createOrGetTeam(
          _team, _sport, _uid, client: mockClient);

      expect(result, 'basketball');
    });
  });
}
