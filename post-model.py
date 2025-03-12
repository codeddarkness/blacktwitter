from datetime import datetime
from models import query_db

class Post:
    @staticmethod
    def get_all():
        """Get all posts with user info"""
        return query_db('''
        SELECT p.id, p.content, p.post_date, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.post_date DESC
        ''')
    
    @staticmethod
    def get_by_id(post_id):
        """Get post by ID with user info"""
        return query_db('''
        SELECT p.id, p.content, p.post_date, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
        ''', [post_id], one=True)
    
    @staticmethod
    def get_by_user(user_id):
        """Get posts by user ID"""
        return query_db('''
        SELECT p.id, p.content, p.post_date
        FROM posts p
        WHERE p.user_id = ?
        ORDER BY p.post_date DESC
        ''', [user_id])
    
    @staticmethod
    def create(user_id, content):
        """Create a new post"""
        query_db(
            'INSERT INTO posts (user_id, content, post_date) VALUES (?, ?, ?)',
            [user_id, content, datetime.now()]
        )
