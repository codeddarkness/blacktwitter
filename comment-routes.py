from flask import Blueprint, redirect, url_for, flash, session, request
from models.comment import Comment

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/comment/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    """Create a new comment on a post"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    content = request.form['content']
    
    if content:
        Comment.create(post_id, session['user_id'], content)
        flash('Comment added successfully')
    
    return redirect(url_for('post.view_post', post_id=post_id))
