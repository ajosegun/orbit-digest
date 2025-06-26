from unittest.mock import Mock, patch

import pytest

from src.main import OrbitDigest


class TestOrbitDigest:
    """Test the main OrbitDigest integration class."""

    @patch("src.main.EmailSender")
    @patch("src.main.CalendarService")
    @patch("src.main.DigestFormatter")
    @patch("src.main.get_env_config")
    def test_orbit_digest_initialization(
        self, mock_get_config, mock_formatter, mock_calendar, mock_email
    ):
        """Test successful OrbitDigest initialization."""
        mock_config = {
            "google_client_id": "test_id",
            "google_client_secret": "test_secret",
            "google_refresh_token": "test_token",
            "resend_api_key": "test_resend_key",
            "email_recipient": "test@example.com",
            "timezone": "Europe/London",
            "digest_hour": 7,
            "quiet_hours_start": 22,
            "quiet_hours_end": 7,
            "sender_email": "test@example.com",
        }
        mock_get_config.return_value = mock_config

        mock_calendar_instance = Mock()
        mock_calendar.return_value = mock_calendar_instance

        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance

        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance

        digest = OrbitDigest()

        assert digest.calendar_service == mock_calendar_instance
        assert digest.email_sender == mock_email_instance
        assert digest.formatter == mock_formatter_instance
        assert digest.config == mock_config

    @patch("src.main.EmailSender")
    @patch("src.main.CalendarService")
    @patch("src.main.DigestFormatter")
    @patch("src.main.get_env_config")
    def test_run_digest_success(
        self, mock_get_config, mock_formatter, mock_calendar, mock_email
    ):
        """Test successful digest run with events."""
        from src.calendar import Event
        from datetime import datetime, timezone

        mock_config = {
            "google_client_id": "test_id",
            "google_client_secret": "test_secret",
            "google_refresh_token": "test_token",
            "resend_api_key": "test_resend_key",
            "email_recipient": "test@example.com",
            "timezone": "Europe/London",
            "digest_hour": 7,
            "quiet_hours_start": 22,
            "quiet_hours_end": 7,
            "sender_email": "test@example.com",
        }
        mock_get_config.return_value = mock_config

        # Mock calendar service
        mock_calendar_instance = Mock()
        mock_calendar.return_value = mock_calendar_instance
        events = [
            Event(
                summary="Team Standup",
                start=datetime(2023, 6, 26, 9, 0, tzinfo=timezone.utc),
                end=datetime(2023, 6, 26, 9, 30, tzinfo=timezone.utc),
                location="Zoom",
                attendees=["alice@example.com"],
            )
        ]
        mock_calendar_instance.get_today_events.return_value = events

        # Mock formatter
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance
        mock_formatter_instance.format_digest.return_value = "Formatted digest content"

        # Mock email sender
        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance
        mock_email_instance.send_digest.return_value = True

        digest = OrbitDigest()
        result = digest.run_digest()

        assert result is True
        mock_calendar_instance.get_today_events.assert_called_once_with(
            timezone_str="Europe/London", quiet_start=22, quiet_end=7
        )
        mock_formatter_instance.format_digest.assert_called_once_with(events)
        mock_email_instance.send_digest.assert_called_once_with(
            recipient="test@example.com", content="Formatted digest content"
        )

    @patch("src.main.EmailSender")
    @patch("src.main.CalendarService")
    @patch("src.main.DigestFormatter")
    @patch("src.main.get_env_config")
    def test_run_digest_no_events(
        self, mock_get_config, mock_formatter, mock_calendar, mock_email
    ):
        """Test digest run with no events."""
        mock_config = {
            "google_client_id": "test_id",
            "google_client_secret": "test_secret",
            "google_refresh_token": "test_token",
            "resend_api_key": "test_resend_key",
            "email_recipient": "test@example.com",
            "timezone": "Europe/London",
            "digest_hour": 7,
            "quiet_hours_start": 22,
            "quiet_hours_end": 7,
            "sender_email": "test@example.com",
        }
        mock_get_config.return_value = mock_config

        # Mock calendar service with no events
        mock_calendar_instance = Mock()
        mock_calendar.return_value = mock_calendar_instance
        mock_calendar_instance.get_today_events.return_value = []

        # Mock formatter
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance
        mock_formatter_instance.format_digest.return_value = (
            "You have no meetings scheduled today. Enjoy your day!"
        )

        # Mock email sender
        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance
        mock_email_instance.send_digest.return_value = True

        digest = OrbitDigest()
        result = digest.run_digest()

        assert result is True
        mock_formatter_instance.format_digest.assert_called_once_with([])

    @patch("src.main.EmailSender")
    @patch("src.main.CalendarService")
    @patch("src.main.DigestFormatter")
    @patch("src.main.get_env_config")
    def test_run_digest_calendar_error(
        self, mock_get_config, mock_formatter, mock_calendar, mock_email
    ):
        """Test digest run with calendar service error."""
        from googleapiclient.errors import HttpError

        mock_config = {
            "google_client_id": "test_id",
            "google_client_secret": "test_secret",
            "google_refresh_token": "test_token",
            "resend_api_key": "test_resend_key",
            "email_recipient": "test@example.com",
            "timezone": "Europe/London",
            "digest_hour": 7,
            "quiet_hours_start": 22,
            "quiet_hours_end": 7,
            "sender_email": "test@example.com",
        }
        mock_get_config.return_value = mock_config

        # Mock calendar service with error
        mock_calendar_instance = Mock()
        mock_calendar.return_value = mock_calendar_instance
        mock_calendar_instance.get_today_events.side_effect = HttpError(
            Mock(status=403), b"Access denied"
        )

        # Mock other services
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance

        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance

        digest = OrbitDigest()
        result = digest.run_digest()

        assert result is False
        mock_formatter_instance.format_digest.assert_not_called()
        mock_email_instance.send_digest.assert_not_called()

    @patch("src.main.EmailSender")
    @patch("src.main.CalendarService")
    @patch("src.main.DigestFormatter")
    @patch("src.main.get_env_config")
    def test_run_digest_email_failure(
        self, mock_get_config, mock_formatter, mock_calendar, mock_email
    ):
        """Test digest run with email failure."""
        from src.calendar import Event
        from datetime import datetime, timezone

        mock_config = {
            "google_client_id": "test_id",
            "google_client_secret": "test_secret",
            "google_refresh_token": "test_token",
            "resend_api_key": "test_resend_key",
            "email_recipient": "test@example.com",
            "timezone": "Europe/London",
            "digest_hour": 7,
            "quiet_hours_start": 22,
            "quiet_hours_end": 7,
            "sender_email": "test@example.com",
        }
        mock_get_config.return_value = mock_config

        # Mock calendar service
        mock_calendar_instance = Mock()
        mock_calendar.return_value = mock_calendar_instance
        events = [
            Event(
                summary="Team Standup",
                start=datetime(2023, 6, 26, 9, 0, tzinfo=timezone.utc),
                end=datetime(2023, 6, 26, 9, 30, tzinfo=timezone.utc),
                location="Zoom",
                attendees=["alice@example.com"],
            )
        ]
        mock_calendar_instance.get_today_events.return_value = events

        # Mock formatter
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance
        mock_formatter_instance.format_digest.return_value = "Formatted digest content"

        # Mock email sender with failure
        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance
        mock_email_instance.send_digest.return_value = False

        digest = OrbitDigest()
        result = digest.run_digest()

        # Should return False if email fails
        assert result is False
        mock_email_instance.send_digest.assert_called_once()
