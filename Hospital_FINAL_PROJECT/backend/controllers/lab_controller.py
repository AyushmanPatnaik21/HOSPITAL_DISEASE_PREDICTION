from flask import request, redirect, render_template, session, flash, url_for, send_from_directory
from backend.models.lab_model import *
from backend.models.patient_model import get_all_patients, get_patient_by_user_id
from backend.utils.auth import is_admin, get_current_user_id
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'frontend', 'static', 'reports')
LAB_REPORT_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'frontend', 'static', 'uploads', 'lab_reports')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== API ENDPOINTS ====================

def get_test_parameters_api(booking_id):
    """API endpoint to fetch test parameters for dynamic form rendering"""
    if not is_admin():
        return {"error": "Unauthorized"}, 403
    
    booking = get_test_booking_by_id(booking_id)
    if not booking:
        return {"error": "Booking not found"}, 404
    
    test_id = booking[2]  # booking[2] is test_id
    test = get_lab_test_type_by_id(test_id)
    if not test:
        return {"error": "Test type not found"}, 404
    
    parameters = []
    if test[4]:  # test[4] is parameters
        parameters = [p.strip() for p in test[4].split(',') if p.strip()]
    
    return {
        "test_id": test[0],
        "test_name": test[1],
        "parameters": parameters
    }, 200

# ==================== ADMIN DASHBOARD ====================

def admin_dashboard():
    """Admin dashboard with statistics"""
    if not is_admin():
        return redirect('/lab-tests')
    
    stats = get_dashboard_stats()
    recent_bookings = get_recent_bookings(limit=5)
    
    return render_template('admin_dashboard.html', stats=stats, recent_bookings=recent_bookings)

# ==================== PATIENT FEATURES ====================

def list_available_tests():
    """List all available lab test types for patients to book"""
    # Note: Admins will see a redirect message in the template instead
    tests = get_all_lab_test_types()
    return render_template('lab_tests.html', tests=tests)

def book_test_form():
    """Show booking form for patients"""
    # Admin check - admins cannot book tests
    if is_admin():
        flash('Admins cannot book tests. Use the Admin Dashboard to manage bookings.', 'danger')
        return redirect('/admin/dashboard')
    
    user_id = get_current_user_id()
    patient = get_patient_by_user_id(user_id)

    if not patient:
        flash('Patient profile not found. Please contact administration to complete your profile.', 'danger')
        return redirect('/dashboard')

    tests = get_all_lab_test_types()
    
    # Get pre-selected test ID from query parameter
    selected_test_id = request.args.get('test_id')
    
    return render_template('book_test.html', tests=tests, patient=patient, selected_test_id=selected_test_id)

def book_test():
    """Handle test booking submission"""
    # Admin check - admins cannot book tests
    if is_admin():
        flash('Admins cannot book tests. Use the Admin Dashboard to manage bookings.', 'danger')
        return redirect('/admin/dashboard')
    
    if request.method != 'POST':
        return redirect('/lab-tests')

    user_id = get_current_user_id()
    patient = get_patient_by_user_id(user_id)

    if not patient:
        flash('Patient profile not found.', 'danger')
        return redirect('/lab-tests')

    test_id = request.form.get('test_id')
    booking_date = request.form.get('booking_date')
    booking_time = request.form.get('booking_time')

    # Validate required fields
    if not all([test_id, booking_date]):
        flash('Please fill in all required fields.', 'danger')
        return redirect('/book-test')

    # Check for duplicate booking
    if check_duplicate_booking(patient[0], test_id, booking_date):
        flash('You already have a booking for this test on the selected date.', 'danger')
        return redirect('/book-test')

    # Handle prescription file upload
    prescription_file = None
    if 'prescription' in request.files:
        file = request.files['prescription']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(file_path)
            prescription_file = unique_filename

    notes = request.form.get('notes')

    try:
        booking_id = create_test_booking(patient[0], test_id, booking_date, booking_time, prescription_file, notes)
        flash('Lab test booked successfully!', 'success')
        return redirect('/my-lab-tests')
    except Exception as e:
        flash('Error booking test. Please try again.', 'danger')
        return redirect('/book-test')

def my_lab_tests():
    """Patient dashboard for their lab test bookings"""
    # Admin check - admins use admin dashboard instead
    if is_admin():
        return redirect('/admin/dashboard')
    
    user_id = get_current_user_id()
    patient = get_patient_by_user_id(user_id)

    if not patient:
        flash('Patient profile not found. Please contact administration to complete your profile.', 'danger')
        return redirect('/dashboard')

    bookings = get_test_bookings_by_patient(patient[0])
    return render_template('my_lab_tests.html', bookings=bookings)

def find_report_path(filename):
    if not filename:
        return None
    primary = os.path.join(LAB_REPORT_UPLOAD_FOLDER, filename)
    fallback = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(primary):
        return LAB_REPORT_UPLOAD_FOLDER
    if os.path.exists(fallback):
        return UPLOAD_FOLDER
    return None


def download_report(booking_id):
    """Download lab test report"""
    user_id = get_current_user_id()
    patient = get_patient_by_user_id(user_id)

    if not patient:
        flash('Access denied.', 'danger')
        return redirect('/my-lab-tests')

    booking = get_test_booking_by_id(booking_id)

    if not booking or booking[1] != patient[0]:  # booking[1] is patient_id
        flash('Access denied.', 'danger')
        return redirect('/my-lab-tests')

    if not booking[7]:  # booking[7] is report_file
        flash('Report not available yet.', 'danger')
        return redirect('/my-lab-tests')

    report_dir = find_report_path(booking[7])
    if not report_dir:
        flash('Report file not found on disk.', 'danger')
        return redirect('/my-lab-tests')

    return send_from_directory(report_dir, booking[7], as_attachment=True)


def generate_lab_report(report_data):
    """Generate dynamic lab report based on test parameters"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        raise RuntimeError('ReportLab is required to generate PDF reports.')

    os.makedirs(LAB_REPORT_UPLOAD_FOLDER, exist_ok=True)
    filename = f"lab_report_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(LAB_REPORT_UPLOAD_FOLDER, filename)
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin

    c.setFont('Helvetica-Bold', 16)
    c.drawString(margin, y, 'Hospital Lab Report')
    y -= 30
    c.setFont('Helvetica', 10)
    c.drawString(margin, y, f"Date: {report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}")
    y -= 25
    c.setFont('Helvetica-Bold', 12)
    c.drawString(margin, y, f"Patient Name: {report_data.get('patient_name', 'N/A')}")
    y -= 20
    c.drawString(margin, y, f"Test Name: {report_data.get('test_name', 'N/A')}")
    y -= 30

    c.setFont('Helvetica-Bold', 11)
    c.drawString(margin, y, 'Results:')
    y -= 20
    c.setFont('Helvetica', 10)
    
    # Dynamically render parameters instead of hardcoded fields
    parameters = report_data.get('parameters', [])
    for param in parameters:
        param_name = param.strip()
        param_value = report_data.get(param_name.lower().replace(' ', '_'), 'N/A')
        c.drawString(margin, y, f"{param_name}: {param_value}")
        y -= 18

    y -= 10
    c.setFont('Helvetica-Bold', 11)
    c.drawString(margin, y, 'Remarks:')
    y -= 18
    c.setFont('Helvetica', 10)
    text = c.beginText(margin, y)
    text.textLines(report_data.get('remarks', 'No remarks provided.'))
    c.drawText(text)
    y -= 60

    c.setFont('Helvetica-Bold', 11)
    c.drawString(margin, y, 'Signature: _______________________________')
    y -= 30

    c.setFont('Helvetica-Oblique', 9)
    c.drawString(margin, y, 'Generated by Hospital Management System')
    c.showPage()
    c.save()

    return filename

# ==================== ADMIN FEATURES ====================

def manage_test_types():
    """Admin page to manage lab test types"""
    if not is_admin():
        return redirect('/lab-tests')

    tests = get_all_lab_test_types()
    return render_template('admin_lab_tests.html', tests=tests)

def add_test_type():
    """Add new lab test type"""
    if not is_admin():
        return redirect('/lab-tests')

    if request.method == 'POST':
        test_name = request.form.get('test_name')
        price = request.form.get('price')
        description = request.form.get('description')

        if not all([test_name, price]):
            flash('Please fill in all required fields.', 'error')
            return redirect('/admin/lab-tests')

        try:
            create_lab_test_type(test_name, float(price), description)
            flash('Lab test type added successfully!', 'success')
        except Exception as e:
            flash('Error adding test type. Please try again.', 'danger')

        return redirect('/admin/lab-tests')

    return render_template('add_lab_test_type.html')

def edit_test_type(test_id):
    """Edit existing lab test type"""
    if not is_admin():
        return redirect('/lab-tests')

    test = get_lab_test_type_by_id(test_id)
    if not test:
        flash('Test type not found.', 'danger')
        return redirect('/admin/lab-tests')

    if request.method == 'POST':
        test_name = request.form.get('test_name')
        price = request.form.get('price')
        description = request.form.get('description')

        if not all([test_name, price]):
            flash('Please fill in all required fields.', 'error')
            return redirect(f'/admin/edit-test/{test_id}')

        try:
            update_lab_test_type(test_id, test_name, float(price), description)
            flash('Lab test type updated successfully!', 'success')
        except Exception as e:
            flash('Error updating test type. Please try again.', 'danger')

        return redirect('/admin/lab-tests')

    return render_template('edit_lab_test_type.html', test=test)

def delete_test_type(test_id):
    """Delete lab test type"""
    if not is_admin():
        return redirect('/lab-tests')

    try:
        delete_lab_test_type(test_id)
        flash('Lab test type deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting test type. Please try again.', 'danger')

    return redirect('/admin/lab-tests')

def manage_bookings():
    """Admin page to manage all test bookings"""
    if not is_admin():
        return redirect('/lab-tests')

    bookings = get_all_test_bookings()
    return render_template('admin_bookings.html', bookings=bookings)

def update_booking_status_route(booking_id):
    """Update booking status (admin)"""
    if not is_admin():
        return redirect('/lab-tests')

    if request.method == 'POST':
        status = request.form.get('status')
        report_method = request.form.get('report_method')
        report_file = None

        booking = get_test_booking_by_id(booking_id)
        existing_report = booking[7] if booking else None

        if status == 'Completed':
            if report_method == 'generate':
                test_id = booking[2] if booking else None
                test = get_lab_test_type_by_id(test_id) if test_id else None
                
                if not test:
                    flash('Test details not found.', 'danger')
                    return redirect('/admin/bookings')
                
                # Get parameters from test
                parameters = []
                if test[4]:  # test[4] is parameters
                    parameters = [p.strip() for p in test[4].split(',') if p.strip()]
                
                # Validate all parameters are provided
                form_data = {}
                for param in parameters:
                    value = request.form.get(param.lower().replace(' ', '_'), '').strip()
                    if not value:
                        flash(f'Please fill in all required values ({param}).', 'danger')
                        return redirect('/admin/bookings')
                    form_data[param.lower().replace(' ', '_')] = value
                
                remarks = request.form.get('remarks', '').strip()
                
                report_data = {
                    'patient_name': booking[13] if booking else 'Patient',
                    'test_name': booking[10] if booking else 'Test',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'parameters': parameters,
                    'remarks': remarks,
                }
                report_data.update(form_data)
                
                try:
                    report_file = generate_lab_report(report_data)
                except Exception as e:
                    flash(str(e), 'danger')
                    return redirect('/admin/bookings')

            elif report_method == 'upload':
                if 'report' in request.files:
                    file = request.files['report']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        unique_filename = f"{uuid.uuid4()}_{filename}"
                        file_path = os.path.join(LAB_REPORT_UPLOAD_FOLDER, unique_filename)
                        os.makedirs(LAB_REPORT_UPLOAD_FOLDER, exist_ok=True)
                        file.save(file_path)
                        report_file = unique_filename

                if not report_file and not existing_report:
                    flash('Please upload or generate a lab report before completing the test.', 'danger')
                    return redirect('/admin/bookings')

            else:
                if not existing_report:
                    flash('Please select a report method and upload or generate a report before completing.', 'danger')
                    return redirect('/admin/bookings')

        try:
            update_booking_status(booking_id, status, report_file)
            flash('Booking status updated successfully!', 'success')
        except Exception as e:
            flash('Error updating booking status. Please try again.', 'danger')

    return redirect('/admin/bookings')

# ==================== DOCTOR FEATURES ====================

def prescribe_test():
    """Doctor can prescribe lab tests to patients"""
    # This would be integrated with appointment system
    # For now, redirect to patient search or appointment view
    flash('Test prescription feature coming soon. Please use the booking system.', 'info')
    return redirect('/patients')

# ==================== LEGACY FUNCTIONS (for backward compatibility) ====================

def create_test():
    # Only admins can create tests
    if not is_admin():
        return redirect('/lab-tests')

    patient_id = request.form['patient_id']
    test_type = request.form['test_type']

    add_test(patient_id, test_type)

    return redirect('/lab-tests')


def list_tests():
    # Check if user is admin or patient
    admin = is_admin()
    if admin:
        tests = get_all_tests()
    else:
        # Patient can only see their own tests
        user_id = get_current_user_id()
        tests = get_tests_by_user(user_id)

    return render_template('lab_tests.html', tests=tests, is_admin=admin)


def update_test_result():
    # Only admins can update test results
    if not is_admin():
        return redirect('/lab-tests')

    test_id = request.form['test_id']
    result = request.form['result']

    update_result(test_id, result)

    return redirect('/lab-tests')


def test_form():
    if is_admin():
        # Admin can select any patient
        patients = get_all_patients()
    else:
        # Patient can only see their own info
        user_id = get_current_user_id()
        patient = get_patient_by_user_id(user_id)
        patients = [patient] if patient else []

    return render_template('add_test.html', patients=patients)