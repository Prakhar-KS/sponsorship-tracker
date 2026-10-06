import datetime
import sys
from src.config import SPREADSHEET_ID, SHEET_NAME, logging
from src.auth import get_sheets_service

class SheetsClient:
    def __init__(self):
        if not SPREADSHEET_ID:
            logging.error("SPREADSHEET_ID environment variable is missing. Please set it in .env")
            sys.exit(1)
        self.service = get_sheets_service()
        self.sheet = self.service.spreadsheets()

    def get_rows(self):
        result = self.sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:E"
        ).execute()
        rows = result.get('values', [])
        
        if not rows:
            raise ValueError("Sheet is empty.")
            
        header = rows[0]
        expected_header = ['Sponsor Name', 'Email', 'Company']
        if len(header) < 3 or header[:3] != expected_header:
            raise ValueError(f"Header row mismatch. Expected starting with {expected_header}, got {header}")
            
        return rows

    def update_status(self, row_number: int, status: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        range_name = f"{SHEET_NAME}!D{row_number}:E{row_number}"
        body = {
            'values': [[status, timestamp]]
        }
        self.sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
