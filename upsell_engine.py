from database import (get_service_by_name,
                       get_customer)

UPSELL_RULES = {
    'Haircut': {
        'upsell': 'Head Massage',
        'reason': 'Perfect combo — '
                  'same visit, only 30 mins extra',
        'discount': None
    },
    'Highlights': {
        'upsell': 'Toning',
        'reason': 'Toning makes highlights '
                  'last 3x longer ✨',
        'discount': None
    },
    'Balayage': {
        'upsell': 'Hair Spa',
        'reason': 'Hair spa after balayage '
                  'seals the color perfectly',
        'discount': 10
    },
    'Root Touchup': {
        'upsell': 'Toning',
        'reason': 'Toning blends root touchup '
                  'seamlessly',
        'discount': None
    },
    'Keratin': {
        'upsell': 'Hair Spa',
        'reason': 'Hair spa maximizes '
                  'keratin results',
        'discount': None
    }
}

def get_upsell_message(service_name, phone):
    customer = get_customer(phone)
    rule = UPSELL_RULES.get(service_name)

    if not rule:
        return None

    upsell_service = get_service_by_name(
        rule['upsell'])
    if not upsell_service:
        return None

    price = upsell_service['price']
    if rule['discount']:
        discounted = int(
            price * (1 - rule['discount']/100))
        price_text = (f"₹{discounted} "
                     f"(₹{price} - "
                     f"{rule['discount']}% off!)")
    else:
        price_text = f"₹{price}"

    name = customer['name'] if customer else "Aap"

    message = (
        f"Ek suggestion {name}! 💡\n\n"
        f"*{rule['upsell']}* add karein? "
        f"{rule['reason']}\n"
        f"Price: {price_text}\n\n"
        f"Add karna hai? Reply *YES* 😊"
    )

    return {
        'message': message,
        'upsell_service': rule['upsell'],
        'upsell_price': upsell_service['price']
    }

def log_upsell_result(phone, original,
                       upsell, accepted,
                       revenue):
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO upsell_log
    (customer_phone, original_service,
     upsell_offered, accepted, revenue_gained)
    VALUES (?,?,?,?,?)
    ''', (phone, original, upsell,
          accepted, revenue))
    conn.commit()
    conn.close()