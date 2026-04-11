"""
Google Calendar service — fetches today's events.
Falls back gracefully if credentials aren't configured.
"""

import logging
from datetime import datetime, timedelta

import pytz
from moana import config

log = logging.getLogger(__name__)


def get_todays_events() -> list:
    """Fetch today's calendar events.
    Returns list of dicts: {summary, start_time, end_time, location}.
    Returns empty list if not configured.
    """
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import os.path
    except ImportError:
        log.info("Google Calendar libraries not installed, skipping.")
        return []

    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    creds_path = config.GOOGLE_CALENDAR_CREDENTIALS_PATH
    token_path = config.GOOGLE_CALENDAR_TOKEN_PATH

    if not os.path.exists(creds_path):
        log.info("Google Calendar credentials not found, skipping.")
        return []

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    parsed = []
    for event in events_result.get("items", []):
        start = event["start"].get("dateTime", event["start"].get("date", ""))
        end = event["end"].get("dateTime", event["end"].get("date", ""))

        try:
            start_str = datetime.fromisoformat(start).strftime("%-I:%M %p")
        except (ValueError, AttributeError):
            start_str = start

        try:
            end_str = datetime.fromisoformat(end).strftime("%-I:%M %p")
        except (ValueError, AttributeError):
            end_str = end

        parsed.append({
            "summary": event.get("summary", "Untitled"),
            "start_time": start_str,
            "end_time": end_str,
            "location": event.get("location", ""),
        })

    return parsed
