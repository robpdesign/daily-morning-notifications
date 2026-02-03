# Telegram Weather Bot 🌤️

Daily Sydney weather updates sent to Telegram at 7:30am AEST via GitHub Actions.

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
|-------------|-------|
| `TELEGRAM_BOT_TOKEN` | `YOUR TOKEN` |
| `TELEGRAM_CHAT_ID` | `YOUR CHAT ID` |
| `OPENWEATHER_API_KEY` | Your OpenWeatherMap API key |

### 4. Test it

Go to **Actions** → **Daily Sydney Weather** → **Run workflow** to test manually.

## Schedule

- Runs daily at **7:30am Sydney time** (automatically handles daylight saving)
- The workflow triggers at both possible UTC times, but the script checks Sydney time before sending

To adjust timing, edit the cron schedules in `.github/workflows/weather.yml`.

## Message Format

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
