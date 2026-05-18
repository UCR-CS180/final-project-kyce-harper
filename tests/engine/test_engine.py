"""Unit tests for the Fieldbook engine layer (Tool Use + Reflection patterns).

Storage functions are mocked — these tests run without Google Sheets credentials.
Gemini calls are real — ensure GEMINI_API_KEY is set in .env.

Run:
    pytest tests/engine/test_engine.py -v

Patch path is "src.engine.engine.<fn>" because that is where the function is
imported (used), not where it is defined.
"""

from unittest.mock import patch
from src.engine.engine import process_request

_ROSTER = ["Marcus Rodriguez", "Jordan Hall", "Tyler Kim"]


# ---------------------------------------------------------------------------
# Test 1: Log observation — success path
# ---------------------------------------------------------------------------
def test_log_observation_success():
    with patch("src.engine.engine.save_observation", return_value="success"):
        result = process_request(
            "Marcus Rodriguez had excellent footwork today and showed great leadership.",
            roster=_ROSTER,
        )
    assert result["status"] == "success"
    assert "message" in result


# ---------------------------------------------------------------------------
# Test 2: Log observation — duplicate path
# ---------------------------------------------------------------------------
def test_log_observation_duplicate():
    with patch("src.engine.engine.save_observation", return_value="exists"):
        result = process_request(
            "Marcus Rodriguez had excellent footwork today and showed great leadership.",
            roster=_ROSTER,
        )
    assert result["status"] == "exists"
    assert "message" in result


# ---------------------------------------------------------------------------
# Test 3: List observations for a player
# ---------------------------------------------------------------------------
def test_list_observations_returns_success_with_data():
    mock_obs = [
        {"player_name": "Marcus Rodriguez", "notes": "Good footwork", "tags": "technique"}
    ]
    with patch("src.engine.engine.get_observations", return_value=mock_obs):
        result = process_request("Show me all observations.", roster=_ROSTER)
    assert result["status"] == "success"
    assert isinstance(result["data"], list)


# ---------------------------------------------------------------------------
# Test 4: Reflection — ambiguous name blocks storage call
# ---------------------------------------------------------------------------
def test_ambiguous_name_blocked_before_storage():
    ambiguous_roster = ["Marcus Rodriguez", "Marcus Liu", "Jordan Hall"]
    with patch("src.engine.engine.save_observation") as mock_save:
        result = process_request(
            "Marcus played well today.",
            roster=ambiguous_roster,
        )
    assert result["status"] == "incomplete"
    assert "missing" in result
    mock_save.assert_not_called()


# ---------------------------------------------------------------------------
# Test 5: Unknown intent — graceful fallback
# ---------------------------------------------------------------------------
def test_unknown_intent_returns_unknown_status():
    result = process_request("What is the meaning of life?", roster=_ROSTER)
    assert result["status"] == "unknown"
    assert "message" in result
