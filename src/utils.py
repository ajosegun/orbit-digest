"""Utility functions for configuration and timezone handling."""

import os
import re
from datetime import datetime, time
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

import pytz
from loguru import logger


def get_env_config() -> Dict[str, Any]:
    """
    Load and validate environment configuration.

    Returns:
        Dict containing validated configuration values.

    Raises:
        ValueError: If required environment variables are missing or invalid.
    """
    required_vars = [
        "GOOGLE_REFRESH_TOKEN",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "RESEND_API_KEY",
        "EMAIL_RECIPIENT",
        "SENDER_EMAIL",
        "TIMEZONE",
        "DIGEST_HOUR",
        "QUIET_HOURS_START",
        "QUIET_HOURS_END",
    ]

    # Check for missing required variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variable: {', '.join(missing_vars)}"
        )

    # Load and validate configuration
    config = {
        "google_refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "google_client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "resend_api_key": os.getenv("RESEND_API_KEY"),
        "email_recipient": os.getenv("EMAIL_RECIPIENT"),
        "timezone": validate_timezone(os.getenv("TIMEZONE")),
        "sender_email": os.getenv("SENDER_EMAIL"),
    }

    # Validate numeric values
    try:
        config["digest_hour"] = int(os.getenv("DIGEST_HOUR", "7"))
        config["quiet_hours_start"] = int(os.getenv("QUIET_HOURS_START", "22"))
        config["quiet_hours_end"] = int(os.getenv("QUIET_HOURS_END", "7"))
    except ValueError:
        raise ValueError("Invalid hour value")

    # Validate hour ranges
    for hour_name, hour_value in [
        ("digest_hour", config["digest_hour"]),
        ("quiet_hours_start", config["quiet_hours_start"]),
        ("quiet_hours_end", config["quiet_hours_end"]),
    ]:
        if not 0 <= hour_value <= 23:
            raise ValueError(f"Invalid hour value for {hour_name}: {hour_value}")

    logger.info("Environment configuration loaded successfully")
    return config


def validate_timezone(timezone_str: str) -> str:
    """
    Validate timezone string.

    Args:
        timezone_str: IANA timezone string to validate.

    Returns:
        Validated timezone string.

    Raises:
        ValueError: If timezone is invalid.
    """
    try:
        pytz.timezone(timezone_str)
        return timezone_str
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValueError(f"Invalid timezone: {timezone_str}")


def parse_time_string(time_str: str) -> time:
    """
    Parse time string to time object.

    Args:
        time_str: Time string in format "HH" or "HH:MM".

    Returns:
        time object.

    Raises:
        ValueError: If time format is invalid.
    """
    try:
        if ":" in time_str:
            hour, minute = map(int, time_str.split(":"))
        else:
            hour, minute = int(time_str), 0

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time format")

        return time(hour, minute)
    except (ValueError, TypeError):
        raise ValueError("Invalid time format")


def is_quiet_hours(dt: datetime, quiet_start: int, quiet_end: int) -> bool:
    """
    Check if datetime is within quiet hours.

    Args:
        dt: Datetime to check.
        quiet_start: Start hour of quiet period (0-23).
        quiet_end: End hour of quiet period (0-23).

    Returns:
        True if datetime is within quiet hours, False otherwise.
    """
    current_hour = dt.hour

    if quiet_start == quiet_end:
        return False  # No quiet hours if start == end

    if quiet_start < quiet_end:
        # Normal case: quiet hours within same day (e.g., 22:00 - 07:00)
        return quiet_start <= current_hour < quiet_end
    else:
        # Overnight case: quiet hours span midnight (e.g., 22:00 - 07:00)
        return current_hour >= quiet_start or current_hour < quiet_end
