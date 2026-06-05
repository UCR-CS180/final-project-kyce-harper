"""Unit tests for the engine layer (Tool Use + Reflection patterns).

Storage functions and the Anthropic client are fully mocked — zero network calls.

Patch paths follow the Lab 6 rule: patch where symbols are USED (imported),
not where they are defined.
  - Storage: "src.engine.engine.save_observation", etc.
  - Claude client: "anthropic.Anthropic"

Run:
    pytest tests/engine/test_engine.py -v
"""

import json
from unittest.mock import MagicMock, patch

from src.engine.engine import process_request

_ROSTER = ["John Smith", "Sarah Jones", "Mike Davis"]
_TEAM   = "Varsity Hawks"


def _build_mock_client(*response_dicts: dict) -> MagicMock:
    """Return a mock Anthropic client whose messages.create yields each dict in order."""
    client = MagicMock()
    responses = []
    for d in response_dicts:
        msg = MagicMock()
        msg.content = [MagicMock(text=json.dumps(d))]
        responses.append(msg)
    client.messages.create.side_effect = responses
    return client


# ── Test 1: log_notes — happy path ────────────────────────────────────────────

def test_log_notes_success():
    """Extraction → Reflection(valid) → save_observation called once per player."""
    extraction = {
        "intent": "log_notes",
        "data": {
            "observations": [
                {"player_name": "John Smith",  "notes": "Great footwork."},
                {"player_name": "Sarah Jones", "notes": "Needs work on defense."},
            ]
        },
    }
    reflection = {"valid": True, "missing": []}

    with patch("anthropic.Anthropic", return_value=_build_mock_client(extraction, reflection)):
        with patch("src.engine.engine.save_observation", return_value="success") as mock_save:
            result = process_request(
                "John had great footwork, Sarah needs work on defense.",
                roster=_ROSTER,
                team_name=_TEAM,
            )

    assert result["status"] == "success"
    assert "message" in result
    assert mock_save.call_count == 2


# ── Test 2: log_notes — unknown player blocked by Reflection ──────────────────

def test_log_notes_unknown_player_blocked():
    """Reflection failure → incomplete status, save_observation never called."""
    extraction = {
        "intent": "log_notes",
        "data": {
            "observations": [
                {"player_name": "John Smith",  "notes": "Great footwork."},
                {"player_name": "Unknown Kid", "notes": "Was there."},
            ]
        },
    }
    reflection = {"valid": False, "missing": ["Unknown Kid"]}

    with patch("anthropic.Anthropic", return_value=_build_mock_client(extraction, reflection)):
        with patch("src.engine.engine.save_observation") as mock_save:
            result = process_request(
                "John had great footwork, Unknown Kid was there.",
                roster=_ROSTER,
                team_name=_TEAM,
            )

    assert result["status"] == "incomplete"
    assert "missing" in result
    assert "Unknown Kid" in result["missing"]
    mock_save.assert_not_called()


# ── Test 3: player_summary — happy path ──────────────────────────────────────

def test_player_summary_success():
    """Extraction → get_observations(mocked) → synthesis → status 'success'."""
    extraction = {"intent": "player_summary", "data": {"player_name": "John Smith"}}
    synthesis  = {"summary": "John has shown strong footwork over multiple sessions."}

    mock_obs = [
        {"player_name": "John Smith", "team_name": _TEAM,
         "session_date": "2026-06-01", "notes": "Great footwork."},
    ]

    with patch("anthropic.Anthropic", return_value=_build_mock_client(extraction, synthesis)):
        with patch("src.engine.engine.get_observations", return_value=mock_obs):
            result = process_request(
                "Give me a summary for John Smith.",
                roster=_ROSTER,
                team_name=_TEAM,
            )

    assert result["status"] == "success"
    assert "message" in result
    assert result.get("data") is not None


# ── Test 4: improve_advice — happy path ──────────────────────────────────────

def test_improve_advice_success():
    """Extraction → get_observations(mocked) → advice → status 'success'."""
    extraction = {"intent": "improve_advice", "data": {"player_name": "Sarah Jones"}}
    advice     = {"advice": "Focus on defensive footwork drills twice a week."}

    mock_obs = [
        {"player_name": "Sarah Jones", "team_name": _TEAM,
         "session_date": "2026-06-01", "notes": "Needs work on defense."},
    ]

    with patch("anthropic.Anthropic", return_value=_build_mock_client(extraction, advice)):
        with patch("src.engine.engine.get_observations", return_value=mock_obs):
            result = process_request(
                "How can I help Sarah Jones improve?",
                roster=_ROSTER,
                team_name=_TEAM,
            )

    assert result["status"] == "success"
    assert "message" in result


# ── Test 5: unknown intent ────────────────────────────────────────────────────

def test_unknown_intent_returns_unknown_status():
    """Extraction returns 'unknown' → status 'unknown', no storage calls."""
    extraction = {"intent": "unknown", "data": {}}

    with patch("anthropic.Anthropic", return_value=_build_mock_client(extraction)):
        result = process_request(
            "What is the meaning of life?",
            roster=_ROSTER,
            team_name=_TEAM,
        )

    assert result["status"] == "unknown"
    assert "message" in result
