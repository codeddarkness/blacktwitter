from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.verify_password(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash('Login successful')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username exists
        user_exists = User.get_by_username(username)
        
        if user_exists:
            flash('Username already exists')
        else:
            User.create(username, password)
            flash('Registration successful, please login')
            return redirect(url_for('auth.login'))
    
    return render_template('register.html')
