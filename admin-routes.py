from flask import Blueprint, render_template, redirect, url_for, flash, session
from models.user import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_panel():
    """Admin panel for user management"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access')
        return redirect(url_for('main.index'))
    
    users = User.get_all()
    
    return render_template('admin.html', users=users)
