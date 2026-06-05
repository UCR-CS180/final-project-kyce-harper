"""CI diagnostic: verifies service_account.json, Sheets connectivity, and storage layer."""
import json
import os
import traceback
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env"))

print("=== service_account.json ===")
try:
    with open("service_account.json") as f:
        data = json.load(f)
    print(f"  client_email : {data.get('client_email')}")
    print(f"  project_id   : {data.get('project_id')}")
    print("  JSON parsed OK")
except Exception as e:
    print(f"  FAILED to parse: {e}")
    traceback.print_exc()

print("\n=== Environment ===")
name = os.environ.get("SPREADSHEET_NAME", "(not set)")
print(f"  SPREADSHEET_NAME = {name!r}")

print("\n=== storage_handler module values ===")
try:
    from src.storage import storage_handler as sh
    print(f"  _PROJECT_ROOT        = {sh._PROJECT_ROOT}")
    print(f"  _SERVICE_ACCOUNT_PATH = {sh._SERVICE_ACCOUNT_PATH}")
    print(f"  SPREADSHEET_NAME     = {sh.SPREADSHEET_NAME!r}")
    print(f"  sa file exists       = {sh._SERVICE_ACCOUNT_PATH.exists()}")
except Exception as e:
    print(f"  FAILED to import storage_handler: {e}")
    traceback.print_exc()

print("\n=== Google Sheets connection (direct) ===")
try:
    import gspread
    client = gspread.service_account(filename="service_account.json")
    ss = client.open(name)
    print(f"  Connected to : {ss.title!r}")
    print(f"  Worksheets   : {[ws.title for ws in ss.worksheets()]}")
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()

print("\n=== storage_handler.save_player (live call) ===")
try:
    from src.storage.storage_handler import save_player, _open_spreadsheet
    # Test _open_spreadsheet directly first
    ss2 = _open_spreadsheet()
    print(f"  _open_spreadsheet() succeeded: {ss2.title!r}")
    result = save_player({
        "player_id": str(uuid.uuid4()),
        "team_name": "diag-team",
        "player_name": "Diag Player",
    })
    print(f"  save_player result: {result!r}")
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
