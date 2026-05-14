import frappe
from frappe.utils import now_datetime, today, flt, getdate
import math


# ── Geometry ──────────────────────────────────────────────────────────────────

def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    to_rad = math.radians
    dLat = to_rad(lat2 - lat1)
    dLon = to_rad(lon2 - lon1)
    a = math.sin(dLat / 2) ** 2 + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(dLon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _get_sales_person(user):
    return frappe.db.get_value("Sales Person", {"custom_user_id": user}, "name")


# ── Trail logging (called from update_presence) ───────────────────────────────

def log_location_trail(user, latitude, longitude, accuracy=None):
    """
    Insert a Sales Person Location record and compute distance from the previous point.
    Safe to call on every presence ping — quick, no document framework overhead.
    """
    sp = _get_sales_person(user)
    ref_today = today()
    ts = now_datetime()
    lat = flt(latitude)
    lon = flt(longitude)

    # Find previous point today to calculate incremental distance
    prev = frappe.db.sql('''
        SELECT latitude, longitude FROM `tabSales Person Location`
        WHERE user = %(user)s AND date = %(date)s
        ORDER BY timestamp DESC LIMIT 1
    ''', {'user': user, 'date': ref_today}, as_dict=True)

    dist_km = 0.0
    if prev:
        dist_km = _haversine_km(flt(prev[0].latitude), flt(prev[0].longitude), lat, lon)

    frappe.db.sql('''
        INSERT INTO `tabSales Person Location`
        (name, user, sales_person, date, timestamp, latitude, longitude, accuracy, distance_from_prev_km,
         owner, creation, modified, modified_by, docstatus)
        VALUES
        (%(name)s, %(user)s, %(sp)s, %(date)s, %(ts)s, %(lat)s, %(lon)s, %(acc)s, %(dist)s,
         %(user)s, %(ts)s, %(ts)s, %(user)s, 0)
    ''', {
        'name': f'SPL-{user}-{frappe.generate_hash(length=10)}',
        'user': user, 'sp': sp or None,
        'date': ref_today, 'ts': ts,
        'lat': lat, 'lon': lon,
        'acc': flt(accuracy) if accuracy else None,
        'dist': round(dist_km, 6),
    })
    frappe.db.commit()


# ── Public API ────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_active_locations(date=None):
    """
    Return every rep's trail for a given date (default today), grouped by user.
    'Active' means a location logged within the last 30 minutes (for today).
    """
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("Authentication required", frappe.AuthenticationError)

    ref_date = date or today()

    rows = frappe.db.sql('''
        SELECT
            l.user, l.sales_person, l.latitude, l.longitude,
            l.timestamp, l.distance_from_prev_km,
            u.full_name
        FROM `tabSales Person Location` l
        JOIN `tabUser` u ON u.name = l.user
        WHERE l.date = %(date)s
        ORDER BY l.user, l.timestamp ASC
    ''', {'date': ref_date}, as_dict=True)

    # Group by user
    reps = {}
    now = now_datetime()
    for r in rows:
        uid = r.user
        if uid not in reps:
            reps[uid] = {
                'user': uid,
                'full_name': r.full_name,
                'sales_person': r.sales_person,
                'trail': [],
                'total_km': 0.0,
                'active': False,
                'last_seen': None,
            }
        reps[uid]['trail'].append({
            'lat': flt(r.latitude),
            'lng': flt(r.longitude),
            'timestamp': str(r.timestamp),
            'dist_km': flt(r.distance_from_prev_km),
        })
        reps[uid]['total_km'] = round(reps[uid]['total_km'] + flt(r.distance_from_prev_km), 3)
        reps[uid]['last_seen'] = str(r.timestamp)

    # Mark active: last ping within 30 minutes (today only)
    if ref_date == today():
        for uid, rep in reps.items():
            if rep['last_seen']:
                diff_secs = (now - frappe.utils.get_datetime(rep['last_seen'])).total_seconds()
                rep['active'] = diff_secs < 1800

    return list(reps.values())


@frappe.whitelist()
def get_distance_summary(from_date=None, to_date=None):
    """
    Return per-rep per-day distance totals for the given date range.
    Used for the Team tab distance table and stipend calculation.
    """
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("Authentication required", frappe.AuthenticationError)

    ref_today = today()
    from_date = from_date or frappe.utils.add_days(ref_today, -29)
    to_date = to_date or ref_today

    rows = frappe.db.sql('''
        SELECT
            l.user,
            u.full_name,
            l.sales_person,
            l.date,
            ROUND(SUM(l.distance_from_prev_km), 3) AS total_km,
            COUNT(*) AS pings
        FROM `tabSales Person Location` l
        JOIN `tabUser` u ON u.name = l.user
        WHERE l.date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY l.user, l.date
        ORDER BY l.date DESC, total_km DESC
    ''', {'from_date': from_date, 'to_date': to_date}, as_dict=True)

    for r in rows:
        r['total_km'] = flt(r['total_km'])
        r['miles'] = round(r['total_km'] * 0.621371, 3)

    return rows
