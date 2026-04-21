from flask import request, redirect, render_template, session, flash
from backend.models.billing_model import *
from backend.models.patient_model import get_all_patients, get_patient_by_user_id
from backend.utils.auth import is_admin, get_current_user_id
from datetime import datetime

# ==================== ADMIN FEATURES ====================

def admin_billing():
    """Admin: List all bills"""
    if not is_admin():
        return redirect('/dashboard')
    
    bills = get_all_bills()
    stats = get_billing_dashboard_stats()
    return render_template('admin_billing.html', bills=bills, stats=stats)

def create_bill_form():
    """Admin: Show create bill form"""
    if not is_admin():
        return redirect('/dashboard')
    
    patients = get_all_patients()
    return render_template('create_bill.html', patients=patients)

def handle_create_bill():
    """Admin: Create a new bill"""
    if not is_admin():
        return redirect('/dashboard')
    
    patient_id = request.form.get('patient_id')
    
    if not patient_id:
        flash('Please select a patient.', 'danger')
        return redirect('/admin/create-bill')
    
    # Initialize billing tables
    init_billing_tables()
    
    bill_id = create_bill(patient_id)
    flash(f'Bill created successfully! Bill ID: {bill_id}', 'success')
    return redirect(f'/admin/bill-detail/{bill_id}')

def bill_detail(bill_id):
    """Admin/Patient: View bill details"""
    bill = get_bill_by_id(bill_id)
    
    if not bill:
        flash('Bill not found.', 'danger')
        return redirect('/dashboard')
    
    # Check access permissions
    if not is_admin():
        # Patient can only view their own bills
        user_id = get_current_user_id()
        patient = get_patient_by_user_id(user_id)
        if not patient or patient[0] != bill[1]:  # bill[1] is patient_id
            flash('You do not have permission to view this bill.', 'danger')
            return redirect('/dashboard')
    
    items = get_bill_items(bill_id)
    return render_template('bill_detail.html', bill=bill, items=items, is_admin=is_admin())

def add_item(bill_id):
    """Admin: Add item to bill"""
    if not is_admin():
        return redirect('/dashboard')
    
    if request.method == 'POST':
        description = request.form.get('description')
        try:
            amount = float(request.form.get('amount', 0))
        except ValueError:
            flash('Invalid amount.', 'danger')
            return redirect(f'/admin/bill-detail/{bill_id}')
        
        if not description or amount <= 0:
            flash('Please provide description and valid amount.', 'danger')
            return redirect(f'/admin/bill-detail/{bill_id}')
        
        add_bill_item(bill_id, description, amount)
        flash('Item added successfully!', 'success')
    
    return redirect(f'/admin/bill-detail/{bill_id}')

def delete_item(bill_id, item_id):
    """Admin: Delete item from bill"""
    if not is_admin():
        return redirect('/dashboard')
    
    delete_bill_item(item_id)
    flash('Item deleted successfully!', 'success')
    return redirect(f'/admin/bill-detail/{bill_id}')

def mark_paid(bill_id):
    """Admin: Mark bill as paid"""
    if not is_admin():
        return redirect('/dashboard')
    
    update_bill_status(bill_id, 'Paid')
    flash('Bill marked as Paid!', 'success')
    return redirect(f'/admin/bill-detail/{bill_id}')

def mark_unpaid(bill_id):
    """Admin: Mark bill as unpaid"""
    if not is_admin():
        return redirect('/dashboard')
    
    update_bill_status(bill_id, 'Unpaid')
    flash('Bill marked as Unpaid!', 'success')
    return redirect(f'/admin/bill-detail/{bill_id}')

def delete_bill_route(bill_id):
    """Admin: Delete a bill"""
    if not is_admin():
        return redirect('/dashboard')
    
    delete_bill(bill_id)
    flash('Bill deleted successfully!', 'success')
    return redirect('/admin/billing')

# ==================== PATIENT FEATURES ====================

def my_bills():
    """Patient: View their own bills"""
    user_id = get_current_user_id()
    patient = get_patient_by_user_id(user_id)
    
    if not patient:
        flash('Patient profile not found.', 'danger')
        return redirect('/dashboard')
    
    bills = get_bills_by_patient(patient[0])
    
    # Calculate totals
    total_amount = sum(bill[3] for bill in bills)  # bill[3] is total_amount
    pending_amount = sum(bill[3] for bill in bills if bill[4] == 'Unpaid')  # bill[4] is status
    
    return render_template('my_bills.html', bills=bills, total_amount=total_amount, pending_amount=pending_amount)

def view_bill(bill_id):
    """Patient: View bill details"""
    bill = get_bill_by_id(bill_id)
    
    if not bill:
        flash('Bill not found.', 'danger')
        return redirect('/my-bills')
    
    # Verify patient access
    user_id = get_current_user_id()
    patient = get_patient_by_user_id(user_id)
    
    if not patient or patient[0] != bill[1]:  # bill[1] is patient_id
        flash('You do not have permission to view this bill.', 'danger')
        return redirect('/my-bills')
    
    items = get_bill_items(bill_id)
    return render_template('bill_detail.html', bill=bill, items=items, is_admin=False)
