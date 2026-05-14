import frappe


def _is_system_manager():
	return "System Manager" in frappe.get_roles()


def _parse_item_groups(raw):
	"""Parse the stored JSON list, return [] on any error."""
	if not raw:
		return []
	try:
		import json
		val = json.loads(raw)
		return val if isinstance(val, list) else []
	except Exception:
		return []


@frappe.whitelist()
def get_app_settings():
	"""Public — readable by all logged-in users (Sales User, Sales Manager, System Manager)."""
	is_admin = _is_system_manager()
	current_user = frappe.session.user
	try:
		doc = frappe.get_single("Live App Settings")
		return {
			"default_price_list": doc.default_price_list or "",
			"default_taxes_and_charges": doc.default_taxes_and_charges or "",
			"default_warehouse": doc.default_warehouse or "Finished Goods - CAL",
			"approval_threshold": doc.approval_threshold or 100000,
			"app_title": doc.app_title or "Live Sales",
			"welcome_message": doc.welcome_message or "",
			"allowed_item_groups": _parse_item_groups(doc.allowed_item_groups),
			"is_admin": is_admin,
			"current_user": current_user,
		}
	except Exception:
		return {
			"default_price_list": "",
			"default_taxes_and_charges": "",
			"default_warehouse": "Finished Goods - CAL",
			"approval_threshold": 100000,
			"app_title": "Live Sales",
			"welcome_message": "",
			"allowed_item_groups": [],
			"is_admin": is_admin,
			"current_user": current_user,
		}


@frappe.whitelist()
def save_app_settings(
	default_price_list="",
	default_taxes_and_charges="",
	default_warehouse="",
	approval_threshold=100000,
	app_title="Live Sales",
	welcome_message="",
	allowed_item_groups=None,
):
	"""System Manager only."""
	import json
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Only System Managers can update app settings.", frappe.PermissionError)

	doc = frappe.get_single("Live App Settings")
	doc.default_price_list = default_price_list
	doc.default_taxes_and_charges = default_taxes_and_charges
	doc.default_warehouse = default_warehouse or "Finished Goods - CAL"
	doc.approval_threshold = frappe.utils.flt(approval_threshold) or 100000
	doc.app_title = app_title or "Live Sales"
	doc.welcome_message = welcome_message
	if allowed_item_groups is not None:
		if isinstance(allowed_item_groups, str):
			try:
				allowed_item_groups = json.loads(allowed_item_groups)
			except Exception:
				allowed_item_groups = []
		doc.allowed_item_groups = json.dumps(allowed_item_groups if isinstance(allowed_item_groups, list) else [])
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
def get_all_item_groups():
	"""Return non-group item groups for the allowed_item_groups picker."""
	return frappe.get_all(
		"Item Group",
		filters={"is_group": 0},
		fields=["name"],
		order_by="name asc",
	)


@frappe.whitelist()
def get_all_tax_templates():
	"""Return active Sales Taxes and Charges Templates."""
	return frappe.get_all(
		"Sales Taxes and Charges Template",
		filters={"disabled": 0},
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
