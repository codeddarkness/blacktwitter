from flask import Blueprint, render_template, redirect, url_for, session
from models.user import User
from models.post import Post

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    """View user profile"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.get_by_id(session['user_id'])
    posts = Post.get_by_user(session['user_id'])
    
    return render_template('profile.html', user=user, posts=posts)
