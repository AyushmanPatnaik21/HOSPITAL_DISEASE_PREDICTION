from flask import Blueprint
from backend.controllers.dashboard_controller import admin_dashboard
from backend.utils.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/admin-dashboard')
@login_required
def dashboard():
    return admin_dashboard()