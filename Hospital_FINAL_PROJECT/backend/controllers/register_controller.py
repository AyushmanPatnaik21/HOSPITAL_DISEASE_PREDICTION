import sqlite3
from flask import request, redirect, flash, render_template

def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect('database/hospital.db')
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("⚠️ User already exists! Please login.")
            return redirect('/login')

        # Insert new user
        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, password, role))

        conn.commit()
        conn.close()

        flash("✅ Registration successful! Please login.")
        return redirect('/login')

    return render_template('register.html')