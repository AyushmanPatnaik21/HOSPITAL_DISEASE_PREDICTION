from flask import request, redirect, render_template, session
from backend.models.patient_model import *
from backend.models.appointment_model import get_appointments_by_patient

def create_patient():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    contact = request.form['contact']
    address = request.form['address']
    medical_history = request.form['medical_history']

    user_id = None
    if session.get('role') == 'patient':
        user_id = session.get('user_id')

    add_patient(name, age, gender, contact, address, medical_history, user_id=user_id)

    if session.get('role') == 'patient':
        return redirect('/dashboard')  # redirect to patient dashboard
    else:
        return redirect('/patients')


def setup_patient_profile():
    """Setup patient profile after first login"""
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']
        address = request.form['address']
        medical_history = request.form['medical_history']
        
        user_id = session.get('user_id')
        patient_id = add_patient(name, age, gender, contact, address, medical_history, user_id=user_id)
        
        # After setup, send user directly to their profile page
        return redirect(f'/patient/{patient_id}')
    
    return render_template('setup_patient_profile.html')


def list_patients():
    patients = get_all_patients()
    return render_template('patients.html', patients=patients)


def view_patient(patient_id):
    patient = get_patient(patient_id)
    appointments = get_appointments_by_patient(patient_id)
    return render_template('patient_detail.html', patient=patient, appointments=appointments)


def update_patient_data(patient_id):
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    contact = request.form['contact']
    address = request.form['address']
    medical_history = request.form['medical_history']

    update_patient(patient_id, name, age, gender, contact, address, medical_history)

    return redirect('/patients')


def delete_patient_data(patient_id):
    delete_patient(patient_id)
    return redirect('/patients')