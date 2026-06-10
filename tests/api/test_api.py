"""Unit tests for the API layer (FastAPI endpoints).

Storage functions and the engine are fully mocked — zero network calls.

Patch paths follow the Lab 6 rule: patch where symbols are USED (imported
into src.api.main), not where they are defined.
  - Storage: "src.api.main.get_team", "src.api.main.save_team", etc.
  - Engine:  "src.api.main.process_request"

Run:
    pytest tests/api/test_api.py -v
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app

_TEAM   = "Hawks"
_SPORT  = "football"
_UID    = "user-abc-123"
_ROSTER = ["Kyle", "Jordan"]


# ── POST /teams ────────────────────────────────────────────────────────────────

def test_create_team_success():
    """get_team→None, save_team→"success" → POST /teams returns success + sport_category."""
    with patch("src.api.main.get_team", return_value=None):
        with patch("src.api.main.save_team", return_value="success"):
            client = TestClient(app)
            response = client.post(
                "/teams",
                json={"team_name": _TEAM, "sport_category": _SPORT, "user_id": _UID},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["sport_category"] == _SPORT


def test_create_team_exists_returns_existing_sport():
    """get_team→existing row → POST /teams returns exists + stored sport_category."""
    existing = {"team_name": _TEAM, "sport_category": "basketball", "user_id": _UID}
    with patch("src.api.main.get_team", return_value=existing):
        client = TestClient(app)
        response = client.post(
            "/teams",
            json={"team_name": _TEAM, "sport_category": _SPORT, "user_id": _UID},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "exists"
    assert body["sport_category"] == "basketball"


def test_create_team_missing_user_id_returns_422():
    """POST /teams body omits user_id → Pydantic rejects with 422."""
    client = TestClient(app)
    response = client.post(
        "/teams",
        json={"team_name": _TEAM, "sport_category": _SPORT},
    )
    assert response.status_code == 422


# ── GET /teams ─────────────────────────────────────────────────────────────────

def test_list_teams_for_user():
    """get_teams_for_user→rows → GET /teams?user_id returns teams list."""
    mock_teams = [{"team_name": _TEAM, "sport_category": _SPORT, "user_id": _UID}]
    with patch("src.api.main.get_teams_for_user", return_value=mock_teams):
        client = TestClient(app)
        response = client.get(f"/teams?user_id={_UID}")

    assert response.status_code == 200
    assert response.json()["teams"] == mock_teams


def test_list_teams_missing_user_id_returns_422():
    """GET /teams with no user_id query param → FastAPI rejects with 422."""
    client = TestClient(app)
    response = client.get("/teams")
    assert response.status_code == 422


# ── GET /roster ────────────────────────────────────────────────────────────────

def test_roster_returns_players():
    """get_players→rows → GET /roster/{team_name} returns players list."""
    mock_players = [{"player_name": "Kyle", "position": "Forward"}]
    with patch("src.api.main.get_players", return_value=mock_players):
        client = TestClient(app)
        response = client.get(f"/roster/{_TEAM}")

    assert response.status_code == 200
    assert response.json()["players"] == mock_players


# ── POST /chat ─────────────────────────────────────────────────────────────────

def test_chat_routes_to_engine():
    """process_request→success dict → POST /chat passes result through unchanged."""
    engine_result = {"status": "success", "message": "Note logged.", "data": None}
    with patch("src.api.main.process_request", return_value=engine_result):
        client = TestClient(app)
        response = client.post(
            "/chat",
            json={
                "team_name": _TEAM,
                "user_input": "Kyle had great footwork today.",
                "roster": _ROSTER,
                "sport_category": _SPORT,
            },
        )

    assert response.status_code == 200
    assert response.json() == engine_result
