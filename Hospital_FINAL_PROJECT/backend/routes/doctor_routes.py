from flask import Blueprint, render_template, request
from backend.controllers.doctor_controller import *
from backend.utils.auth import login_required, admin_required

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/doctors')
@login_required
def doctors():
    return list_doctors()

@doctor_bp.route('/add-doctor', methods=['GET', 'POST'])
@admin_required
def add_doctor_route():
    if request.method == 'POST':
        return create_doctor()
    return render_template('add_doctor.html')

@doctor_bp.route('/setup-doctor-profile', methods=['GET', 'POST'])
def setup_doctor_profile_route():
    return setup_doctor_profile()

@doctor_bp.route('/delete-doctor/<int:id>')
@admin_required
def delete_doctor_route(id):
    return delete_doctor_data(id)