import frappe
from frappe.utils import flt
import json


@frappe.whitelist()
def get_stock(item_codes, warehouse=None):
    """
    Return actual_qty for each item_code.
    item_codes: JSON-encoded list of item codes, or a single code string.
    """
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.throw('Authentication required', frappe.AuthenticationError)

    if isinstance(item_codes, str):
        try:
            codes = json.loads(item_codes)
        except Exception:
            codes = [item_codes]
    else:
        codes = list(item_codes)

    if not codes:
        return {}

    params = {'codes': codes}
    wh_clause = ''
    if warehouse:
        wh_clause = 'AND warehouse = %(warehouse)s'
        params['warehouse'] = warehouse

    rows = frappe.db.sql(f'''
        SELECT item_code, warehouse, actual_qty, reserved_qty, projected_qty
        FROM `tabBin`
        WHERE item_code IN %(codes)s
          {wh_clause}
        ORDER BY actual_qty DESC
    ''', params, as_dict=True)

    result = {}
    for r in rows:
        code = r.item_code
        if code not in result:
            result[code] = {
                'item_code': code,
                'actual_qty': 0,
                'reserved_qty': 0,
                'projected_qty': 0,
                'by_warehouse': [],
            }
        result[code]['actual_qty'] += flt(r.actual_qty)
        result[code]['reserved_qty'] += flt(r.reserved_qty)
        result[code]['projected_qty'] += flt(r.projected_qty)
        result[code]['by_warehouse'].append({
            'warehouse': r.warehouse,
            'actual_qty': flt(r.actual_qty),
        })

    # Fill in items with no bin record
    for code in codes:
        if code not in result:
            result[code] = {
                'item_code': code,
                'actual_qty': 0,
                'reserved_qty': 0,
                'projected_qty': 0,
                'by_warehouse': [],
            }

    return result


@frappe.whitelist()
def get_catalog(search=None, warehouse=None, page=0, page_size=50):
    """
    Return items with stock levels for the product catalog.
    """
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.throw('Authentication required', frappe.AuthenticationError)

    page = int(page or 0)
    page_size = int(page_size or 50)
    search_clause = ''
    params = {'limit': page_size, 'offset': page * page_size}

    if search:
        search_clause = 'AND (item.name LIKE %(search)s OR item.item_name LIKE %(search)s)'
        params['search'] = f'%{search}%'

    items = frappe.db.sql(f'''
        SELECT
            item.name as item_code,
            item.item_name,
            item.item_group,
            item.description,
            item.standard_rate,
            item.stock_uom,
            COALESCE(SUM(bin.actual_qty), 0) as actual_qty,
            COALESCE(SUM(bin.reserved_qty), 0) as reserved_qty
        FROM `tabItem` item
        LEFT JOIN `tabBin` bin ON bin.item_code = item.name
        WHERE item.disabled = 0 AND item.is_sales_item = 1
          {search_clause}
        GROUP BY item.name
        ORDER BY item.item_name ASC
        LIMIT %(limit)s OFFSET %(offset)s
    ''', params, as_dict=True)

    for i in items:
        i['actual_qty'] = flt(i['actual_qty'])
        i['reserved_qty'] = flt(i['reserved_qty'])
        i['standard_rate'] = flt(i['standard_rate'])
        i['available_qty'] = max(0, i['actual_qty'] - i['reserved_qty'])

        if i['available_qty'] <= 0:
            i['stock_status'] = 'out'
        elif i['available_qty'] <= 10:
            i['stock_status'] = 'low'
        else:
            i['stock_status'] = 'in'

    total = frappe.db.sql(f'''
        SELECT COUNT(*) as cnt FROM `tabItem`
        WHERE disabled = 0 AND is_sales_item = 1
        {search_clause}
    ''', params, as_dict=True)[0].cnt

    return {'items': items, 'total': int(total), 'page': page, 'page_size': page_size}
