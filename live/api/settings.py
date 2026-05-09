import frappe


def _is_system_manager():
	return "System Manager" in frappe.get_roles()


@frappe.whitelist()
def get_app_settings():
	"""Public — readable by all logged-in users (Sales User, Sales Manager, System Manager)."""
	try:
		doc = frappe.get_single("Live App Settings")
		return {
			"default_price_list": doc.default_price_list or "",
			"default_warehouse": doc.default_warehouse or "Finished Goods - CAL",
			"approval_threshold": doc.approval_threshold or 100000,
			"app_title": doc.app_title or "Live Sales",
			"welcome_message": doc.welcome_message or "",
			"is_admin": _is_system_manager(),
		}
	except Exception:
		return {
			"default_price_list": "",
			"default_warehouse": "Finished Goods - CAL",
			"approval_threshold": 100000,
			"app_title": "Live Sales",
			"welcome_message": "",
			"is_admin": _is_system_manager(),
		}


@frappe.whitelist()
def save_app_settings(
	default_price_list="",
	default_warehouse="",
	approval_threshold=100000,
	app_title="Live Sales",
	welcome_message="",
):
	"""System Manager only."""
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Only System Managers can update app settings.", frappe.PermissionError)

	doc = frappe.get_single("Live App Settings")
	doc.default_price_list = default_price_list
	doc.default_warehouse = default_warehouse or "Finished Goods - CAL"
	doc.approval_threshold = frappe.utils.flt(approval_threshold) or 100000
	doc.app_title = app_title or "Live Sales"
	doc.welcome_message = welcome_message
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"success": True}


@frappe.whitelist()
def get_all_price_lists():
	"""Return active selling price lists."""
	return frappe.get_all(
		"Price List",
		filters={"enabled": 1, "selling": 1},
		fields=["name"],
		order_by="name asc",
	)


@frappe.whitelist()
def get_all_warehouses():
	"""Return warehouses that are not group warehouses."""
	return frappe.get_all(
		"Warehouse",
		filters={"is_group": 0, "disabled": 0},
		fields=["name", "warehouse_name"],
		order_by="name asc",
	)
