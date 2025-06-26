"""Google Calendar integration for fetching events."""

from datetime import datetime, timezone
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from loguru import logger


class Event:
    """Data class representing a calendar event."""

    def __init__(
        self,
        summary: str,
        start: datetime,
        end: datetime,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        description: Optional[str] = None,
    ):
        self.summary = summary
        self.start = start
        self.end = end
        self.location = location
        self.attendees = attendees or []
        self.description = description


class CalendarService:
    """Service for interacting with Google Calendar API."""

    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        """
        Initialize CalendarService with OAuth credentials.

        Args:
            client_id: Google OAuth client ID.
            client_secret: Google OAuth client secret.
            refresh_token: Google OAuth refresh token.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token

        # Create credentials and service
        self.credentials = Credentials(
            None,  # No access token initially
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        )

        # Refresh credentials
        self.credentials.refresh(Request())

        # Build service
        self.service = build("calendar", "v3", credentials=self.credentials)
        logger.info("Calendar service initialized successfully")

    def get_today_events(
        self,
        timezone_str: str,
        quiet_start: Optional[int] = None,
        quiet_end: Optional[int] = None,
    ) -> List[Event]:
        """
        Get today's events from Google Calendar.

        Args:
            timezone_str: IANA timezone string.
            quiet_start: Start hour of quiet period (optional).
            quiet_end: End hour of quiet period (optional).

        Returns:
            List of Event objects for today.
        """
        import pytz

        # Get timezone
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)

        # Get start and end of today in the specified timezone
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        # Convert to UTC for API call
        start_utc = start_of_day.astimezone(pytz.UTC)
        end_utc = end_of_day.astimezone(pytz.UTC)

        logger.info(f"Fetching events for {now.date()} in {timezone_str}")

        try:
            # Call Calendar API
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=start_utc.isoformat(),
                    timeMax=end_utc.isoformat(),
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])
            logger.info(f"Found {len(events)} events")

            # Filter and convert events
            filtered_events = []
            for event in events:
                # Skip cancelled events
                if event.get("status") == "cancelled":
                    continue

                # Skip all-day events
                if "date" in event["start"]:
                    continue

                # Parse event data
                event_obj = self._parse_event(event, tz)

                # Filter by quiet hours if specified
                if quiet_start is not None and quiet_end is not None:
                    from .utils import is_quiet_hours

                    if is_quiet_hours(event_obj.start, quiet_start, quiet_end):
                        continue

                filtered_events.append(event_obj)

            logger.info(f"Returning {len(filtered_events)} filtered events")
            return filtered_events

        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            raise

    def _parse_event(self, event_data: dict, tz) -> Event:
        """
        Parse Google Calendar event data into Event object.

        Args:
            event_data: Raw event data from Google Calendar API.
            tz: Timezone object.

        Returns:
            Event object.
        """
        # Parse start and end times
        start_str = event_data["start"]["dateTime"]
        end_str = event_data["end"]["dateTime"]

        # Parse as UTC and convert to target timezone
        start_utc = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        end_utc = datetime.fromisoformat(end_str.replace("Z", "+00:00"))

        start_local = start_utc.astimezone(tz)
        end_local = end_utc.astimezone(tz)

        # Extract attendees
        attendees = []
        if "attendees" in event_data:
            attendees = [
                attendee.get("email", "") for attendee in event_data["attendees"]
            ]

        return Event(
            summary=event_data.get("summary", "No title"),
            start=start_local,
            end=end_local,
            location=event_data.get("location"),
            attendees=attendees,
            description=event_data.get("description"),
        )
