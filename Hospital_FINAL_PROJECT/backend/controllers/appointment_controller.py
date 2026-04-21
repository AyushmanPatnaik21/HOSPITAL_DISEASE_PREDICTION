from flask import request, redirect, render_template, session, flash
from backend.models.appointment_model import *
from backend.models.patient_model import get_all_patients, get_patient_by_user_id, add_patient
from backend.models.doctor_model import get_all_doctors
from backend.utils.auth import is_admin, get_current_user_id


def book_appointment():
    # Admin cannot book appointments
    if is_admin():
        return redirect('/appointments')

    user_id = get_current_user_id()
    patient_name = request.form.get('patient_name', '').strip()

    if not patient_name:
        flash('Patient name is required', 'error')
        return redirect('/add-appointment')

    # Look up patient by name
    from backend.models.patient_model import check_patient_exists_by_name, get_patients_by_user_id
    
    if not check_patient_exists_by_name(user_id, patient_name):
        flash(f'Patient profile "{patient_name}" does not exist. Please add the patient first.', 'error')
        return redirect('/add-appointment')

    # Get all patients for user and find the one with matching name
    patients = get_patients_by_user_id(user_id)
    patient_id = None
    for p in patients:
        if p[1] == patient_name:  # p[1] is the name
            patient_id = p[0]  # p[0] is the patient_id
            break

    if not patient_id:
        flash('Patient not found', 'error')
        return redirect('/add-appointment')

    doctor_id = request.form['doctor_id']
    date = request.form['date']
    time = request.form['time']  # Now contains time slot like "10:00"
    
    # Validate that time is in correct format
    if not time or ':' not in time:
        flash('Please select a valid time slot', 'error')
        return redirect('/add-appointment')
    
    add_appointment(patient_id, doctor_id, date, time)

    flash('Appointment booked successfully!', 'success')
    return redirect('/appointments')


def extract_start_time_from_range(time_range):
    """
    Extract start time from time range format (e.g., "10.00am-2.30pm" -> "10:00")
    """
    try:
        # Split by dash and take the first part
        start_part = time_range.split('-')[0]
        
        # Remove 'am' or 'pm' and convert to 24-hour format
        start_clean = start_part.replace('am', '').replace('pm', '')
        
        # Split by dot to get hours and minutes
        parts = start_clean.split('.')
        if len(parts) == 2:
            hours = int(parts[0])
            minutes = int(parts[1])
            
            # Convert to 24-hour format if it's PM and not 12
            if 'pm' in start_part.lower() and hours != 12:
                hours += 12
            # Handle 12 AM
            elif 'am' in start_part.lower() and hours == 12:
                hours = 0
            
            return f"{hours:02d}:{minutes:02d}"
        
        # Fallback: try to parse as is
        return start_clean.replace('.', ':')
    except:
        # If parsing fails, return the original time_range
        return time_range


def list_appointments():
    # Check if user is admin or patient
    admin = is_admin()
    if admin:
        appointments = get_all_appointments()
    else:
        # Patient can only see their own appointments
        user_id = get_current_user_id()
        appointments = get_appointments_by_user(user_id)
    
    return render_template('appointments.html', appointments=appointments, is_admin=admin)


def cancel_appointment_data(id):
    cancel_appointment(id)
    return redirect('/appointments')


def delete_appointment_data(id):
    delete_appointment(id)
    return redirect('/appointments')


def appointment_form():
    admin = is_admin()
    doctors = get_all_doctors()

    if admin:
        # Admin can select any patient
        patients = get_all_patients()
        current_patient = None
        patient_names = []
    else:
        # Non-admin patient can only act on own profile
        user_id = get_current_user_id()
        from backend.models.patient_model import get_patients_by_user_id
        user_patients = get_patients_by_user_id(user_id)
        # Extract patient names for the user
        patient_names = [p[1] for p in user_patients]
        current_patient = user_patients[0] if user_patients else None
        patients = []

    return render_template(
        'add_appointment.html',
        patients=patients,
        doctors=doctors,
        is_admin=admin,
        current_patient=current_patient,
        patient_names=patient_names
    )


def get_available_slots(doctor_id, date):
    return get_available_slots_model(doctor_id, date)