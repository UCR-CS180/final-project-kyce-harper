"""Engine layer: Tool Use + Reflection for Coach Notes Organizer.

Architecture position:
    interface → engine → storage

process_request() is the only public function. It:
  1. Calls Claude to extract intent + data from coach input (Tool Use pattern)
  2. For log_notes: calls Claude again to validate player names against the
     roster before any storage write (Reflection pattern)
  3. Dispatches to the correct storage function(s)
  4. For summary/advice: calls Claude a third time to synthesize a response

Return contract — every code path returns a dict with "status" and "message":
  {"status": "success",    "message": str, "data": list | None}
  {"status": "exists",     "message": str, "data": None}
  {"status": "incomplete", "message": str, "missing": list[str]}
  {"status": "unknown",    "message": str, "data": None}
  {"status": "error",      "message": str, "data": None}
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import date
from difflib import get_close_matches

import anthropic
from dotenv import load_dotenv

from src.storage.storage_handler import (
    get_observations,
    get_players,
    save_observation,
    save_player,
    update_player_position,
)

load_dotenv()

_MODEL = "claude-haiku-4-5-20251001"

# ── Personas ──────────────────────────────────────────────────────────────────

_PERSONAS: dict[str, str] = {
    "football": (
        "a grizzled southern NFL head coach — old-school Texas football, straight-talking, "
        "cowboy attitude. You call players by their first name, use southern expressions "
        "naturally ('I'll tell you what', 'ain't gonna sugarcoat it'), and hold players "
        "accountable while genuinely caring about their development."
    ),
    "basketball": (
        "an intense, analytics-driven NBA head coach. You talk fast, love metrics and "
        "efficiency, reference shot charts and defensive ratings, and push players to be "
        "mentally sharp. Direct, demanding, but fair."
    ),
    "soccer": (
        "a composed, technical European football manager. You speak precisely, value "
        "tactical intelligence and positioning, reference formations, and stay calm under "
        "pressure. Think Pep Guardiola energy — thoughtful and exacting."
    ),
    "baseball": (
        "a patient, old-school baseball skipper. You talk in baseball metaphors, believe "
        "in fundamentals and repetition, respect the game's history, and never rush a "
        "young player's development. Steady, wise, unhurried."
    ),
    "personal_training": (
        "a chill, funny, and motivational personal trainer. You keep sessions upbeat, use "
        "humor to push clients through tough sets, celebrate small wins loudly, and always "
        "make people feel capable. No judgment — just energy and results."
    ),
    "volleyball": (
        "an energetic, team-focused volleyball club coach. You read momentum well, emphasize "
        "communication and court awareness, and keep the vibe competitive but fun. You're "
        "loud on the sideline in the best way."
    ),
    "track": (
        "a methodical sprint and endurance coach. You live in split times, talk about "
        "form mechanics and periodization, and are precise about load and recovery. "
        "Data-driven, calm, relentlessly focused on marginal gains."
    ),
    "general": (
        "a professional, supportive, sport-agnostic coach. You are direct, encouraging, "
        "and adapt your language to whatever the athlete needs. No sport-specific jargon "
        "unless it fits the context."
    ),
}

_DEFAULT_PERSONA = _PERSONAS["general"]


def _get_persona(sport_category: str) -> str:
    return _PERSONAS.get(sport_category, _DEFAULT_PERSONA)


# ── Prompts ───────────────────────────────────────────────────────────────────

_EXTRACTION_PROMPT = """\
You are a Coach Notes Engine. Analyze the coach's message and return strict JSON only — no markdown, no code fences, no extra text.

Recognize exactly one intent:
  "add_player"     — coach wants to add one or more players to the roster
  "set_position"   — coach is assigning or updating a player's position or role
                     e.g. "Kyce is a QB", "Mark plays center", "Sara is our libero"
  "log_notes"      — coach is describing what players did in practice or a session
  "player_summary" — coach wants a summary, overview, or report of a specific player's history
  "improve_advice" — coach wants advice, a workout plan, training tips, or improvement help for a specific player
  "list_players"   — coach wants to see the current roster
  "unknown"        — input is completely unrelated to coaching, players, or practice

Response format per intent:

add_player (supports one OR multiple names):
{"intent": "add_player", "data": {"player_names": ["<name1>", "<name2>"]}}

set_position (normalize abbreviations to full names: QB→Quarterback, PG→Point Guard, GK→Goalkeeper, etc.):
{"intent": "set_position", "data": {"player_name": "<name>", "position": "<full position name>"}}

log_notes:
{"intent": "log_notes", "data": {"observations": [{"player_name": "<name>", "notes": "<observation>"}, ...]}}

player_summary or improve_advice:
{"intent": "<intent>", "data": {"player_name": "<name>"}}

list_players or unknown:
{"intent": "<intent>", "data": {}}"""

_REFLECTION_PROMPT = """\
You are a player-name validator for a sports coaching app.

The coach submitted a practice note. The engine extracted these player names:
{extracted_names}

The team's current roster is:
{roster}

For each extracted name: does it clearly refer to exactly one player on the roster?
- Valid: matches (or is an obvious abbreviation/nickname for) exactly one roster player.
- Invalid: matches zero players OR is ambiguous (could match more than one).

Return strict JSON only — no extra text:
{{"valid": <true|false>, "missing": ["<invalid_name>", ...]}}

valid=true only if EVERY extracted name maps to exactly one roster player.
If valid=true, missing must be []."""

_SUMMARY_PROMPT = """\
You are {persona}.

Summarize this player's practice history in your voice.

Player: {player_name}
Position: {position}
Team: {team_name}
Observations:
{observations_text}

Write a 2-3 sentence summary in your voice. Be honest about what you've seen.
Return strict JSON only — no markdown, no code fences:
{{"summary": "<your summary in your voice>"}}"""

_ADVICE_PROMPT = """\
You are {persona}.

Build a workout plan for this player.

Coach's request: {user_input}
Player: {player_name}
Position: {position}
Team: {team_name}
Total observations on file: {obs_count}
Observations:
{observations_text}

Rules:
- If the coach's request specifies a number of exercises, use exactly that number. Otherwise default to 5.
- If observations are limited (1-3 sessions), draw what you can from the notes and fill remaining slots with sound position-appropriate fundamentals. Never refuse or return fewer exercises than requested.
- Tailor exercises to the player's position and sport where relevant.
- For each exercise: give a specific name, a prescription (sets x reps or duration), and one concrete watch_for cue tied to what you've actually seen in the notes about THIS player.
- coach_note must mention how many sessions are on file, acknowledge we're still learning this player, and tell the coach what specific details to log next time to sharpen future plans.
- Write entirely in your coach persona voice.

Return strict JSON only — no markdown, no code fences:
{{"exercises": [{{"name": "<exercise>", "prescription": "<sets x reps or duration>", "watch_for": "<specific cue for this player>"}}], "coach_note": "<1-2 sentences in your voice>"}}"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _call_claude(client: anthropic.Anthropic, system: str, user: str) -> dict:
    msg = client.messages.create(
        model=_MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = msg.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


def _format_obs(obs_rows: list[dict]) -> str:
    return "\n".join(
        f"- [{r.get('session_date', '?')}] {r.get('notes', '')}"
        for r in obs_rows
    )


def _resolve_name(extracted: str, roster: list[str]) -> str:
    lower = extracted.lower()
    for name in roster:
        if name.lower() == lower:
            return name
    return extracted


def _player_position(player_name: str, team_name: str) -> str:
    """Look up a player's position from storage. Falls back to 'Player'."""
    players = get_players(team_name)
    for p in players:
        if p.get("player_name", "").lower() == player_name.lower():
            return str(p.get("position", "")) or "Player"
    return "Player"


# ── Public API ────────────────────────────────────────────────────────────────

def process_request(
    user_input: str,
    roster: list[str],
    team_name: str,
    sport_category: str = "general",
) -> dict:
    """Process a coach's natural-language input using Tool Use and Reflection.

    Args:
        user_input: Raw text from the coach.
        roster: Current player names for this team.
        team_name: The team's name used as a partition key in storage.
        sport_category: Sport type key — controls AI persona and advice style.

    Returns:
        dict with "status" and "message" keys. See module docstring for full contract.
    """
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        persona = _get_persona(sport_category)

        # ── Step 1: Tool Use — extract intent and data ────────────────────────
        extraction = _call_claude(client, _EXTRACTION_PROMPT, user_input)
        intent = extraction.get("intent", "unknown")
        data   = extraction.get("data", {})

        # ── Dispatch ──────────────────────────────────────────────────────────

        if intent == "add_player":
            names = data.get("player_names") or []
            if not names:
                single = data.get("player_name", "").strip()
                names = [single] if single else []
            if not names:
                return {"status": "error", "message": "Could not extract any player names.", "data": None}

            added, skipped = [], []
            for player_name in names:
                player_name = player_name.strip()
                row = {
                    "player_id":   str(uuid.uuid4()),
                    "team_name":   team_name,
                    "player_name": player_name,
                    "position":    "Player",
                }
                result = save_player(row)
                if result == "success":
                    added.append(player_name)
                elif result == "exists":
                    skipped.append(player_name)

            parts = []
            if added:
                parts.append(f"Added: {', '.join(added)}")
            if skipped:
                parts.append(f"Already on roster: {', '.join(skipped)}")
            status = "success" if added else "exists"
            return {"status": status, "message": " | ".join(parts), "data": None}

        if intent == "set_position":
            player_name = _resolve_name(data.get("player_name", "").strip(), roster)
            position = data.get("position", "").strip()
            if not position:
                return {"status": "error", "message": "Couldn't identify a position in that message.", "data": None}
            result = update_player_position(player_name, team_name, position)
            if result == "success":
                return {"status": "success", "message": f"Got it — {player_name} is now listed as {position}.", "data": None}
            elif result == "not_found":
                return {"status": "error", "message": f"{player_name} isn't on the roster yet. Add them first.", "data": None}
            else:
                return {"status": "error", "message": "Couldn't update the position. Try again.", "data": None}

        if intent == "log_notes":
            observations = data.get("observations", [])
            if not observations:
                return {"status": "error", "message": "No player observations found in your note.", "data": None}

            # ── Step 2: Reflection — validate names before any write ──────────
            extracted_names = [obs["player_name"] for obs in observations]
            reflection = _call_claude(
                client,
                "You are a JSON-only validator. Return only valid JSON.",
                _REFLECTION_PROMPT.format(
                    extracted_names=json.dumps(extracted_names),
                    roster=json.dumps(roster),
                ),
            )
            if not reflection.get("valid", False):
                missing = reflection.get("missing", [])
                suggestions = {}
                for name in missing:
                    matches = get_close_matches(name, roster, n=1, cutoff=0.5)
                    if not matches:
                        lower_map = {r.lower(): r for r in roster}
                        matches = get_close_matches(name.lower(), lower_map.keys(), n=1, cutoff=0.5)
                        if matches:
                            suggestions[name] = lower_map[matches[0]]
                    else:
                        suggestions[name] = matches[0]
                return {
                    "status": "incomplete",
                    "message": "Some player names in your note do not match the roster.",
                    "missing": missing,
                    "suggestions": suggestions,
                }

            # ── Step 3: Save one observation row per player ───────────────────
            today = date.today().isoformat()
            saved = 0
            for obs in observations:
                row = {
                    "obs_id":       str(uuid.uuid4()),
                    "player_name":  obs["player_name"],
                    "team_name":    team_name,
                    "session_date": today,
                    "notes":        obs["notes"],
                }
                if save_observation(row) == "success":
                    saved += 1

            if saved == 0:
                return {"status": "error", "message": "Storage error — no observations saved.", "data": None}
            return {"status": "success", "message": f"Logged notes for {saved} player(s).", "data": None}

        if intent == "list_players":
            players = get_players(team_name)
            return {
                "status": "success",
                "message": f"{len(players)} player(s) on the roster.",
                "data": players,
            }

        if intent == "player_summary":
            player_name = _resolve_name(data.get("player_name", "").strip(), roster)
            position = _player_position(player_name, team_name)
            obs_rows = get_observations(player_name, team_name)
            if not obs_rows:
                return {"status": "success", "message": f"No notes found for {player_name} yet.", "data": []}
            synthesis = _call_claude(
                client,
                "You are a JSON-only sports assistant. Return only valid JSON, no markdown.",
                _SUMMARY_PROMPT.format(
                    persona=persona,
                    player_name=player_name,
                    position=position,
                    team_name=team_name,
                    observations_text=_format_obs(obs_rows),
                ),
            )
            return {
                "status": "success",
                "message": synthesis.get("summary", "No summary generated."),
                "data": obs_rows,
            }

        if intent == "improve_advice":
            player_name = _resolve_name(data.get("player_name", "").strip(), roster)
            position = _player_position(player_name, team_name)
            obs_rows = get_observations(player_name, team_name)
            if not obs_rows:
                return {"status": "success", "message": f"No notes found for {player_name} yet.", "data": []}
            advice = _call_claude(
                client,
                "You are a JSON-only sports assistant. Return only valid JSON, no markdown.",
                _ADVICE_PROMPT.format(
                    persona=persona,
                    user_input=user_input,
                    player_name=player_name,
                    position=position,
                    team_name=team_name,
                    obs_count=len(obs_rows),
                    observations_text=_format_obs(obs_rows),
                ),
            )
            exercises = advice.get("exercises", [])
            coach_note = advice.get("coach_note", "")
            lines = [coach_note, ""]
            for i, ex in enumerate(exercises, 1):
                lines.append(f"{i}. {ex.get('name', '')} — {ex.get('prescription', '')}")
                lines.append(f"   \U0001f440 Watch: {ex.get('watch_for', '')}")
                lines.append("")
            return {
                "status": "success",
                "message": "\n".join(lines).strip(),
                "data": None,
            }

        # unknown — persona-aware fallback
        return {
            "status": "unknown",
            "message": "I can help you add players, log session notes, get a player summary, ask for improvement advice, or list your roster.",
            "data": None,
        }

    except Exception as exc:
        return {"status": "error", "message": str(exc), "data": None}
