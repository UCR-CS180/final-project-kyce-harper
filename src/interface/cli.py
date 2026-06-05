"""Interface layer: CLI presentation for Coach Notes Organizer.

Architecture position:
    interface → engine → storage

Responsibilities:
  - Ask for team name at startup
  - Load the roster from storage once at session start
  - Run a REPL loop, passing each coach message to the engine
  - Format the engine result dict into a human-readable string

This layer makes NO AI calls and does NOT write to storage directly.
"""

from __future__ import annotations

from src.engine.engine import process_request
from src.storage.storage_handler import get_players

_BANNER = """
========================================
  Coach Notes Organizer
========================================

Commands (just type naturally):
  Add players:      "Add Steve, Bradley, and Kyce"
  Log practice:     "Steve had great footwork, Bradley needs to work on defense"
  Player summary:   "Summarize Steve"
  Improve advice:   "How can I help Bradley improve?"
  List roster:      "List players"
  Quit:             quit / exit
"""

_HELP = (
    "I can help you:\n"
    "  - Add players:      'Add Steve, Bradley, and Kyce'\n"
    "  - Log practice:     'Steve had great footwork, Bradley needs defense work'\n"
    "  - Player summary:   'Summarize Steve'\n"
    "  - Improve advice:   'How can I help Bradley improve?'\n"
    "  - List roster:      'List players'"
)


def format_response(result: dict) -> str:
    """Convert an engine result dict to a human-readable string.

    Args:
        result: Dict with at minimum a "status" key.

    Returns:
        A plain string. Never raises.
    """
    status = result.get("status")

    if status == "success":
        out = result.get("message", "")
        data = result.get("data")
        if data:
            for row in data:
                name  = row.get("player_name", "")
                notes = row.get("notes", "")
                dt    = row.get("session_date", "")
                if notes:
                    out += f"\n  - {name} [{dt}]: {notes}"
                else:
                    out += f"\n  - {name}"
        return out

    if status == "exists":
        return result.get("message", "Already exists.")

    if status == "incomplete":
        missing = ", ".join(result.get("missing", []))
        return result.get("message", "") + f"\n  Unrecognized names: {missing}"

    if status == "unknown":
        return result.get("message", "") + "\n\n" + _HELP

    # "error" and anything unexpected
    return result.get("message", "An unexpected error occurred.")


def run_session(team_name: str, process_fn=None):
    """Run a REPL session for the given team.

    Args:
        team_name: Set once at startup; passed to process_request on every call.
        process_fn: Callable (user_input: str) -> dict. Defaults to a closure
                    over process_request with team_name and roster bound.
                    Pass a mock for testing — roster is not loaded when a
                    process_fn is provided.
    """
    if process_fn is None:
        roster: list[str] = [r["player_name"] for r in get_players(team_name)]

        def process_fn(user_input: str) -> dict:
            nonlocal roster
            res = process_request(user_input, roster=roster, team_name=team_name)
            # Refresh in-memory roster after any successful add_player
            if res.get("status") in ("success", "exists") and "Added:" in res.get("message", ""):
                roster = [r["player_name"] for r in get_players(team_name)]
            return res

        print(_BANNER)
        print(f"\nTeam: {team_name}")
        if roster:
            print(f"Roster: {', '.join(roster)}")
        else:
            print("Roster: (empty — add players first)")
        print()
    else:
        print(_BANNER)
        print(f"\nTeam: {team_name}\n")

    while True:
        try:
            user_input = input("Coach: ").strip()
        except EOFError:
            print("Goodbye!")
            return

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            return

        result = process_fn(user_input)
        print(f"Assistant: {format_response(result)}\n")


if __name__ == "__main__":
    team = input("Enter team name: ").strip()
    run_session(team_name=team)
