"""Storage layer: persists team, player, and observation records to Google Sheets.

Architecture position:
    interface → engine → storage

Sheets in the Google Sheets document:
  teams:        team_id | team_name | sport_category
  players:      player_id | team_name | player_name | position
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

_TEAM_COLUMNS  = ["team_id", "team_name", "sport_category"]
_TEAM_REQUIRED = {"team_id", "team_name", "sport_category"}

_PLAYER_COLUMNS  = ["player_id", "team_name", "player_name", "position"]
_PLAYER_REQUIRED = {"player_id", "team_name", "player_name"}

_OBS_COLUMNS  = ["obs_id", "player_name", "team_name", "session_date", "notes"]
_OBS_REQUIRED = set(_OBS_COLUMNS)


def _open_spreadsheet() -> gspread.Spreadsheet:
    client = gspread.service_account(filename=str(_SERVICE_ACCOUNT_PATH))
    return client.open(SPREADSHEET_NAME)


# ── Team functions ─────────────────────────────────────────────────────────────

def save_team(data: dict) -> str:
    """Save a team to the 'teams' sheet. Deduplicates on team_name.

    Returns:
        "success" — row appended.
        "exists"  — team_name already present; no write.
        "error"   — missing required keys or any exception.
    """
    if not _TEAM_REQUIRED.issubset(data):
        return "error"
    try:
        ss = _open_spreadsheet()
        ws = ss.worksheet("teams")
        rows = ws.get_all_records()
        for row in rows:
            if row.get("team_name") == data["team_name"]:
                return "exists"
        ws.append_row([data[col] for col in _TEAM_COLUMNS])
        return "success"
    except Exception:
        return "error"


def get_team(team_name: str) -> dict | None:
    """Return the team record for team_name, or None if not found."""
    try:
        ss = _open_spreadsheet()
        ws = ss.worksheet("teams")
        rows = ws.get_all_records()
        for row in rows:
            if row.get("team_name") == team_name:
                return row
        return None
    except Exception:
        return None


# ── Player functions ───────────────────────────────────────────────────────────

def save_player(data: dict) -> str:
    """Save a player to the 'players' sheet.

    Duplicate check on (team_name, player_name) before writing.
    Position defaults to 'Player' if not provided.

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
        row_data = [
            data["player_id"],
            data["team_name"],
            data["player_name"],
            data.get("position", "Player"),
        ]
        ws.append_row(row_data)
        return "success"
    except Exception:
        return "error"


def get_players(team_name: str) -> list[dict]:
    """Return all players for a team as a list of dicts (includes position).

    Returns [] on any exception.
    """
    try:
        ss = _open_spreadsheet()
        ws = ss.worksheet("players")
        rows = ws.get_all_records()
        return [r for r in rows if r.get("team_name") == team_name]
    except Exception:
        return []


def update_player_position(player_name: str, team_name: str, position: str) -> str:
    """Update the position column for a player.

    Returns:
        "success"   — position updated.
        "not_found" — no matching (team_name, player_name) row.
        "error"     — any exception.
    """
    try:
        ss = _open_spreadsheet()
        ws = ss.worksheet("players")
        headers = ws.row_values(1)
        try:
            pos_col = headers.index("position") + 1  # 1-indexed
        except ValueError:
            return "error"
        rows = ws.get_all_records()
        for i, row in enumerate(rows, start=2):  # data starts at row 2
            if (
                row.get("team_name") == team_name
                and row.get("player_name", "").lower() == player_name.lower()
            ):
                ws.update_cell(i, pos_col, position)
                return "success"
        return "not_found"
    except Exception:
        return "error"


# ── Observation functions ──────────────────────────────────────────────────────

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


def get_all_observations(team_name: str) -> list[dict]:
    """Return all observations for a team sorted by session_date descending.

    Returns [] on any exception.
    """
    try:
        ss = _open_spreadsheet()
        ws = ss.worksheet("observations")
        rows = ws.get_all_records()
        team_rows = [r for r in rows if r.get("team_name") == team_name]
        return sorted(team_rows, key=lambda r: r.get("session_date", ""), reverse=True)
    except Exception:
        return []
