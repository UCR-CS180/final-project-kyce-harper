# Coach Notes Organizer

A CLI tool for coaches to log practice observations and get per-player summaries and improvement advice, backed by Google Sheets for persistence and Claude AI for natural-language understanding.

## What It Does

- Add players to a team roster
- Dump free-text practice notes — Claude extracts per-player observations and saves them
- Request a narrative summary of any player's history
- Ask how to help a specific player improve
- List the current roster

The **Reflection** safety gate validates every player name extracted from a note dump against the real roster before writing anything to storage. If a name doesn't match, the entire batch is rejected.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Sheets

1. Create a Google Sheet named `coach-notes`
2. Add two tabs with these exact header rows:
   - `players` tab: `player_id | team_name | player_name`
   - `observations` tab: `obs_id | player_name | team_name | session_date | notes`
3. Share the sheet with the service account email in `service_account.json`

### 3. Environment variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SPREADSHEET_NAME=coach-notes
```

Place your Google service account credentials file at `service_account.json` in the project root.

## How to Run

```bash
python3 -m src.interface.cli
```

You will be prompted for a team name, then the REPL starts.

## Usage Examples

```
Enter team name: Varsity Hawks

Coach: Add John Smith to the roster
Assistant: Added John Smith to the roster.

Coach: Add Sarah Jones to the roster
Assistant: Added Sarah Jones to the roster.

Coach: John had great footwork today, Sarah needs to work on her defensive positioning
Assistant: Logged notes for 2 player(s).

Coach: John had great footwork, Unknown Kid was there
Assistant: Some player names in your note do not match the roster.
  Unrecognized names: Unknown Kid

Coach: Give me a summary for John Smith
Assistant: John has consistently demonstrated strong footwork across multiple sessions...

Coach: How can I help Sarah Jones improve?
Assistant: Focus on defensive positioning drills — specifically lateral shuffles and drop-step...

Coach: List all players
Assistant: 2 player(s) on the roster.
  - John Smith
  - Sarah Jones

Coach: quit
Goodbye!
```

## Running Tests

```bash
# Engine + interface tests (fully mocked, no credentials needed)
python3 -m pytest tests/engine/ tests/interface/ -v

# Storage tests (requires service_account.json + live Google Sheet)
python3 -m pytest tests/storage/ -v

# Full suite with coverage
python3 -m pytest tests/ --cov=src --cov-report=term-missing -v
```

## Project Structure

```
src/
  storage/storage_handler.py   Google Sheets persistence (4 functions)
  engine/engine.py             Claude AI — Tool Use + Reflection patterns
  interface/cli.py             REPL loop + response formatting
tests/
  storage/test_storage.py      Integration tests (hit real Sheets)
  engine/test_engine.py        Unit tests (fully mocked)
  interface/test_interface.py  Unit tests (engine mocked)
CONTRACT.md                    Layer-by-layer API contracts
FUNCTIONALITY.md               Feature reference and scope
```
