import os
import requests
from datetime import datetime
import pytz

# Configuration from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')

# Sydney coordinates
SYDNEY_LAT = -33.8688
SYDNEY_LON = 151.2093

def get_weather_data():
    """Fetch current weather and forecast for Sydney"""
    
    # Current weather
    current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={SYDNEY_LAT}&lon={SYDNEY_LON}&appid={OPENWEATHER_API_KEY}&units=metric"
    current_response = requests.get(current_url)
    current_data = current_response.json()
    
    # Check for API errors
    if current_data.get('cod') != 200:
        error_msg = current_data.get('message', 'Unknown error')
        raise Exception(f"Weather API error: {error_msg}")
    
    # 5-day forecast (3-hour intervals)
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={SYDNEY_LAT}&lon={SYDNEY_LON}&appid={OPENWEATHER_API_KEY}&units=metric"
    forecast_response = requests.get(forecast_url)
    forecast_data = forecast_response.json()
    
    # Check for API errors
    if str(forecast_data.get('cod')) != '200':
        error_msg = forecast_data.get('message', 'Unknown error')
        raise Exception(f"Forecast API error: {error_msg}")
    
    return current_data, forecast_data

def parse_forecast_for_today(forecast_data):
    """Extract today's highs, lows, and rain chances from forecast"""
    
    sydney_tz = pytz.timezone('Australia/Sydney')
    today = datetime.now(sydney_tz).date()
    
    temps = []
    rain_periods = []
    
    for item in forecast_data.get('list', []):
        # Convert timestamp to Sydney time
        dt = datetime.fromtimestamp(item['dt'], tz=pytz.UTC).astimezone(sydney_tz)
        
        if dt.date() == today:
            temps.append(item['main']['temp'])
            
            # Check for rain probability
            pop = item.get('pop', 0) * 100  # Probability of precipitation (0-1 to %)
            if pop > 20:  # Only note if >20% chance
                rain_periods.append({
                    'time': dt.strftime('%I:%M %p'),
                    'chance': int(pop),
                    'description': item['weather'][0]['description'] if item.get('weather') else ''
                })
    
    return {
        'high': max(temps) if temps else None,
        'low': min(temps) if temps else None,
        'rain_periods': rain_periods
    }

def format_message(current_data, today_forecast):
    """Format the weather message for Telegram"""
    
    sydney_tz = pytz.timezone('Australia/Sydney')
    now = datetime.now(sydney_tz)
    
    # Current conditions
    current_temp = current_data['main']['temp']
    feels_like = current_data['main']['feels_like']
    description = current_data['weather'][0]['description'].title()
    humidity = current_data['main']['humidity']
    
    # Today's forecast
    high = today_forecast['high']
    low = today_forecast['low']
    rain_periods = today_forecast['rain_periods']
    
    # Build message
    lines = [
        f"☀️ **Sydney Weather** — {now.strftime('%A, %d %B')}",
        "",
        f"**Right now:** {current_temp:.1f}°C ({description})",
        f"**Feels like:** {feels_like:.1f}°C",
        "",
    ]
    
    if high and low:
        lines.append(f"**Today's range:** {low:.1f}°C → {high:.1f}°C")
    
    lines.append(f"**Humidity:** {humidity}%")
    lines.append("")
    
    # Rain forecast
    if rain_periods:
        lines.append("🌧️ **Rain expected:**")
        for period in rain_periods[:4]:  # Limit to 4 periods
            lines.append(f"  • {period['time']}: {period['chance']}% chance")
    else:
        lines.append("☂️ **Rain:** Not expected today")
    
    lines.append("")
    lines.append("Have a good day! 🚴")
    
    return "\n".join(lines)

def send_telegram_message(message):
    """Send message via Telegram bot"""
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def write_github_output(key, value):
    """Write output variable for GitHub Actions"""
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"{key}={value}\n")

def main():
    try:
        sydney_tz = pytz.timezone('Australia/Sydney')
        sydney_now = datetime.now(sydney_tz)
        sydney_date = sydney_now.strftime('%Y-%m-%d')
        
        is_manual = os.environ.get('MANUAL_TRIGGER', 'false').lower() == 'true'
        
        print(f"🕐 Sydney time: {sydney_now.strftime('%I:%M %p %Z')}")
        
        # Fetch weather data
        current_data, forecast_data = get_weather_data()
        
        # Parse today's forecast
        today_forecast = parse_forecast_for_today(forecast_data)
        
        # Format message
        message = format_message(current_data, today_forecast)
        
        # Send to Telegram
        result = send_telegram_message(message)
        
        if result.get('ok'):
            print("✅ Weather update sent successfully!")
            write_github_output('sent_date', sydney_date)
        else:
            print(f"❌ Failed to send message: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        error_msg = f"⚠️ Weather bot error:\n{str(e)}"
        send_telegram_message(error_msg)

if __name__ == "__main__":
    main()

