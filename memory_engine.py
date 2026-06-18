from database import (get_customer,
                       update_customer_profile,
                       get_service_by_name)

# ── EXTRACT INFO FROM MESSAGES ─────────

def extract_name(message):
    triggers = [
        'mera naam', 'my name is',
        "i'm", 'i am', 'naam hai',
        'main hoon', 'naam'
    ]
    words = message.split()
    msg_lower = message.lower()

    for trigger in triggers:
        if trigger in msg_lower:
            idx = msg_lower.find(trigger)
            after = message[idx+len(trigger):]
            after = after.strip()
            if after:
                name = after.split()[0]
                name = name.strip('.,!?')
                return name.capitalize()

    # If message is just ONE word
    # and previous AI message asked for name
    # treat it as the name
    if (len(words) == 1 and
            len(message) > 1 and
            message.isalpha()):
        return message.strip().capitalize()

    return None

def extract_birthday(message):
    import re
    patterns = [
        r'(\d{1,2})\s*(jan|feb|mar|apr|may|jun|'
        r'jul|aug|sep|oct|nov|dec)',
        r'(\d{1,2})[/-](\d{1,2})',
        r'(january|february|march|april|may|june|'
        r'july|august|september|october|'
        r'november|december)\s+(\d{1,2})'
    ]
    msg_lower = message.lower()
    for pattern in patterns:
        match = re.search(pattern, msg_lower)
        if match:
            return match.group(0)
    return None

def extract_allergy(message):
    allergy_words = [
        'allergy', 'allergic', 'sensitive',
        'reaction', 'chemical nahi',
        'irritation', 'rash'
    ]
    msg_lower = message.lower()
    if any(word in msg_lower
           for word in allergy_words):
        return message
    return None

def build_customer_context(phone):
    customer = get_customer(phone)

    if not customer:
        return {
            'is_new': True,
            'name': None,
            'context_text': (
                "NEW CUSTOMER — first time. "
                "Be welcoming. Try to get name."
            )
        }

    visits = customer['total_visits']
    name = customer['name'] or None

    context = f"""
RETURNING CUSTOMER:
Name: {name or 'Unknown - ask for name'}
Total Visits: {visits}
Last Service: {customer['last_service'] or 'None'}
"""

    return {
        'is_new': False,
        'name': name,
        'context_text': context,
        'customer': customer
    }
    visits = customer['total_visits']
    name = customer['name'] or 'Customer'

    if visits == 0:
        relationship = "First time customer"
    elif visits < 3:
        relationship = "New customer"
    elif visits < 10:
        relationship = "Regular customer"
    else:
        relationship = "VIP loyal customer"

    context = f"""
RETURNING CUSTOMER PROFILE:
Name: {name}
Relationship: {relationship}
Total Visits: {visits}
Total Spent: ₹{customer['total_spent']}
Last Service: {customer['last_service'] or 'Unknown'}
Last Visit: {customer['last_visit_date'] or 'Unknown'}
Preferred Stylist: {customer['preferred_stylist'] or 'No preference'}
Hair Formula: {customer['hair_formula'] or 'Not recorded'}
Allergies: {customer['allergies'] or 'None noted'}
Usual Order: {customer['usual_order'] or 'Varies'}

PERSONALIZATION RULES:
- Always use their name: {name}
- Reference their last service
- Suggest preferred stylist first
- Never ask info you already have
"""

    if customer['allergies']:
        context += (f"\n⚠️ ALLERGY ALERT: "
                   f"{customer['allergies']} "
                   f"— never suggest related services!")

    return {
        'is_new': False,
        'name': name,
        'context_text': context,
        'customer': customer
    }

def update_memory_from_message(phone, message):
    updates = {}

    name = extract_name(message)
    if name:
        updates['name'] = name

    birthday = extract_birthday(message)
    if birthday:
        updates['birthday'] = birthday

    allergy = extract_allergy(message)
    if allergy:
        updates['allergies'] = allergy

    if updates:
        update_customer_profile(phone, **updates)

    return updates
