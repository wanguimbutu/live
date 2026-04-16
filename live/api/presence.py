import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist()
def update_presence(latitude=None, longitude=None, accuracy=None, battery_level=None, is_charging=0):
    """
    Upsert a User Presence record for the currently logged-in user.
    Called by the frontend every ~2 minutes or on battery change.
    """
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Authentication required"), frappe.AuthenticationError)

    existing = frappe.db.get_value("User Presence", {"user": user}, "name")

    if existing:
        doc = frappe.get_doc("User Presence", existing)
    else:
        doc = frappe.new_doc("User Presence")
        doc.user = user

    if latitude is not None:
        doc.latitude = float(latitude)
    if longitude is not None:
        doc.longitude = float(longitude)
    if accuracy is not None:
        doc.accuracy = float(accuracy)
    if battery_level is not None:
        doc.battery_level = int(float(battery_level))

    doc.is_charging = frappe.utils.cint(is_charging)
    doc.is_active = 1
    doc.last_seen = now_datetime()

    doc.flags.ignore_permissions = True
    doc.save()
    frappe.db.commit()

    return {
        "user": user,
        "last_seen": str(doc.last_seen),
        "battery_level": doc.battery_level,
        "latitude": doc.latitude,
        "longitude": doc.longitude,
    }
