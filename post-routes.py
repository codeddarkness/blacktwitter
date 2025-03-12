from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.post import Post
from models.comment import Comment

post_bp = Blueprint('post', __name__)

@post_bp.route('/post', methods=['POST'])
def create_post():
    """Create a new post"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    content = request.form['content']
    
    if content:
        Post.create(session['user_id'], content)
        flash('Post created successfully')
    
    return redirect(url_for('main.index'))

@post_bp.route('/post/<int:post_id>')
def view_post(post_id):
    """View a single post with comments"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found')
        return redirect(url_for('main.index'))
    
    comments = Comment.get_by_post(post_id)
    
    return render_template('post.html', post=post, comments=comments)
