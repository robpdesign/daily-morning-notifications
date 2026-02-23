import os
import json
import requests
from datetime import datetime
import pytz

# Configuration from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def load_birthdays():
    """Load birthdays from JSON file"""
    with open('birthdays.json', 'r') as f:
        return json.load(f)

def parse_date(date_str):
    """Parse date strings like '9th April', '24th Jan' into (day, month)"""
    # Remove ordinal suffixes
    date_str = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
    
    # Map month names to numbers
    months = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    parts = date_str.strip().split()
    if len(parts) >= 2:
        day = int(parts[0])
        month_str = parts[1].lower()
        month = months.get(month_str, 0)
        return (day, month)
    return None

def get_todays_events(birthdays):
    """Find any birthdays/events matching today's date"""
    sydney_tz = pytz.timezone('Australia/Sydney')
    today = datetime.now(sydney_tz)
    today_day = today.day
    today_month = today.month
    
    matches = []
    
    for entry in birthdays:
        name = entry['name']
        date_str = entry['date']
        event_type = entry.get('type', 'birthday')
        year = entry.get('year')  # Optional year for anniversaries
        
        parsed = parse_date(date_str)
        if parsed:
            day, month = parsed
            if day == today_day and month == today_month:
                match = {
                    'name': name,
                    'type': event_type,
                    'date': date_str
                }
                # Calculate years for anniversaries
                if year and event_type == 'anniversary':
                    years = today.year - year
                    match['years'] = years
                matches.append(match)
    
    return matches

def format_message(events):
    """Format the birthday/anniversary message"""
    sydney_tz = pytz.timezone('Australia/Sydney')
    today = datetime.now(sydney_tz)
    
    lines = [f"🎂 **Reminder** — {today.strftime('%A, %d %B')}", ""]
    
    for event in events:
        if event['type'] == 'anniversary' and 'years' in event:
            lines.append(f"💍 **{event['name']}** — {event['years']} years!")
        elif event['type'] == 'mothers_day':
            lines.append(f"💐 **{event['name']}** today!")
        else:
            lines.append(f"🎈 **{event['name']}** today!")
    
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

def main():
    try:
        sydney_tz = pytz.timezone('Australia/Sydney')
        sydney_now = datetime.now(sydney_tz)
        current_hour = sydney_now.hour
        sydney_minute = sydney_now.minute
        
        # Allow manual triggers anytime
        is_manual = os.environ.get('MANUAL_TRIGGER', 'false').lower() == 'true'
        
        # Allow 7:00am - 8:30am window
        in_window = (current_hour == 7) or (current_hour == 8 and sydney_minute <= 30)
        
        if not is_manual and not in_window:
            print(f"⏭️ Skipping - Sydney time is {sydney_now.strftime('%I:%M %p')}, outside 7:00-8:30am window")
            return
        
        print(f"🕐 Sydney time: {sydney_now.strftime('%I:%M %p %Z')}")
        
        # Load birthdays and check for today's events
        birthdays = load_birthdays()
        todays_events = get_todays_events(birthdays)
        
        if not todays_events:
            print("📅 No birthdays or anniversaries today")
            return
        
        # Format and send message
        message = format_message(todays_events)
        result = send_telegram_message(message)
        
        if result.get('ok'):
            print(f"✅ Reminder sent for: {', '.join(e['name'] for e in todays_events)}")
        else:
            print(f"❌ Failed to send message: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
