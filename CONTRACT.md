# Coach Notes Organizer — Layer Contracts

## Architecture

    interface (cli.py) → engine (engine.py) → storage (storage_handler.py)

Each layer communicates only with the layer directly below it.
The interface layer never calls storage. The storage layer never calls the engine.

---

## Storage Layer Contract

File: `src/storage/storage_handler.py`

### `save_player(data: dict) -> str`

**Required keys:** `player_id`, `team_name`, `player_name`

**Returns:**
- `"success"` — player row appended to the `players` sheet
- `"exists"` — same `(team_name, player_name)` already present; no write performed
- `"error"` — missing required keys OR any exception

**Duplicate check:** read existing `(team_name, player_name)` pairs from the sheet before writing.

---

### `get_players(team_name: str) -> list[dict]`

**Returns:** list of row dicts from the `players` sheet filtered to `team_name`.
Returns `[]` on any exception.

---

### `save_observation(data: dict) -> str`

**Required keys:** `obs_id`, `player_name`, `team_name`, `session_date`, `notes`

**Returns:**
- `"success"` — observation row appended to the `observations` sheet
- `"error"` — missing required keys OR any exception

No duplicate check — each note dump is a distinct record.

---

### `get_observations(player_name: str, team_name: str) -> list[dict]`

**Returns:** list of row dicts from the `observations` sheet where both
`player_name` and `team_name` match. Returns `[]` on any exception.

---

## Engine Layer Contract

File: `src/engine/engine.py`

### `process_request(user_input: str, roster: list[str], team_name: str) -> dict`

**Intents recognized:** `add_player`, `log_notes`, `player_summary`,
`improve_advice`, `list_players`, `unknown`

**Return shapes (all paths must include `status` and `message`):**

```
{"status": "success",    "message": str, "data": list | None}
{"status": "exists",     "message": str, "data": None}
{"status": "incomplete", "message": str, "missing": list[str]}
{"status": "unknown",    "message": str, "data": None}
{"status": "error",      "message": str, "data": None}
```

**Claude call sequence for `log_notes`:**
1. Extraction call → `{"intent": "log_notes", "data": {"observations": [...]}}`
2. Reflection call → `{"valid": bool, "missing": [...]}`
   - If `valid=False` → return `incomplete` immediately; storage is **never called**
   - If `valid=True` → call `save_observation()` once per player

**Claude call sequence for `player_summary` / `improve_advice`:**
1. Extraction call → `{"intent": "...", "data": {"player_name": "..."}}`
2. `get_observations(player_name, team_name)`
3. Synthesis call → `{"summary": "..."}` or `{"advice": "..."}`

---

## Interface Layer Contract

File: `src/interface/cli.py`

### `format_response(result: dict) -> str`

Pure function. Converts any engine result dict to a human-readable string.
Never raises. Never calls engine or storage.

### `run_session(team_name: str, process_fn=None)`

REPL loop. `process_fn` defaults to a closure over `process_request` with
`team_name` and `roster` bound. Accepts a mock via `process_fn` for testing.
Loads roster from storage at startup (only this layer–boundary crossing is permitted).
