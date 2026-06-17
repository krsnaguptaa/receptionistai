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

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# ── INTENT DETECTION ──────────────────

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
                if period == 'pm' and hour != 12:
                    hour += 12
                elif period == 'am' and hour == 12:
                    hour = 0
            return f"{hour:02d}:00"
    return None

# ── MAIN AI RESPONSE ──────────────────

def get_ai_response(phone, message):
    try:
        print(f"🤖 Groq processing: {message}")

        customer_ctx = build_customer_context(phone)
        services_text = get_services_formatted()

        system_prompt = f"""Tu ek friendly AI receptionist hai {BUSINESS_NAME} ke liye Delhi mein.

LANGUAGE — HINGLISH:
Hindi aur English mix karo naturally.
Jaise Delhi ke log actually baat karte hain.
Example: "Haan bilkul! Amit kal free hai 😊"
WhatsApp ke liye SHORT rakho — max 4 lines.
Emojis thode use karo — zyada nahi.

BUSINESS INFORMATION:
Naam: {BUSINESS_NAME}
Location: {BUSINESS_LOCATION}
Timings: {BUSINESS_HOURS}
Closed: {', '.join(BUSINESS_CLOSED)}

SERVICES AND PRICES:
{services_text}

CUSTOMER PROFILE:
{customer_ctx['context_text']}

STRICT RULES — KABHI MAT TODNA:
1. Price SIRF upar wali list se batao. Khud se koi price mat banao.
2. Jo service list mein nahi — "Ye service nahi hai humare paas"
3. Booking ke liye: "Main check karke confirm karta hoon! ✅"
4. Complaint aaye to calm raho, apologize karo
5. Agar kuch nahi pata: "Main owner se confirm karke batata hoon!"
6. KABHI BHAI MAT BOLO — professional raho
"""
7. Agar customer ka naam nahi pata:
   Pehle pooch lo: "Aapka naam kya hai?"
   Phir booking confirm karo
8. Customer ko KABHI "Customer" mat bolo
   Naam nahi pata toh "Aap" use karo
"""

BOOKING FLOW:
Jab customer book karna chahe:
1. Kaunsi service?
2. Kaunsi date?
3. Kaunsa time?
4. Name? (naye customer ke liye)
5. "Main check karke confirm karta hoon! ✅"

PERSONALITY:
Warm, helpful, local Delhi feel.
Dost jaisi baat karo — professional bhi."""

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
        print(f"✅ Groq replied: {reply[:80]}")

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
