from database import (get_all_services,
                       get_service_by_name)
from config import BUSINESS_HOURS
from config import BUSINESS_CLOSED, FALLBACK_MESSAGE

# ── SAFE ANSWER CHECKER ────────────────

def is_price_question(message):
    keywords = ['price', 'cost', 'kitna',
                'rate', 'charge', 'fees',
                'how much', 'kitne']
    return any(k in message.lower()
               for k in keywords)

def is_availability_question(message):
    keywords = ['available', 'free', 'open',
                'slot', 'time', 'kal', 'aaj',
                'today', 'tomorrow', 'sunday',
                'saturday', 'monday', 'book',
                'appointment']
    return any(k in message.lower()
               for k in keywords)

def get_safe_price_answer(service_name):
    service = get_service_by_name(service_name)
    if service:
        return (f"*{service['name']}* ki "
                f"price hai ₹{service['price']} "
                f"({service['duration_mins']} mins). "
                f"Book karna hai? 😊")
    else:
        services = get_all_services()
        names = [s['name'] for s in services]
        return (f"Hmm, '{service_name}' "
                f"humari services mein nahi hai. "
                f"Humari services hain: "
                f"{', '.join(names)}. "
                f"Koi chahiye? ✨")

def check_closed_day(date_str):
    from datetime import datetime
    try:
        date_obj = datetime.strptime(
            date_str, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')
        return day_name in BUSINESS_CLOSED
    except:
        return False

def get_fallback_response():
    return FALLBACK_MESSAGE

def validate_ai_response(response, message):
    # Check if AI made up a price
    import re
    prices_in_response = re.findall(
        r'₹\s*(\d+)', response)

    if prices_in_response and is_price_question(message):
        services = get_all_services()
        valid_prices = [str(s['price'])
                        for s in services]

        for price in prices_in_response:
            if price not in valid_prices:
                # AI made up a price — use fallback
                return get_fallback_response()

    return response