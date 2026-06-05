# Coach Notes Organizer — Functionality Reference

## What This App Does

A CLI tool for coaches to log practice observations and get per-player summaries
and improvement advice, backed by Google Sheets for persistence.

## Supported Commands (natural language)

| What you type | Intent | What happens |
|---|---|---|
| "Add John Smith to the roster" | `add_player` | Saves player to `players` sheet |
| "John had great footwork, Sarah needs defense work" | `log_notes` | Extracts per-player notes, validates names against roster (Reflection), saves to `observations` sheet |
| "Give me a summary for John" | `player_summary` | Retrieves all of John's observations, returns a narrative paragraph |
| "How can I help Sarah improve?" | `improve_advice` | Retrieves Sarah's observations, returns 2-4 specific recommendations |
| "List all players" | `list_players` | Returns current roster for this team |
| Anything else | `unknown` | Returns help text listing available actions |

## Startup Sequence

1. App prompts: `Enter team name: `
2. Coach types the team name (e.g. "Varsity Hawks")
3. App loads the existing roster from Google Sheets for that team
4. REPL loop starts — every message is routed through the engine

## Reflection Safety Gate

When logging notes, Claude extracts player names from the free-text dump and
checks each one against the loaded roster. If any name does not match a roster
player, the **entire batch is rejected** and the coach is told which names are
unrecognized. Nothing is written to storage until all names are confirmed.

## Session Behavior

- Team name is set once at startup and held for the whole session
- Roster is loaded at startup and refreshed in memory after each successful `add_player`
- No state persists between sessions beyond what is in Google Sheets

## Known Limitations (MVP Scope)

- No deletion of players or observations
- No multi-team support within a single session
- Player names in note dumps must be close enough for Claude to match to the roster
- No session history or timestamped session IDs (only `session_date` is stored)
