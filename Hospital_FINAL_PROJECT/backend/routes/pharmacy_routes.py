from flask import Blueprint, request, redirect, session
from backend.controllers.pharmacy_controller import (
    pharmacy_redirect,
    admin_medicines,
    admin_add_medicine,
    admin_edit_medicine,
    admin_delete_medicine,
    admin_sell_medicine,
    admin_sales_history,
    doctor_prescriptions,
    doctor_add_prescription,
    patient_prescriptions,
    patient_purchases,
)
from backend.utils.auth import (
    login_required,
    admin_required,
    doctor_required,
    patient_required,
)

pharmacy_bp = Blueprint('pharmacy', __name__)

@pharmacy_bp.route('/pharmacy')
@login_required
def pharmacy():
    return pharmacy_redirect()


@pharmacy_bp.route('/admin/medicines')
@admin_required
def admin_medicines_route():
    return admin_medicines()


@pharmacy_bp.route('/add-medicine')
@admin_required
def add_medicine_alias():
    return redirect('/admin/add-medicine')


@pharmacy_bp.route('/admin/add-medicine', methods=['GET', 'POST'])
@admin_required
def add_medicine_route():
    return admin_add_medicine()


@pharmacy_bp.route('/admin/edit-medicine/<int:medicine_id>', methods=['GET', 'POST'])
@admin_required
def edit_medicine_route(medicine_id):
    return admin_edit_medicine(medicine_id)


@pharmacy_bp.route('/admin/delete-medicine/<int:medicine_id>')
@admin_required
def delete_medicine_route(medicine_id):
    return admin_delete_medicine(medicine_id)


@pharmacy_bp.route('/admin/sell-medicine', methods=['GET', 'POST'])
@admin_required
def sell_medicine_route():
    return admin_sell_medicine()


@pharmacy_bp.route('/issue-medicine', methods=['POST'])
@admin_required
def issue_medicine_route():
    return admin_sell_medicine()


@pharmacy_bp.route('/admin/sales')
@admin_required
def sales_history_route():
    return admin_sales_history()


@pharmacy_bp.route('/doctor/prescription')
@doctor_required
def doctor_prescriptions_route():
    return doctor_prescriptions()


@pharmacy_bp.route('/doctor/add-prescription', methods=['GET', 'POST'])
@doctor_required
def doctor_add_prescription_route():
    return doctor_add_prescription()


@pharmacy_bp.route('/my-prescriptions')
@patient_required
def my_prescriptions_route():
    return patient_prescriptions()


@pharmacy_bp.route('/my-purchases')
@patient_required
def my_purchases_route():
    return patient_purchases()