from flask import Blueprint, request, redirect
from backend.controllers.billing_controller import *
from backend.utils.auth import login_required, is_admin

billing_bp = Blueprint('billing', __name__)

# ==================== ADMIN ROUTES ====================

@billing_bp.route('/admin/billing')
@login_required
def admin_billing_route():
    """Admin: List all bills"""
    return admin_billing()

@billing_bp.route('/admin/create-bill', methods=['GET', 'POST'])
@login_required
def create_bill_route():
    """Admin: Create bill form or process bill creation"""
    if request.method == 'POST':
        return handle_create_bill()
    return create_bill_form()

@billing_bp.route('/admin/bill-detail/<int:bill_id>')
@login_required
def bill_detail_route(bill_id):
    """Admin/Patient: View bill details"""
    return bill_detail(bill_id)

@billing_bp.route('/admin/bill-detail/<int:bill_id>/add-item', methods=['POST'])
@login_required
def add_item_route(bill_id):
    """Admin: Add item to bill"""
    return add_item(bill_id)

@billing_bp.route('/admin/bill-detail/<int:bill_id>/delete-item/<int:item_id>')
@login_required
def delete_item_route(bill_id, item_id):
    """Admin: Delete item from bill"""
    return delete_item(bill_id, item_id)

@billing_bp.route('/admin/bill-detail/<int:bill_id>/mark-paid')
@login_required
def mark_paid_route(bill_id):
    """Admin: Mark bill as paid"""
    return mark_paid(bill_id)

@billing_bp.route('/admin/bill-detail/<int:bill_id>/mark-unpaid')
@login_required
def mark_unpaid_route(bill_id):
    """Admin: Mark bill as unpaid"""
    return mark_unpaid(bill_id)

@billing_bp.route('/admin/bill-detail/<int:bill_id>/delete')
@login_required
def delete_bill_route_handler(bill_id):
    """Admin: Delete a bill"""
    return delete_bill_route(bill_id)

# ==================== PATIENT ROUTES ====================

@billing_bp.route('/my-bills')
@login_required
def my_bills_route():
    """Patient: View their own bills"""
    return my_bills()

@billing_bp.route('/bill/<int:bill_id>')
@login_required
def view_bill_route(bill_id):
    """Patient: View bill details"""
    return view_bill(bill_id)

# ==================== UNIFIED ROUTE ====================

@billing_bp.route('/bills')
@login_required
def bills_redirect():
    """Redirect to appropriate billing page based on user role"""
    if is_admin():
        return redirect('/admin/billing')
    else:
        return redirect('/my-bills')
