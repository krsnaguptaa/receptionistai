from groq import Groq
from config import (GROQ_API_KEY,
                    BUSINESS_NAME,
                    BUSINESS_HOURS,
                    BUSINESS_LOCATION,
                    BUSINESS_CLOSED)
from database import get_services_formatted
from memory_engine import build_customer_context
from safety_engine import validate_ai_response
import re

client = Groq(api_key=GROQ_API_KEY)

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
                day_num -
                today.weekday() + 7) % 7
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
                if (period == 'pm'
                        and hour != 12):
                    hour += 12
                elif (period == 'am'
                        and hour == 12):
                    hour = 0
            return f"{hour:02d}:00"
    return None

def get_ai_response(phone, message):
    try:
        print(f"🤖 Processing: {message}")

        customer_ctx = build_customer_context(phone)
        services_text = get_services_formatted()

        # Get customer name safely
        customer_name = "Aap"
        if (customer_ctx and
                not customer_ctx.get('is_new') and
                customer_ctx.get('name')):
            customer_name = customer_ctx['name']

        system_prompt = (
            f"Tu ek friendly AI receptionist hai "
            f"{BUSINESS_NAME} ke liye Delhi mein.\n\n"
            f"LANGUAGE — HINGLISH:\n"
            f"Hindi aur English mix karo naturally.\n"
            f"Jaise Delhi ke log baat karte hain.\n"
            f"WhatsApp ke liye short rakho — max 4 lines.\n"
            f"Emojis thode use karo.\n\n"
            f"BUSINESS:\n"
            f"Naam: {BUSINESS_NAME}\n"
            f"Location: {BUSINESS_LOCATION}\n"
            f"Timings: {BUSINESS_HOURS}\n"
            f"Closed: {', '.join(BUSINESS_CLOSED)}\n\n"
            f"SERVICES:\n"
            f"{services_text}\n\n"
            f"CUSTOMER INFO:\n"
            f"{customer_ctx['context_text']}\n\n"
            f"RULES:\n"
            f"- Price sirf list se batao\n"
            f"- Jo service nahi: clearly bolo\n"
            f"- Booking ke liye date time name pooch lo\n"
            f"- Naam nahi pata: 'Aap' use karo\n"
            f"- Kabhi 'Customer' mat likho\n"
            f"- Complaint: calm raho\n"
            f"- Booking confirm: "
            f"'Main check karke confirm karta hoon!'\n\n"
            f"BOOKING FLOW:\n"
            f"Service pooch lo, date pooch lo, "
            f"time pooch lo, naam pooch lo, confirm karo.\n\n"
            f"Warm, helpful, local Delhi feel."
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=300,
            temperature=0.7
        )

        reply = response.choices[0].message.content.strip()
        print(f"✅ Reply: {reply[:80]}")

        reply = validate_ai_response(reply, message)
        return reply

    except Exception as e:
        print(f"❌ GROQ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return (
            f"Namaste! 😊\n"
            f"{BUSINESS_NAME} mein aapka swagat hai!\n"
            f"Services ke liye reply karo!"
        )
