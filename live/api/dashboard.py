import frappe
from frappe.utils import today, add_days, flt, getdate, now_datetime
import json
from datetime import datetime, timedelta


def _is_manager():
    return any(r in frappe.get_roles() for r in ('System Manager', 'Sales Manager', 'Accounts Manager'))


def _require_auth():
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.throw('Authentication required', frappe.AuthenticationError)


def _user_filter(alias='so'):
    user = frappe.session.user
    if _is_manager():
        return '', {}
    return f'AND {alias}.owner = %(user)s', {'user': user}


@frappe.whitelist()
def get_kpis(from_date=None, to_date=None, sales_person=None):
    _require_auth()
    user = frappe.session.user
    ref_today = today()
    from_date = from_date or add_days(ref_today, -29)
    to_date = to_date or ref_today
    is_mgr = _is_manager()

    owner_clause = ''
    params = {'from_date': from_date, 'to_date': to_date, 'today': ref_today}

    if not is_mgr:
        owner_clause = 'AND owner = %(owner)s'
        params['owner'] = user
    elif sales_person:
        owner_clause = 'AND owner = %(owner)s'
        params['owner'] = sales_person

    # Orders for the selected period
    orders = frappe.db.sql(f'''
        SELECT grand_total, transaction_date
        FROM `tabSales Order`
        WHERE docstatus != 2
          AND transaction_date BETWEEN %(from_date)s AND %(to_date)s
          {owner_clause}
    ''', params, as_dict=True)

    total_orders = len(orders)
    total_revenue = sum(flt(o.grand_total) for o in orders)
    avg_order = round(total_revenue / total_orders, 2) if total_orders else 0

    today_orders = [o for o in orders if str(o.transaction_date) == ref_today]

    # This week (Monday to today)
    week_start = str(getdate(ref_today) - timedelta(days=getdate(ref_today).weekday()))
    week_orders = [o for o in orders if str(o.transaction_date) >= week_start]

    # Visits
    visit_clause = ''
    if not is_mgr:
        visit_clause = 'AND user = %(owner)s'
    elif sales_person:
        visit_clause = 'AND user = %(owner)s'

    visits = frappe.db.sql(f'''
        SELECT name, sales_order, end_time
        FROM `tabCustomer Visits`
        WHERE start_time >= %(from_date)s AND start_time <= %(to_date_end)s
          {visit_clause}
    ''', {**params, 'to_date_end': f'{to_date} 23:59:59'}, as_dict=True)

    total_visits = len(visits)
    completed_visits = sum(1 for v in visits if v.end_time)
    visits_with_order = sum(1 for v in visits if v.sales_order)

    # Outstanding
    outstanding = flt(frappe.db.sql('''
        SELECT COALESCE(SUM(outstanding_amount), 0) as total
        FROM `tabSales Invoice`
        WHERE outstanding_amount > 0 AND docstatus = 1
    ''', as_dict=True)[0].total)

    # Attendance this week (working days with at least one IN check-in)
    checkins = frappe.db.sql(f'''
        SELECT DATE(time) as day
        FROM `tabEmployee Checkin`
        WHERE log_type = "IN"
          AND DATE(time) >= %(week_start)s AND DATE(time) <= %(today)s
          {"" if is_mgr else "AND employee IN (SELECT name FROM `tabEmployee` WHERE user_id = %(owner)s)"}
        GROUP BY DATE(time)
    ''', {**params, 'week_start': week_start}, as_dict=True)

    working_days_so_far = len(set(str(getdate(ref_today) - timedelta(days=i)).ljust(10) for i in range(7) if (getdate(ref_today) - timedelta(days=i)).weekday() < 5 and str(getdate(ref_today) - timedelta(days=i)) >= week_start))
    attendance_rate = round(len(checkins) / max(working_days_so_far, 1) * 100, 1)

    return {
        'today_orders': len(today_orders),
        'today_revenue': sum(flt(o.grand_total) for o in today_orders),
        'week_orders': len(week_orders),
        'week_revenue': sum(flt(o.grand_total) for o in week_orders),
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order,
        'total_visits': total_visits,
        'completed_visits': completed_visits,
        'visits_with_order': visits_with_order,
        'visit_conversion': round(visits_with_order / total_visits * 100, 1) if total_visits else 0,
        'outstanding': outstanding,
        'attendance_rate': attendance_rate,
        'is_manager': is_mgr,
        'from_date': from_date,
        'to_date': to_date,
    }


@frappe.whitelist()
def get_trend(from_date=None, to_date=None, sales_person=None):
    _require_auth()
    user = frappe.session.user
    ref_today = today()
    from_date = from_date or add_days(ref_today, -29)
    to_date = to_date or ref_today
    is_mgr = _is_manager()

    owner_clause = ''
    params = {'from_date': from_date, 'to_date': to_date}

    if not is_mgr:
        owner_clause = 'AND owner = %(owner)s'
        params['owner'] = user
    elif sales_person:
        owner_clause = 'AND owner = %(owner)s'
        params['owner'] = sales_person

    rows = frappe.db.sql(f'''
        SELECT
            DATE(transaction_date) as date,
            COUNT(*) as order_count,
            COALESCE(SUM(grand_total), 0) as revenue
        FROM `tabSales Order`
        WHERE docstatus != 2
          AND transaction_date BETWEEN %(from_date)s AND %(to_date)s
          {owner_clause}
        GROUP BY DATE(transaction_date)
        ORDER BY date ASC
    ''', params, as_dict=True)

    # Fill in missing dates with zeros
    result = []
    current = getdate(from_date)
    end = getdate(to_date)
    row_map = {str(r.date): r for r in rows}

    while current <= end:
        ds = str(current)
        if ds in row_map:
            r = row_map[ds]
            result.append({'date': ds, 'orders': int(r.order_count), 'revenue': flt(r.revenue)})
        else:
            result.append({'date': ds, 'orders': 0, 'revenue': 0})
        current += timedelta(days=1)

    return result


@frappe.whitelist()
def get_leaderboard(from_date=None, to_date=None):
    _require_auth()
    ref_today = today()
    from_date = from_date or add_days(ref_today, -29)
    to_date = to_date or ref_today

    rows = frappe.db.sql('''
        SELECT
            owner,
            COUNT(*) as order_count,
            COALESCE(SUM(grand_total), 0) as revenue
        FROM `tabSales Order`
        WHERE docstatus != 2
          AND transaction_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY owner
        ORDER BY revenue DESC
        LIMIT 10
    ''', {'from_date': from_date, 'to_date': to_date}, as_dict=True)

    result = []
    for r in rows:
        full_name = frappe.db.get_value('User', r.owner, 'full_name') or r.owner
        result.append({
            'user': r.owner,
            'name': full_name,
            'order_count': int(r.order_count),
            'revenue': flt(r.revenue),
        })
    return result


@frappe.whitelist()
def get_outstanding_aging():
    _require_auth()
    rows = frappe.db.sql('''
        SELECT
            CASE
                WHEN DATEDIFF(CURDATE(), posting_date) BETWEEN 0 AND 30 THEN "0-30 days"
                WHEN DATEDIFF(CURDATE(), posting_date) BETWEEN 31 AND 60 THEN "31-60 days"
                WHEN DATEDIFF(CURDATE(), posting_date) BETWEEN 61 AND 90 THEN "61-90 days"
                ELSE "90+ days"
            END as bucket,
            COUNT(*) as invoice_count,
            COALESCE(SUM(outstanding_amount), 0) as amount
        FROM `tabSales Invoice`
        WHERE outstanding_amount > 0 AND docstatus = 1
        GROUP BY bucket
        ORDER BY MIN(DATEDIFF(CURDATE(), posting_date)) ASC
    ''', as_dict=True)

    order = ['0-30 days', '31-60 days', '61-90 days', '90+ days']
    row_map = {r.bucket: r for r in rows}
    return [
        {
            'bucket': b,
            'amount': flt(row_map[b].amount) if b in row_map else 0,
            'count': int(row_map[b].invoice_count) if b in row_map else 0,
        }
        for b in order
    ]


@frappe.whitelist()
def get_alerts():
    _require_auth()
    ref_today = today()
    three_days_ago = add_days(ref_today, -3)
    alerts = []

    # Sales reps with no orders in 3 days
    active_users = frappe.db.sql('''
        SELECT DISTINCT owner FROM `tabSales Order`
        WHERE transaction_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
          AND docstatus != 2
    ''', as_dict=True)
    active_owners = {r.owner for r in active_users}

    recent_users = frappe.db.sql('''
        SELECT DISTINCT owner FROM `tabSales Order`
        WHERE transaction_date >= %(since)s AND docstatus != 2
    ''', {'since': three_days_ago}, as_dict=True)
    recent_owners = {r.owner for r in recent_users}

    inactive = active_owners - recent_owners
    for u in inactive:
        full_name = frappe.db.get_value('User', u, 'full_name') or u
        alerts.append({
            'type': 'low_activity',
            'severity': 'warning',
            'message': f'{full_name} has no orders in the last 3 days',
            'user': u,
        })

    # Customers with high outstanding (> 500k KES)
    high_outstanding = frappe.db.sql('''
        SELECT customer, customer_name, SUM(outstanding_amount) as total
        FROM `tabSales Invoice`
        WHERE outstanding_amount > 0 AND docstatus = 1
        GROUP BY customer
        HAVING total > 500000
        ORDER BY total DESC
        LIMIT 10
    ''', as_dict=True)

    for c in high_outstanding:
        alerts.append({
            'type': 'high_outstanding',
            'severity': 'danger',
            'message': f'{c.customer_name} has KES {flt(c.total):,.0f} outstanding',
            'customer': c.customer,
        })

    # Pending approvals
    pending_count = frappe.db.count('Sales Order Approval', {'status': 'Pending'})
    if pending_count:
        alerts.append({
            'type': 'pending_approvals',
            'severity': 'info',
            'message': f'{pending_count} order{"s" if pending_count > 1 else ""} awaiting approval',
        })

    return alerts


@frappe.whitelist()
def get_team_members():
    _require_auth()
    if not _is_manager():
        return []
    rows = frappe.db.sql('''
        SELECT DISTINCT owner as user, u.full_name as name
        FROM `tabSales Order` so
        JOIN `tabUser` u ON u.name = so.owner
        WHERE so.docstatus != 2
          AND so.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
        ORDER BY u.full_name
    ''', as_dict=True)
    return rows


@frappe.whitelist()
def get_visit_map(from_date=None, to_date=None):
    _require_auth()
    ref_today = today()
    from_date = from_date or add_days(ref_today, -6)
    to_date = to_date or ref_today
    user = frappe.session.user
    is_mgr = _is_manager()

    owner_clause = '' if is_mgr else 'AND user = %(user)s'
    rows = frappe.db.sql(f'''
        SELECT
            customer, latitude, longitude, user,
            start_time, end_time, duration_minutes, sales_order
        FROM `tabCustomer Visits`
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
          AND start_time >= %(from)s AND start_time <= %(to)s
          {owner_clause}
        LIMIT 500
    ''', {'from': f'{from_date} 00:00:00', 'to': f'{to_date} 23:59:59', 'user': user}, as_dict=True)

    for r in rows:
        r['customer_name'] = frappe.db.get_value('Customer', r.customer, 'customer_name') or r.customer
        r['user_name'] = frappe.db.get_value('User', r.user, 'full_name') or r.user
        r['latitude'] = flt(r.latitude)
        r['longitude'] = flt(r.longitude)

    return rows
