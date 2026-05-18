# Project Rules for Claude

## Follow Lab Examples Unless Told Otherwise

All architecture, implementation, testing, and TDD for this project must follow the patterns,
structure, and examples provided in the CS180 lab templates unless I explicitly say otherwise.

This applies to:
- **Software architecture** — `interface → engine → storage` 3-tier structure from Labs 4–6
- **File/folder structure** — mirror the lab scaffold (`src/storage`, `src/engine`, `src/interface`, `tests/`)
- **Storage layer** — follow `storage_handler.py` template from Lab 5/6; gspread + Google Sheets; return only `"success"`, `"exists"`, `"error"`; duplicate check in Python before any write
- **Engine layer** — follow `engine.py` template from Lab 6; Tool Use pattern (Gemini extracts intent + data) then Reflection pattern (second Gemini call validates completeness before storage is touched)
- **TDD workflow** — write failing tests first (red), then implement to make them pass (green); never implement before tests exist
- **Test structure** — mock storage in engine tests; hit real Google Sheets in storage integration tests; patch at the usage site (`src.engine.engine.<fn>`), not the definition site
- **Return contracts** — every engine path returns `{"status": ..., "message": ..., "data": ...}`; storage always returns one of the defined string statuses
- **Agent prompts** — use guardrail prompts from lab `AGENT_PROMPTS.md` files as the baseline
- **Milestones** — treat lab checkoff requirements and deliverables as the definition of done for each phase

## Git Commits

Never add Claude as a co-author or contributor in commit messages. No `Co-Authored-By` lines.

## Lab Reference Locations

Lab templates live in the sibling labs repo at:
`../Lab6/templates/` (engine, storage, tests)
`../Lab 5/` (storage patterns, agent prompts)
`../Lab 4/` (architecture contracts)
