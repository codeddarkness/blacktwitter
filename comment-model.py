from datetime import datetime
from models import query_db

class Comment:
    @staticmethod
    def get_by_post(post_id):
        """Get comments for a post with user info"""
        return query_db('''
        SELECT c.id, c.content, c.comment_date, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.comment_date
        ''', [post_id])
    
    @staticmethod
    def create(post_id, user_id, content):
        """Create a new comment"""
        query_db(
            'INSERT INTO comments (post_id, user_id, content, comment_date) VALUES (?, ?, ?, ?)',
            [post_id, user_id, content, datetime.now()]
        )
