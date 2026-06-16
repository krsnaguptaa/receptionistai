from database import get_db
from datetime import datetime

def get_full_analytics():
    conn = get_db()
    c = conn.cursor()

    # Monthly bookings
    month = datetime.now().strftime('%Y-%m')
    c.execute('''
    SELECT COUNT(*) FROM bookings
    WHERE date LIKE ?
    AND status IN ('confirmed','completed')
    ''', (f'{month}%',))
    monthly_bookings = c.fetchone()[0]

    # Monthly revenue
    c.execute('''
    SELECT COALESCE(SUM(price),0)
    FROM bookings
    WHERE date LIKE ?
    AND status IN ('confirmed','completed')
    ''', (f'{month}%',))
    monthly_revenue = c.fetchone()[0]

    # Upsell revenue
    c.execute('''
    SELECT COALESCE(SUM(upsell_revenue),0)
    FROM bookings
    WHERE date LIKE ?
    ''', (f'{month}%',))
    upsell_revenue = c.fetchone()[0]

    # Top services
    c.execute('''
    SELECT service, COUNT(*) as count,
    SUM(price) as revenue
    FROM bookings
    WHERE date LIKE ?
    GROUP BY service
    ORDER BY count DESC LIMIT 5
    ''', (f'{month}%',))
    top_services = c.fetchall()

    # New customers this month
    c.execute('''
    SELECT COUNT(*) FROM customers
    WHERE date(created_at) LIKE ?
    ''', (f'{month}%',))
    new_customers = c.fetchone()[0]

    # Campaigns won back
    c.execute('''
    SELECT COUNT(*) FROM campaigns
    WHERE campaign_type LIKE 'churn%'
    AND booking_created=1
    AND date(sent_at) LIKE ?
    ''', (f'{month}%',))
    won_back = c.fetchone()[0]

    # Reviews sent
    c.execute('''
    SELECT COUNT(*) FROM bookings
    WHERE review_sent=1
    AND date LIKE ?
    ''', (f'{month}%',))
    reviews_sent = c.fetchone()[0]

    conn.close()

    return {
        'monthly_bookings': monthly_bookings,
        'monthly_revenue': monthly_revenue,
        'upsell_revenue': upsell_revenue,
        'top_services': top_services,
        'new_customers': new_customers,
        'won_back': won_back,
        'reviews_sent': reviews_sent
    }