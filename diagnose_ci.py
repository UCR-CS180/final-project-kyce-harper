"""CI diagnostic: verifies service_account.json and Sheets connectivity."""
import json
import os
import traceback
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

print("\n=== Google Sheets connection ===")
try:
    import gspread
    client = gspread.service_account(filename="service_account.json")
    ss = client.open(name)
    print(f"  Connected to : {ss.title!r}")
    print(f"  Worksheets   : {[ws.title for ws in ss.worksheets()]}")
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
