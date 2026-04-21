from flask import render_template, session
from backend.models.patient_model import get_all_patients
from backend.models.doctor_model import get_all_doctors
from backend.models.appointment_model import get_all_appointments
from backend.models.billing_model import get_all_bills
from backend.models.prediction_history_model import get_prediction_analytics


def admin_dashboard():
    patients = get_all_patients()
    doctors = get_all_doctors()
    appointments = get_all_appointments()
    bills = get_all_bills()

    total_revenue = sum([b[2] for b in bills if b[3] == 'Paid'])

    # Get AI prediction analytics
    ai_analytics = get_prediction_analytics()

    return render_template(
        'dashboard.html',
        total_patients=len(patients),
        total_doctors=len(doctors),
        total_appointments=len(appointments),
        total_revenue=total_revenue,
        ai_analytics=ai_analytics,
        doctors=doctors,
        patients=patients,
        appointments=appointments,
        role=session.get('role')
    )


def patient_dashboard():
    user_id = session.get('user_id')
    # Get patients linked to this user
    from backend.models.patient_model import get_patients_by_user_id
    patients = get_patients_by_user_id(user_id)
    
    return render_template('patient_dashboard.html', patients=patients, role='patient')