import sqlite3
from flask import request, redirect, session, flash, render_template

def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database/hospital.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            user_id = user[0]
            user_name = user[1]
            user_email = user[2]
            role = user[4]
            
            session['user_id'] = user_id
            session['role'] = role
            session['user_name'] = user_name
            session['user_email'] = user_email

            # Check if user has completed their profile
            if role == 'doctor':
                conn = sqlite3.connect('database/hospital.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM doctors WHERE user_id=?", (user_id,))
                doctor_profile = cursor.fetchone()
                conn.close()
                
                if not doctor_profile:
                    return redirect('/setup-doctor-profile')
            
            elif role == 'patient':
                conn = sqlite3.connect('database/hospital.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE user_id=?", (user_id,))
                patient_profile = cursor.fetchone()
                conn.close()
                
                if not patient_profile:
                    return redirect('/setup-patient-profile')

            return redirect('/home')
        else:
            flash("❌ Invalid email or password")

    return render_template('login.html')