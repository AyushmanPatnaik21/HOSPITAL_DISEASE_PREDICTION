from flask import Flask, render_template, session, redirect

# import all blueprints
from backend.routes.auth_routes import auth_bp
from backend.routes.patient_routes import patient_bp
from backend.routes.doctor_routes import doctor_bp
from backend.routes.appointment_routes import appointment_bp
from backend.routes.ehr_routes import ehr_bp
from backend.routes.billing_routes import billing_bp
from backend.routes.pharmacy_routes import pharmacy_bp
from backend.routes.lab_routes import lab_bp
from backend.routes.ml_routes import ml_bp
from backend.routes.dashboard_routes import dashboard_bp

# helper models
from backend.models.patient_model import get_db as get_patient_db
from backend.models.doctor_model import get_db as get_doctor_db
from backend.models.prediction_history_model import create_prediction_history_table
from backend.controllers.dashboard_controller import admin_dashboard

app = Flask(__name__,static_folder="frontend/static", template_folder="frontend/templates")

# important for session
app.secret_key = "secret123"

# Custom Jinja2 filter for formatting datetime
from datetime import datetime

@app.template_filter('format_datetime')
def format_datetime_filter(dt_string):
    """Format datetime string to readable format"""
    if not dt_string:
        return 'N/A'
    try:
        dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d %b %Y at %I:%M %p')
    except:
        return dt_string

# ---------------- REGISTER BLUEPRINTS ----------------
app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(appointment_bp)
app.register_blueprint(ehr_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(pharmacy_bp)
app.register_blueprint(lab_bp)
app.register_blueprint(ml_bp)
app.register_blueprint(dashboard_bp)

# ---------------- BASIC PAGES ----------------

@app.route('/')
def splash():
    if session.get('splash_shown'):
        return redirect('/home')
    session['splash_shown'] = True
    return render_template('splash.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


from flask import request, render_template, flash

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # (optional: save to DB)

        flash("✅ Your message has been sent! We will get back to you soon.")
        return render_template('contact.html')

    return render_template('contact.html')

@app.route('/facilities')
def facilities():
    return render_template('view_facilities.html')


from flask import render_template, session, redirect



@app.route('/dashboard')
def dashboard():
    role = session.get('role')
    user_id = session.get('user_id')

    if not role:
        return redirect('/login')

    # Patients see their patient dashboard
    if role == 'patient':
        from backend.controllers.dashboard_controller import patient_dashboard
        return patient_dashboard()

    # Doctors can view the doctor list by default
    if role == 'doctor':
        conn = get_doctor_db()
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_id FROM doctors WHERE user_id=?", (user_id,))
        doctor = cursor.fetchone()
        conn.close()

        if doctor:
            return redirect('/doctors')
        return redirect('/setup-doctor-profile')

    # Admin/other roles see a live dashboard
    from backend.controllers.dashboard_controller import admin_dashboard
    return admin_dashboard()

# Note: Disease prediction is now handled by backend/routes/ml_routes.py and ml_model/predict_dl.py

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    try:
        create_prediction_history_table()
    except Exception as e:
        print(f"Warning: could not create prediction_history table: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)