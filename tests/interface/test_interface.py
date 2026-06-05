"""Unit tests for the interface layer.

Engine is mocked via dependency injection — no API calls or Sheets access.

Run:
    pytest tests/interface/test_interface.py -v
"""

from src.interface.cli import format_response, run_session


# ── format_response ───────────────────────────────────────────────────────────

def test_format_success_with_data_shows_player_info():
    result = {
        "status": "success",
        "message": "Logged notes for 2 player(s).",
        "data": [
            {"player_name": "John Smith",  "notes": "Great footwork.", "session_date": "2026-06-04"},
            {"player_name": "Sarah Jones", "notes": "Needs defense work.", "session_date": "2026-06-04"},
        ],
    }
    output = format_response(result)
    assert "John Smith" in output
    assert "Great footwork" in output
    assert "Sarah Jones" in output


def test_format_incomplete_lists_missing_player_names():
    result = {
        "status": "incomplete",
        "message": "Some player names do not match the roster.",
        "missing": ["Unknown Kid", "JJ"],
    }
    output = format_response(result)
    assert "Unknown Kid" in output
    assert "JJ" in output


def test_format_unknown_includes_help_text():
    result = {
        "status": "unknown",
        "message": "I can add players, log notes, summarize a player, or give advice.",
        "data": None,
    }
    output = format_response(result)
    lower = output.lower()
    assert "add" in lower or "log" in lower or "summary" in lower or "advice" in lower


def test_format_success_no_data_shows_message():
    result = {
        "status": "success",
        "message": "Added John Smith to the roster.",
        "data": None,
    }
    output = format_response(result)
    assert "John Smith" in output


# ── run_session ───────────────────────────────────────────────────────────────

def test_run_session_prints_formatted_engine_response(monkeypatch, capsys):
    def mock_engine(user_input):
        return {"status": "success", "message": "Logged notes for 1 player(s).", "data": None}

    inputs = iter(["John had great footwork today.", "quit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run_session(team_name="Varsity Hawks", process_fn=mock_engine)

    captured = capsys.readouterr()
    assert "Logged notes for 1 player(s)." in captured.out
