from flask import Blueprint, render_template, request, jsonify
from backend.controllers.patient_controller import *
from backend.utils.auth import login_required, admin_required

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/patients')
@admin_required
def patients():
    return list_patients()

@patient_bp.route('/add-patient', methods=['GET', 'POST'])
@login_required
def add_patient_route():
    if request.method == 'POST':
        return create_patient()
    return render_template('add_patient.html')

@patient_bp.route('/setup-patient-profile', methods=['GET', 'POST'])
def setup_patient_profile_route():
    return setup_patient_profile()

@patient_bp.route('/patient/<int:id>')
def view_patient_route(id):
    return view_patient(id)


@patient_bp.route('/update-patient/<int:id>', methods=['POST'])
@admin_required
def update_patient_route(id):
    return update_patient_data(id)


@patient_bp.route('/delete-patient/<int:id>')
@admin_required
def delete_patient_route(id):
    return delete_patient_data(id)


@patient_bp.route('/api/check-patient-name', methods=['GET'])
@login_required
def check_patient_name():
    """API endpoint to check if a patient name exists for the current user"""
    from backend.utils.auth import get_current_user_id
    from backend.models.patient_model import check_patient_exists_by_name
    
    patient_name = request.args.get('name', '').strip()
    
    if not patient_name:
        return jsonify({'exists': False, 'message': 'Patient name is required'}), 400
    
    user_id = get_current_user_id()
    exists = check_patient_exists_by_name(user_id, patient_name)
    
    return jsonify({'exists': exists})