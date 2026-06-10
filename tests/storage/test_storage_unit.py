"""Unit tests for new storage functions — get_teams_for_user and save_team with user_id.

gspread is fully mocked — zero network calls, no service account required.

Patch path follows the Lab 6 rule: patch where USED, not where defined.
  - "src.storage.storage_handler._open_spreadsheet"

Run:
    pytest tests/storage/test_storage_unit.py -v
"""

from unittest.mock import MagicMock, patch

from src.storage.storage_handler import get_teams_for_user, save_team

_TEAM  = "Hawks"
_SPORT = "football"
_UID   = "user-abc-123"
_OTHER = "user-xyz-999"


# ── get_teams_for_user ─────────────────────────────────────────────────────────

def test_get_teams_for_user_returns_matching_rows():
    """Sheet has two users' rows → only rows for _UID returned."""
    rows = [
        {"team_name": _TEAM,    "sport_category": _SPORT,        "user_id": _UID},
        {"team_name": "Lakers", "sport_category": "basketball",  "user_id": _OTHER},
    ]
    with patch("src.storage.storage_handler._open_spreadsheet") as mock_open:
        mock_ws = MagicMock()
        mock_open.return_value.worksheet.return_value = mock_ws
        mock_ws.get_all_records.return_value = rows

        result = get_teams_for_user(_UID)

    assert len(result) == 1
    assert result[0]["team_name"] == _TEAM


def test_get_teams_for_user_excludes_other_users():
    """Sheet has only other user's rows → result is empty for _UID."""
    rows = [{"team_name": "Lakers", "sport_category": "basketball", "user_id": _OTHER}]
    with patch("src.storage.storage_handler._open_spreadsheet") as mock_open:
        mock_ws = MagicMock()
        mock_open.return_value.worksheet.return_value = mock_ws
        mock_ws.get_all_records.return_value = rows

        result = get_teams_for_user(_UID)

    assert result == []


def test_get_teams_for_user_returns_empty_on_exception():
    """_open_spreadsheet raises → get_teams_for_user returns [] without crashing."""
    with patch(
        "src.storage.storage_handler._open_spreadsheet",
        side_effect=RuntimeError("timeout"),
    ):
        result = get_teams_for_user(_UID)

    assert result == []


# ── save_team ──────────────────────────────────────────────────────────────────

def test_save_team_writes_user_id():
    """save_team with full dict → append_row writes user_id in the 4th column position."""
    with patch("src.storage.storage_handler._open_spreadsheet") as mock_open:
        mock_ws = MagicMock()
        mock_open.return_value.worksheet.return_value = mock_ws
        mock_ws.get_all_records.return_value = []

        save_team({
            "team_id":       "t-001",
            "team_name":     _TEAM,
            "sport_category": _SPORT,
            "user_id":       _UID,
        })

    appended_row = mock_ws.append_row.call_args[0][0]
    assert appended_row[3] == _UID
