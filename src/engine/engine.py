"""Fieldbook engine layer: Tool Use + Reflection design patterns.

Architecture position:
    interface -> engine -> storage

Receives raw coach input and a team roster. Uses Tool Use to extract
structured per-player observations, then Reflection to validate all
player names are unambiguous before any storage write occurs.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv

from src.storage.storage_handler import save_observation
from src.storage.storage_handler_extended import get_observations

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
_MODEL = os.getenv("MODEL_NAME", "gemini-2.5-flash")

# --- Prompts ---

_EXTRACTION_PROMPT = """
You are a Fieldbook Coaching Engine. Analyze the coach's post-practice input and extract intent and data.

Intents:
- "log": the coach is describing player performance (mentions players with observations)
- "list": the coach wants to retrieve existing observations
- "unknown": the input is unrelated to logging or listing observations

If intent is "log", extract per-player data. Tags must come only from this vocabulary:
technique, mentality, physical, flag, praise

Return strict JSON only — no extra text:
{
  "intent": "<log|list|unknown>",
  "observations": [
    {
      "player_name_raw": "<name as mentioned in the text>",
      "notes": "<clean observation string>",
      "tags": ["<tag>"]
    }
  ]
}

If intent is not "log", return an empty observations array.
""".strip()

_REFLECTION_PROMPT = """
You are a name resolution validator for a sports coaching app.

Extracted player name tokens: {extracted_names}
Team roster: {roster}

For each extracted name token, determine if it uniquely matches exactly one player on the roster.
A name is ambiguous if it partially matches more than one roster entry (e.g. "Marcus" when both
"Marcus Rodriguez" and "Marcus Liu" are on the roster).
A name is unresolvable if it matches no roster entry at all.

Return strict JSON only — no extra text:
{{"complete": <true|false>, "unresolved": ["<name_token>", ...]}}

Return complete=true only if every extracted name maps to exactly one roster player.
""".strip()


def process_request(coach_input: str, roster: list[str]) -> dict:
    """Process a coach's natural-language input using Tool Use and Reflection.

    Return contract (every path returns a dict with "status" and "message"):
    - {"status": "success",    "message": str, "data": list | None}
    - {"status": "exists",     "message": str, "data": None}
    - {"status": "incomplete", "message": str, "missing": list}
    - {"status": "unknown",    "message": str, "data": None}
    - {"status": "error",      "message": str, "data": None}
    """
    try:
        from google import genai
        from google.genai.types import HttpOptions

        client = genai.Client(http_options=HttpOptions(api_version="v1"))

        # --------------------------------------------------------------------
        # Step 1 — Tool Use: extract intent and per-player observations
        # --------------------------------------------------------------------
        extraction_response = client.models.generate_content(
            model=_MODEL,
            contents=coach_input,
            config={
                "system_instruction": _EXTRACTION_PROMPT,
                "response_mime_type": "application/json",
            },
        )
        extraction = json.loads(extraction_response.text)
        intent = extraction.get("intent", "unknown")
        observations = extraction.get("observations", [])

        # --------------------------------------------------------------------
        # Step 2 — Reflection: validate player names against roster before save
        # --------------------------------------------------------------------
        if intent == "log":
            extracted_names = [obs["player_name_raw"] for obs in observations]
            reflection_prompt = _REFLECTION_PROMPT.format(
                extracted_names=json.dumps(extracted_names),
                roster=json.dumps(roster),
            )
            reflection_response = client.models.generate_content(
                model=_MODEL,
                contents=reflection_prompt,
                config={"response_mime_type": "application/json"},
            )
            reflection = json.loads(reflection_response.text)

            if not reflection.get("complete", False):
                return {
                    "status": "incomplete",
                    "message": "Player names could not be uniquely resolved against the roster.",
                    "missing": reflection.get("unresolved", []),
                }

        # --------------------------------------------------------------------
        # Step 3 — Dispatch: call the correct storage function
        # --------------------------------------------------------------------
        if intent == "log":
            last_result = "error"
            for obs in observations:
                data = {
                    "observation_id": str(uuid.uuid4()),
                    "session_id": str(uuid.uuid4()),
                    "player_id": obs["player_name_raw"].lower().replace(" ", "_"),
                    "player_name": obs["player_name_raw"],
                    "notes": obs["notes"],
                    "tags": ",".join(obs.get("tags", [])),
                }
                last_result = save_observation(data)

            if last_result == "success":
                return {"status": "success", "message": f"Logged observations for {len(observations)} player(s).", "data": None}
            elif last_result == "exists":
                return {"status": "exists", "message": "Observation already logged for this session.", "data": None}
            else:
                return {"status": "error", "message": "Storage error.", "data": None}

        elif intent == "list":
            all_obs = get_observations("")
            return {"status": "success", "message": f"{len(all_obs)} observation(s) found.", "data": all_obs}

        else:
            return {"status": "unknown", "message": "I can log or retrieve coaching observations.", "data": None}

    except Exception as exc:
        return {"status": "error", "message": str(exc), "data": None}
