from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError

from src.calendar import CalendarService, Event


class TestEvent:
    """Test Event data class."""

    def test_event_creation(self):
        """Test Event object creation."""
        start_time = datetime(2023, 6, 26, 9, 0, tzinfo=timezone.utc)
        end_time = datetime(2023, 6, 26, 9, 30, tzinfo=timezone.utc)

        event = Event(
            summary="Test Meeting",
            start=start_time,
            end=end_time,
            location="Test Location",
            attendees=["test@example.com"],
            description="Test description",
        )

        assert event.summary == "Test Meeting"
        assert event.start == start_time
        assert event.end == end_time
        assert event.location == "Test Location"
        assert event.attendees == ["test@example.com"]
        assert event.description == "Test description"

    def test_event_creation_minimal(self):
        """Test Event object creation with minimal fields."""
        start_time = datetime(2023, 6, 26, 9, 0, tzinfo=timezone.utc)
        end_time = datetime(2023, 6, 26, 9, 30, tzinfo=timezone.utc)

        event = Event(
            summary="Test Meeting",
            start=start_time,
            end=end_time,
        )

        assert event.summary == "Test Meeting"
        assert event.start == start_time
        assert event.end == end_time
        assert event.location is None
        assert event.attendees == []
        assert event.description is None


class TestCalendarService:
    """Test CalendarService for Google Calendar integration."""

    @patch("src.calendar.build")
    @patch("src.calendar.Credentials")
    @patch("src.calendar.Request")
    def test_calendar_service_initialization(
        self, mock_request, mock_credentials, mock_build
    ):
        """Test successful CalendarService initialization."""
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        service = CalendarService("test_id", "test_secret", "test_token")

        assert service.service == mock_service
        mock_credentials.assert_called_once()
        mock_creds.refresh.assert_called_once_with(mock_request.return_value)
        mock_build.assert_called_once_with("calendar", "v3", credentials=mock_creds)

    @patch("src.calendar.build")
    @patch("src.calendar.Credentials")
    @patch("src.calendar.Request")
    def test_calendar_service_auth_error(
        self, mock_request, mock_credentials, mock_build
    ):
        """Test CalendarService initialization with auth error."""
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds
        mock_creds.refresh.side_effect = RefreshError(
            "Invalid refresh token", None, None
        )

        with pytest.raises(RefreshError):
            CalendarService("test_id", "test_secret", "invalid_token")

    @patch("src.calendar.build")
    @patch("src.calendar.Credentials")
    @patch("src.calendar.Request")
    def test_get_today_events_success(self, mock_request, mock_credentials, mock_build):
        """Test successful event retrieval."""
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock API response
        mock_events = Mock()
        mock_events.list.return_value.execute.return_value = {
            "items": [
                {
                    "summary": "Team Standup",
                    "start": {"dateTime": "2023-06-26T09:00:00Z"},
                    "end": {"dateTime": "2023-06-26T09:30:00Z"},
                    "location": "Zoom",
                    "attendees": [
                        {"email": "alice@example.com"},
                        {"email": "bob@example.com"},
                    ],
                    "description": "Daily team sync",
                }
            ]
        }
        mock_service.events.return_value = mock_events

        service = CalendarService("test_id", "test_secret", "test_token")
        events = service.get_today_events("Europe/London", 22, 7)

        assert len(events) == 1
        event = events[0]
        assert event.summary == "Team Standup"
        assert event.location == "Zoom"
        assert event.attendees == ["alice@example.com", "bob@example.com"]
        assert event.description == "Daily team sync"

    @patch("src.calendar.build")
    @patch("src.calendar.Credentials")
    @patch("src.calendar.Request")
    def test_get_today_events_filters_all_day(
        self, mock_request, mock_credentials, mock_build
    ):
        """Test that all-day events are filtered out."""
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock API response with all-day event
        mock_events = Mock()
        mock_events.list.return_value.execute.return_value = {
            "items": [
                {
                    "summary": "All Day Event",
                    "start": {"date": "2023-06-26"},
                    "end": {"date": "2023-06-26"},
                },
                {
                    "summary": "Regular Meeting",
                    "start": {"dateTime": "2023-06-26T09:00:00Z"},
                    "end": {"dateTime": "2023-06-26T09:30:00Z"},
                },
            ]
        }
        mock_service.events.return_value = mock_events

        service = CalendarService("test_id", "test_secret", "test_token")
        events = service.get_today_events("Europe/London", 22, 7)

        assert len(events) == 1
        assert events[0].summary == "Regular Meeting"

    @patch("src.calendar.build")
    @patch("src.calendar.Credentials")
    @patch("src.calendar.Request")
    def test_get_today_events_filters_cancelled(
        self, mock_request, mock_credentials, mock_build
    ):
        """Test that cancelled events are filtered out."""
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock API response with cancelled event
        mock_events = Mock()
        mock_events.list.return_value.execute.return_value = {
            "items": [
                {
                    "summary": "Cancelled Meeting",
                    "start": {"dateTime": "2023-06-26T09:00:00Z"},
                    "end": {"dateTime": "2023-06-26T09:30:00Z"},
                    "status": "cancelled",
                },
                {
                    "summary": "Regular Meeting",
                    "start": {"dateTime": "2023-06-26T10:00:00Z"},
                    "end": {"dateTime": "2023-06-26T10:30:00Z"},
                },
            ]
        }
        mock_service.events.return_value = mock_events

        service = CalendarService("test_id", "test_secret", "test_token")
        events = service.get_today_events("Europe/London", 22, 7)

        assert len(events) == 1
        assert events[0].summary == "Regular Meeting"

    @patch("src.calendar.build")
    @patch("src.calendar.Credentials")
    @patch("src.calendar.Request")
    def test_get_today_events_filters_quiet_hours(
        self, mock_request, mock_credentials, mock_build
    ):
        """Test that events in quiet hours are filtered out."""
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock API response with events in quiet hours
        # For Europe/London timezone, quiet hours are 22:00-07:00 (exclusive)
        # In summer (BST), London is UTC+1
        # These events should be filtered out:
        # 22:00 UTC = 23:00 local (quiet hours, since 23 >= 22)
        # 05:00 UTC = 06:00 local (quiet hours, since 6 < 7)
        # This event should remain:
        # 14:00 UTC = 15:00 local (not quiet hours)
        mock_events = Mock()
        mock_events.list.return_value.execute.return_value = {
            "items": [
                {
                    "summary": "Late Night Meeting",
                    "start": {"dateTime": "2023-06-26T22:00:00Z"},
                    "end": {"dateTime": "2023-06-26T22:30:00Z"},
                },
                {
                    "summary": "Early Morning Meeting",
                    "start": {"dateTime": "2023-06-26T05:00:00Z"},
                    "end": {"dateTime": "2023-06-26T05:30:00Z"},
                },
                {
                    "summary": "Regular Meeting",
                    "start": {"dateTime": "2023-06-26T14:00:00Z"},
                    "end": {"dateTime": "2023-06-26T14:30:00Z"},
                },
            ]
        }
        mock_service.events.return_value = mock_events

        service = CalendarService("test_id", "test_secret", "test_token")
        events = service.get_today_events("Europe/London", 22, 7)

        # Should only return the regular meeting (14:00 UTC = 15:00 local)
        # The 22:00 UTC event becomes 23:00 local, which IS quiet hours (23 >= 22)
        # The 05:00 UTC event becomes 06:00 local, which IS quiet hours (6 < 7)
        # The 14:00 UTC event becomes 15:00 local, which is NOT quiet hours
        assert len(events) == 1
        assert events[0].summary == "Regular Meeting"

    @patch("src.calendar.build")
    @patch("src.calendar.Credentials")
    @patch("src.calendar.Request")
    def test_get_today_events_api_error(
        self, mock_request, mock_credentials, mock_build
    ):
        """Test handling of API errors."""
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock API error
        mock_events = Mock()
        mock_events.list.return_value.execute.side_effect = HttpError(
            Mock(status=403), b"Access denied"
        )
        mock_service.events.return_value = mock_events

        service = CalendarService("test_id", "test_secret", "test_token")

        with pytest.raises(HttpError):
            service.get_today_events("Europe/London", 22, 7)

    @patch("src.calendar.build")
    @patch("src.calendar.Credentials")
    @patch("src.calendar.Request")
    def test_get_today_events_empty_response(
        self, mock_request, mock_credentials, mock_build
    ):
        """Test handling of empty API response."""
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock empty response
        mock_events = Mock()
        mock_events.list.return_value.execute.return_value = {"items": []}
        mock_service.events.return_value = mock_events

        service = CalendarService("test_id", "test_secret", "test_token")
        events = service.get_today_events("Europe/London", 22, 7)

        assert len(events) == 0
