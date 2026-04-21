from flask import Blueprint, request
from backend.controllers.ehr_controller import *
from backend.utils.auth import login_required, admin_required

ehr_bp = Blueprint('ehr', __name__)

@ehr_bp.route('/ehr')
@admin_required
def list_ehr():
    return list_all_ehr()

@ehr_bp.route('/add-ehr', methods=['GET', 'POST'])
@admin_required
def add_ehr_route():
    if request.method == 'POST':
        return add_ehr_record()
    return ehr_form()

@ehr_bp.route('/ehr/<int:patient_id>')
@admin_required
def view_ehr_route(patient_id):
    return view_ehr(patient_id)

@ehr_bp.route('/ehr-record/<int:record_id>')
@admin_required
def view_ehr_detail_route(record_id):
    return view_record_detail(record_id)

@ehr_bp.route('/delete-ehr/<int:record_id>')
@admin_required
def delete_ehr_route(record_id):
    return delete_ehr_record(record_id)