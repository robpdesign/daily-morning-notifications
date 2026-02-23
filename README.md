# Daily Telegram Bot 🌤️🎂

Daily morning notifications via Telegram, powered by GitHub Actions.

**Features:**
- **Weather updates** – Sydney forecast with temperature range and rain chances
- **Birthday reminders** – Notifications on the day of birthdays and anniversaries

## Setup

### 1. Create a GitHub repository

Create a new repo (can be private) and push these files to it.

### 2. Get an OpenWeatherMap API key

1. Sign up at [openweathermap.org](https://openweathermap.org/api)
2. Go to your account → API Keys
3. Copy your API key (free tier works fine)

### 3. Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these three secrets:

| Secret Name | Value |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `OPENWEATHER_API_KEY` | Your OpenWeatherMap API key |

### 4. Test it

Go to **Actions** → **Daily Sydney Weather** → **Run workflow** to test manually.

## Schedule

- Runs daily at **7:30am Sydney time** (automatically handles daylight saving)
- The workflow triggers at both possible UTC times, but the script checks Sydney time before sending

## Message Formats

### Weather
```
☀️ Sydney Weather — Monday, 03 February

Right now: 24.5°C (Partly Cloudy)
Feels like: 25.2°C

Today's range: 19.0°C → 28.5°C
Humidity: 65%

🌧️ Rain expected:
  • 02:00 PM: 40% chance
  • 05:00 PM: 60% chance

Have a good day! 🚴
```

### Birthday/Anniversary
```
🎂 Reminder — Thursday, 10 April

🎈 'Name' Bday today!
```

```
🎂 Reminder — Thursday, 08 May

💐 Mother's Day today!
💍 Wedding Anniversary — 15 years!
```

## Managing Birthdays

Edit `birthdays.json` to add, remove, or update entries:

```json
{"name": "Dad Bday", "date": "9th Aug", "type": "birthday"},
{"name": "Wedding Anniversary", "date": "7th July", "type": "anniversary", "year": 2015},
{"name": "Mother's Day", "date": "8th May", "type": "mothers_day"}
```

**Types:** `birthday`, `anniversary`, `mothers_day`

For anniversaries, include `year` to show how many years (e.g., "15 years!").

## Files

| File | Purpose |
| --- | --- |
| `weather.py` | Fetches weather and sends Telegram message |
| `birthdays.py` | Checks for today's birthdays/anniversaries |
| `birthdays.json` | Birthday and anniversary data |
| `.github/workflows/weather.yml` | GitHub Actions schedule |
