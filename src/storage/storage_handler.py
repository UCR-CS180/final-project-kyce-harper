"""Storage layer: persists coaching observation records to Google Sheets via gspread."""

from __future__ import annotations

import os
from pathlib import Path

import gspread

REQUIRED_KEYS = {"observation_id", "session_id", "player_id", "player_name", "notes", "tags"}

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SERVICE_ACCOUNT_PATH = _PROJECT_ROOT / "service_account.json"

_COLUMNS = ["observation_id", "session_id", "player_id", "player_name", "notes", "tags"]
_SESSION_COL = _COLUMNS.index("session_id") + 1
_PLAYER_COL = _COLUMNS.index("player_id") + 1

SPREADSHEET_NAME = os.environ.get("SPREADSHEET_NAME", "fieldbook-observations")


def _get_worksheet() -> gspread.Worksheet:
    client = gspread.service_account(filename=str(_SERVICE_ACCOUNT_PATH))
    return client.open(SPREADSHEET_NAME).sheet1


def _existing_pairs(worksheet: gspread.Worksheet) -> set[tuple[str, str]]:
    """Return all (session_id, player_id) pairs already in the sheet."""
    sessions = worksheet.col_values(_SESSION_COL)[1:]
    players = worksheet.col_values(_PLAYER_COL)[1:]
    return {(s.strip(), p.strip()) for s, p in zip(sessions, players) if s and p}


def save_observation(data: dict) -> str:
    """Persist a coaching observation to Google Sheets.

    Returns:
        "success"  - record appended.
        "exists"   - same (session_id, player_id) already present; no write performed.
        "error"    - missing required fields or any unexpected exception.
    """
    if not REQUIRED_KEYS.issubset(data):
        return "error"

    try:
        worksheet = _get_worksheet()

        pair = (data["session_id"].strip(), data["player_id"].strip())
        if pair in _existing_pairs(worksheet):
            return "exists"

        worksheet.append_row([data[col] for col in _COLUMNS])
        return "success"

    except Exception:
        return "error"
