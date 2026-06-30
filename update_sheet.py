import os
import io
import json
import requests
import pandas as pd
import gspread

from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

# ============================================================
# CONFIGURATION
# ============================================================

SHEET_ID = "1RN9qviprW8eCBz5BuftKyi_UqxDx3a-1NjjqVv2Fklw"
WORKSHEET_NAME = "Rista_Business_Level_New_Last_24_months"

REDASH_URL = os.getenv("RESDAH_QUERIES_10726")

# ============================================================
# Download CSV
# ============================================================

print("Downloading Redash data...")

response = requests.get(REDASH_URL, timeout=300)
response.raise_for_status()

df = pd.read_csv(io.StringIO(response.text), low_memory=False)

print(f"Rows : {len(df)}")
print(f"Columns : {len(df.columns)}")

# Replace NaN with blank
df = df.fillna("")

# Convert everything to string
df = df.astype(str)

# ============================================================
# Google Authentication
# ============================================================

service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    service_account_info,
    scopes=scopes
)

gc = gspread.authorize(credentials)

# ============================================================
# Open Sheet
# ============================================================

spreadsheet = gc.open_by_key(SHEET_ID)
worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

print("Connected to Google Sheet.")

# ============================================================
# Clear Existing Data
# ============================================================

worksheet.clear()

# ============================================================
# Upload Data
# ============================================================

values = [df.columns.tolist()] + df.values.tolist()

BATCH_SIZE = 5000

print("Uploading data...")

for i in range(0, len(values), BATCH_SIZE):

    batch = values[i:i + BATCH_SIZE]

    start_row = i + 1
    end_row = i + len(batch)

    cell_range = f"A{start_row}"

    worksheet.update(
        cell_range,
        batch,
        value_input_option="RAW"
    )

    print(f"Uploaded rows {start_row}-{end_row}")

print("Upload Completed Successfully.")
