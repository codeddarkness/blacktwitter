from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import query_db

class User:
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        return query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        return query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    
    @staticmethod
    def create(username, password, is_admin=0):
        """Create a new user"""
        hashed_password = generate_password_hash(password)
        query_db(
            'INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)',
            [username, hashed_password, datetime.now(), is_admin]
        )
    
    @staticmethod
    def verify_password(username, password):
        """Verify user password"""
        user = User.get_by_username(username)
        if user and check_password_hash(user['password'], password):
            return user
        return None
    
    @staticmethod
    def get_all():
        """Get all users"""
        return query_db('SELECT * FROM users ORDER BY joined_date DESC')
