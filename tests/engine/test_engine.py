"""Unit tests for the Fieldbook engine layer (Tool Use + Reflection patterns).

Both storage functions AND Gemini API calls are mocked — these tests run
instantly with zero network calls and zero API quota consumed.

The Gemini mock controls exactly what the model "returns" so we can test
every code path deterministically.

Run:
    pytest tests/engine/test_engine.py -v
"""

import json
from unittest.mock import MagicMock, patch

from src.engine.engine import process_request

_ROSTER = ["Marcus Rodriguez", "Jordan Hall", "Tyler Kim"]


def _mock_client(extraction: dict, reflection: dict = None):
    """Build a mock genai.Client whose generate_content returns controlled JSON."""
    client = MagicMock()
    responses = []

    ext_resp = MagicMock()
    ext_resp.text = json.dumps(extraction)
    responses.append(ext_resp)

    if reflection is not None:
        ref_resp = MagicMock()
        ref_resp.text = json.dumps(reflection)
        responses.append(ref_resp)

    client.models.generate_content.side_effect = responses
    return client


# ---------------------------------------------------------------------------
# Test 1: Log observation — success path
# ---------------------------------------------------------------------------
def test_log_observation_success():
    extraction = {
        "intent": "log",
        "observations": [
            {"player_name_raw": "Marcus Rodriguez", "notes": "Excellent footwork.", "tags": ["technique"]}
        ],
    }
    reflection = {"complete": True, "unresolved": []}

    with patch("google.genai.Client", return_value=_mock_client(extraction, reflection)):
        with patch("src.engine.engine.save_observation", return_value="success"):
            result = process_request(
                "Marcus Rodriguez had excellent footwork today.",
                roster=_ROSTER,
            )
    assert result["status"] == "success"
    assert "message" in result


# ---------------------------------------------------------------------------
# Test 2: Log observation — duplicate path
# ---------------------------------------------------------------------------
def test_log_observation_duplicate():
    extraction = {
        "intent": "log",
        "observations": [
            {"player_name_raw": "Marcus Rodriguez", "notes": "Excellent footwork.", "tags": ["technique"]}
        ],
    }
    reflection = {"complete": True, "unresolved": []}

    with patch("google.genai.Client", return_value=_mock_client(extraction, reflection)):
        with patch("src.engine.engine.save_observation", return_value="exists"):
            result = process_request(
                "Marcus Rodriguez had excellent footwork today.",
                roster=_ROSTER,
            )
    assert result["status"] == "exists"
    assert "message" in result


# ---------------------------------------------------------------------------
# Test 3: List observations
# ---------------------------------------------------------------------------
def test_list_observations_returns_success_with_data():
    extraction = {"intent": "list", "observations": []}
    mock_obs = [
        {"player_name": "Marcus Rodriguez", "notes": "Good footwork", "tags": "technique"}
    ]

    with patch("google.genai.Client", return_value=_mock_client(extraction)):
        with patch("src.engine.engine.get_observations", return_value=mock_obs):
            result = process_request("Show me all observations.", roster=_ROSTER)

    assert result["status"] == "success"
    assert isinstance(result["data"], list)


# ---------------------------------------------------------------------------
# Test 4: Reflection — ambiguous name blocks storage call
# ---------------------------------------------------------------------------
def test_ambiguous_name_blocked_before_storage():
    extraction = {
        "intent": "log",
        "observations": [
            {"player_name_raw": "Marcus", "notes": "Played well.", "tags": ["mentality"]}
        ],
    }
    reflection = {"complete": False, "unresolved": ["Marcus"]}

    with patch("google.genai.Client", return_value=_mock_client(extraction, reflection)):
        with patch("src.engine.engine.save_observation") as mock_save:
            result = process_request(
                "Marcus played well today.",
                roster=["Marcus Rodriguez", "Marcus Liu", "Jordan Hall"],
            )

    assert result["status"] == "incomplete"
    assert "missing" in result
    mock_save.assert_not_called()


# ---------------------------------------------------------------------------
# Test 5: Unknown intent — graceful fallback
# ---------------------------------------------------------------------------
def test_unknown_intent_returns_unknown_status():
    extraction = {"intent": "unknown", "observations": []}

    with patch("google.genai.Client", return_value=_mock_client(extraction)):
        result = process_request("What is the meaning of life?", roster=_ROSTER)

    assert result["status"] == "unknown"
    assert "message" in result
