// Widget tests for AuthScreen — UI structure and toggle behavior.
//
// Firebase is NOT initialized here. AuthScreen only accesses FirebaseAuth.instance
// inside _submit(), which is triggered by the button tap — never during build().
// These tests exercise UI rendering and the sign-in/sign-up toggle without
// submitting the form, so no Firebase connection is needed.
//
// Auth call correctness (signIn / createUser) belongs in integration tests
// once a Firebase emulator is configured.
//
// Run:
//     flutter test test/auth_screen_test.dart

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:coach_notes/screens/auth_screen.dart';

void main() {
  Widget _wrap(Widget child) => MaterialApp(home: child);

  // ── Test 1 ──────────────────────────────────────────────────────────────────

  testWidgets('renders email and password fields', (tester) async {
    await tester.pumpWidget(_wrap(const AuthScreen()));

    expect(
      find.byWidgetPredicate((w) =>
          w is TextField && w.decoration?.hintText == 'Email'),
      findsOneWidget,
    );
    expect(
      find.byWidgetPredicate((w) =>
          w is TextField && w.decoration?.hintText == 'Password'),
      findsOneWidget,
    );
  });

  // ── Test 2 ──────────────────────────────────────────────────────────────────

  testWidgets('shows Sign In button by default', (tester) async {
    await tester.pumpWidget(_wrap(const AuthScreen()));

    expect(find.text('Sign In'), findsOneWidget);
  });

  // ── Test 3 ──────────────────────────────────────────────────────────────────

  testWidgets('toggle shows Create Account button', (tester) async {
    await tester.pumpWidget(_wrap(const AuthScreen()));

    await tester.tap(find.text("Don't have an account? Sign up"));
    await tester.pump();

    expect(find.text('Create Account'), findsOneWidget);
  });

  // ── Test 4 ──────────────────────────────────────────────────────────────────

  testWidgets('toggle back returns to Sign In', (tester) async {
    await tester.pumpWidget(_wrap(const AuthScreen()));

    await tester.tap(find.text("Don't have an account? Sign up"));
    await tester.pump();

    await tester.tap(find.text('Already have an account? Sign in'));
    await tester.pump();

    expect(find.text('Sign In'), findsOneWidget);
  });
}
