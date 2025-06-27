# from unittest.mock import Mock, patch

# import pytest
# # from resend import ResendError  # Remove this import

# from src.email_sender import EmailSender


# class TestEmailSender:
#     """Test EmailSender for Resend email integration."""

#     def test_email_sender_initialization(self):
#         """Test successful EmailSender initialization."""
#         with patch("src.email_sender.resend") as mock_resend:
#             mock_client = Mock()
#             mock_resend.Resend.return_value = mock_client

#             sender = EmailSender("test_api_key", "sender@example.com")

#             assert sender.client == mock_client
#             assert sender.sender_email == "sender@example.com"
#             mock_resend.Resend.assert_called_once_with(api_key="test_api_key")

#     def test_send_email_success(self):
#         """Test successful email sending."""
#         with patch("src.email_sender.resend") as mock_resend:
#             mock_client = Mock()
#             mock_resend.api_key = "test_api_key"

#             mock_client.Emails.send.return_value = {"id": "test_email_id"}

#             sender = EmailSender("test_api_key", "sender@example.com")
#             result = sender.send_email(
#                 "recipient@example.com", "Test Subject", "Test Body"
#             )

#             assert result is True
#             mock_client.Emails.send.assert_called_once_with(
#                 {
#                     "from": "sender@example.com",
#                     "to": ["recipient@example.com"],
#                     "subject": "Test Subject",
#                     "text": "Test Body",
#                 }
#             )

#     def test_send_email_resend_error(self):
#         """Test email sending with Resend API error."""
#         with patch("src.email_sender.resend") as mock_resend:
#             mock_client = Mock()
#             mock_resend.Resend.return_value = mock_client
#             mock_client.Emails.send.side_effect = Exception(
#                 "API Error"
#             )  # Use Exception

#             sender = EmailSender("test_api_key", "sender@example.com")
#             result = sender.send_email(
#                 "recipient@example.com", "Test Subject", "Test Body"
#             )

#             assert result is False

#     def test_send_email_invalid_recipient(self):
#         """Test email sending with invalid recipient."""
#         with patch("src.email_sender.resend") as mock_resend:
#             mock_client = Mock()
#             mock_resend.Resend.return_value = mock_client

#             sender = EmailSender("test_api_key", "sender@example.com")
#             result = sender.send_email("invalid-email", "Test Subject", "Test Body")

#             assert result is False
#             mock_client.Emails.send.assert_not_called()

#     def test_send_email_empty_subject(self):
#         """Test email sending with empty subject."""
#         with patch("src.email_sender.resend") as mock_resend:
#             mock_client = Mock()
#             mock_resend.Resend.return_value = mock_client

#             sender = EmailSender("test_api_key", "sender@example.com")
#             result = sender.send_email("recipient@example.com", "", "Test Body")

#             assert result is False
#             mock_client.Emails.send.assert_not_called()

#     def test_send_email_empty_body(self):
#         """Test email sending with empty body."""
#         with patch("src.email_sender.resend") as mock_resend:
#             mock_client = Mock()
#             mock_resend.Resend.return_value = mock_client

#             sender = EmailSender("test_api_key", "sender@example.com")
#             result = sender.send_email("recipient@example.com", "Test Subject", "")

#             assert result is False
#             mock_client.Emails.send.assert_not_called()

#     def test_send_digest_success(self):
#         """Test successful digest email sending."""
#         with patch("src.email_sender.resend") as mock_resend:
#             mock_client = Mock()
#             mock_resend.Resend.return_value = mock_client
#             mock_client.Emails.send.return_value = {"id": "test_email_id"}

#             sender = EmailSender("test_api_key", "sender@example.com")
#             result = sender.send_digest("recipient@example.com", "Test digest content")

#             assert result is True
#             mock_client.Emails.send.assert_called_once()

#             call_args = mock_client.Emails.send.call_args[0][0]
#             assert call_args["from"] == "sender@example.com"
#             assert call_args["to"] == ["recipient@example.com"]
#             assert "Your schedule for today" in call_args["subject"]
#             assert call_args["text"] == "Test digest content"

#     def test_send_digest_with_date_in_subject(self):
#         """Test that digest subject includes the current date."""
#         with (
#             patch("src.email_sender.resend") as mock_resend,
#             patch("src.email_sender.datetime") as mock_datetime,
#         ):
#             mock_client = Mock()
#             mock_resend.Resend.return_value = mock_client
#             mock_client.emails.send.return_value = {"id": "test_email_id"}

#             # Mock current date
#             from datetime import datetime

#             mock_datetime.now.return_value = datetime(2023, 6, 26)

#             sender = EmailSender("test_api_key", "sender@example.com")
#             result = sender.send_digest("recipient@example.com", "Test digest content")

#             assert result is True
#             call_args = mock_client.Emails.send.call_args[0][0]
#             assert "2023-06-26" in call_args["subject"]

#     def test_send_digest_failure(self):
#         """Test digest sending failure."""
#         with patch("src.email_sender.resend") as mock_resend:
#             mock_client = Mock()
#             mock_resend.Resend.return_value = mock_client
#             mock_client.Emails.send.side_effect = Exception(
#                 "API Error"
#             )  # Use Exception

#             sender = EmailSender("test_api_key", "sender@example.com")
#             result = sender.send_digest("recipient@example.com", "Test digest content")

#             assert result is False

#     def test_validate_email_valid(self):
#         """Test email validation with valid emails."""
#         with patch("src.email_sender.resend"):
#             sender = EmailSender("test_api_key", "sender@example.com")

#             valid_emails = [
#                 "test@example.com",
#                 "user.name@domain.co.uk",
#                 "user+tag@example.org",
#             ]

#             for email in valid_emails:
#                 assert sender._validate_email(email) is True

#     def test_validate_email_invalid(self):
#         """Test email validation with invalid emails."""
#         with patch("src.email_sender.resend"):
#             sender = EmailSender("test_api_key", "sender@example.com")

#             invalid_emails = [
#                 "invalid-email",
#                 "@example.com",
#                 "user@",
#                 "user@.com",
#                 "",
#                 None,
#             ]

#             for email in invalid_emails:
#                 assert sender._validate_email(email) is False
