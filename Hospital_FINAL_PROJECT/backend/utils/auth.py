from flask import session, redirect
import sqlite3
import os

def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "database", "hospital.db")
    return sqlite3.connect(db_path)

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect('/login')
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect('/login')
        if not is_admin():
            return redirect('/dashboard')  # or some error page
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def get_current_user_id():
    """Get the current user ID from session"""
    return session.get('user_id')

def get_current_user_role():
    """Get the current user's role from session"""
    return session.get('role')

def is_admin():
    """Check if current user is an admin"""
    return get_current_user_role() == 'admin'


def is_doctor():
    """Check if current user is a doctor"""
    return get_current_user_role() == 'doctor'


def admin_or_doctor_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect('/login')
        if not (is_admin() or is_doctor()):
            return redirect('/dashboard')
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def doctor_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect('/login')
        if not is_doctor():
            return redirect('/dashboard')
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def patient_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect('/login')
        if get_current_user_role() != 'patient':
            return redirect('/dashboard')
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def get_patient_id_for_user(user_id):
    """Get the patient_id associated with a user_id"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def can_access_patient(patient_id):
    """Check if current user can access a patient's data
    - Admins can access all patients
    - Patients can only access their own data
    """
    if is_admin():
        return True
    
    user_id = get_current_user_id()
    if not user_id:
        return False
    
    # Check if this patient belongs to the current user
    patient_user_id = get_patient_user_id(patient_id)
    return patient_user_id == user_id

def get_patient_user_id(patient_id):
    """Get the user_id associated with a patient_id"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM patients WHERE patient_id = ?", (patient_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None