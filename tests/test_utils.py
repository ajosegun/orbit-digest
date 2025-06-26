import os
from datetime import datetime, time
from unittest.mock import patch
from dotenv import load_dotenv

load_dotenv()

import pytest
import pytz

from src.utils import (
    get_env_config,
    is_quiet_hours,
    parse_time_string,
    validate_timezone,
)


class TestUtils:
    """Test utilities for configuration and timezone handling."""

    def test_get_env_config_success(self):
        """Test successful environment configuration loading."""
        with patch.dict(
            os.environ,
            {
                "GOOGLE_REFRESH_TOKEN": "test_token",
                "GOOGLE_CLIENT_ID": "test_id",
                "GOOGLE_CLIENT_SECRET": "test_secret",
                "RESEND_API_KEY": "test_resend_key",
                "TIMEZONE": "Europe/London",
                "DIGEST_HOUR": "7",
                "QUIET_HOURS_START": "22",
                "QUIET_HOURS_END": "07",
                "EMAIL_RECIPIENT": "test@example.com",
                "SENDER_EMAIL": "test@example.com",
            },
        ):
            config = get_env_config()
            assert config["timezone"] == "Europe/London"
            assert config["digest_hour"] == 7
            assert config["quiet_hours_start"] == 22
            assert config["quiet_hours_end"] == 7
            assert config["email_recipient"] == "test@example.com"
            assert config["sender_email"] == "test@example.com"

    def test_get_env_config_missing_required(self):
        """Test that missing required environment variables raise ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="Missing required environment variable"
            ):
                get_env_config()

    def test_get_env_config_invalid_hour(self):
        """Test that invalid hour values raise ValueError."""
        with patch.dict(
            os.environ,
            {
                "GOOGLE_REFRESH_TOKEN": "test_token",
                "GOOGLE_CLIENT_ID": "test_id",
                "GOOGLE_CLIENT_SECRET": "test_secret",
                "RESEND_API_KEY": "test_resend_key",
                "TIMEZONE": "Europe/London",
                "DIGEST_HOUR": "25",  # Invalid hour
                "QUIET_HOURS_START": "22",
                "QUIET_HOURS_END": "07",
                "EMAIL_RECIPIENT": "test@example.com",
                "SENDER_EMAIL": "test@example.com",
            },
        ):
            with pytest.raises(ValueError, match="Invalid hour value"):
                get_env_config()

    def test_validate_timezone_valid(self):
        """Test that valid timezone strings are accepted."""
        assert validate_timezone("Europe/London") == "Europe/London"
        assert validate_timezone("America/New_York") == "America/New_York"
        assert validate_timezone("UTC") == "UTC"
        assert validate_timezone("Europe/Berlin") == "Europe/Berlin"

    def test_validate_timezone_invalid(self):
        """Test that invalid timezone strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid timezone"):
            validate_timezone("Invalid/Timezone")

    def test_parse_time_string_valid(self):
        """Test parsing valid time strings."""
        assert parse_time_string("07") == time(7, 0)
        assert parse_time_string("14:30") == time(14, 30)
        assert parse_time_string("23:45") == time(23, 45)

    def test_parse_time_string_invalid(self):
        """Test that invalid time strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_time_string("25:00")
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_time_string("12:60")
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_time_string("invalid")

    def test_is_quiet_hours_normal_case(self):
        """Test quiet hours detection for normal case (22:00 - 07:00)."""
        # Test during quiet hours
        quiet_times = [
            datetime(2023, 1, 1, 23, 0),  # 11 PM
            datetime(2023, 1, 1, 2, 0),  # 2 AM
            datetime(2023, 1, 1, 6, 30),  # 6:30 AM
        ]

        for dt in quiet_times:
            assert is_quiet_hours(dt, 22, 7) is True

        # Test outside quiet hours
        active_times = [
            datetime(2023, 1, 1, 8, 0),  # 8 AM
            datetime(2023, 1, 1, 14, 0),  # 2 PM
            datetime(2023, 1, 1, 21, 0),  # 9 PM
        ]

        for dt in active_times:
            assert is_quiet_hours(dt, 22, 7) is False

    def test_is_quiet_hours_same_start_end(self):
        """Test quiet hours when start and end are the same (no quiet hours)."""
        dt = datetime(2023, 1, 1, 23, 0)
        assert is_quiet_hours(dt, 22, 22) is False

    def test_is_quiet_hours_edge_cases(self):
        """Test quiet hours edge cases."""
        # Exactly at start time
        assert is_quiet_hours(datetime(2023, 1, 1, 22, 0), 22, 7) is True

        # Exactly at end time (7:00 is not in quiet hours, it's the end)
        assert is_quiet_hours(datetime(2023, 1, 1, 7, 0), 22, 7) is False
