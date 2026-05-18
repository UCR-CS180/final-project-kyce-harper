"""Run from project root to confirm Google Sheets is wired up correctly.

    python verify_connection.py

Expected output:
    Connected to: fieldbook-observations
    Header row: ['observation_id', 'session_id', 'player_id', 'player_name', 'notes', 'tags']
    Row count (data only): 0
    Connection OK.
"""

from pathlib import Path
import gspread

_SERVICE_ACCOUNT_PATH = Path(__file__).resolve().parent / "service_account.json"
SPREADSHEET_NAME = "fieldbook-observations"
EXPECTED_HEADERS = ["observation_id", "session_id", "player_id", "player_name", "notes", "tags"]

client = gspread.service_account(filename=str(_SERVICE_ACCOUNT_PATH))
sheet = client.open(SPREADSHEET_NAME).sheet1

print(f"Connected to: {SPREADSHEET_NAME}")
headers = sheet.row_values(1)
print(f"Header row: {headers}")
print(f"Row count (data only): {len(sheet.get_all_records())}")

if headers != EXPECTED_HEADERS:
    print(f"ERROR: Expected headers {EXPECTED_HEADERS}, got {headers}")
else:
    print("Connection OK.")
