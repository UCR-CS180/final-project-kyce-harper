"""Storage layer tests for Fieldbook.

These are integration tests — they hit a real Google Sheet.
Run only after Google Sheets is configured and service_account.json is in the project root.

Run:
    pytest tests/storage/test_storage.py -v
"""

import uuid
from src.storage.storage_handler import save_observation
from src.storage.storage_handler_extended import get_observations, delete_observation

_TEST_SESSION_ID = "test-session-001"


def _make_observation(player_id: str = None, name: str = "Test Player") -> dict:
    return {
        "observation_id": str(uuid.uuid4()),
        "session_id": _TEST_SESSION_ID,
        "player_id": player_id or str(uuid.uuid4()),
        "player_name": name,
        "notes": "Strong footwork. Good attitude throughout the session.",
        "tags": "technique,mentality",
    }


# ---------------------------------------------------------------------------
# Happy path — new observation is saved successfully
# ---------------------------------------------------------------------------
def test_save_observation_success():
    data = _make_observation()
    result = save_observation(data)
    assert result == "success"


# ---------------------------------------------------------------------------
# Duplicate path — same (session_id, player_id) is rejected
# ---------------------------------------------------------------------------
def test_save_observation_duplicate():
    player_id = str(uuid.uuid4())
    data = _make_observation(player_id=player_id)
    save_observation(data)

    duplicate = _make_observation(player_id=player_id)
    duplicate["session_id"] = _TEST_SESSION_ID
    result = save_observation(duplicate)
    assert result == "exists"


# ---------------------------------------------------------------------------
# Missing fields — returns error without writing
# ---------------------------------------------------------------------------
def test_save_observation_missing_fields():
    result = save_observation({"player_name": "Bob"})
    assert result == "error"


# ---------------------------------------------------------------------------
# Get observations — returns a list for a known player
# ---------------------------------------------------------------------------
def test_get_observations_returns_list():
    player_id = str(uuid.uuid4())
    data = _make_observation(player_id=player_id)
    save_observation(data)

    results = get_observations(player_id)
    assert isinstance(results, list)
    assert len(results) >= 1


# ---------------------------------------------------------------------------
# Delete observation — removes the row successfully
# ---------------------------------------------------------------------------
def test_delete_observation_success():
    obs_id = str(uuid.uuid4())
    data = _make_observation()
    data["observation_id"] = obs_id
    save_observation(data)

    result = delete_observation(obs_id)
    assert result == "success"


# ---------------------------------------------------------------------------
# Delete observation — not_found for unknown id
# ---------------------------------------------------------------------------
def test_delete_observation_not_found():
    result = delete_observation("nonexistent-id-xyz")
    assert result == "not_found"
