from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import query_db
import os

# Set legacy provider for OpenSSL 3.x
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

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
        try:
            # Use simpler hashing method compatible with OpenSSL 3.x
            hashed_password = generate_password_hash(password, method='sha256')
            query_db(
                'INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)',
                [username, hashed_password, datetime.now(), is_admin]
            )
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    @staticmethod
    def verify_password(username, password):
        """Verify user password"""
        try:
            user = User.get_by_username(username)
            if user and check_password_hash(user['password'], password):
                return user
            return None
        except ValueError as e:
            # Handle OpenSSL 3.x issues
            print(f"OpenSSL error: {e}")
            print("This is likely due to legacy hash algorithms being disabled in OpenSSL 3.x")
            print("Please run the application with OPENSSL_LEGACY_PROVIDER=1 environment variable")
            return None
        except Exception as e:
            print(f"Error verifying password: {e}")
            return None
    
    @staticmethod
    def get_all():
        """Get all users"""
        return query_db('SELECT * FROM users ORDER BY joined_date DESC')
