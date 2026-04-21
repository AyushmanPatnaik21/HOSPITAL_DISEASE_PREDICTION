from flask import Blueprint, request, redirect, jsonify
from backend.controllers.appointment_controller import *
from backend.utils.auth import login_required, is_admin

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/appointments')
@login_required
def appointments():
    return list_appointments()


@appointment_bp.route('/add-appointment', methods=['GET', 'POST'])
@login_required
def add_appointment_route():
    if is_admin():
        return redirect('/appointments')
    if request.method == 'POST':
        return book_appointment()
    return appointment_form()


@appointment_bp.route('/cancel-appointment/<int:id>')
def cancel_appointment_route(id):
    return cancel_appointment_data(id)


@appointment_bp.route('/delete-appointment/<int:id>')
def delete_appointment_route(id):
    return delete_appointment_data(id)


@appointment_bp.route('/api/available-times')
@login_required
def get_available_times():
    doctor_id = request.args.get('doctor_id')
    date = request.args.get('date')
    if not doctor_id or not date:
        return jsonify({'error': 'Missing parameters'}), 400
    
    from backend.models.appointment_model import get_available_slots, format_time_to_12hour
    available_times = get_available_slots(doctor_id, date)
    
    # Convert to 12-hour format for display
    formatted_times = [format_time_to_12hour(time) for time in available_times]
    
    return jsonify({'times': available_times, 'formatted_times': formatted_times})


@appointment_bp.route('/api/available-days')
@login_required
def get_available_days():
    doctor_id = request.args.get('doctor_id')
    if not doctor_id:
        return jsonify({'error': 'Missing doctor_id'}), 400
    
    from backend.models.doctor_model import get_doctor
    from backend.models.appointment_model import parse_doctor_availability
    
    doctor = get_doctor(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    availability = parse_doctor_availability(doctor[4])  # availability is at index 4
    if not availability:
        return jsonify({'error': 'No availability information'}), 400
    
    return jsonify(availability)