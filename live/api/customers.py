import frappe
from frappe.utils import flt


def _is_manager():
    return any(r in frappe.get_roles() for r in ("System Manager", "Sales Manager"))


def _get_sales_person(user):
    return frappe.db.get_value("Sales Person", {"custom_user_id": user}, "name")


def _my_customer_names(user):
    """Return a list of customer names assigned to the current user's Sales Person."""
    sp = _get_sales_person(user)
    if not sp:
        return None  # signals "no sales person found — fall back to owner filter"

    rows = frappe.db.sql('''
        SELECT DISTINCT parent FROM `tabSales Team`
        WHERE parenttype = 'Customer' AND sales_person = %(sp)s
    ''', {'sp': sp}, as_dict=True)

    return [r.parent for r in rows]


@frappe.whitelist()
def get_my_customers(search='', limit_start=0, limit_page_length=20):
    """
    Return customers scoped to the current user:
    - Managers/admins → all customers
    - Sales reps → only customers in their Sales Team (via custom_user_id → Sales Person)
    """
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("Authentication required", frappe.AuthenticationError)

    limit_start = int(limit_start or 0)
    limit_page_length = int(limit_page_length or 20)
    user = frappe.session.user

    base_filters = []
    if search:
        base_filters.append(["customer_name", "like", f"%{search}%"])

    if _is_manager():
        return frappe.get_all(
            "Customer",
            filters=base_filters,
            fields=["name", "customer_name"],
            order_by="customer_name asc",
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )

    customer_names = _my_customer_names(user)

    if customer_names is None:
        # No Sales Person linked — fall back to owner filter
        base_filters.append(["owner", "=", user])
        return frappe.get_all(
            "Customer",
            filters=base_filters,
            fields=["name", "customer_name"],
            order_by="customer_name asc",
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )

    if not customer_names:
        return []

    # Filter by the specific customer list
    name_filter = ["name", "in", customer_names]
    all_filters = [name_filter] + base_filters
    return frappe.get_all(
        "Customer",
        filters=all_filters,
        fields=["name", "customer_name"],
        order_by="customer_name asc",
        limit_start=limit_start,
        limit_page_length=limit_page_length,
    )


@frappe.whitelist()
def get_my_outstanding():
    """
    Return outstanding invoices scoped to the current user's customers.
    Managers → all; Sales reps → only their assigned customers.
    """
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("Authentication required", frappe.AuthenticationError)

    user = frappe.session.user

    if _is_manager():
        rows = frappe.db.sql('''
            SELECT name, customer, customer_name, posting_date, due_date,
                   grand_total, outstanding_amount
            FROM `tabSales Invoice`
            WHERE outstanding_amount > 0 AND docstatus = 1
            ORDER BY outstanding_amount DESC
            LIMIT 500
        ''', as_dict=True)
        return _format_invoices(rows)

    customer_names = _my_customer_names(user)

    if customer_names is None:
        # Fall back to owner filter via customer
        rows = frappe.db.sql('''
            SELECT si.name, si.customer, si.customer_name, si.posting_date,
                   si.due_date, si.grand_total, si.outstanding_amount
            FROM `tabSales Invoice` si
            JOIN `tabCustomer` c ON c.name = si.customer
            WHERE si.outstanding_amount > 0 AND si.docstatus = 1
              AND c.owner = %(user)s
            ORDER BY si.outstanding_amount DESC
            LIMIT 500
        ''', {'user': user}, as_dict=True)
        return _format_invoices(rows)

    if not customer_names:
        return []

    rows = frappe.db.sql('''
        SELECT name, customer, customer_name, posting_date, due_date,
               grand_total, outstanding_amount
        FROM `tabSales Invoice`
        WHERE outstanding_amount > 0 AND docstatus = 1
          AND customer IN %(customers)s
        ORDER BY outstanding_amount DESC
        LIMIT 500
    ''', {'customers': customer_names}, as_dict=True)
    return _format_invoices(rows)


def _format_invoices(rows):
    for r in rows:
        r['outstanding_amount'] = flt(r['outstanding_amount'])
        r['grand_total'] = flt(r['grand_total'])
    return rows
