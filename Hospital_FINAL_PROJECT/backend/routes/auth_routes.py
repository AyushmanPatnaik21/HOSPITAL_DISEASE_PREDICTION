from flask import Blueprint, render_template,request,session,redirect
from backend.controllers.auth_controller import register_user, login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return register_user()
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return login_user()
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/home')