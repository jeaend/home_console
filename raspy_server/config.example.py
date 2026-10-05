IMAP_SERVER = "imap.gmail.com"
TARGET_EMAIL = "your-target-address@gmail.com"
EMAIL_USER = "your-account@gmail.com"
EMAIL_PASS = "your-app-password"

# Apple Calendar (iCloud)
# App-specific password: appleid.apple.com > Sign-In and Security > App-Specific Passwords
ICLOUD_USER = "your-apple-id@icloud.com"
ICLOUD_APP_PASSWORD = "xxxx-xxxx-xxxx-xxxx"
# Calendar names exactly as they appear in the Calendar app; leave empty to show all
CALENDAR_NAMES = ["Home", "Work"]

# iCal links: Google Calendar secret addresses and subscribed calendars
# Google: calendar.google.com > Settings > (pick a calendar) > Integrate calendar > Secret address in iCal format
# Subscribed (Mac Calendar): right-click the calendar > Get Info > URL
ICAL_URLS = [
    "https://calendar.google.com/calendar/ical/.../private-.../basic.ics",
    "webcal://example.com/subscribed.ics",
]
