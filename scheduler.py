import schedule
import time
import threading
from database import (get_todays_bookings,
                       get_db)
from retention_engine import (run_churn_campaigns,
                               run_birthday_campaigns)
from review_engine import send_post_visit_message
from whatsapp import send_reminder
from datetime import datetime
import requests
import os

def keep_alive():
    try:
        url = os.environ.get(
            'RENDER_URL', '')
        if url:
            requests.get(
                f"https://{url}/",
                timeout=10)
            print("💓 Keep alive ping sent")
    except Exception as e:
        print(f"Keep alive error: {e}")

# Add to run_scheduler():
# Ping every 10 minutes
schedule.every(10).minutes.do(keep_alive)

def send_daily_reminders():
    bookings = get_todays_bookings()
    now_hour = datetime.now().hour

    for booking in bookings:
        booking_hour = int(
            booking['time'].split(':')[0])

        # 2 hour reminder
        if booking_hour - now_hour == 2:
            send_reminder(
                booking['customer_phone'],
                booking['customer_name'],
                booking['service'],
                booking['time'],
                booking['stylist']
            )
            print(f"⏰ Reminder sent to "
                  f"{booking['customer_name']}")

def send_morning_report():
    from database import (get_todays_revenue,
                           get_total_customers,
                           get_churn_risk_customers)
    from config import OWNER_WHATSAPP
    from whatsapp import send_message

    bookings = get_todays_bookings()
    revenue = get_todays_revenue()
    customers = get_total_customers()
    churn = get_churn_risk_customers()

    report = (
        f"☀️ *Good Morning! Daily Report*\n\n"
        f"📅 Aaj ke bookings: "
        f"{len(bookings)}\n"
        f"💰 Expected revenue: ₹{revenue}\n"
        f"👥 Total customers: {customers}\n"
        f"⚠️ Churn risk: {len(churn)}\n\n"
        f"Dashboard: "
        f"http://localhost:5000\n\n"
        f"Acha din ho! 🌟"
    )
    send_message(OWNER_WHATSAPP, report)

def run_scheduler():
    # Morning report at 9am
    schedule.every().day.at("09:00").do(
        send_morning_report)

    # Reminders every hour
    schedule.every().hour.do(
        send_daily_reminders)

    # Churn campaigns daily at 10am
    schedule.every().day.at("10:00").do(
        run_churn_campaigns)

    # Birthday campaigns daily at 9am
    schedule.every().day.at("09:00").do(
        run_birthday_campaigns)

    print("✅ Scheduler running...")
    while True:
        schedule.run_pending()
        time.sleep(60)

def start_scheduler_thread():
    thread = threading.Thread(
        target=run_scheduler,
        daemon=True
    )
    thread.start()
