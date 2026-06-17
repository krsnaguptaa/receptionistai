from google import genai
from config import (GEMINI_API_KEY,
                    BUSINESS_NAME,
                    BUSINESS_HOURS,
                    BUSINESS_LOCATION,
                    BUSINESS_CLOSED)
from database import get_services_formatted
from memory_engine import build_customer_context
from safety_engine import validate_ai_response
import re

client = genai.Client(api_key=GEMINI_API_KEY)

def detect_booking_intent(message):
    keywords = [
        'book', 'booking', 'appointment',
        'slot', 'available', 'kal', 'aaj',
        'saturday', 'sunday', 'monday',
        'tuesday', 'wednesday', 'thursday',
        'friday', 'baje', 'pm', 'am',
        'time', 'fix karo', 'schedule',
        'aana hai', 'visit', 'confirm'
    ]
    return any(k in message.lower()
               for k in keywords)

def detect_complaint(message):
    keywords = [
        'complaint', 'problem', 'issue',
        'angry', 'bad', 'worst', 'terrible',
        'bura', 'ganda', 'bakwaas', 'bekar'
    ]
    return any(k in message.lower()
               for k in keywords)

def detect_upsell_acceptance(message):
    positive = [
        'yes', 'haan', 'ok', 'okay',
        'sure', 'add karo', 'theek hai',
        'kar do', 'bilkul', 'why not',
        'haa', 'yep', 'yeah', 'done'
    ]
    return any(k in message.lower()
               for k in positive)

def extract_service_from_message(message):
    from database import get_all_services
    services = get_all_services()
    msg_lower = message.lower()
    for service in services:
        if service['name'].lower() in msg_lower:
            return service['name']
    keywords = {
        'haircut': 'Haircut',
        'baal': 'Haircut',
        'cut': 'Haircut',
        'highlight': 'Highlights',
        'colour': 'Highlights',
        'color': 'Highlights',
        'balayage': 'Balayage',
        'root': 'Root Touchup',
        'keratin': 'Keratin',
        'spa': 'Hair Spa',
        'massage': 'Head Massage',
        'toning': 'Toning'
    }
    for kw, name in keywords.items():
        if kw in msg_lower:
            return name
    return None

def extract_date_from_message(message):
    from datetime import datetime, timedelta
    today = datetime.now()
    msg_lower = message.lower()
    if 'aaj' in msg_lower or 'today' in msg_lower:
        return today.strftime('%Y-%m-%d')
    if 'kal' in msg_lower or 'tomorrow' in msg_lower:
        return (today + timedelta(days=1)
                ).strftime('%Y-%m-%d')
    days = {
        'monday': 0, 'tuesday': 1,
        'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5,
        'sunday': 6
    }
    for day_name, day_num in days.items():
        if day_name in msg_lower:
            days_ahead = (
                day_num - today.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
            target = today + timedelta(
                days=days_ahead)
            return target.strftime('%Y-%m-%d')
    return None

def extract_time_from_message(message):
    patterns = [
        r'(\d{1,2}):(\d{2})\s*(am|pm)?',
        r'(\d{1,2})\s*(am|pm)',
        r'(\d{1,2})\s*baje'
    ]
    msg_lower = message.lower()
    for pattern in patterns:
        match = re.search(pattern, msg_lower)
        if match:
            groups = match.groups()
            hour = int(groups[0])
            if len(groups) > 1 and groups[-1]:
                period = groups[-1]
                if period == 'pm' and hour != 12:
                    hour += 12
                elif period == 'am' and hour == 12:
                    hour = 0
            return f"{hour:02d}:00"
    return None

def get_ai_response(phone, message):
    try:
        print(f"🤖 Getting AI response for: {message}")
        print(f"🔑 Key: {GEMINI_API_KEY[:15]}...")

        customer_ctx = build_customer_context(phone)
        services_text = get_services_formatted()

        # NOTE: THIS MUST BE f""" NOT JUST """
        prompt = f"""Tu ek friendly AI receptionist hai {BUSINESS_NAME} ke liye Delhi mein.

LANGUAGE — HINGLISH:
Hindi aur English mix karo naturally.
Jaise Delhi ke log baat karte hain.
WhatsApp ke liye short rakho — max 4 lines.
Emojis thode use karo.

BUSINESS:
Naam: {BUSINESS_NAME}
Location: {BUSINESS_LOCATION}
Timings: {BUSINESS_HOURS}
Closed: {', '.join(BUSINESS_CLOSED)}

SERVICES:
{services_text}

CUSTOMER INFO:
{customer_ctx['context_text']}

STRICT RULES:
1. Price SIRF upar wali list se batao
2. Jo service list mein nahi — clearly bolo
3. Booking ke liye: "Main check karke confirm karta hoon!"
4. Complaint aaye to calm raho
5. Agar nahi pata — "Owner se confirm karke batata hoon"

BOOKING FLOW:
Service → Date → Time → Name → Confirm

Customer ka message: {message}

Tera Hinglish reply:"""

        print(f"📤 Calling Gemini...")
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )

        reply = response.text.strip()
        print(f"✅ Gemini replied: {reply[:80]}")

        reply = validate_ai_response(reply, message)
        return reply

    except Exception as e:
        print(f"❌ GEMINI ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return (
            f"Namaste! 😊\n"
            f"{BUSINESS_NAME} mein aapka swagat hai!\n"
            f"Kya help kar sakta hoon?"
        )
