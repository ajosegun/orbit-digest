# Project PRD: Daily Google Calendar Digest to Email and WhatsApp

## 🧭 Objective

Create a scheduled GitHub Actions workflow that retrieves a user's Google Calendar events for the current day, formats them into a readable digest, and sends it to both:

- 📧 **Email** (via Resend)
- 💬 **WhatsApp** (via Twilio or Meta WhatsApp Cloud API)

The script should run without LLMs or agents, using plain Python in a `src/` layout and `uv` for dependency management.

---

## ✅ Functional Requirements

### 1. Google Calendar Integration

- Authenticate using **OAuth 2.0 + refresh token**
- Use **Google Calendar API** to fetch **today’s events** in the configured timezone
- Exclude:
  - All-day events
  - Cancelled events
  - Events outside **quiet hours**
- Required fields per event:
  - `summary`
  - `start` and `end` time
  - `location`
  - `attendees`
  - `description` (optional)

---

### 2. Quiet Hours & Preferred Summary Time

Allow user customization via `.env` or GitHub Secrets:
```dotenv
DIGEST_HOUR=7                 # Send digest at 7 AM local time
QUIET_HOURS_START=22          # Don't show events after 10 PM
QUIET_HOURS_END=07            # Don't show events before 7 AM
TIMEZONE=Europe/Lagos         # IANA timezone string
```

---

### 3. Message Formatting

Generate a plain-text digest:
```
Good morning! Here's your schedule for today (Thu, June 26):

- 09:00 – 09:30: Team Standup
  Location: Zoom
  Attendees: Alice, Bob

- 13:00 – 14:00: Product Sync
```

If no events:
```
You have no meetings scheduled today. Enjoy your day!
```

---

### 4. Delivery Channels

#### a. Email
- Use [Resend](https://resend.com/)
- Subject: `"Your schedule for today - YYYY-MM-DD"`
- Plain text only

#### b. WhatsApp
- Use Twilio or Meta WhatsApp Cloud API
- Send same text as email
- Fallback to email-only on failure

---

### 5. GitHub Actions Scheduling

Run daily via GitHub Actions:

- Trigger: `schedule` (cron) + `workflow_dispatch`
- Use UTC conversion of `DIGEST_HOUR`

**Example workflow:**
```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # 7 AM GMT+1
  workflow_dispatch:
```

---

## 🧱 Project Structure

```
calendar-digest/
├── src/
│   ├── main.py
│   ├── calendar.py
│   ├── formatter.py
│   ├── email_sender.py
│   ├── whatsapp_sender.py
│   └── utils.py
├── requirements.txt
├── .env.example
├── README.md
└── .github/
    └── workflows/
        └── calendar-digest.yml
```

---

## 🔐 Secrets Configuration (via GitHub)

- `GOOGLE_REFRESH_TOKEN`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `RESEND_API_KEY`
- `WHATSAPP_API_KEY`
- `EMAIL_RECIPIENT`
- `WHATSAPP_PHONE`
- `TIMEZONE`, `DIGEST_HOUR`, `QUIET_HOURS_START`, `QUIET_HOURS_END`

---

## 🧪 Non-Functional Requirements

- Secure token management with GitHub Secrets
- Timezone-aware event filtering and scheduling
- Basic logging in GitHub Actions logs
- Graceful fallback if one channel fails

---

## 🌱 Future Enhancements

- Send weekly summaries or "Tomorrow’s Preview"
- Export .ics file as attachment
- Add Slack or Telegram delivery
- Inline RSVP support or summaries from descriptions

---

## 💡 Project Name Ideas

1. **OrbitDigest** – For orbiting your calendar each day with a clean, readable summary.
2. **WhizNotify** – Lightweight, quick, and no-nonsense notification system.
