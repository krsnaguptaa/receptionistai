from database import get_db, get_customer
from whatsapp import send_message
from datetime import datetime

def get_cafe_menu():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM cafe_menu
    WHERE is_available=1
    ORDER BY category, name
    ''')
    items = c.fetchall()
    conn.close()
    return items

def get_menu_formatted():
    items = get_cafe_menu()
    if not items:
        return "Menu abhi available nahi."

    categories = {}
    for item in items:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    text = "☕ *Hamara Menu:*\n\n"
    for cat, items_list in categories.items():
        text += f"*{cat}*\n"
        for item in items_list:
            veg = ("🟢" if item['is_veg']
                   else "🔴")
            text += (f"{veg} {item['name']}"
                    f" — ₹{item['price']}\n")
        text += "\n"
    return text

def create_order(phone, name,
                  items_text, table_no=None):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO cafe_orders
    (customer_phone, customer_name,
     items, table_number, status)
    VALUES (?,?,?,?,'pending')
    ''', (phone, name, items_text, table_no))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id

def update_order_status(order_id, status):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE cafe_orders
    SET status=?,
    updated_at=CURRENT_TIMESTAMP
    WHERE id=?
    ''', (status, order_id))
    conn.commit()
    conn.close()

def get_todays_orders():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM cafe_orders
    WHERE date(created_at)=?
    ORDER BY created_at DESC
    ''', (today,))
    orders = c.fetchall()
    conn.close()
    return orders

def send_order_confirmation(phone, name,
                             order_id, items,
                             table_no):
    location = (f"Table {table_no}"
                if table_no else "Counter")
    msg = (
        f"✅ *Order Confirmed #{order_id}!*\n\n"
        f"👤 {name}\n"
        f"📍 {location}\n\n"
        f"*Your Order:*\n{items}\n\n"
        f"⏱️ Ready in 10-15 mins!\n"
        f"Hum batayenge jab ready ho 😊"
    )
    send_message(phone, msg)

def send_order_ready(phone, name, order_id):
    msg = (
        f"🎉 *Order Ready {name}!*\n\n"
        f"Order #{order_id} ready hai!\n"
        f"Please collect kar lo 😊☕"
    )
    send_message(phone, msg)

def get_todays_cafe_revenue():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT COALESCE(SUM(total_amount),0)
    FROM cafe_orders
    WHERE date(created_at)=?
    AND status='completed'
    ''', (today,))
    result = c.fetchone()[0]
    conn.close()
    return result

def get_todays_special():
    conn = get_db()
    c = conn.cursor()
    day = datetime.now().strftime('%A')
    c.execute('''
    SELECT * FROM daily_specials
    WHERE day=? OR day='Daily'
    LIMIT 1
    ''', (day,))
    special = c.fetchone()
    conn.close()
    return special