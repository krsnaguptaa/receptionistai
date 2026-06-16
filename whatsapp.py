import requests
from config import (WHATSAPP_TOKEN,
                    PHONE_NUMBER_ID,
                    GOOGLE_REVIEW_URL,
                    BUSINESS_NAME)

BASE = (f"https://graph.facebook.com"
        f"/v18.0/{PHONE_NUMBER_ID}")

def _send(to, body):
    try:
        r = requests.post(
            f"{BASE}/messages",
            headers={
                "Authorization":
                    f"Bearer {WHATSAPP_TOKEN}",
                "Content-Type":
                    "application/json"
            },
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": body}
            }
        )
        return r.json()
    except Exception as e:
        print(f"Send error: {e}")
        return None

def send_message(to, message):
    return _send(to, message)

def send_booking_confirmation(to, b):
    msg = (
        f"✅ *Booking Confirmed!*\n\n"
        f"👤 {b['name']}\n"
        f"💇 {b['service']}\n"
        f"👨‍💼 Stylist: {b['stylist']}\n"
        f"📅 {b['date']}\n"
        f"⏰ {b['time']}\n"
        f"💰 ₹{b['price']}\n\n"
        f"📍 {BUSINESS_NAME}\n"
        f"_Changes ke liye reply karo_ 😊"
    )
    return _send(to, msg)

def send_reminder(to, name,
                  service, time, stylist):
    msg = (
        f"⏰ *Reminder {name}!*\n\n"
        f"Aaj ka appointment:\n"
        f"💇 {service} with {stylist}\n"
        f"🕐 {time}\n\n"
        f"Cancel ke liye reply karo 🙏"
    )
    return _send(to, msg)

def send_invoice_and_review(to, name,
                             service, price):
    msg = (
        f"🧾 *Shukriya {name}!*\n\n"
        f"*Invoice:*\n"
        f"Service: {service}\n"
        f"Amount: ₹{price}\n"
        f"Date: Aaj\n\n"
        f"━━━━━━━━━━━━\n"
        f"⭐ Achha laga? 10 second mein\n"
        f"review do — humari bahut "
        f"help hogi!\n"
        f"👉 {GOOGLE_REVIEW_URL}\n\n"
        f"Milte hain agli baar! 🌟"
    )
    return _send(to, msg)

def send_churn_winback(to, name,
                        days, discount):
    msg = (
        f"Hey {name}! 👋\n\n"
        f"Aapko miss kar rahe hain hum! 😊\n"
        f"{days} din ho gaye last visit ko.\n\n"
        f"Wapas aao — special offer:\n"
        f"🎁 *{discount}% OFF* next service\n\n"
        f"Is week valid hai!\n"
        f"Slot book karna hai? ✨"
    )
    return _send(to, msg)

def send_birthday_message(to, name):
    msg = (
        f"🎂 *Happy Birthday {name}!*\n\n"
        f"{BUSINESS_NAME} ki taraf se\n"
        f"bahut saari shubhkamnayein! 🎉\n\n"
        f"Birthday gift:\n"
        f"🎁 *20% OFF* koi bhi service\n"
        f"Is week valid!\n\n"
        f"Book karna hai? 🌟"
    )
    return _send(to, msg)

def send_owner_alert(to, alert_type, details):
    alerts = {
        'new_booking': '📅 New Booking!',
        'complaint': '⚠️ Customer Complaint!',
        'new_customer': '👤 New Customer!',
        'churn_risk': '🔴 Churn Risk Alert!'
    }
    title = alerts.get(alert_type, '🔔 Alert!')
    msg = f"{title}\n\n{details}"
    return _send(to, msg)

def send_broadcast(to, message):
    return _send(to, message)