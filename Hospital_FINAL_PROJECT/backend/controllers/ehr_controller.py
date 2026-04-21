from flask import request, redirect, render_template, session, flash
from backend.models.ehr_model import *
from backend.models.patient_model import get_all_patients, get_patient_by_user_id
from backend.models.doctor_model import get_all_doctors
from backend.utils.auth import is_admin, get_current_user_id


def add_ehr_record():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    diagnosis = request.form['diagnosis']
    treatment_plan = request.form['treatment_plan']
    medications = request.form['medications']
    notes = request.form['notes']

    add_record(patient_id, doctor_id, diagnosis, treatment_plan, medications, notes)

    return redirect('/ehr')


def ehr_form():
    doctors = get_all_doctors()
    patients = get_all_patients()

    return render_template('add_ehr.html', doctors=doctors, patients=patients)


def list_all_ehr():
    """View all EHR records"""
    if is_admin():
        records = get_all_records()
    else:
        # Patient can only see their own EHR records
        user_id = get_current_user_id()
        records = get_records_by_user(user_id)
    
    return render_template('ehr.html', records=records)


def view_ehr(patient_id):
    """View EHR records for a specific patient"""
    records = get_records_by_patient(patient_id)
    return render_template('ehr.html', records=records)


def view_record_detail(record_id):
    """View detailed EHR record"""
    record = get_record_by_id(record_id)
    return render_template('ehr_detail.html', record=record)


def delete_ehr_record(record_id):
    """Delete an EHR record"""
    delete_record(record_id)
    return redirect('/ehr')