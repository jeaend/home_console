import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import json
import os

# Load configuration if available
try:
    import config
    IMAP_SERVER = config.IMAP_SERVER
    EMAIL_USER = config.EMAIL_USER
    EMAIL_PASS = config.EMAIL_PASS
except ImportError:
    IMAP_SERVER = "imap.gmail.com"
    EMAIL_USER = "your_email@gmail.com"
    EMAIL_PASS = "your_app_password"

def fetch_latest_email():
    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        
        # Select the custom Kindle_Console folder instead of INBOX
        mail.select("Kindle_Console")
        
        # Search for all messages in the folder
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            return
            
        email_ids = messages[0].split()
        if not email_ids:
            # If no emails found, save an empty or default state
            cache_data = {"sender": "", "subject": "No messages in Kindle_Console"}
            with open("/tmp/latest_email.json", "w") as f:
                json.dump(cache_data, f)
            mail.logout()
            return
            
        # Get the latest email (last ID in the list)
        latest_id = email_ids[-1]
        status, msg_data = mail.fetch(latest_id, "(RFC822)")
        if status != "OK":
            mail.logout()
            return
            
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # Decode Subject
                subject_raw, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject_raw, bytes):
                    subject = subject_raw.decode(encoding or "utf-8", errors="ignore")
                else:
                    subject = str(subject_raw)
                    
                # Decode Sender
                from_raw, encoding = decode_header(msg["From"])[0]
                if isinstance(from_raw, bytes):
                    sender = from_raw.decode(encoding or "utf-8", errors="ignore")
                else:
                    sender = str(from_raw)
                    
                try:
                    received = parsedate_to_datetime(msg["Date"]).astimezone().isoformat()
                except Exception:
                    received = None

                cache_data = {
                    "sender": sender,
                    "subject": subject,
                    "received": received
                }
                
                with open("/tmp/latest_email.json", "w") as f:
                    json.dump(cache_data, f)
                    
        mail.logout()
    except Exception as e:
        print(f"Error fetching email: {e}")

if __name__ == "__main__":
    fetch_latest_email()
    print("Test fetch completed.")
