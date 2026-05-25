"""Unit tests for the Fieldbook interface layer.

The engine layer is mocked — these tests run without a Gemini API key or
Google Sheets credentials.

Run:
    pytest tests/interface/test_interface.py -v
"""

from src.interface.cli import format_response, run_session


# ---------------------------------------------------------------------------
# Test 1: format_response — success with observation data
# ---------------------------------------------------------------------------
def test_format_success_with_data_shows_player_and_notes():
    result = {
        "status": "success",
        "message": "2 observation(s) found.",
        "data": [
            {"player_name": "Marcus Rodriguez", "notes": "Excellent footwork.", "tags": "technique"},
            {"player_name": "Jordan Hall", "notes": "Great attitude.", "tags": "mentality"},
        ],
    }
    output = format_response(result)
    assert "Marcus Rodriguez" in output
    assert "Excellent footwork." in output
    assert "Jordan Hall" in output


# ---------------------------------------------------------------------------
# Test 2: format_response — duplicate observation
# ---------------------------------------------------------------------------
def test_format_exists_shows_duplicate_message():
    result = {"status": "exists", "message": "Observation already logged.", "data": None}
    output = format_response(result)
    assert "already logged" in output


# ---------------------------------------------------------------------------
# Test 3: format_response — incomplete lists unresolved player names
# ---------------------------------------------------------------------------
def test_format_incomplete_lists_unresolved_names():
    result = {
        "status": "incomplete",
        "message": "Player names could not be uniquely resolved against the roster.",
        "missing": ["Marcus", "J. Hall"],
    }
    output = format_response(result)
    assert "Marcus" in output
    assert "J. Hall" in output


# ---------------------------------------------------------------------------
# Test 4: format_response — unknown intent includes help text
# ---------------------------------------------------------------------------
def test_format_unknown_includes_help_text():
    result = {
        "status": "unknown",
        "message": "I can log or retrieve coaching observations.",
        "data": None,
    }
    output = format_response(result)
    assert "log" in output.lower() or "list" in output.lower()


# ---------------------------------------------------------------------------
# Test 5: run_session — mocked engine, response appears in stdout
# ---------------------------------------------------------------------------
def test_run_session_prints_formatted_engine_response(monkeypatch, capsys):
    def mock_engine(coach_input):
        return {"status": "success", "message": "Logged observations for 1 player(s).", "data": None}

    inputs = iter(["Marcus had great footwork today.", "quit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    roster = ["Marcus Rodriguez", "Jordan Hall"]
    run_session(roster, process_fn=mock_engine)

    captured = capsys.readouterr()
    assert "Logged observations for 1 player(s)." in captured.out
