from database import (get_service_by_name,
                       check_slot_available,
                       save_booking,
                       update_after_visit,
                       get_db)
from whatsapp import send_booking_confirmation
from datetime import datetime, timedelta

def get_available_slots(date, stylist):
    all_slots = [
        "10:00", "10:30", "11:00", "11:30",
        "12:00", "12:30", "13:00", "13:30",
        "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00", "17:30",
        "18:00", "18:30", "19:00", "19:30"
    ]
    available = []
    for slot in all_slots:
        if check_slot_available(
                date, slot, stylist):
            available.append(slot)
    return available

def get_next_available(stylist, days_ahead=7):
    results = []
    for i in range(days_ahead):
        date = (datetime.now() +
                timedelta(days=i+1))
        date_str = date.strftime('%Y-%m-%d')
        day_name = date.strftime('%A')

        # Skip Sundays
        if day_name == 'Sunday':
            continue

        slots = get_available_slots(
            date_str, stylist)
        if slots:
            results.append({
                'date': date_str,
                'day': day_name,
                'slots': slots[:3]
            })
        if len(results) >= 3:
            break
    return results

def process_booking(phone, name,
                    service_name,
                    date, time,
                    stylist=None):
    # Get service from database
    service = get_service_by_name(service_name)

    if not service:
        return {
            'success': False,
            'message': (
                f"Sorry bhai, "
                f"'{service_name}' humari "
                f"services mein nahi hai. "
                f"Services list dekhni hai? 😊"
            )
        }

    # Set stylist
    if not stylist:
        stylist = (service['stylist']
                   if service['stylist'] != 'Any'
                   else 'Amit')

    # Check if closed day
    try:
        date_obj = datetime.strptime(
            date, '%Y-%m-%d')
        if date_obj.strftime('%A') == 'Sunday':
            return {
                'success': False,
                'message': (
                    "Sunday ko hum closed hain! 😊"
                    "\nKoi aur din chalega?"
                )
            }
    except:
        pass

    # Check availability
    is_free = check_slot_available(
        date, time, stylist)

    if not is_free:
        # Get next available slots
        available = get_available_slots(
            date, stylist)

        if available:
            slots_text = "\n".join(
                [f"→ {s}" for s in available[:3]])
            return {
                'success': False,
                'message': (
                    f"{stylist} {time} pe "
                    f"available nahi hai. 😔\n\n"
                    f"Ye slots free hain:\n"
                    f"{slots_text}\n\n"
                    f"Kaunsa chahiye? 😊"
                )
            }
        else:
            return {
                'success': False,
                'message': (
                    f"{date} ko {stylist} "
                    f"fully booked hai.\n"
                    f"Koi aur din try karein? 📅"
                )
            }

    # Save booking
    booking_id = save_booking(
        phone=phone,
        name=name,
        service=service['name'],
        stylist=stylist,
        date=date,
        time=time,
        duration=service['duration_mins'],
        price=service['price'],
        booking_type='whatsapp'
    )

    # Update customer record
    update_after_visit(
        phone,
        service['name'],
        stylist,
        service['price']
    )

    # Send confirmation
    booking_details = {
        'name': name,
        'service': service['name'],
        'stylist': stylist,
        'date': date,
        'time': time,
        'price': service['price']
    }
    send_booking_confirmation(
        phone, booking_details)

    return {
        'success': True,
        'booking_id': booking_id,
        'message': 'Booking confirmed!'
    }

def add_walkin(phone, name,
               service_name, stylist):
    service = get_service_by_name(service_name)
    if not service:
        return False

    today = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now().strftime('%H:%M')

    save_booking(
        phone=phone or 'walkin_customer',
        name=name,
        service=service['name'],
        stylist=stylist,
        date=today,
        time=now,
        duration=service['duration_mins'],
        price=service['price'],
        booking_type='walkin'
    )
    return True

def cancel_booking(booking_id, phone):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE bookings SET status='cancelled'
    WHERE id=? AND customer_phone=?
    ''', (booking_id, phone))
    conn.commit()
    conn.close()
    return True

def get_customer_bookings(phone):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM bookings
    WHERE customer_phone=?
    ORDER BY date DESC, time DESC
    LIMIT 10
    ''', (phone,))
    result = c.fetchall()
    conn.close()
    return result

def format_available_slots(slots_data):
    if not slots_data:
        return "Abhi koi slots available nahi."

    text = "Available slots:\n\n"
    for day_data in slots_data:
        text += f"📅 *{day_data['day']}* "
        text += f"({day_data['date']})\n"
        for slot in day_data['slots']:
            text += f"   ⏰ {slot}\n"
        text += "\n"
    return text