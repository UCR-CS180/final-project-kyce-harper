"""Storage layer: persists player and observation records to Google Sheets.

Architecture position:
    interface → engine → storage

Two sheets in one Google Sheets document:
  players:      player_id | team_name | player_name
  observations: obs_id | player_name | team_name | session_date | notes
"""

from __future__ import annotations

import os
from pathlib import Path

import gspread
from dotenv import load_dotenv

load_dotenv()

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SERVICE_ACCOUNT_PATH = _PROJECT_ROOT / "service_account.json"

SPREADSHEET_NAME = os.environ.get("SPREADSHEET_NAME", "coach-notes")

_PLAYER_COLUMNS  = ["player_id", "team_name", "player_name"]
_PLAYER_REQUIRED = set(_PLAYER_COLUMNS)

_OBS_COLUMNS  = ["obs_id", "player_name", "team_name", "session_date", "notes"]
_OBS_REQUIRED = set(_OBS_COLUMNS)


def _open_spreadsheet() -> gspread.Spreadsheet:
    client = gspread.service_account(filename=str(_SERVICE_ACCOUNT_PATH))
    return client.open(SPREADSHEET_NAME)


def save_player(data: dict) -> str:
    """Save a player to the 'players' sheet.

    Duplicate check on (team_name, player_name) before writing.

    Returns:
        "success" — row appended.
        "exists"  — same (team_name, player_name) already present; no write.
        "error"   — missing required keys or any exception.
    """
    if not _PLAYER_REQUIRED.issubset(data):
        return "error"
    try:
        ss = _open_spreadsheet()
        ws = ss.worksheet("players")
        rows = ws.get_all_records()
        for row in rows:
            if (
                row.get("team_name") == data["team_name"]
                and row.get("player_name", "").lower() == data["player_name"].lower()
            ):
                return "exists"
        ws.append_row([data[col] for col in _PLAYER_COLUMNS])
        return "success"
    except Exception:
        return "error"


def get_players(team_name: str) -> list[dict]:
    """Return all players for a team as a list of dicts.

    Returns [] on any exception.
    """
    try:
        ss = _open_spreadsheet()
        ws = ss.worksheet("players")
        rows = ws.get_all_records()
        return [r for r in rows if r.get("team_name") == team_name]
    except Exception:
        return []


def save_observation(data: dict) -> str:
    """Append an observation to the 'observations' sheet.

    No duplicate check — each note dump is a distinct record.

    Returns:
        "success" — row appended.
        "error"   — missing required keys or any exception.
    """
    if not _OBS_REQUIRED.issubset(data):
        return "error"
    try:
        ss = _open_spreadsheet()
        ws = ss.worksheet("observations")
        ws.append_row([data[col] for col in _OBS_COLUMNS])
        return "success"
    except Exception:
        return "error"


def get_observations(player_name: str, team_name: str) -> list[dict]:
    """Return all observations for a player on a team.

    Returns [] on any exception.
    """
    try:
        ss = _open_spreadsheet()
        ws = ss.worksheet("observations")
        rows = ws.get_all_records()
        return [
            r for r in rows
            if r.get("player_name") == player_name
            and r.get("team_name") == team_name
        ]
    except Exception:
        return []
