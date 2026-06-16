import sqlite3
from datetime import datetime

def get_db():
    conn = sqlite3.connect('receptionistai.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    conn = get_db()
    c = conn.cursor()

    # CUSTOMERS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id                INTEGER PRIMARY KEY,
        phone             TEXT UNIQUE NOT NULL,
        name              TEXT,
        email             TEXT,
        birthday          TEXT,
        anniversary       TEXT,
        preferred_stylist TEXT,
        last_service      TEXT,
        last_visit_date   TEXT,
        hair_formula      TEXT,
        hair_type         TEXT,
        allergies         TEXT,
        usual_order       TEXT,
        dietary_notes     TEXT,
        total_visits      INTEGER DEFAULT 0,
        total_spent       INTEGER DEFAULT 0,
        avg_spend         INTEGER DEFAULT 0,
        status            TEXT DEFAULT 'active',
        churn_stage       INTEGER DEFAULT 0,
        privacy_consent   INTEGER DEFAULT 0,
        created_at        TIMESTAMP
                          DEFAULT CURRENT_TIMESTAMP
    )''')

    # STYLISTS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS stylists (
        id          INTEGER PRIMARY KEY,
        name        TEXT NOT NULL,
        speciality  TEXT,
        experience  TEXT,
        is_active   INTEGER DEFAULT 1
    )''')

    # SERVICES TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id            INTEGER PRIMARY KEY,
        name          TEXT NOT NULL,
        price         INTEGER NOT NULL,
        duration_mins INTEGER NOT NULL,
        category      TEXT,
        stylist       TEXT DEFAULT 'Any',
        upsell_1      TEXT,
        upsell_2      TEXT,
        description   TEXT,
        is_active     INTEGER DEFAULT 1
    )''')

    # BOOKINGS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id              INTEGER PRIMARY KEY,
        customer_phone  TEXT,
        customer_name   TEXT,
        service         TEXT,
        stylist         TEXT,
        date            TEXT,
        time            TEXT,
        duration_mins   INTEGER,
        price           INTEGER,
        upsell_added    TEXT,
        upsell_revenue  INTEGER DEFAULT 0,
        booking_type    TEXT DEFAULT 'whatsapp',
        status          TEXT DEFAULT 'confirmed',
        invoice_sent    INTEGER DEFAULT 0,
        review_sent     INTEGER DEFAULT 0,
        completed_at    TIMESTAMP,
        created_at      TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
    )''')

    # CONVERSATIONS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id              INTEGER PRIMARY KEY,
        customer_phone  TEXT,
        direction       TEXT,
        message         TEXT,
        timestamp       TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
    )''')

    # CAMPAIGNS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS campaigns (
        id              INTEGER PRIMARY KEY,
        customer_phone  TEXT,
        campaign_type   TEXT,
        message_sent    TEXT,
        sent_at         TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP,
        responded       INTEGER DEFAULT 0,
        booking_created INTEGER DEFAULT 0
    )''')

    # BROADCASTS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS broadcasts (
        id              INTEGER PRIMARY KEY,
        title           TEXT,
        message         TEXT,
        target_segment  TEXT,
        sent_count      INTEGER DEFAULT 0,
        response_count  INTEGER DEFAULT 0,
        created_at      TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
    )''')

    # UPSELL LOG TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS upsell_log (
        id               INTEGER PRIMARY KEY,
        customer_phone   TEXT,
        original_service TEXT,
        upsell_offered   TEXT,
        accepted         INTEGER DEFAULT 0,
        revenue_gained   INTEGER DEFAULT 0,
        created_at       TIMESTAMP
                         DEFAULT CURRENT_TIMESTAMP
    )''')

    # CAFE MENU TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS cafe_menu (
        id             INTEGER PRIMARY KEY,
        name           TEXT NOT NULL,
        price          INTEGER NOT NULL,
        category       TEXT,
        description    TEXT,
        is_veg         INTEGER DEFAULT 1,
        is_available   INTEGER DEFAULT 1,
        prep_time_mins INTEGER DEFAULT 10
    )''')

    # CAFE ORDERS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS cafe_orders (
        id             INTEGER PRIMARY KEY,
        customer_phone TEXT,
        customer_name  TEXT,
        items          TEXT,
        total_amount   INTEGER DEFAULT 0,
        table_number   TEXT,
        status         TEXT DEFAULT 'pending',
        created_at     TIMESTAMP
                       DEFAULT CURRENT_TIMESTAMP,
        updated_at     TIMESTAMP
    )''')

    # DAILY SPECIALS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS daily_specials (
        id             INTEGER PRIMARY KEY,
        name           TEXT,
        price          INTEGER,
        original_price INTEGER,
        description    TEXT,
        day            TEXT DEFAULT 'Daily'
    )''')

    # INSERT SAMPLE DATA
    _insert_sample_data(c)
    conn.commit()
    conn.close()
    print("✅ Database ready!")

def _insert_sample_data(c):
    # Stylists
    stylists = [
        (1,'Amit','Balayage, Highlights','5 years'),
        (2,'Raj','Haircut, Color','3 years'),
        (3,'Priya','Keratin, Smoothening','4 years')
    ]
    for s in stylists:
        c.execute('''INSERT OR IGNORE INTO stylists
                     (id,name,speciality,experience)
                     VALUES (?,?,?,?)''', s)

    # Services
    services = [
        (1,'Haircut',500,45,'Hair',
         'Any','Head Massage','Hair Spa',
         'Classic haircut'),
        (2,'Highlights',2500,120,'Color',
         'Amit','Toning','Hair Spa',
         'Full head highlights'),
        (3,'Balayage',4500,180,'Color',
         'Amit','Toning','Keratin',
         'Natural balayage'),
        (4,'Root Touchup',1500,90,'Color',
         'Any','Toning','Hair Spa',
         'Root touch-up'),
        (5,'Keratin',3500,180,'Treatment',
         'Priya','Hair Spa','Head Massage',
         'Keratin treatment'),
        (6,'Hair Spa',800,60,'Treatment',
         'Any','Head Massage',None,
         'Deep conditioning'),
        (7,'Head Massage',300,30,'Treatment',
         'Any',None,None,
         'Relaxing massage'),
        (8,'Toning',500,30,'Color',
         'Any',None,None,
         'Hair toning')
    ]
    for s in services:
        c.execute('''INSERT OR IGNORE INTO services
            (id,name,price,duration_mins,
             category,stylist,upsell_1,
             upsell_2,description)
            VALUES (?,?,?,?,?,?,?,?,?)''', s)

    # Cafe menu
    cafe_items = [
        (1,'Espresso',120,'Coffee',
         'Strong Italian shot',1,1,5),
        (2,'Cappuccino',180,'Coffee',
         'Espresso with steamed milk',1,1,7),
        (3,'Cold Brew',220,'Coffee',
         'Slow steeped cold coffee',1,1,3),
        (4,'Mango Cold Brew',260,'Coffee',
         'Cold brew with mango',1,1,3),
        (5,'Croissant',120,'Bakery',
         'Fresh buttery croissant',1,1,2),
        (6,'Almond Croissant',140,'Bakery',
         'Croissant with almond filling',1,1,2),
        (7,'Avocado Toast',280,'Food',
         'Sourdough with avocado',1,1,8),
        (8,'Pancakes',220,'Food',
         'Fluffy pancakes with maple',1,1,10),
    ]
    for item in cafe_items:
        c.execute('''INSERT OR IGNORE INTO
            cafe_menu
            (id,name,price,category,
             description,is_veg,
             is_available,prep_time_mins)
            VALUES (?,?,?,?,?,?,?,?)''', item)

    # Daily special
    c.execute('''INSERT OR IGNORE INTO
        daily_specials
        (id,name,price,original_price,
         description,day)
        VALUES (1,
        'Mango Cold Brew + Croissant',
        320,380,
        'Monday special combo',
        'Monday')''')

# ── CUSTOMER FUNCTIONS ─────────────────

def get_customer(phone):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM customers WHERE phone=?",
        (phone,))
    result = c.fetchone()
    conn.close()
    return result

def save_customer(phone, name=None):
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO customers
                 (phone, privacy_consent)
                 VALUES (?, 1)''', (phone,))
    if name:
        c.execute('''UPDATE customers
                     SET name=?
                     WHERE phone=?''',
                  (name, phone))
    conn.commit()
    conn.close()

def update_customer_profile(phone, **kwargs):
    conn = get_db()
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(
            f"UPDATE customers SET {key}=?"
            f" WHERE phone=?",
            (value, phone))
    conn.commit()
    conn.close()

def update_after_visit(phone, service,
                        stylist, amount):
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    c = conn.cursor()
    c.execute('''UPDATE customers SET
                 last_service=?,
                 last_visit_date=?,
                 preferred_stylist=?,
                 total_visits=total_visits+1,
                 total_spent=total_spent+?,
                 churn_stage=0,
                 status='active'
                 WHERE phone=?''',
              (service, today, stylist,
               amount, phone))
    conn.commit()
    conn.close()

def get_all_customers():
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM customers "
        "ORDER BY created_at DESC")
    result = c.fetchall()
    conn.close()
    return result

def get_churn_risk_customers():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM customers
    WHERE last_visit_date IS NOT NULL
    AND status='active'
    AND julianday('now') -
        julianday(last_visit_date) >= 30
    ORDER BY last_visit_date ASC
    ''')
    result = c.fetchall()
    conn.close()
    return result

def get_birthday_customers_today():
    today = datetime.now().strftime('%m-%d')
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM customers
    WHERE birthday IS NOT NULL
    AND substr(birthday,6,5)=?
    ''', (today,))
    result = c.fetchall()
    conn.close()
    return result

# ── SERVICE FUNCTIONS ──────────────────

def get_all_services():
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM services "
        "WHERE is_active=1 "
        "ORDER BY category")
    result = c.fetchall()
    conn.close()
    return result

def get_service_by_name(name):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM services WHERE "
        "LOWER(name) LIKE LOWER(?)",
        (f'%{name}%',))
    result = c.fetchone()
    conn.close()
    return result

def get_services_formatted():
    services = get_all_services()
    categories = {}
    for s in services:
        cat = s['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(s)

    text = ""
    for cat, items in categories.items():
        text += f"\n*{cat}:*\n"
        for item in items:
            text += (f"• {item['name']}: "
                    f"₹{item['price']} "
                    f"({item['duration_mins']}"
                    f" mins)\n")
    return text

# ── BOOKING FUNCTIONS ──────────────────

def get_todays_bookings():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM bookings
    WHERE date=? AND status='confirmed'
    ORDER BY time
    ''', (today,))
    result = c.fetchall()
    conn.close()
    return result

def get_bookings_by_date(date):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM bookings
    WHERE date=? AND status='confirmed'
    ORDER BY time
    ''', (date,))
    result = c.fetchall()
    conn.close()
    return result

def check_slot_available(date, time, stylist):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT id FROM bookings
    WHERE date=? AND time=?
    AND stylist=?
    AND status='confirmed'
    ''', (date, time, stylist))
    result = c.fetchone()
    conn.close()
    return result is None

def save_booking(phone, name, service,
                 stylist, date, time,
                 duration, price,
                 booking_type='whatsapp'):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO bookings
    (customer_phone, customer_name,
     service, stylist, date, time,
     duration_mins, price, booking_type)
    VALUES (?,?,?,?,?,?,?,?,?)
    ''', (phone, name, service, stylist,
          date, time, duration, price,
          booking_type))
    booking_id = c.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def mark_booking_complete(booking_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE bookings SET
    status='completed',
    completed_at=CURRENT_TIMESTAMP
    WHERE id=?
    ''', (booking_id,))
    conn.commit()
    conn.close()

def get_todays_revenue():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT COALESCE(SUM(price+
    COALESCE(upsell_revenue,0)),0)
    FROM bookings
    WHERE date=?
    AND status IN ('confirmed','completed')
    ''', (today,))
    result = c.fetchone()[0]
    conn.close()
    return result

def get_monthly_revenue():
    month = datetime.now().strftime('%Y-%m')
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT COALESCE(SUM(price),0)
    FROM bookings
    WHERE date LIKE ?
    AND status IN ('confirmed','completed')
    ''', (f'{month}%',))
    result = c.fetchone()[0]
    conn.close()
    return result

def get_total_customers():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM customers")
    result = c.fetchone()[0]
    conn.close()
    return result

def log_conversation(phone, direction, message):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO conversations
    (customer_phone, direction, message)
    VALUES (?,?,?)
    ''', (phone, direction, message))
    conn.commit()
    conn.close()