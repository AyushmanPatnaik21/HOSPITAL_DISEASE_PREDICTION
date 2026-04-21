from flask import Blueprint, request, redirect
from backend.controllers.lab_controller import *
from backend.utils.auth import login_required, is_admin

lab_bp = Blueprint('lab', __name__)

# ==================== ADMIN ROUTES ====================

@lab_bp.route('/admin/dashboard')
@login_required
def admin_dashboard_route():
    return admin_dashboard()

# ==================== PATIENT ROUTES ====================

@lab_bp.route('/lab-tests')
@login_required
def lab_tests():
    return list_available_tests()

@lab_bp.route('/book-test', methods=['GET', 'POST'])
@login_required
def book_test_route():
    if request.method == 'POST':
        return book_test()
    return book_test_form()

@lab_bp.route('/my-lab-tests')
@login_required
def my_lab_tests_route():
    return my_lab_tests()

@lab_bp.route('/download-report/<int:booking_id>')
@login_required
def download_report_route(booking_id):
    return download_report(booking_id)

# ==================== ADMIN ROUTES ====================

@lab_bp.route('/admin/lab-tests')
@login_required
def admin_lab_tests():
    return manage_test_types()

@lab_bp.route('/admin/add-test-type', methods=['GET', 'POST'])
@login_required
def add_test_type_route():
    return add_test_type()

@lab_bp.route('/admin/edit-test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def edit_test_type_route(test_id):
    return edit_test_type(test_id)

@lab_bp.route('/admin/delete-test/<int:test_id>')
@login_required
def delete_test_type_route(test_id):
    return delete_test_type(test_id)

@lab_bp.route('/admin/bookings')
@login_required
def admin_bookings():
    return manage_bookings()

@lab_bp.route('/admin/update-booking/<int:booking_id>', methods=['POST'])
@login_required
def update_booking_route(booking_id):
    return update_booking_status_route(booking_id)

# ==================== API ROUTES ====================

@lab_bp.route('/api/test-parameters/<int:booking_id>', methods=['GET'])
@login_required
def test_parameters_api(booking_id):
    """API endpoint to fetch test parameters for dynamic form rendering"""
    from flask import jsonify
    result, status_code = get_test_parameters_api(booking_id)
    return jsonify(result), status_code

# ==================== DOCTOR ROUTES ====================

@lab_bp.route('/prescribe-test')
@login_required
def prescribe_test_route():
    return prescribe_test()

# ==================== LEGACY ROUTES (for backward compatibility) ====================

@lab_bp.route('/add-test', methods=['GET', 'POST'])
@login_required
def add_test_route():
    if not is_admin():
        return redirect('/lab-tests')
    if request.method == 'POST':
        return create_test()
    return test_form()

@lab_bp.route('/update-test', methods=['POST'])
@login_required
def update_test_route():
    if not is_admin():
        return redirect('/lab-tests')
    return update_test_result()