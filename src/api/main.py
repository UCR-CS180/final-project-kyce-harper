"""FastAPI HTTP layer for Coach Notes Organizer.

Architecture position:
    Flutter app → (HTTP) → FastAPI (this file) → engine → storage

Endpoints:
    POST /teams                  — create a team with sport category
    GET  /teams/{team_name}      — get team info (includes sport_category)
    GET  /roster/{team_name}     — player name list for a team
    GET  /observations/{team_name} — all observations for a team, newest first
    POST /chat                   — send a coach message through the engine
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.engine.engine import process_request
from src.storage.storage_handler import (
    get_all_observations,
    get_players,
    get_team,
    save_team,
)

app = FastAPI(title="Coach Notes Organizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ─────────────────────────────────────────────────────────────

class TeamRequest(BaseModel):
    team_name: str
    sport_category: str


class ChatRequest(BaseModel):
    team_name: str
    user_input: str
    roster: list[str]
    sport_category: str = "general"


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.post("/teams")
def create_team(req: TeamRequest) -> dict:
    """Create a team. Returns existing team unchanged if team_name already exists."""
    existing = get_team(req.team_name)
    if existing:
        return {"status": "exists", "sport_category": existing.get("sport_category", "general")}
    result = save_team({
        "team_id": str(uuid.uuid4()),
        "team_name": req.team_name,
        "sport_category": req.sport_category,
    })
    if result == "error":
        raise HTTPException(status_code=500, detail="Failed to save team.")
    return {"status": "success", "sport_category": req.sport_category}


@app.get("/teams/{team_name}")
def fetch_team(team_name: str) -> dict:
    """Return team record including sport_category."""
    team = get_team(team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")
    return team


@app.get("/roster/{team_name}")
def get_roster(team_name: str) -> dict:
    """Return full player rows (including position) for a team."""
    rows = get_players(team_name)
    return {"players": rows}


@app.get("/observations/{team_name}")
def get_team_observations(team_name: str) -> dict:
    """Return all observations for a team, newest first."""
    return {"observations": get_all_observations(team_name)}


@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    """Route a coach's natural-language message through the engine."""
    return process_request(req.user_input, req.roster, req.team_name, req.sport_category)
