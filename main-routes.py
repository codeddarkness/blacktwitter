from flask import Blueprint, render_template, redirect, url_for, session
from models.post import Post

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main page with post timeline"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    posts = Post.get_all()
    
    return render_template('blacktwitter.html', posts=posts)
