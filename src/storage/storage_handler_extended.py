"""Extended storage: read and delete operations for coaching observations."""

from __future__ import annotations

import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SERVICE_ACCOUNT_PATH = _PROJECT_ROOT / "service_account.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_NAME = os.environ.get("SPREADSHEET_NAME", "fieldbook-observations")

_OBS_ID_COL = 1
_PLAYER_ID_COL = 3


def _open_sheet() -> gspread.Worksheet:
    creds = Credentials.from_service_account_file(str(_SERVICE_ACCOUNT_PATH), scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open(SPREADSHEET_NAME).sheet1


def get_observations(player_id: str) -> list[dict]:
    """Return all observation rows for a given player_id as a list of dicts.

    Returns [] when no matching rows exist or on any exception.
    """
    try:
        sheet = _open_sheet()
        all_rows = sheet.get_all_records()
        return [row for row in all_rows if str(row.get("player_id", "")).strip() == player_id.strip()]
    except Exception:
        return []


def delete_observation(observation_id: str) -> str:
    """Delete the row whose observation_id matches.

    Returns:
        "success"   - matching row found and deleted.
        "not_found" - no row contains that observation_id.
        "error"     - any exception during the operation.
    """
    try:
        sheet = _open_sheet()
        cell = sheet.find(observation_id, in_column=_OBS_ID_COL)
        if cell is None or cell.row == 1:
            return "not_found"
        sheet.delete_rows(cell.row)
        return "success"
    except Exception:
        return "error"
