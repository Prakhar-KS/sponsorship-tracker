# Automated Sponsorship Outreach Tracker

A lightweight Python automation using the Gmail and Google Sheets APIs to send personalized cold outreach emails for campus event sponsorships (such as MNNIT Allahabad's E-Cell "Renaissance" E-Summit and TEDxMNNIT drives) and log every result in a shared Google Sheet. It replaces manually writing and tracking sponsorship emails one by one.

## Features
- **Automated Sending**: Uses Gmail API to send emails directly from your account.
- **Personalized Templates**: Fills placeholders like `{sponsor_name}` and `{company}`.
- **Idempotent**: Tracks status in Google Sheets ("Sent", "Pending", "Error") so re-runs never send duplicate emails.
- **Safe Execution**: Supports `--dry-run` to test rendering without sending, and `--draft-only` to stage drafts in Gmail.

## Architecture / Folder Tree
```text
sponsorship-tracker/
  src/
    __init__.py
    config.py          # Configuration & environment variables
    auth.py            # Google OAuth logic
    sheets_client.py   # Read/update Google Sheet
    gmail_client.py    # Build and send/draft emails
    template_engine.py # Load and render template.txt
    main.py            # CLI orchestration
  scripts/
    create_test_sheet.py # Generates a test Google Sheet
  template.txt         # Email body and subject template
  .env.example         # Environment variables template
  requirements.txt     # Python dependencies
  README.md            # Project documentation
```

## Prerequisites
- Python 3.9+
- A Google Cloud project with the **Gmail API** and **Google Sheets API** enabled.
- OAuth consent screen configured (with test users added if in testing mode).
- A Desktop OAuth client ID created. Download the JSON file, rename it to `credentials.json`, and place it in the project root.

## Installation
For Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Google Sheet Format
The Google Sheet should have the following columns (A to E):

| Sponsor Name | Email | Company | Status | Last Updated |
| --- | --- | --- | --- | --- |
| John Doe | john@example.com | TechCorp | | |
| Jane Smith | jane@example.com | Innovate Inc | Sent | 2026-10-07 10:00:00 |

- **Status Values**: 
  - Empty or "Pending": Will be processed.
  - "Sent": Will be skipped.
  - "Drafted": Will be skipped.
  - "Error: ...": Will be skipped on future runs unless cleared.

## Configuration
Copy `.env.example` to `.env` and fill in the values:
```env
SPREADSHEET_ID=your_spreadsheet_id_here
SHEET_NAME=Sponsors
SENDER_NAME=Your Name
SENDER_ROLE=Your Role
SENDER_PHONE=+91-XXXXXXXXXX
SEND_DELAY_SECONDS=5
```

## Usage
1. **Generate a Test Sheet**:
   ```bash
   python scripts/create_test_sheet.py
   ```
2. **Dry Run** (preview rendered emails):
   ```bash
   python -m src.main --dry-run
   ```
3. **Draft Only** (create Gmail drafts):
   ```bash
   python -m src.main --draft-only
   ```
4. **Full Run** (send emails):
   ```bash
   python -m src.main --limit 10
   ```

## Customizing Template
Edit `template.txt`. The first line must start with `Subject: `. Available placeholders: `{sponsor_name}`, `{company}`, `{sender_name}`, `{sender_role}`, `{sender_phone}`.

## Security Notes
- **Never** commit `credentials.json`, `token.json`, or `.env` to version control.
- If your OAuth consent screen is in "Testing" mode, the generated `token.json` will expire every 7 days, requiring re-authentication.
- Be mindful of Gmail API sending limits (usually 500 emails/day for standard accounts).

## Troubleshooting
- **invalid_grant / access_denied**: Ensure your email is added to the Test Users list in the Google Cloud Console.
- **403 insufficient scopes**: You may have modified the `SCOPES` in `config.py` after creating `token.json`. Delete `token.json` and authenticate again.

## License
MIT License
