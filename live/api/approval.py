import frappe
from frappe.utils import flt, now_datetime
import json

APPROVAL_THRESHOLD_KES = 100000  # Orders above this require manager sign-off


def _require_auth():
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.throw('Authentication required', frappe.AuthenticationError)


def _is_manager():
    return any(r in frappe.get_roles() for r in ('System Manager', 'Sales Manager', 'Accounts Manager'))


@frappe.whitelist()
def check_needs_approval(total_amount, customer=None):
    """Return whether this order requires manager approval."""
    _require_auth()
    amount = flt(total_amount)
    if amount >= APPROVAL_THRESHOLD_KES:
        return {
            'needs_approval': True,
            'reason': f'Order total KES {amount:,.0f} exceeds the approval threshold of KES {APPROVAL_THRESHOLD_KES:,.0f}',
        }
    return {'needs_approval': False, 'reason': None}


@frappe.whitelist()
def submit_for_approval(order_data, total_amount, customer=None, reason=None):
    """Create a Sales Order Approval record and return its name."""
    _require_auth()
    user = frappe.session.user

    if isinstance(order_data, str):
        order_data_parsed = json.loads(order_data)
    else:
        order_data_parsed = order_data

    customer_name = customer or order_data_parsed.get('customer', '')

    doc = frappe.new_doc('Sales Order Approval')
    doc.sales_rep = user
    doc.customer = customer_name
    doc.total_amount = flt(total_amount)
    doc.status = 'Pending'
    doc.reason = reason or ''
    doc.order_data = json.dumps(order_data_parsed, default=str)
    doc.submitted_at = now_datetime()
    doc.flags.ignore_permissions = True
    doc.insert()
    frappe.db.commit()

    # Notify managers (send system notification)
    managers = frappe.db.sql('''
        SELECT u.name FROM `tabUser` u
        JOIN `tabHas Role` r ON r.parent = u.name
        WHERE r.role IN ('Sales Manager', 'System Manager')
          AND u.enabled = 1
    ''', as_dict=True)
    for mgr in managers:
        frappe.publish_realtime(
            'live_approval_request',
            {'approval': doc.name, 'customer': customer_name, 'amount': flt(total_amount), 'rep': user},
            user=mgr.name,
        )

    return {'approval': doc.name, 'status': 'Pending'}


@frappe.whitelist()
def get_pending_approvals():
    """Return all pending approval requests. Managers see all; reps see their own."""
    _require_auth()
    user = frappe.session.user
    is_mgr = _is_manager()

    filters = {}
    if not is_mgr:
        filters['sales_rep'] = user

    rows = frappe.get_all(
        'Sales Order Approval',
        filters=filters,
        fields=['name', 'sales_rep', 'customer', 'total_amount', 'status',
                'submitted_at', 'reason', 'approved_by', 'approved_at',
                'rejection_reason', 'sales_order'],
        order_by='submitted_at desc',
        limit=100,
    )

    for r in rows:
        r['sales_rep_name'] = frappe.db.get_value('User', r.sales_rep, 'full_name') or r.sales_rep
        r['customer_name'] = frappe.db.get_value('Customer', r.customer, 'customer_name') or r.customer
        r['total_amount'] = flt(r.total_amount)
        r['order_items'] = []
        try:
            raw = frappe.db.get_value('Sales Order Approval', r.name, 'order_data') or '{}'
            d = json.loads(raw)
            r['order_items'] = d.get('items', [])
        except Exception:
            pass

    return {'rows': rows, 'is_manager': is_mgr}


@frappe.whitelist()
def process_approval(approval_name, approved, rejection_reason=None):
    """Approve or reject a Sales Order Approval. Creates the Sales Order on approval."""
    _require_auth()
    if not _is_manager():
        frappe.throw('Only managers can approve orders', frappe.PermissionError)

    doc = frappe.get_doc('Sales Order Approval', approval_name)
    if doc.status != 'Pending':
        frappe.throw(f'This request is already {doc.status}')

    approved = frappe.utils.cint(approved)
    doc.approved_by = frappe.session.user
    doc.approved_at = now_datetime()

    if approved:
        doc.status = 'Approved'
        # Create the actual Sales Order
        order_data = json.loads(doc.order_data or '{}')
        headers = {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': frappe.generate_hash(length=16),
        }
        # Use Frappe doc API directly
        so = frappe.new_doc('Sales Order')
        so.customer = order_data.get('customer', doc.customer)
        so.delivery_date = order_data.get('delivery_date')
        so.currency = order_data.get('currency', 'KES')
        if order_data.get('selling_price_list'):
            so.selling_price_list = order_data['selling_price_list']
        if order_data.get('taxes_and_charges'):
            so.taxes_and_charges = order_data['taxes_and_charges']

        for item in order_data.get('items', []):
            so.append('items', {
                'item_code': item.get('item_code'),
                'qty': flt(item.get('qty', 1)),
                'rate': flt(item.get('rate', 0)),
                'warehouse': item.get('warehouse', 'FG Stores'),
            })

        so.flags.ignore_permissions = True
        so.insert()
        so.submit()
        frappe.db.commit()
        doc.sales_order = so.name
    else:
        doc.status = 'Rejected'
        doc.rejection_reason = rejection_reason or ''

    doc.flags.ignore_permissions = True
    doc.save()
    frappe.db.commit()

    # Notify the sales rep
    frappe.publish_realtime(
        'live_approval_result',
        {
            'approval': doc.name,
            'status': doc.status,
            'sales_order': doc.sales_order,
            'rejection_reason': doc.rejection_reason,
        },
        user=doc.sales_rep,
    )

    return {
        'status': doc.status,
        'sales_order': doc.sales_order,
    }


@frappe.whitelist()
def get_my_approval_status(approval_name):
    _require_auth()
    doc = frappe.get_doc('Sales Order Approval', approval_name)
    if doc.sales_rep != frappe.session.user and not _is_manager():
        frappe.throw('Permission denied', frappe.PermissionError)
    return {
        'status': doc.status,
        'sales_order': doc.sales_order,
        'rejection_reason': doc.rejection_reason,
    }
