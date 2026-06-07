"""FastAPI HTTP layer for Coach Notes Organizer.

Architecture position:
    Flutter app → (HTTP) → FastAPI (this file) → engine → storage

Two endpoints:
    GET  /roster/{team_name}  — load the current roster for a team
    POST /chat                — send a coach message through the engine
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.engine.engine import process_request
from src.storage.storage_handler import get_players

app = FastAPI(title="Coach Notes Organizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    team_name: str
    user_input: str
    roster: list[str]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/roster/{team_name}")
def get_roster(team_name: str) -> dict:
    """Return the player name list for a team."""
    rows = get_players(team_name)
    return {"players": [r["player_name"] for r in rows]}


@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    """Route a coach's natural-language message through the engine.

    Returns the engine result dict unchanged — the Flutter app reads
    status, message, data, and missing directly.
    """
    return process_request(req.user_input, req.roster, req.team_name)
