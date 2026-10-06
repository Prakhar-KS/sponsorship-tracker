import argparse
import time
import re
from src.config import SENDER_NAME, SENDER_ROLE, SENDER_PHONE, SEND_DELAY_SECONDS, logging, COL_SPONSOR_NAME, COL_EMAIL, COL_COMPANY, COL_STATUS
from src.sheets_client import SheetsClient
from src.gmail_client import GmailClient
from src.template_engine import render_template
from src.auth import get_credentials

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))

def main():
    parser = argparse.ArgumentParser(description="Automated Sponsorship Outreach Tracker")
    parser.add_argument("--dry-run", action="store_true", help="Render and log emails without sending or updating sheets")
    parser.add_argument("--draft-only", action="store_true", help="Create Gmail drafts instead of sending")
    parser.add_argument("--limit", type=int, help="Limit the number of emails to process")
    parser.add_argument("--template", type=str, default="template.txt", help="Path to template file")
    args = parser.parse_args()

    logging.info("Authenticating...")
    get_credentials()
    
    sheets = SheetsClient()
    gmail = GmailClient()
    
    logging.info("Reading sheet...")
    rows = sheets.get_rows()
    
    sent_count = 0
    skipped_count = 0
    error_count = 0
    
    # Skip header
    for i in range(1, len(rows)):
        if args.limit and sent_count >= args.limit:
            break
            
        row = rows[i]
        row_number = i + 1 # 1-indexed
        
        sponsor_name = row[COL_SPONSOR_NAME] if len(row) > COL_SPONSOR_NAME else ""
        email = row[COL_EMAIL] if len(row) > COL_EMAIL else ""
        company = row[COL_COMPANY] if len(row) > COL_COMPANY else ""
        status = row[COL_STATUS] if len(row) > COL_STATUS else ""
        
        if status and status.strip().lower() not in ["", "pending"]:
            skipped_count += 1
            logging.info(f"Row {row_number}: Skipped '{company}' (Status: {status})")
            continue
            
        if not is_valid_email(email):
            error_count += 1
            logging.error(f"Row {row_number}: Invalid email '{email}'")
            if not args.dry_run:
                sheets.update_status(row_number, "Error: invalid email")
            continue
            
        context = {
            "sponsor_name": sponsor_name,
            "company": company,
            "sender_name": SENDER_NAME,
            "sender_role": SENDER_ROLE,
            "sender_phone": SENDER_PHONE
        }
        
        try:
            subject, body = render_template(args.template, context)
        except Exception as e:
            error_count += 1
            logging.error(f"Row {row_number}: Template error: {e}")
            if not args.dry_run:
                sheets.update_status(row_number, f"Error: template issue")
            continue
            
        if args.dry_run:
            logging.info(f"[DRY RUN] Row {row_number} - To: {email}")
            logging.info(f"[DRY RUN] Subject: {subject}")
            logging.info(f"[DRY RUN] Body excerpt: {body[:100]}...")
            sent_count += 1
            continue
            
        success, detail = gmail.send_email(email, subject, body, draft_only=args.draft_only)
        if success:
            new_status = "Drafted" if args.draft_only else "Sent"
            sheets.update_status(row_number, new_status)
            sent_count += 1
            logging.info(f"Row {row_number}: {new_status} to {email}")
        else:
            sheets.update_status(row_number, f"Error: {detail[:20]}")
            error_count += 1
            logging.error(f"Row {row_number}: Failed to send to {email}. {detail}")
            
        if not args.draft_only and not args.dry_run:
            time.sleep(SEND_DELAY_SECONDS)
            
    logging.info(f"Summary: {sent_count} sent/drafted, {skipped_count} skipped, {error_count} errors.")

if __name__ == "__main__":
    main()
