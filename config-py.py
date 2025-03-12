import os

class Config:
    # Application configuration
    DEBUG = True
    SECRET_KEY = os.urandom(24)
    
    # Database configuration
    DATABASE = 'blacktwitter.db'
    DATABASE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), DATABASE)
    
    # Admin credentials
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'btadmin'
