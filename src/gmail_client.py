import base64
import time
from email.message import EmailMessage
from googleapiclient.errors import HttpError
from src.auth import get_gmail_service
from src.config import logging

class GmailClient:
    def __init__(self):
        self.service = get_gmail_service()

    def create_message(self, to_email: str, subject: str, body: str) -> dict:
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to_email
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': encoded_message}

    def send_email(self, to_email: str, subject: str, body: str, draft_only: bool = False) -> tuple:
        raw_msg = self.create_message(to_email, subject, body)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if draft_only:
                    draft = {'message': raw_msg}
                    self.service.users().drafts().create(userId="me", body=draft).execute()
                    return True, "Draft created"
                else:
                    self.service.users().messages().send(userId="me", body=raw_msg).execute()
                    return True, "Sent"
            except HttpError as error:
                status_code = error.resp.status
                if status_code in [429, 500, 502, 503, 504]:
                    delay = 2 ** attempt
                    logging.warning(f"HttpError {status_code}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    return False, f"HttpError: {error}"
            except Exception as e:
                return False, f"Error: {e}"
                
        return False, "Max retries exceeded"
