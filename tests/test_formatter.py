from datetime import datetime, timezone
from unittest.mock import patch
import pytz

import pytest

from src.calendar import Event
from src.formatter import DigestFormatter


class TestDigestFormatter:
    """Test DigestFormatter for message formatting."""

    def test_format_digest_with_events(self):
        """Test formatting digest with multiple events."""
        events = [
            Event(
                summary="Team Standup",
                start=datetime(2023, 6, 26, 9, 0, tzinfo=timezone.utc),
                end=datetime(2023, 6, 26, 9, 30, tzinfo=timezone.utc),
                location="Zoom",
                attendees=["alice@example.com", "bob@example.com"],
                description="Daily team sync",
            ),
            Event(
                summary="Product Sync",
                start=datetime(2023, 6, 26, 13, 0, tzinfo=timezone.utc),
                end=datetime(2023, 6, 26, 14, 0, tzinfo=timezone.utc),
                location="Conference Room A",
                attendees=["charlie@example.com"],
            ),
        ]

        with patch("src.formatter.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2023, 6, 26, 7, 0, tzinfo=timezone.utc
            )
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            formatter = DigestFormatter("Europe/London")
            digest = formatter.format_digest(events)

            expected_lines = [
                "Dear Olusegun! ",
                "",
                "Here's your schedule for today (Mon, June 26):",
                "",
                "- 09:00 – 09:30 \n Summary: Team Standup",
                "  Location: Zoom",
                "  Attendees: alice@example.com, bob@example.com",
                "  Description: Daily team sync",
                "\n<============================================================>\n",
                "- 13:00 – 14:00 \n Summary: Product Sync",
                "  Location: Conference Room A",
                "  Attendees: charlie@example.com",
                "\n<============================================================>\n",
                "\nHere's to a day full of wins, big and small!",
            ]

            assert digest == "\n".join(expected_lines)

    def test_format_digest_with_events_no_location(self):
        """Test formatting digest with events that have no location."""
        events = [
            Event(
                summary="Team Standup",
                start=datetime(2023, 6, 26, 9, 0, tzinfo=timezone.utc),
                end=datetime(2023, 6, 26, 9, 30, tzinfo=timezone.utc),
                attendees=["alice@example.com"],
            ),
        ]

        with patch("src.formatter.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2023, 6, 26, 7, 0, tzinfo=timezone.utc
            )
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            formatter = DigestFormatter("Europe/London")
            digest = formatter.format_digest(events)

            expected_lines = [
                "Dear Olusegun! ",
                "",
                "Here's your schedule for today (Mon, June 26):",
                "",
                "- 09:00 – 09:30 \n Summary: Team Standup",
                "  Attendees: alice@example.com",
                "\n<============================================================>\n",
                "\nHere's to a day full of wins, big and small!",
            ]

            assert digest == "\n".join(expected_lines)

    def test_format_digest_with_events_no_attendees(self):
        """Test formatting digest with events that have no attendees."""
        events = [
            Event(
                summary="Focus Time",
                start=datetime(2023, 6, 26, 10, 0, tzinfo=timezone.utc),
                end=datetime(2023, 6, 26, 11, 0, tzinfo=timezone.utc),
                location="Home Office",
            ),
        ]

        with patch("src.formatter.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2023, 6, 26, 7, 0, tzinfo=timezone.utc
            )
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            formatter = DigestFormatter("Europe/London")
            digest = formatter.format_digest(events)

            expected_lines = [
                "Dear Olusegun! ",
                "",
                "Here's your schedule for today (Mon, June 26):",
                "",
                "- 10:00 – 11:00 \n Summary: Focus Time",
                "  Location: Home Office",
                "\n<============================================================>\n",
                "\nHere's to a day full of wins, big and small!",
            ]

            assert digest == "\n".join(expected_lines)

    def test_format_digest_no_events(self):
        """Test formatting digest when there are no events."""
        with patch("src.formatter.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2023, 6, 26, 7, 0, tzinfo=timezone.utc
            )
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            formatter = DigestFormatter("Europe/London")
            digest = formatter.format_digest([])

            assert digest == "You have no meetings scheduled today. Enjoy your day!"

    def test_format_digest_different_timezone(self):
        """Test formatting digest with different timezone."""
        # Create events with local timezone (not UTC)
        ny_tz = pytz.timezone("America/New_York")
        start_local = ny_tz.localize(datetime(2023, 6, 26, 5, 0))  # 5:00 AM EDT
        end_local = ny_tz.localize(datetime(2023, 6, 26, 5, 30))  # 5:30 AM EDT

        events = [
            Event(
                summary="Team Standup",
                start=start_local,
                end=end_local,
                location="Zoom",
                attendees=["alice@example.com"],
            ),
        ]

        with patch("src.formatter.datetime") as mock_datetime:
            # Mock current time
            mock_datetime.now.return_value = datetime(2023, 6, 26, 7, 0)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            formatter = DigestFormatter("America/New_York")
            digest = formatter.format_digest(events)

            # Should show the local time (5:00 AM)
            assert "- 05:00 – 05:30" in digest

    def test_format_digest_with_description(self):
        """Test formatting digest with event description."""
        events = [
            Event(
                summary="Team Standup",
                start=datetime(2023, 6, 26, 9, 0, tzinfo=timezone.utc),
                end=datetime(2023, 6, 26, 9, 30, tzinfo=timezone.utc),
                location="Zoom",
                attendees=["alice@example.com"],
                description="Daily team sync to discuss progress and blockers",
            ),
        ]

        with patch("src.formatter.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2023, 6, 26, 7, 0, tzinfo=timezone.utc
            )
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            formatter = DigestFormatter("Europe/London")
            digest = formatter.format_digest(events)

            expected_lines = [
                "Dear Olusegun! ",
                "",
                "Here's your schedule for today (Mon, June 26):",
                "",
                "- 09:00 – 09:30 \n Summary: Team Standup",
                "  Location: Zoom",
                "  Attendees: alice@example.com",
                "  Description: Daily team sync to discuss progress and blockers",
                "\n<============================================================>\n",
                "\nHere's to a day full of wins, big and small!",
            ]

            assert digest == "\n".join(expected_lines)

    def test_format_digest_sorted_by_time(self):
        """Test that events are sorted by start time."""
        events = [
            Event(
                summary="Later Meeting",
                start=datetime(2023, 6, 26, 14, 0, tzinfo=timezone.utc),
                end=datetime(2023, 6, 26, 15, 0, tzinfo=timezone.utc),
            ),
            Event(
                summary="Earlier Meeting",
                start=datetime(2023, 6, 26, 9, 0, tzinfo=timezone.utc),
                end=datetime(2023, 6, 26, 10, 0, tzinfo=timezone.utc),
            ),
        ]

        with patch("src.formatter.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2023, 6, 26, 7, 0, tzinfo=timezone.utc
            )
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            formatter = DigestFormatter("Europe/London")
            digest = formatter.format_digest(events)

            # Check that earlier meeting comes first
            earlier_index = digest.find("Earlier Meeting")
            later_index = digest.find("Later Meeting")
            assert earlier_index < later_index

    def test_format_digest_edge_case_midnight(self):
        """Test formatting digest with events around midnight."""
        events = [
            Event(
                summary="Late Night Meeting",
                start=datetime(2023, 6, 26, 23, 30, tzinfo=timezone.utc),
                end=datetime(2023, 6, 27, 0, 30, tzinfo=timezone.utc),
                location="Zoom",
            ),
        ]

        with patch("src.formatter.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2023, 6, 26, 7, 0, tzinfo=timezone.utc
            )
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            formatter = DigestFormatter("Europe/London")
            digest = formatter.format_digest(events)

            # Should handle midnight crossing correctly
            assert "23:30 – 00:30" in digest or "23:30 – 01:30" in digest
