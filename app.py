from flask import (Flask, request,
                   jsonify, render_template)
from config import (VERIFY_TOKEN,
                    OWNER_WHATSAPP,
                    BUSINESS_NAME)
from gemini_brain import (
    get_ai_response,
    detect_booking_intent,
    detect_complaint,
    detect_upsell_acceptance)
from whatsapp import (send_message,
                       send_owner_alert,
                       send_booking_confirmation)
from database import (
    create_database,
    save_customer,
    get_customer,
    log_conversation,
    get_todays_bookings,
    get_todays_revenue,
    get_monthly_revenue,
    get_total_customers,
    get_churn_risk_customers,
    get_all_customers,
    get_all_services,
    mark_booking_complete,
    update_customer_profile)
from memory_engine import (
    update_memory_from_message)
from upsell_engine import (
    get_upsell_message,
    log_upsell_result)
from analytics_engine import get_full_analytics
from booking_engine import (process_booking,
                              add_walkin)
from scheduler import start_scheduler_thread
from cafe_engine import (
    get_todays_orders,
    get_cafe_menu,
    update_order_status,
    send_order_ready,
    get_todays_cafe_revenue)
from stylist_manager import (
    get_all_stylists,
    add_stylist,
    update_stylist,
    toggle_stylist,
    get_stylist_bookings_today,
    get_stylist_revenue_month)
from datetime import datetime
import json
import os

app = Flask(__name__)

# Conversation states
states = {}
pending_upsells = {}

# ── WEBHOOK ──────────────────────────

@app.route('/webhook', methods=['GET'])
def verify():
    if (request.args.get('hub.verify_token')
            == VERIFY_TOKEN):
        return request.args.get(
            'hub.challenge'), 200
    return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        value = (data['entry'][0]
                 ['changes'][0]['value'])
        if 'messages' not in value:
            return jsonify({"status": "ok"})

        msg = value['messages'][0]
        phone = msg['from']

        # ── HANDLE IMAGE (Selfie Feature) ──
        if msg['type'] == 'image':
            try:
                from ai_image_engine import (
                    handle_image_message)
                image_id = msg['image']['id']
                caption = msg['image'].get(
                    'caption', '')
                save_customer(phone)
                send_message(phone,
                    "📸 Selfie mil gayi!\n"
                    "AI analyze kar raha hai..."
                    " ⏳\n"
                    "30 seconds mein "
                    "batata hoon! 🔍")
                handle_image_message(
                    phone, image_id, caption)
            except Exception as img_err:
                print(f"Image error: {img_err}")
                send_message(phone,
                    "Selfie nahi dekh paya 😅\n"
                    "Dobara try karo!")
            return jsonify({"status": "ok"})

        # ── HANDLE NON-TEXT ───────────────
        if msg['type'] not in ['text']:
            send_message(phone,
                "Hi! 😊 Text message bhejo\n"
                "Ya hairstyle ke liye "
                "selfie bhejo! 📸")
            return jsonify({"status": "ok"})

        # ── HANDLE TEXT ───────────────────
        text = msg['text']['body']
        print(f"\n📱 {phone}: {text}")

        # Save customer
        save_customer(phone)

        # Update memory
        update_memory_from_message(phone, text)

        # Log incoming
        log_conversation(phone, 'in', text)

        # Check pending upsell response
        if phone in pending_upsells:
            if detect_upsell_acceptance(text):
                upsell = pending_upsells[phone]
                send_message(phone,
                    f"✅ *{upsell['upsell_service']}"
                    f"* add kar diya!\n"
                    f"₹{upsell['upsell_price']}"
                    f" extra.\n"
                    f"See you soon! 💇")
                log_upsell_result(
                    phone,
                    upsell.get('original', ''),
                    upsell['upsell_service'],
                    1,
                    upsell['upsell_price'])
                del pending_upsells[phone]
                return jsonify({"status": "ok"})
            else:
                del pending_upsells[phone]

        # Complaint detection
        if detect_complaint(text):
            customer = get_customer(phone)
            name = (customer['name']
                    if customer and customer['name']
                    else phone)
            send_owner_alert(
                OWNER_WHATSAPP,
                'complaint',
                f"Customer: {name}\n"
                f"Message: {text}")

        # Get AI response
        reply = get_ai_response(phone, text)
        send_message(phone, reply)

        # Log outgoing
        log_conversation(phone, 'out', reply)

        # Booking intent handling
        if detect_booking_intent(text):
            customer = get_customer(phone)
            name = (customer['name']
                    if customer and customer['name']
                    else phone)

            # Notify owner
            send_owner_alert(
                OWNER_WHATSAPP,
                'new_booking',
                f"📅 Booking inquiry!\n"
                f"Customer: {name}\n"
                f"Message: {text}")

            # Check upsell opportunity
            from gemini_brain import (
                extract_service_from_message)
            service = extract_service_from_message(
                text)
            if service:
                upsell = get_upsell_message(
                    service, phone)
                if upsell:
                    pending_upsells[phone] = upsell
                    send_message(
                        phone,
                        upsell['message'])

        print(f"🤖 Replied: {reply[:60]}...")

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()

    return jsonify({"status": "ok"})
# ── MAIN DASHBOARD ────────────────────

@app.route('/')
def dashboard():
    bookings = get_todays_bookings()
    revenue = get_todays_revenue()
    monthly = get_monthly_revenue()
    total_c = get_total_customers()
    churn = get_churn_risk_customers()
    analytics = get_full_analytics()

    alerts = []
    if len(churn) > 0:
        alerts.append(
            f"⚠️ {len(churn)} customers "
            f"30+ days se nahi aaye!")
    if len(bookings) == 0:
        alerts.append(
            "📭 Aaj koi booking nahi abhi")

    return render_template('dashboard.html',
        business_name=BUSINESS_NAME,
        bookings=bookings,
        todays_count=len(bookings),
        todays_revenue=f"{revenue:,}",
        monthly_revenue=f"{monthly:,}",
        total_customers=total_c,
        churn_count=len(churn),
        alerts=alerts,
        analytics=analytics)

# ── CUSTOMERS PAGE ────────────────────

@app.route('/customers')
def customers():
    all_customers = get_all_customers()
    return render_template('customers.html',
        customers=all_customers,
        business_name=BUSINESS_NAME)

# ── SERVICES PAGE ─────────────────────

@app.route('/services')
def services():
    from database import get_all_services, get_db
    # Get ALL services including inactive
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM services "
        "ORDER BY category, name")
    all_services = c.fetchall()
    conn.close()

    # Get stylists for dropdown
    all_stylists = get_all_stylists()

    return render_template('services.html',
        services=all_services,
        stylists=all_stylists,
        business_name=BUSINESS_NAME)

# ── STYLISTS PAGE ─────────────────────

@app.route('/stylists')
def stylists_page():
    stylists = get_all_stylists()
    stylist_data = []
    for s in stylists:
        bookings = get_stylist_bookings_today(
            s['name'])
        revenue = get_stylist_revenue_month(
            s['name'])
        stylist_data.append({
            'id': s['id'],
            'name': s['name'],
            'speciality': s['speciality'] or '',
            'experience': s['experience'] or '',
            'is_active': s['is_active'],
            'today_bookings': len(bookings),
            'month_revenue': revenue
        })
    return render_template('stylists.html',
        business_name=BUSINESS_NAME,
        stylists=stylist_data)

# ── CAFE PAGE ─────────────────────────

@app.route('/cafe')
def cafe():
    orders = get_todays_orders()
    menu = get_cafe_menu()
    pending = [o for o in orders
               if o['status'] == 'pending']
    completed = [o for o in orders
                 if o['status'] == 'completed']
    return render_template('cafe.html',
        business_name=BUSINESS_NAME,
        orders=orders,
        menu=menu,
        pending_count=len(pending),
        completed_count=len(completed),
        todays_revenue=get_todays_revenue())

# ── ANALYTICS PAGE ────────────────────

@app.route('/analytics')
def analytics():
    data = get_full_analytics()
    return render_template('analytics.html',
        data=data,
        business_name=BUSINESS_NAME)

# ── API — BOOKINGS ────────────────────

@app.route('/api/complete-booking',
           methods=['POST'])
def complete_booking():
    data = request.json
    mark_booking_complete(data['booking_id'])
    from review_engine import (
        send_post_visit_message)
    send_post_visit_message(data['booking_id'])
    return jsonify({"success": True})

@app.route('/api/add-walkin', methods=['POST'])
def api_add_walkin():
    data = request.json
    name = data.get('name')
    phone = data.get('phone', '')
    service = data.get('service')
    stylist = data.get('stylist')

    if not phone:
        import time
        phone = f"walkin_{int(time.time())}"

    # Save to customers
    save_customer(phone, name)
    update_customer_profile(phone,
        last_service=service,
        last_visit_date=datetime.now().strftime(
            '%Y-%m-%d'),
        preferred_stylist=stylist)

    result = add_walkin(
        phone, name, service, stylist)
    return jsonify({"success": result})

# ── API — SERVICES ────────────────────

@app.route('/api/update-service',
           methods=['POST'])
def update_service():
    from database import get_db
    data = request.json
    print(f"Update service: {data}")

    name = data.get('name', '').strip()
    price = data.get('price', 0)
    duration = data.get('duration', 30)
    category = data.get('category', 'Hair')
    stylist = data.get('stylist', 'Any')
    is_active = data.get('is_active', 1)
    description = data.get('description', '')
    service_id = data.get('id')

    if not name or not service_id:
        return jsonify({
            "success": False,
            "error": "Name and ID required"})

    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE services SET
    name=?, price=?,
    duration_mins=?,
    category=?, stylist=?,
    is_active=?, description=?
    WHERE id=?
    ''', (name, price, duration,
          category, stylist,
          is_active, description,
          service_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/delete-service',
           methods=['POST'])
def delete_service_route():
    from database import get_db
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "DELETE FROM services WHERE id=?",
        (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# ── API — STYLISTS ────────────────────

@app.route('/api/add-stylist',
           methods=['POST'])
def api_add_stylist():
    data = request.json
    add_stylist(
        data['name'],
        data.get('speciality', ''),
        data.get('experience', ''))
    return jsonify({"success": True})

@app.route('/api/update-stylist',
           methods=['POST'])
def api_update_stylist():
    data = request.json
    update_stylist(
        data['id'], data['name'],
        data['speciality'],
        data['experience'])
    return jsonify({"success": True})

@app.route('/api/toggle-stylist',
           methods=['POST'])
def api_toggle_stylist():
    data = request.json
    toggle_stylist(
        data['id'], data['is_active'])
    return jsonify({"success": True})

# ── API — CAFE ────────────────────────

@app.route('/api/order-ready',
           methods=['POST'])
def order_ready():
    data = request.json
    update_order_status(
        data['order_id'], 'ready')
    send_order_ready(
        data['phone'],
        data['name'],
        data['order_id'])
    return jsonify({"success": True})

@app.route('/api/order-complete',
           methods=['POST'])
def order_complete():
    data = request.json
    update_order_status(
        data['order_id'], 'completed')
    return jsonify({"success": True})

# ── API — BROADCAST ───────────────────

@app.route('/api/send-broadcast',
           methods=['POST'])
def send_broadcast_api():
    data = request.json
    message = data.get('message')
    segment = data.get('segment', 'all')
    customers = get_all_customers()
    sent = 0
    for customer in customers:
        if not customer['phone']:
            continue
        if (segment == 'active' and
                customer['status'] != 'active'):
            continue
        from whatsapp import send_broadcast
        send_broadcast(
            customer['phone'], message)
        sent += 1
    return jsonify({
        "success": True,
        "sent_count": sent})

# ── CAFE MENU API ─────────────────────

@app.route('/api/update-menu-item',
           methods=['POST'])
def update_menu_item():
    from database import get_db
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE cafe_menu SET
    name=?, price=?,
    category=?, description=?,
    is_veg=?, is_available=?,
    prep_time_mins=?
    WHERE id=?
    ''', (
        data['name'],
        data['price'],
        data['category'],
        data.get('description',''),
        data.get('is_veg', 1),
        data.get('is_available', 1),
        data.get('prep_time_mins', 5),
        data['id']
    ))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/add-menu-item',
           methods=['POST'])
def add_menu_item():
    from database import get_db
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO cafe_menu
    (name, price, category,
     description, is_veg,
     is_available, prep_time_mins)
    VALUES (?,?,?,?,?,1,?)
    ''', (
        data['name'],
        data['price'],
        data['category'],
        data.get('description',''),
        data.get('is_veg', 1),
        data.get('prep_time_mins', 5)
    ))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/delete-menu-item',
           methods=['POST'])
def delete_menu_item():
    from database import get_db
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "DELETE FROM cafe_menu WHERE id=?",
        (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/onboard')
def onboard():
    return render_template('onboard.html',
        business_name=BUSINESS_NAME)

@app.route('/api/onboard-business',
           methods=['POST'])
def onboard_business():
    from database import get_db
    data = request.json

    try:
        conn = get_db()
        c = conn.cursor()

        # Add all services
        for svc in data.get('services', []):
            if svc['name']:
                c.execute('''
                INSERT OR IGNORE INTO services
                (name, price, duration_mins,
                 category, stylist, is_active)
                VALUES (?,?,?,'Hair','Any',1)
                ''', (
                    svc['name'],
                    svc['price'],
                    svc['duration']
                ))

        conn.commit()
        conn.close()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)})

# ── START ─────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    create_database()
    start_scheduler_thread()
    print("\n" + "━"*40)
    print("🚀 ReceptionistAI LIVE!")
    print(f"📊 Dashboard → localhost:{port}")
    print("━"*40 + "\n")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False)