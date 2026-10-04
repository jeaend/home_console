import imaplib
from config import IMAP_SERVER, TARGET_EMAIL, EMAIL_USER, EMAIL_PASS

print(f"Connecting to {IMAP_SERVER} as {EMAIL_USER}...")
try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    print("✅ Successfully logged into IMAP server!")
    
    mail.select("inbox")
    status, messages = mail.search(None, f'(TO "{TARGET_EMAIL}")')
    if status == "OK":
        email_ids = messages[0].split()
        print(f"✅ Search successful! Found {len(email_ids)} emails matching TO: {TARGET_EMAIL}")
    else:
        print("⚠️ Connected and logged in, but search returned status:", status)
        
    mail.logout()
except Exception as e:
    print(f"❌ Connection failed: {e}")
