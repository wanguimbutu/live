import frappe
from frappe import _
from frappe.utils import now_datetime, time_diff_in_seconds
from live.api.location import log_location_trail


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

    # Also append to the location trail for distance tracking
    if latitude is not None and longitude is not None:
        try:
            log_location_trail(user, latitude, longitude, accuracy)
        except Exception:
            pass  # never block presence update if trail logging fails

    frappe.db.commit()

    return {
        "user": user,
        "last_seen": str(doc.last_seen),
        "battery_level": doc.battery_level,
        "latitude": doc.latitude,
        "longitude": doc.longitude,
    }


@frappe.whitelist()
def get_all_presence():
    """Return presence data for all users. For the admin control panel."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required"), frappe.AuthenticationError)

    records = frappe.get_all(
        "User Presence",
        fields=["user", "last_seen", "is_active", "latitude", "longitude",
                "accuracy", "battery_level", "is_charging"],
        order_by="last_seen desc",
    )

    now = now_datetime()
    enriched = []
    for r in records:
        # Mark inactive if not seen in 10 minutes
        if r.last_seen:
            secs = time_diff_in_seconds(now, r.last_seen)
            r["online"] = secs < 600
        else:
            r["online"] = False

        # Fetch display name
        r["full_name"] = frappe.db.get_value("User", r.user, "full_name") or r.user

        enriched.append(r)

    # Also fetch recent checkins
    checkins = frappe.get_all(
        "Employee Checkin",
        fields=["employee", "employee_name", "log_type", "time", "latitude", "longitude"],
        order_by="time desc",
        limit=50,
    )

    return {"presence": enriched, "checkins": checkins}
