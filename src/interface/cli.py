"""Fieldbook interface layer — Presentation Layer (Skin) of the system.

Architecture position:
    interface -> engine -> storage

Collects coach input from the terminal, passes it to process_request() in
the engine layer, and formats the result dict into a human-readable string.

This layer makes no AI calls and does not access storage directly.
"""

from __future__ import annotations

from src.engine.engine import process_request

_WELCOME_BANNER = """
========================================
  Fieldbook — Coaching Assistant
  Type 'quit' or 'exit' to stop.
========================================
"""

_HELP_TEXT = (
    "I can help you:\n"
    "  - Log post-practice observations for players\n"
    "  - List existing observations\n"
    "Just describe what you want in plain English."
)

_DEFAULT_ROSTER = [
    "Marcus Rodriguez",
    "Jordan Hall",
    "Tyler Kim",
]


def format_response(result: dict) -> str:
    """Convert an engine result dict to a human-readable string.

    Always returns a plain string — never raises.
    """
    status = result.get("status")
    if status == "success":
        out = result["message"]
        data = result.get("data")
        if data:
            for obs in data:
                out += f"\n  - {obs['player_name']}: {obs['notes']} [{obs.get('tags', '')}]"
        return out
    elif status == "exists":
        return result["message"]
    elif status == "incomplete":
        return result["message"] + "\n  Unresolved: " + ", ".join(result["missing"])
    elif status == "unknown":
        return result["message"] + "\n\n" + _HELP_TEXT
    else:
        return result.get("message", "Unexpected response.")


def run_session(roster: list[str], process_fn=None):
    """Run a REPL session: read coach input, call engine, print formatted response.

    Parameters
    ----------
    roster:
        List of player names passed to the engine for disambiguation.
    process_fn:
        Callable that accepts a str and returns a dict. Defaults to a lambda
        wrapping process_request with the roster bound. Pass a mock here in
        tests so the session runs without a live AI or Google Sheets connection.
    """
    if process_fn is None:
        process_fn = lambda inp: process_request(inp, roster)

    print(_WELCOME_BANNER)
    print(f"Roster loaded: {', '.join(roster)}\n")

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
    run_session(_DEFAULT_ROSTER)
