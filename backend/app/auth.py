from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle both form and JSON
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            remember = data.get('remember', False)
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

        user = User.get_by_email(email)

        if not user or not user.check_password(password):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        
        if request.is_json:
            return jsonify({
                'success': True, 
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'role': user.role,
                    'is_admin': user.is_admin,
                    'is_superadmin': user.is_superadmin
                }
            })

        # Redirect based on role
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
            
        return redirect(url_for('main.index'))

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            email = request.form.get('email')
            password = request.form.get('password')

        user = User.get_by_email(email)

        if user:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Email already exists'}), 400
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        # Create new user
        new_user = User.create(email, password, role='user')

        login_user(new_user)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'user': {
                    'id': str(new_user.id),
                    'email': new_user.email,
                    'role': new_user.role,
                    'is_admin': new_user.is_admin,
                    'is_superadmin': new_user.is_superadmin
                }
            })
            
        return redirect(url_for('main.index'))

    return render_template('signup.html')

@auth.route('/user')
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': str(current_user.id),
                'email': current_user.email,
                'role': current_user.role,
                'is_admin': current_user.is_admin,
                'is_superadmin': current_user.is_superadmin
            }
        })
    return jsonify({'authenticated': False}), 200

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    if request.is_json:
        return jsonify({'success': True}), 200
    return redirect(url_for('auth.login'))
