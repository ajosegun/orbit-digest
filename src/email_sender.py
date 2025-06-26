"""Email sending via Resend API."""

import re
from datetime import datetime
from typing import Optional

import resend
from loguru import logger


class EmailSender:
    """Service for sending emails via Resend."""

    def __init__(self, api_key: str, sender_email: str):
        """
        Initialize EmailSender.

        Args:
            api_key: Resend API key.
            sender_email: Email address to send from.
        """
        self.client = resend.Resend(api_key=api_key)
        self.sender_email = sender_email
        logger.info(f"Email sender initialized with sender: {sender_email}")

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Send an email.

        Args:
            recipient: Email address to send to.
            subject: Email subject.
            body: Email body (plain text).

        Returns:
            True if email sent successfully, False otherwise.
        """
        # Validate inputs
        if not self._validate_email(recipient):
            logger.error(f"Invalid recipient email: {recipient}")
            return False

        if not subject.strip():
            logger.error("Empty email subject")
            return False

        if not body.strip():
            logger.error("Empty email body")
            return False

        try:
            response = self.client.emails.send(
                {
                    "from": self.sender_email,
                    "to": [recipient],
                    "subject": subject,
                    "text": body,
                }
            )

            logger.info(
                f"Email sent successfully to {recipient}, ID: {response.get('id')}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            return False

    def send_digest(self, recipient: str, content: str) -> bool:
        """
        Send a digest email.

        Args:
            recipient: Email address to send to.
            content: Digest content.

        Returns:
            True if email sent successfully, False otherwise.
        """
        # Generate subject with current date
        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"Your schedule for today - {today}"

        return self.send_email(recipient, subject, content)

    def _validate_email(self, email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not email or not isinstance(email, str):
            return False

        # Basic email regex pattern
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
