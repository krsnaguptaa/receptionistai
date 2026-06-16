from database import get_db
from whatsapp import send_invoice_and_review
from config import GOOGLE_REVIEW_URL

def send_post_visit_message(booking_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM bookings WHERE id=?
    ''', (booking_id,))
    booking = c.fetchone()
    conn.close()

    if not booking:
        return False

    if booking['invoice_sent']:
        return False

    send_invoice_and_review(
        booking['customer_phone'],
        booking['customer_name'] or 'Aap',
        booking['service'],
        booking['price']
    )

    # Mark as sent
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE bookings SET
    invoice_sent=1,
    review_sent=1
    WHERE id=?
    ''', (booking_id,))
    conn.commit()
    conn.close()
    return True

def get_review_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT COUNT(*) FROM bookings
    WHERE review_sent=1
    AND date(created_at) >=
    date('now','-30 days')
    ''')
    monthly = c.fetchone()[0]

    c.execute('''
    SELECT COUNT(*) FROM bookings
    WHERE review_sent=1
    ''')
    total = c.fetchone()[0]
    conn.close()

    return {
        'monthly_reviews_requested': monthly,
        'total_reviews_requested': total
    }
