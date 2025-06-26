# OrbitDigest 🌟

**Daily Google Calendar Digest to Email**

OrbitDigest is a scheduled GitHub Actions workflow that retrieves your Google Calendar events for the current day, formats them into a readable digest, and sends it via email (via Resend).

## ✨ Features

- 📅 **Google Calendar Integration**: Fetches today's events using OAuth 2.0
- 🕐 **Smart Filtering**: Excludes all-day events, cancelled events, and events during quiet hours
- 📧 **Email Delivery**: Sends formatted digest via Resend
- 🌍 **Timezone Support**: Full timezone awareness for accurate scheduling
- 🔧 **Configurable**: Customizable quiet hours, digest time, and timezone
- 🧪 **Test-Driven**: Comprehensive test suite with 100% coverage
- 📝 **Structured Logging**: Detailed logging with Loguru

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ajosegun/orbit-digest.git
cd orbit-digest
```

### 2. Install Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev
```

### 3. Set Up Environment Variables

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your actual values:

```env
# Google Calendar API Configuration
GOOGLE_REFRESH_TOKEN=your_refresh_token_here
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here

# Email Configuration (Resend)
RESEND_API_KEY=your_resend_api_key_here
EMAIL_RECIPIENT=recipient@example.com

# Time and Timezone Configuration
TIMEZONE=Europe/Berlin
DIGEST_HOUR=7
QUIET_HOURS_START=22
QUIET_HOURS_END=07
```

### 4. Run Tests

```bash
uv run pytest tests/ -v
```

### 5. Test Locally

```bash
uv run python -m src.main
```

## 🔧 Configuration

### Environment Variables

| Variable               | Description                 | Required | Default       |
| ---------------------- | --------------------------- | -------- | ------------- |
| `GOOGLE_REFRESH_TOKEN` | Google OAuth refresh token  | ✅       | -             |
| `GOOGLE_CLIENT_ID`     | Google OAuth client ID      | ✅       | -             |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret  | ✅       | -             |
| `RESEND_API_KEY`       | Resend API key              | ✅       | -             |
| `EMAIL_RECIPIENT`      | Email recipient address     | ✅       | -             |
| `TIMEZONE`             | IANA timezone string        | ✅       | Europe/Berlin |
| `DIGEST_HOUR`          | Hour to send digest (0-23)  | ❌       | 7             |
| `QUIET_HOURS_START`    | Start of quiet hours (0-23) | ❌       | 22            |
| `QUIET_HOURS_END`      | End of quiet hours (0-23)   | ❌       | 7             |

### Quiet Hours

Quiet hours define when events should be excluded from the digest. For example:

- `QUIET_HOURS_START=22` and `QUIET_HOURS_END=07` excludes events between 10 PM and 7 AM
- Set both to the same value to disable quiet hours

## 📋 Setup Instructions

### 1. Google Calendar API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download the credentials and extract:
   - Client ID
   - Client Secret
6. Generate a refresh token using the OAuth flow

### 2. Resend Setup

1. Sign up at [Resend](https://resend.com/)
2. Get your API key from the dashboard
3. Verify your domain (optional but recommended)

### 3. GitHub Secrets

Add the following secrets to your GitHub repository:

```bash
# Google Calendar
GOOGLE_REFRESH_TOKEN
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET

# Resend
RESEND_API_KEY
EMAIL_RECIPIENT

# Configuration
TIMEZONE
DIGEST_HOUR
QUIET_HOURS_START
QUUIET_HOURS_END
```

## 📅 GitHub Actions

The workflow runs daily at 6 AM UTC (configurable) and:

1. ✅ Runs all tests
2. 📅 Fetches today's calendar events
3. 📝 Formats the digest
4. 📧 Sends via email
5. 📊 Uploads logs as artifacts

### Manual Trigger

You can manually trigger the workflow from the GitHub Actions tab.

## 🧪 Testing

Run the full test suite:

```bash
uv run pytest tests/ -v --cov=src --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html
```

## 📁 Project Structure

```
orbit-digest/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main application
│   ├── calendar.py          # Google Calendar integration
│   ├── formatter.py         # Message formatting
│   ├── email_sender.py      # Email sending via Resend
│   └── utils.py             # Configuration and utilities
├── tests/
│   ├── __init__.py
│   ├── test_main.py         # Integration tests
│   ├── test_calendar.py     # Calendar service tests
│   ├── test_formatter.py    # Formatter tests
│   ├── test_email_sender.py # Email sender tests
│   └── test_utils.py        # Utility tests
├── .github/
│   └── workflows/
│       └── calendar-digest.yml  # GitHub Actions workflow
├── pyproject.toml           # Project configuration
├── env.example              # Environment variables template
└── README.md               # This file
```

## 🔒 Security

- All sensitive data is stored in environment variables
- `.env` files are excluded from version control
- GitHub Actions uses repository secrets for production
- No hardcoded API keys or tokens

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the logs in GitHub Actions artifacts
2. Verify your environment variables are set correctly
3. Ensure your Google Calendar API credentials are valid
4. Check that your Resend API key is active

## 🚀 Deployment

The application is designed to run via GitHub Actions. Simply:

1. Fork this repository
2. Set up your environment variables as GitHub secrets
3. The workflow will run automatically every day at 6 AM UTC

You can also run it locally for testing by setting up your `.env` file and running:

```bash
uv run python -m src.main
```
