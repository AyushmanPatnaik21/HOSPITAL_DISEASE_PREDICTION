from flask import request, redirect, render_template, session
from backend.models.doctor_model import *
from backend.utils.auth import is_admin

def create_doctor():
    name = request.form['name']
    specialization = request.form['specialization']
    contact = request.form['contact']
    availability = request.form['availability']

    add_doctor(name, specialization, contact, availability)

    return redirect('/doctors')


def setup_doctor_profile():
    """Setup doctor profile after first login"""
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        contact = request.form['contact']
        availability = request.form['availability']
        
        user_id = session.get('user_id')
        add_doctor(name, specialization, contact, availability, user_id=user_id)
        
        return redirect('/home')
    
    return render_template('setup_doctor_profile.html')


def list_doctors():
    doctors = get_all_doctors()
    return render_template('doctors.html', doctors=doctors, is_admin=is_admin())


def delete_doctor_data(doctor_id):
    delete_doctor(doctor_id)
    return redirect('/doctors')