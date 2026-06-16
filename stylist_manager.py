from database import get_db
from datetime import datetime

def get_all_stylists():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM stylists")
    result = c.fetchall()
    conn.close()
    return result

def add_stylist(name, speciality, experience):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO stylists
    (name, speciality, experience)
    VALUES (?,?,?)
    ''', (name, speciality, experience))
    conn.commit()
    conn.close()
    return True

def update_stylist(stylist_id, name,
                    speciality, experience):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE stylists SET
    name=?, speciality=?, experience=?
    WHERE id=?
    ''', (name, speciality,
          experience, stylist_id))
    conn.commit()
    conn.close()
    return True

def toggle_stylist(stylist_id, is_active):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE stylists SET is_active=?
    WHERE id=?
    ''', (is_active, stylist_id))
    conn.commit()
    conn.close()

def get_stylist_bookings_today(stylist_name):
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM bookings
    WHERE stylist=? AND date=?
    AND status='confirmed'
    ORDER BY time
    ''', (stylist_name, today))
    result = c.fetchall()
    conn.close()
    return result

def get_stylist_revenue_month(stylist_name):
    month = datetime.now().strftime('%Y-%m')
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT COALESCE(SUM(price),0)
    FROM bookings
    WHERE stylist=? AND date LIKE ?
    AND status IN ('confirmed','completed')
    ''', (stylist_name, f'{month}%'))
    result = c.fetchone()[0]
    conn.close()
    return result