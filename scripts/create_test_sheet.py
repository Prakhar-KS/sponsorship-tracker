import os
import sys

# Add parent dir to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth import get_sheets_service, get_gmail_service
from src.config import SHEET_NAME, logging

def update_env_file(spreadsheet_id):
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            
    with open(env_path, "w") as f:
        replaced = False
        for line in lines:
            if line.startswith("SPREADSHEET_ID="):
                f.write(f"SPREADSHEET_ID={spreadsheet_id}\n")
                replaced = True
            else:
                f.write(line)
        if not replaced:
            f.write(f"SPREADSHEET_ID={spreadsheet_id}\n")

def main():
    try:
        gmail = get_gmail_service()
        profile = gmail.users().getProfile(userId="me").execute()
        my_email = profile.get("emailAddress")
    except Exception as e:
        logging.error(f"Failed to fetch user profile: {e}")
        sys.exit(1)
        
    logging.info(f"Using email for testing: {my_email}")
    user_part, domain_part = my_email.split('@')
    
    test_emails = [
        f"{user_part}+test1@{domain_part}",
        f"{user_part}+test2@{domain_part}",
        f"{user_part}+test3@{domain_part}"
    ]

    sheets_service = get_sheets_service()
    
    spreadsheet_body = {
        'properties': {
            'title': 'Sponsorship Outreach - TEST'
        },
        'sheets': [
            {
                'properties': {
                    'title': SHEET_NAME,
                    'gridProperties': {
                        'frozenRowCount': 1
                    }
                }
            }
        ]
    }
    
    try:
        spreadsheet = sheets_service.spreadsheets().create(
            body=spreadsheet_body,
            fields='spreadsheetId,spreadsheetUrl,sheets.properties.sheetId'
        ).execute()
        
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        spreadsheet_url = spreadsheet.get('spreadsheetUrl')
        sheet_id = spreadsheet.get('sheets')[0].get('properties').get('sheetId')
    except Exception as e:
        logging.error(f"Failed to create spreadsheet: {e}")
        sys.exit(1)
        
    logging.info(f"Created Test Spreadsheet: {spreadsheet_url}")
    
    values = [
        ['Sponsor Name', 'Email', 'Company', 'Status', 'Last Updated'],
        ['Test Sponsor One', test_emails[0], 'Test Company A', '', ''],
        ['Test Sponsor Two', test_emails[1], 'Test Company B', '', ''],
        ['Test Sponsor Three', test_emails[2], 'Test Company C', '', '']
    ]
    
    try:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{SHEET_NAME}!A1:E4",
            valueInputOption="USER_ENTERED",
            body={'values': values}
        ).execute()
        
        # Bold formatting for header
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {'bold': True}
                    }
                },
                'fields': 'userEnteredFormat.textFormat.bold'
            }
        }]
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
    except Exception as e:
        logging.error(f"Failed to populate data: {e}")
        sys.exit(1)
        
    update_env_file(spreadsheet_id)
    logging.info(f"Updated .env with SPREADSHEET_ID={spreadsheet_id}")
    print(f"\nSUCCESS! Test sheet generated at:\n{spreadsheet_url}")

if __name__ == "__main__":
    main()
