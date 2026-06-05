"""Integration tests for storage_handler.py.

These hit the real Google Sheet — requires service_account.json and
SPREADSHEET_NAME set in .env.

Run:
    pytest tests/storage/test_storage.py -v
"""

import uuid

from src.storage.storage_handler import (
    get_observations,
    get_players,
    save_observation,
    save_player,
)

_TEAM = "test-team-" + str(uuid.uuid4())[:8]


def _player(name: str = None) -> dict:
    return {
        "player_id": str(uuid.uuid4()),
        "team_name": _TEAM,
        "player_name": name or "Player-" + str(uuid.uuid4())[:4],
    }


def _observation(player_name: str = "Test Player") -> dict:
    return {
        "obs_id": str(uuid.uuid4()),
        "player_name": player_name,
        "team_name": _TEAM,
        "session_date": "2026-06-04",
        "notes": "Strong footwork during warm-up drills.",
    }


# ── save_player ───────────────────────────────────────────────────────────────

def test_save_player_success():
    assert save_player(_player()) == "success"


def test_save_player_exists():
    data = _player("Duplicate Danny")
    save_player(data)
    assert save_player(data) == "exists"


def test_save_player_missing_fields():
    assert save_player({"player_name": "No ID"}) == "error"


# ── save_observation ──────────────────────────────────────────────────────────

def test_save_observation_success():
    assert save_observation(_observation()) == "success"


def test_save_observation_missing_fields():
    assert save_observation({"notes": "good session"}) == "error"


# ── get_observations ──────────────────────────────────────────────────────────

def test_get_observations_returns_saved_rows():
    name = "Observable Oscar " + str(uuid.uuid4())[:4]
    save_observation(_observation(name))
    results = get_observations(name, _TEAM)
    assert isinstance(results, list)
    assert len(results) >= 1
    assert all(r["player_name"] == name for r in results)
