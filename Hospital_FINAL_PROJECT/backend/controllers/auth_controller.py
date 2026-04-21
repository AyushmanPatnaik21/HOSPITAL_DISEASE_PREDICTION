import re
from flask import request, redirect, session, flash, render_template
from backend.models.user_model import create_user, get_user_by_email, get_db

COMMON_PASSWORDS = [
    'password', '123456', '12345678', 'qwerty', 'abc123', '111111', '123123',
    'letmein', 'admin', 'welcome', 'login', 'pass', 'user', '123456789'
]


def is_password_used_before(password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE password = ? LIMIT 1", (password,))
    used = cursor.fetchone() is not None
    conn.close()
    return used


def validate_password(password, name, email):
    errors = []
    normalized_password = password.strip()
    lower_password = normalized_password.lower()
    lower_name = (name or '').strip().lower()
    lower_email = (email or '').strip().lower()

    if len(normalized_password) < 8 or len(normalized_password) > 16:
        errors.append('Password must be 8–16 characters long.')

    if not re.search(r'[A-Z]', normalized_password):
        errors.append('Add at least one uppercase letter.')

    if not re.search(r'[a-z]', normalized_password):
        errors.append('Add at least one lowercase letter.')

    if not re.search(r'\d', normalized_password):
        errors.append('Add at least one number.')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', normalized_password):
        errors.append('Add at least one special character.')

    if lower_password == lower_name and lower_name:
        errors.append('Password cannot be the same as your name.')

    if lower_password == lower_email and lower_email:
        errors.append('Password cannot be the same as your email.')

    if any(common in lower_password for common in COMMON_PASSWORDS):
        errors.append('Avoid common words like "password", "123456" and "admin".')

    if re.search(r'(.)\1\1', normalized_password):
        errors.append('Avoid repeating the same character three or more times.')

    if is_password_used_before(normalized_password):
        errors.append('Choose a password that has not been used before.')

    return errors


def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        validation_errors = validate_password(password, name, email)
        if validation_errors:
            for error in validation_errors:
                flash(f'⚠️ {error}')
            return redirect('/register')

        success = create_user(name, email, password, role)

        if success:
            flash("✅ Registration successful! Please login.")
            return redirect('/login')
        else:
            flash("⚠️ Email already exists! Try another email.")
            return redirect('/register')

    return render_template('signup.html')

def login_user():
    email = request.form['email']
    password = request.form['password']

    user = get_user_by_email(email)

    if user and user[3] == password:
        user_id = user[0]
        user_name = user[1]
        user_email = user[2]
        user_role = user[4]

        session['user_id'] = user_id
        session['role'] = user_role
        session['user_name'] = user_name
        session['user_email'] = user_email

        # Ensure the profile is linked to the user account (user_id)
        if user_role == 'doctor':
            from backend.models.doctor_model import get_db
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM doctors WHERE user_id=?", (user_id,))
            doctor_profile = cursor.fetchone()

            # Try to link existing profile by name if user_id isn't set yet
            if not doctor_profile:
                cursor.execute("SELECT doctor_id FROM doctors WHERE name=?", (user_name,))
                found = cursor.fetchone()
                if found:
                    doctor_id = found[0]
                    cursor.execute("UPDATE doctors SET user_id=? WHERE doctor_id=?", (user_id, doctor_id))
                    conn.commit()
                    doctor_profile = True

            conn.close()

            if not doctor_profile:
                return redirect('/setup-doctor-profile')

        elif user_role == 'patient':
            from backend.models.patient_model import get_db
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM patients WHERE user_id=?", (user_id,))
            patient_profile = cursor.fetchone()

            # Try to link existing profile by name if user_id isn't set yet
            if not patient_profile:
                cursor.execute("SELECT patient_id FROM patients WHERE name=?", (user_name,))
                found = cursor.fetchone()
                if found:
                    patient_id = found[0]
                    cursor.execute("UPDATE patients SET user_id=? WHERE patient_id=?", (user_id, patient_id))
                    conn.commit()
                    patient_profile = True

            conn.close()

            if not patient_profile:
                return redirect('/setup-patient-profile')

            # If profile exists, redirect to the patient detail page
            if isinstance(patient_profile, tuple):
                patient_id = patient_profile[0]
            else:
                patient_id = patient_id

            return redirect(f'/patient/{patient_id}')

        # default landing page for other roles
        return redirect('/dashboard')

    flash("❌ Invalid email or password")
    return render_template('login.html')