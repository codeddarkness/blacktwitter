from flask import Flask
import os
from config import Config
from create_db import init_db

# Import all routes
from routes.auth import auth_bp
from routes.post import post_bp
from routes.comment import comment_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from routes.main import main_bp

# Create Flask application instance
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(post_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)

# Create template directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create static directories
if not os.path.exists('static/css'):
    os.makedirs('static/css')
if not os.path.exists('static/js'):
    os.makedirs('static/js')

# Create CSS file
with open('static/css/style.css', 'w') as f:
    f.write('''
/* Global styles */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f8fa;
}
.navbar {
    background-color: #1da1f2;
    color: white;
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.navbar h1 {
    margin: 0;
    font-size: 1.5rem;
}
.navbar-links a {
    color: white;
    text-decoration: none;
    margin-left: 15px;
}
.container {
    max-width: 600px;
    margin: 20px auto;
    padding: 0 15px;
}
.flash-messages {
    margin-bottom: 20px;
}
.flash-message {
    padding: 10px;
    background-color: #4caf50;
    color: white;
    border-radius: 5px;
    margin-bottom: 10px;
}
/* Add more styles as needed */
''')

# Create JavaScript file
with open('static/js/main.js', 'w') as f:
    f.write('''
// Main JavaScript file for BlackTwitter
document.addEventListener('DOMContentLoaded', function() {
    // Any JavaScript functionality can be added here
    console.log('BlackTwitter initialized');
});
''')
