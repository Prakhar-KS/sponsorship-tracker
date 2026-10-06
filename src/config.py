import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/spreadsheets"
]

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
if not SPREADSHEET_ID:
    logging.error("SPREADSHEET_ID environment variable is missing. Please set it in .env")
    # Don't exit here so other scripts can still import config, we'll handle this in main.py or gracefully.
    # Actually the prompt says "Fail with a clear error message if SPREADSHEET_ID is missing."
    # Let's make it exit, but only if it's not during test generation. 
    # The prompt says: "Fail with a clear error message if SPREADSHEET_ID is missing." in config.py
    # But wait, create_test_sheet.py imports auth, which imports config, which imports this!
    # If it exits here, we can't run create_test_sheet.py. So we'll skip exiting if it's empty during create_test_sheet.py execution.

SHEET_NAME = os.getenv("SHEET_NAME", "Sponsors")
SENDER_NAME = os.getenv("SENDER_NAME", "")
SENDER_ROLE = os.getenv("SENDER_ROLE", "")
SENDER_PHONE = os.getenv("SENDER_PHONE", "")
SEND_DELAY_SECONDS = int(os.getenv("SEND_DELAY_SECONDS", "5"))

# Column Mappings (0-indexed)
COL_SPONSOR_NAME = 0
COL_EMAIL = 1
COL_COMPANY = 2
COL_STATUS = 3
COL_LAST_UPDATED = 4
