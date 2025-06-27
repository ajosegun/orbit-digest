"""Main OrbitDigest application."""

from typing import Dict, Any

from src.calendar import CalendarService
from src.email_sender import EmailSender
from src.formatter import DigestFormatter
from src.utils import get_env_config
from loguru import logger


class OrbitDigest:
    """Main application class for OrbitDigest."""

    def __init__(self):
        """Initialize OrbitDigest with all services."""
        # Load configuration
        self.config = get_env_config()

        # Initialize services
        self.calendar_service = CalendarService(
            client_id=self.config["google_client_id"],
            client_secret=self.config["google_client_secret"],
            refresh_token=self.config["google_refresh_token"],
        )

        self.email_sender = EmailSender(
            api_key=self.config["resend_api_key"],
            sender_email=self.config["sender_email"],  # Default sender
        )

        self.formatter = DigestFormatter(
            timezone_str=self.config["timezone"],
        )

        logger.info("OrbitDigest initialized successfully")

    def run_digest(self) -> bool:
        """
        Run the complete digest workflow.

        Returns:
            True if email sent successfully, False otherwise.
        """
        try:
            logger.info("Starting digest workflow")

            # Get today's events
            events = self.calendar_service.get_today_events(
                timezone_str=self.config["timezone"],
                quiet_start=self.config["quiet_hours_start"],
                quiet_end=self.config["quiet_hours_end"],
            )

            # Format digest
            digest_content = self.formatter.format_digest(events)

            # Send via email
            email_success = self.email_sender.send_digest(
                recipient=self.config["email_recipient"],
                content=digest_content,
            )

            success = email_success

            if success:
                logger.info("Digest sent successfully via email")
            else:
                logger.error("Failed to send digest via email")

            return success

        except Exception as e:
            logger.error(f"Error in digest workflow: {e}")
            return False


def main():
    """Main entry point for the application."""
    # Configure logging
    logger.add(
        "logs/orbit_digest.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
    )

    # try:
    digest = OrbitDigest()
    success = digest.run_digest()

    if success:
        logger.info("OrbitDigest completed successfully")
        return 0
    else:
        logger.error("OrbitDigest failed")
        return 1

    # except Exception as e:
    #     logger.error(f"Fatal error in OrbitDigest: {e}")
    #     return 1


if __name__ == "__main__":
    exit(main())
