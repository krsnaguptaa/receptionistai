// ── TIME DISPLAY ──────────────────────
function updateTime() {
    const el = document.getElementById(
        'current-time');
    if (el) {
        const now = new Date();
        el.textContent = now.toLocaleTimeString(
            'en-IN', {
                hour: '2-digit',
                minute: '2-digit'
            }
        );
    }
}
setInterval(updateTime, 1000);
updateTime();

// ── ADD WALK-IN ───────────────────────
function addWalkin() {
    const name = document.getElementById(
        'walkin-name').value;
    const phone = document.getElementById(
        'walkin-phone').value;
    const service = document.getElementById(
        'walkin-service').value;
    const stylist = document.getElementById(
        'walkin-stylist').value;

    if (!name || !service) {
        alert('Name aur service required hai!');
        return;
    }

    fetch('/api/add-walkin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            phone: phone,
            service: service,
            stylist: stylist
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert(`✅ ${name} added successfully!`);
            location.reload();
        } else {
            alert('Something went wrong!');
        }
    })
    .catch(err => {
        console.error(err);
        alert('Error adding walk-in!');
    });
}

// ── COMPLETE BOOKING ──────────────────
function completeBooking(bookingId) {
    if (!confirm(
        'Mark this booking as complete?\n' +
        'Invoice + review request will be sent.')) {
        return;
    }

    fetch('/api/complete-booking', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            booking_id: bookingId
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert(
                '✅ Done!\n' +
                'Invoice + review sent to customer!'
            );
            location.reload();
        }
    })
    .catch(err => {
        console.error(err);
        alert('Error completing booking!');
    });
}

// ── SEND BROADCAST ────────────────────
function sendBroadcast() {
    const message = document.getElementById(
        'broadcast-message').value;
    const segment = document.getElementById(
        'broadcast-segment').value;

    if (!message) {
        alert('Message likhna zaroori hai!');
        return;
    }

    if (!confirm(
        `Send to ${segment} customers?\n\n` +
        `Message: ${message}`)) {
        return;
    }

    fetch('/api/send-broadcast', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            segment: segment
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert(
                `✅ Broadcast sent!\n` +
                `${data.sent_count} customers ` +
                `ko message gaya!`
            );
            document.getElementById(
                'broadcast-message').value = '';
        }
    })
    .catch(err => {
        console.error(err);
        alert('Broadcast failed!');
    });
}

// ── AUTO REFRESH DASHBOARD ────────────
if (window.location.pathname === '/') {
    setInterval(() => {
        location.reload();
    }, 300000); // Refresh every 5 minutes
}