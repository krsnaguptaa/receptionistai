from database import (get_churn_risk_customers,
                       get_birthday_customers_today,
                       get_db)
from whatsapp import (send_churn_winback,
                       send_birthday_message)
from config import (CHURN_DAY_1, CHURN_DAY_2,
                    CHURN_DAY_3, CHURN_DISCOUNT_1,
                    CHURN_DISCOUNT_2,
                    CHURN_DISCOUNT_3,
                    BIRTHDAY_DISCOUNT)
from datetime import datetime

def run_churn_campaigns():
    customers = get_churn_risk_customers()
    sent_count = 0

    for customer in customers:
        if not customer['phone']:
            continue

        last_visit = customer['last_visit_date']
        if not last_visit:
            continue

        last_date = datetime.strptime(
            last_visit, '%Y-%m-%d')
        days_gone = (datetime.now() -
                     last_date).days

        # Check if already sent campaign
        if already_sent_campaign(
                customer['phone'],
                days_gone):
            continue

        # Determine which campaign to send
        if days_gone >= CHURN_DAY_3:
            discount = CHURN_DISCOUNT_3
            campaign_type = 'churn_90'
        elif days_gone >= CHURN_DAY_2:
            discount = CHURN_DISCOUNT_2
            campaign_type = 'churn_60'
        elif days_gone >= CHURN_DAY_1:
            discount = CHURN_DISCOUNT_1
            campaign_type = 'churn_30'
        else:
            continue

        # Send win-back message
        send_churn_winback(
            customer['phone'],
            customer['name'] or 'Aap',
            days_gone,
            discount
        )

        # Log campaign
        log_campaign(
            customer['phone'],
            campaign_type
        )
        sent_count += 1

    print(f"✅ Churn campaigns sent: {sent_count}")
    return sent_count

def run_birthday_campaigns():
    customers = get_birthday_customers_today()
    sent_count = 0

    for customer in customers:
        if not customer['phone']:
            continue

        # Check not already sent today
        if already_sent_campaign(
                customer['phone'],
                'birthday_today'):
            continue

        send_birthday_message(
            customer['phone'],
            customer['name'] or 'Aap'
        )

        log_campaign(
            customer['phone'],
            'birthday'
        )
        sent_count += 1

    print(f"✅ Birthday messages sent: {sent_count}")
    return sent_count

def already_sent_campaign(phone, campaign_type):
    conn = get_db()
    c = conn.cursor()

    if isinstance(campaign_type, int):
        if campaign_type >= CHURN_DAY_3:
            ctype = 'churn_90'
        elif campaign_type >= CHURN_DAY_2:
            ctype = 'churn_60'
        else:
            ctype = 'churn_30'
    else:
        ctype = campaign_type

    c.execute('''
    SELECT id FROM campaigns
    WHERE customer_phone=?
    AND campaign_type=?
    AND date(sent_at) >= date('now','-30 days')
    ''', (phone, ctype))
    result = c.fetchone()
    conn.close()
    return result is not None

def log_campaign(phone, campaign_type):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO campaigns
    (customer_phone, campaign_type)
    VALUES (?,?)
    ''', (phone, campaign_type))
    conn.commit()
    conn.close()