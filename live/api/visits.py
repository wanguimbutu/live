import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime, today


@frappe.whitelist()
def start_visit(customer, latitude=None, longitude=None, accuracy=None):
    """Create a new Customer Visit record and return its name."""
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Authentication required"), frappe.AuthenticationError)

    doc = frappe.new_doc("Customer Visits")
    doc.customer = customer
    doc.user = user
    doc.start_time = now_datetime()
    if latitude is not None:
        doc.latitude = float(latitude)
    if longitude is not None:
        doc.longitude = float(longitude)

    doc.flags.ignore_permissions = True
    doc.insert()
    frappe.db.commit()

    # Also record the first trail point
    if latitude is not None and longitude is not None:
        _add_trail_point(user, latitude, longitude, accuracy)

    return {"name": doc.name, "start_time": str(doc.start_time)}


@frappe.whitelist()
def end_visit(visit_name, notes=None, sales_order=None, latitude=None, longitude=None, accuracy=None):
    """End a visit — set end_time, duration, optional notes/order."""
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Authentication required"), frappe.AuthenticationError)

    doc = frappe.get_doc("Customer Visits", visit_name)
    doc.end_time = now_datetime()

    if doc.start_time:
        delta = (get_datetime(doc.end_time) - get_datetime(doc.start_time)).total_seconds()
        doc.duration_minutes = max(0, int(delta / 60))

    if notes:
        doc.notes = notes
    if sales_order:
        doc.sales_order = sales_order
    if latitude is not None:
        doc.latitude = float(latitude)
    if longitude is not None:
        doc.longitude = float(longitude)

    doc.flags.ignore_permissions = True
    doc.save()
    frappe.db.commit()

    if latitude is not None and longitude is not None:
        _add_trail_point(user, latitude, longitude, accuracy)

    return {
        "name": doc.name,
        "duration_minutes": doc.duration_minutes,
        "end_time": str(doc.end_time),
    }


@frappe.whitelist()
def add_trail_point(latitude, longitude, accuracy=None):
    """Record a GPS breadcrumb for the current user."""
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Authentication required"), frappe.AuthenticationError)
    _add_trail_point(user, latitude, longitude, accuracy)
    return "ok"


def _add_trail_point(user, latitude, longitude, accuracy=None):
    doc = frappe.new_doc("Visit Trail Point")
    doc.user = user
    doc.timestamp = now_datetime()
    doc.latitude = float(latitude)
    doc.longitude = float(longitude)
    if accuracy is not None:
        doc.accuracy = float(accuracy)
    doc.flags.ignore_permissions = True
    doc.insert()
    frappe.db.commit()


@frappe.whitelist()
def get_my_visits(date=None):
    """Return today's visits and trail for the current user."""
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Authentication required"), frappe.AuthenticationError)

    target_date = date or today()

    visits = frappe.get_all(
        "Customer Visits",
        filters={"user": user, "start_time": [">=", f"{target_date} 00:00:00"]},
        fields=["name", "customer", "start_time", "end_time", "duration_minutes",
                "latitude", "longitude", "notes", "sales_order"],
        order_by="start_time asc",
    )

    # Enrich with customer name
    for v in visits:
        v["customer_name"] = frappe.db.get_value("Customer", v.customer, "customer_name") or v.customer

    trail = frappe.get_all(
        "Visit Trail Point",
        filters={"user": user, "timestamp": [">=", f"{target_date} 00:00:00"]},
        fields=["latitude", "longitude", "timestamp"],
        order_by="timestamp asc",
        limit=500,
    )

    return {"visits": visits, "trail": trail}


@frappe.whitelist()
def get_all_trails(date=None):
    """Return all users' visits and trails for the admin map."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required"), frappe.AuthenticationError)

    target_date = date or today()

    visits = frappe.get_all(
        "Customer Visits",
        filters={"start_time": [">=", f"{target_date} 00:00:00"]},
        fields=["name", "customer", "user", "start_time", "end_time",
                "duration_minutes", "latitude", "longitude", "notes", "sales_order"],
        order_by="start_time asc",
        limit=200,
    )
    for v in visits:
        v["customer_name"] = frappe.db.get_value("Customer", v.customer, "customer_name") or v.customer
        v["user_name"] = frappe.db.get_value("User", v.user, "full_name") or v.user

    trail = frappe.get_all(
        "Visit Trail Point",
        filters={"timestamp": [">=", f"{target_date} 00:00:00"]},
        fields=["user", "latitude", "longitude", "timestamp"],
        order_by="timestamp asc",
        limit=2000,
    )

    return {"visits": visits, "trail": trail}
