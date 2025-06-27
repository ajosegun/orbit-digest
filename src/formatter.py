"""Message formatting for calendar digest."""

from datetime import datetime
from typing import List

from .calendar import Event
from loguru import logger


class DigestFormatter:
    """Formats calendar events into readable digest messages."""

    def __init__(self, timezone_str: str):
        """
        Initialize DigestFormatter.

        Args:
            timezone_str: IANA timezone string for formatting times.
        """
        self.timezone_str = timezone_str
        logger.info(f"Digest formatter initialized for timezone: {timezone_str}")

    def format_digest(self, events: List[Event]) -> str:
        """
        Format events into a digest message.

        Args:
            events: List of Event objects to format.

        Returns:
            Formatted digest message as string.
        """
        if not events:
            return "You have no meetings scheduled today. Enjoy your day!"

        # Sort events by start time
        sorted_events = sorted(events, key=lambda e: e.start)

        # Get current date for header
        now = datetime.now()
        day_name = now.strftime("%a")
        month_name = now.strftime("%B")
        day = now.day

        # Build digest
        lines = [
            "Dear Olusegun! ",
            "",
            f"Here's your schedule for today ({day_name}, {month_name} {day}):",
            "",
        ]

        for event in sorted_events:
            # Format time range
            start_time = event.start.strftime("%H:%M")
            end_time = event.end.strftime("%H:%M")

            # Add event line
            lines.append(f"- {start_time} – {end_time} \n Summary: {event.summary}")

            # Add location if available
            if event.location:
                lines.append(f"  Location: {event.location}")

            # Add attendees if available
            if event.attendees:
                attendees_str = ", ".join(event.attendees)
                lines.append(f"  Attendees: {attendees_str}")

            # Add description if available
            if event.description:
                lines.append(f"  Description: {event.description}")

            # Add spacing between events
            lines.append(
                "\n<============================================================>\n"
            )

        lines.append("\nHere's to a day full of wins, big and small!")
        # Remove trailing empty line
        if lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)
