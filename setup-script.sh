#!/bin/bash

# BlackTwitter Application Setup and Fix Script
# This comprehensive script handles setup, fixes common issues, and prepares
# the application for running

# Set text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Port configuration - ports to try in order of preference
PORT_OPTIONS=(5000 8000 8080 8888 8899)

# Default options
SELECTED_PORT=""
FIX_OPENSSL=1
RESET_ADMIN=0
BACKUP_FILES=1

# Print header
echo -e "${CYAN}=== BlackTwitter Application Setup and Fix ===${NC}"
echo "This script will set up and fix the BlackTwitter application."

# Check current directory structure
echo -e "${YELLOW}Analyzing current directory structure...${NC}"

# Determine application structure (modular or flat)
if [ -d "routes" ] && [ -d "models" ]; then
    APP_STRUCTURE="modular"
    echo -e "${GREEN}Detected modular application structure.${NC}"
elif [ -f "blacktwitter.py" ] && ! [ -d "routes" ]; then
    APP_STRUCTURE="single-file"
    echo -e "${GREEN}Detected single-file application structure.${NC}"
else
    echo -e "${YELLOW}Uncertain application structure. Will attempt to fix anyway.${NC}"
    APP_STRUCTURE="unknown"
fi

# Check for OpenSSL version
echo -e "${YELLOW}Checking OpenSSL version...${NC}"
if command -v openssl &>/dev/null; then
    OPENSSL_VERSION=$(openssl version)
    echo -e "OpenSSL version: ${CYAN}$OPENSSL_VERSION${NC}"
    
    # Detect if it's OpenSSL 3.x
    if [[ "$OPENSSL_VERSION" == *"OpenSSL 3."* ]]; then
        echo -e "${YELLOW}OpenSSL 3.x detected. Will apply hash compatibility fixes.${NC}"
        FIX_OPENSSL=1
    fi
else
    echo -e "${YELLOW}OpenSSL command not found. Assuming OpenSSL 3.x compatibility is needed.${NC}"
    FIX_OPENSSL=1
fi

# Check Python version
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}Python 3 found: $PYTHON_VERSION${NC}"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}Python not found. Please install Python 3.${NC}"
    exit 1
fi

# Check for pip
echo -e "${YELLOW}Checking pip installation...${NC}"
if command -v pip3 &>/dev/null; then
    PIP_CMD="pip3"
    echo -e "${GREEN}pip3 found.${NC}"
elif command -v pip &>/dev/null; then
    PIP_CMD="pip"
    echo -e "${GREEN}pip found.${NC}"
else
    echo -e "${RED}pip not found. Please install pip.${NC}"
    exit 1
fi

# Install required packages
echo -e "${YELLOW}Installing required packages...${NC}"
$PIP_CMD install flask werkzeug

# Create empty __init__.py files in key directories if needed
for dir in routes models templates; do
    # Create directory if it doesn't exist
    if [ ! -d "$dir" ]; then
        echo -e "${YELLOW}Creating $dir directory...${NC}"
        mkdir -p "$dir"
    fi
    
    # Create __init__.py file if it doesn't exist
    if [ ! -f "$dir/__init__.py" ]; then
        echo -e "${YELLOW}Creating $dir/__init__.py${NC}"
        touch "$dir/__init__.py"
    fi
done

# Create models/__init__.py with database helper functions
echo -e "${YELLOW}Updating models/__init__.py with database helpers...${NC}"
cat > "models/__init__.py" << 'EOF'
import sqlite3

def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect('blacktwitter.db')
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    """Execute query and fetch results"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv
EOF
echo -e "${GREEN}Database helpers added to models/__init__.py${NC}"

# Add OpenSSL fix to user model
if [ "$FIX_OPENSSL" = "1" ]; then
    echo -e "${YELLOW}Applying OpenSSL 3.x compatibility fix to user model...${NC}"
    
    # Backup existing model if it exists
    if [ -f "models/user.py" ] && [ "$BACKUP_FILES" = "1" ]; then
        echo -e "${YELLOW}Backing up existing user model...${NC}"
        cp "models/user.py" "models/user.py.bak"
        echo -e "${GREEN}Backup created at models/user.py.bak${NC}"
    fi
    
    # Create fixed user model
    cat > "models/user.py" << 'EOF'
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
            return None
        except Exception as e:
            print(f"Error verifying password: {e}")
            return None
    
    @staticmethod
    def get_all():
        """Get all users"""
        return query_db('SELECT * FROM users ORDER BY joined_date DESC')
EOF
    echo -e "${GREEN}Fixed user model created at models/user.py${NC}"
fi

# Create static directories if they don't exist
if [ ! -d "static/css" ]; then
    echo -e "${YELLOW}Creating static/css directory...${NC}"
    mkdir -p "static/css"
fi

if [ ! -d "static/js" ]; then
    echo -e "${YELLOW}Creating static/js directory...${NC}"
    mkdir -p "static/js"
fi

# Find an available port
echo -e "${YELLOW}Checking for available ports...${NC}"
check_port() {
    local port=$1
    if command -v nc &>/dev/null; then
        nc -z localhost $port &>/dev/null
        if [ $? -eq 0 ]; then
            return 0  # Port is in use
        else
            return 1  # Port is available
        fi
    elif command -v lsof &>/dev/null; then
        lsof -i:$port &>/dev/null
        if [ $? -eq 0 ]; then
            return 0  # Port is in use
        else
            return 1  # Port is available
        fi
    else
        # Fallback method
        (echo > /dev/tcp/localhost/$port) 2>/dev/null
        if [ $? -eq 0 ]; then
            return 0  # Port is in use
        else
            return 1  # Port is available
        fi
    fi
}

for port in "${PORT_OPTIONS[@]}"; do
    if ! check_port $port; then
        echo -e "${GREEN}Port $port is available.${NC}"
        SELECTED_PORT=$port
        break
    else
        echo -e "${YELLOW}Port $port is already in use.${NC}"
    fi
done

if [ -z "$SELECTED_PORT" ]; then
    echo -e "${RED}No available ports found. Using default port 5000.${NC}"
    SELECTED_PORT=5000
fi

# Create run.py if it doesn't exist or update it
if [ -f "run.py" ]; then
    echo -e "${YELLOW}Updating run.py with port $SELECTED_PORT...${NC}"
    if [ "$BACKUP_FILES" = "1" ]; then
        cp run.py run.py.bak
    fi
else
    echo -e "${YELLOW}Creating run.py with port $SELECTED_PORT...${NC}"
fi

if [ "$APP_STRUCTURE" = "modular" ]; then
    cat > run.py << EOF
import os
from flask import Flask
from config import Config
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for OpenSSL 3.x compatibility
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

# Import blueprints
from routes.auth import auth_bp
from routes.post import post_bp
from routes.comment import comment_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from routes.main import main_bp

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DEBUG'] = True

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(post_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)

# Initialize database
from create_db import init_db
init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=$SELECTED_PORT)
EOF
else
    # For single-file app
    cat > run.py << EOF
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for OpenSSL 3.x compatibility
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

from blacktwitter import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=$SELECTED_PORT)
EOF
fi

echo -e "${GREEN}Created/updated run.py to use port $SELECTED_PORT${NC}"

# Create config.py if it doesn't exist
if [ ! -f "config.py" ]; then
    echo -e "${YELLOW}Creating config.py...${NC}"
    cat > config.py << 'EOF'
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
EOF
    echo -e "${GREEN}Created config.py${NC}"
fi

# Create create_db.py if it doesn't exist
if [ ! -f "create_db.py" ]; then
    echo -e "${YELLOW}Creating create_db.py...${NC}"
    cat > create_db.py << 'EOF'
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

# Set environment variables for OpenSSL 3.x compatibility
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

def init_db():
    """Initialize the database with tables and the admin user"""
    DATABASE = 'blacktwitter.db'
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        joined_date TIMESTAMP NOT NULL,
        is_admin BOOLEAN NOT NULL DEFAULT 0
    )
    ''')
    
    # Create posts table
    c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        post_date TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create comments table
    c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        comment_date TIMESTAMP NOT NULL,
        FOREIGN KEY (post_id) REFERENCES posts (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Check if admin user exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_exists = c.fetchone()
    
    # Create admin user if not exists
    if not admin_exists:
        hashed_password = generate_password_hash('btadmin', method='sha256')
        c.execute("INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)",
                 ('admin', hashed_password, datetime.now(), 1))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
EOF
    echo -e "${GREEN}Created create_db.py${NC}"
fi

# Create convenient launch script
echo -e "${YELLOW}Creating launch script...${NC}"
cat > launch_blacktwitter.sh << 'EOF'
#!/bin/bash
# Script to run the BlackTwitter application

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set OpenSSL environment variables for older hash compatibility
export OPENSSL_CONF=/dev/null
export OPENSSL_LEGACY_PROVIDER=1

echo -e "${CYAN}=== Starting BlackTwitter Application ===${NC}"

# Set PYTHONPATH to include current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate || source venv/Scripts/activate
elif [ -d "env" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source env/bin/activate || source env/Scripts/activate
fi

# Initialize database if it doesn't exist
if [ ! -f "blacktwitter.db" ]; then
    echo -e "${YELLOW}Initializing database...${NC}"
    if [ -f "create_db.py" ]; then
        python create_db.py
    else
        echo -e "${RED}Warning: create_db.py not found. Database may not be initialized.${NC}"
    fi
fi

# Run the application
echo -e "${GREEN}Starting application...${NC}"
python run.py

# Deactivate virtual environment on exit
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
EOF
chmod +x launch_blacktwitter.sh
echo -e "${GREEN}Created launch_blacktwitter.sh${NC}"

# Ask user if they want to reset admin password
echo -e "${YELLOW}Do you want to reset the admin password? (y/n): ${NC}"
read -p "" reset_admin

if [[ $reset_admin == "y" || $reset_admin == "Y" ]]; then
    # Create reset_password script
    echo -e "${YELLOW}Creating admin password reset script...${NC}"
    cat > reset_admin.py << 'EOF'
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

# Set environment variables for OpenSSL 3.x compatibility
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

# Connect to database - try different possible locations
db_paths = ['blacktwitter.db', 'app/blacktwitter.db', 'instance/blacktwitter.db']
conn = None

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Found database at {db_path}")
        conn = sqlite3.connect(db_path)
        break

if conn is None:
    print("Could not find database. Creating new one at blacktwitter.db")
    conn = sqlite3.connect('blacktwitter.db')

c = conn.cursor()

# Check if users table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if not c.fetchone():
    print("Creating users table...")
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        joined_date TIMESTAMP NOT NULL,
        is_admin BOOLEAN NOT NULL DEFAULT 0
    )
    ''')

# Generate new password hash with sha256 method
new_password_hash = generate_password_hash('btadmin', method='sha256')

# Check if admin user exists
c.execute("SELECT * FROM users WHERE username = 'admin'")
if c.fetchone():
    # Update admin password
    c.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_password_hash,))
    print("Admin password has been reset to 'btadmin' with SHA-256 hashing.")
else:
    # Create admin user
    c.execute("INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)",
             ('admin', new_password_hash, datetime.now(), 1))
    print("Admin user created with password 'btadmin' using SHA-256 hashing.")

conn.commit()
conn.close()
EOF

    # Run the reset script
    echo -e "${YELLOW}Resetting admin password...${NC}"
    $PYTHON_CMD reset_admin.py
    echo -e "${GREEN}Admin password reset complete. Use 'admin' / 'btadmin' to login.${NC}"
fi

# Create templates if they don't exist
if [ ! -f "templates/blacktwitter.html" ] || [ ! -f "templates/login.html" ]; then
    echo -e "${YELLOW}Creating template generation script...${NC}"
    cat > create_templates.py << 'EOF'
import os

def create_templates():
    """Create HTML templates for the application if they don't exist"""
    # Create template directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    templates = {
        'blacktwitter.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlackTwitter</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
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
        .post-form {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .post-form textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #e1e8ed;
            border-radius: 5px;
            resize: none;
            margin-bottom: 10px;
        }
        .post-form button {
            background-color: #1da1f2;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
        }
        .post {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .post-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .post-user {
            font-weight: bold;
            margin-right: 10px;
        }
        .post-date {
            color: #657786;
            font-size: 0.9rem;
        }
        .post-content {
            margin-bottom: 15px;
        }
        .post-actions {
            display: flex;
            justify-content: space-between;
            color: #657786;
        }
        .post-actions a {
            color: #657786;
            text-decoration: none;
        }
        .post-actions a:hover {
            color: #1da1f2;
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
    </style>
</head>
<body>
    <div class="navbar">
        <h1>BlackTwitter</h1>
        <div class="navbar-links">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('profile') }}">Profile</a>
            {% if session.is_admin %}
            <a href="{{ url_for('admin_panel') }}">Admin</a>
            {% endif %}
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    
    <div class="container">
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <div class="flash-messages">
            {% for message in messages %}
            <div class="flash-message">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        {% endwith %}
        
        <div class="post-form">
            <form action="{{ url_for('create_post_route') }}" method="post">
                <textarea name="content" rows="3" placeholder="What's happening?"></textarea>
                <button type="submit">Post</button>
            </form>
        </div>
        
        {% for post in posts %}
        <div class="post">
            <div class="post-header">
                <div class="post-user">{{ post.username }}</div>
                <div class="post-date">{{ post.post_date }}</div>
            </div>
            <div class="post-content">
                {{ post.content }}
            </div>
            <div class="post-actions">
                <a href="{{ url_for('view_post', post_id=post.id) }}"><i class="far fa-comment"></i> Comment</a>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
''',
        'login.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - BlackTwitter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f8fa;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .login-container {
            background-color: white;
            border-radius: 5px;
            padding: 30px;
            width: 350px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .login-header {
            text-align: center;
            margin-bottom: 20px;
        }
        .login-header h1 {
            color: #1da1f2;
            margin: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 8px;
            border: 1px solid #e1e8ed;
            border-radius: 5px;
        }
        .form-actions {
            margin-top: 20px;
        }
        .form-actions button {
            background-color: #1da1f2;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
        }
        .form-links {
            margin-top: 15px;
            text-align: center;
        }
        .form-links a {
            color: #1da1f2;
            text-decoration: none;
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 10px;
            background-color: #f44336;
            color: white;
            border-radius: 5px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <div class="flash-messages">
            {% for message in messages %}
            <div class="flash-message">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        {% endwith %}
        
        <div class="login-header">
            <h1>BlackTwitter</h1>
            <p>Log in to BlackTwitter</p>
        </div>
        
        <form action="{{ url_for('login') }}" method="post">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div class="form-actions">
                <button type="submit">Log in</button>
            </div>
            
            <div class="form-links">
                <a href="{{ url_for('register') }}">Don't have an account? Sign up</a>
            </div>
        </form>
    </div>
</body>
</html>
''',
        'register.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - BlackTwitter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f8fa;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .register-container {
            background-color: white;
            border-radius: 5px;
            padding: 30px;
            width: 350px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .register-header {
            text-align: center;
            margin-bottom: 20px;
        }
        .register-header h1 {
            color: #1da1f2;
            margin: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 8px;
            border: 1px solid #e1e8ed;
            border-radius: 5px;
        }
        .form-actions {
            margin-top: 20px;
        }
        .form-actions button {
            background-color: #1da1f2;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
        }
        .form-links {
            margin-top: 15px;
            text-align: center;
        }
        .form-links a {
            color: #1da1f2;
            text-decoration: none;
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 10px;
            background-color: #f44336;
            color: white;
            border-radius: 5px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="register-container">
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <div class="flash-messages">
            {% for message in messages %}
            <div class="flash-message">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        {% endwith %}

        <div class="register-header">
            <h1>BlackTwitter</h1>
            <p>Create your account</p>
        </div>

        <form action="{{ url_for('register') }}" method="post">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>

            <div class="form-actions">
                <button type="submit">Sign up</button>
            </div>

            <div class="form-links">
                <a href="{{ url_for('login') }}">Already have an account? Log in</a>
            </div>
        </form>
    </div>
</body>
</html>
''',
        'post.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post - BlackTwitter</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
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
        .post {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .post-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .post-user {
            font-weight: bold;
            margin-right: 10px;
        }
        .post-date {
            color: #657786;
            font-size: 0.9rem;
        }
        .post-content {
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        .comment-form {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .comment-form textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #e1e8ed;
            border-radius: 5px;
            resize: none;
            margin-bottom: 10px;
        }
        .comment-form button {
            background-color: #1da1f2;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
        }
        .comments-section {
            margin-top: 20px;
        }
        .comment {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .comment-header {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .comment-user {
            font-weight: bold;
            margin-right: 10px;
        }
        .comment-date {
            color: #657786;
            font-size: 0.9rem;
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
        .back-link {
            margin-bottom: 20px;
            display: block;
        }
        .back-link a {
            color: #1da1f2;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>BlackTwitter</h1>
        <div class="navbar-links">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('profile') }}">Profile</a>
            {% if session.is_admin %}
            <a href="{{ url_for('admin_panel') }}">Admin</a>
            {% endif %}
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>

    <div class="container">
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <div class="flash-messages">
            {% for message in messages %}
            <div class="flash-message">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        {% endwith %}

        <div class="back-link">
            <a href="{{ url_for('index') }}"><i class="fas fa-arrow-left"></i> Back to timeline</a>
        </div>

        <div class="post">
            <div class="post-header">
                <div class="post-user">{{ post.username }}</div>
                <div class="post-date">{{ post.post_date }}</div>
            </div>
            <div class="post-content">
                {{ post.content }}
            </div>
        </div>

        <div class="comment-form">
            <form action="{{ url_for('create_comment_route', post_id=post.id) }}" method="post">
                <textarea name="content" rows="2" placeholder="Add a comment..."></textarea>
                <button type="submit">Comment</button>
            </form>
        </div>

        <div class="comments-section">
            <h3>Comments</h3>

            {% if comments %}
                {% for comment in comments %}
                <div class="comment">
                    <div class="comment-header">
                        <div class="comment-user">{{ comment.username }}</div>
                        <div class="comment-date">{{ comment.comment_date }}</div>
                    </div>
                    <div class="comment-content">
                        {{ comment.content }}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p>No comments yet.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
''',
        'profile.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile - BlackTwitter</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
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
        .profile-header {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .profile-username {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .profile-joined {
            color: #657786;
            font-size: 0.9rem;
        }
        .profile-stats {
            display: flex;
            margin-top: 15px;
        }
        .stat {
            margin-right: 20px;
        }
        .stat-value {
            font-weight: bold;
        }
        .post {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .post-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .post-user {
            font-weight: bold;
            margin-right: 10px;
        }
        .post-date {
            color: #657786;
            font-size: 0.9rem;
        }
        .post-content {
            margin-bottom: 15px;
        }
        .post-actions {
            display: flex;
            justify-content: space-between;
            color: #657786;
        }
        .post-actions a {
            color: #657786;
            text-decoration: none;
        }
        .post-actions a:hover {
            color: #1da1f2;
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #14171a;
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
    </style>
</head>
<body>
    <div class="navbar">
        <h1>BlackTwitter</h1>
        <div class="navbar-links">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('profile') }}">Profile</a>
            {% if session.is_admin %}
            <a href="{{ url_for('admin_panel') }}">Admin</a>
            {% endif %}
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>

    <div class="container">
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <div class="flash-messages">
            {% for message in messages %}
            <div class="flash-message">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        {% endwith %}

        <div class="profile-header">
            <div class="profile-username">{{ user.username }}</div>
            <div class="profile-joined">Joined: {{ user.joined_date }}</div>
            <div class="profile-stats">
                <div class="stat">
                    <div class="stat-label">Posts</div>
                    <div class="stat-value">{{ posts|length }}</div>
                </div>
            </div>
        </div>

        <div class="section-title">Your Posts</div>

        {% if posts %}
            {% for post in posts %}
            <div class="post">
                <div class="post-header">
                    <div class="post-user">{{ session.username }}</div>
                    <div class="post-date">{{ post.post_date }}</div>
                </div>
                <div class="post-content">
                    {{ post.content }}
                </div>
                <div class="post-actions">
                    <a href="{{ url_for('view_post', post_id=post.id) }}"><i class="far fa-comment"></i> View Comments</a>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <p>You haven't posted anything yet.</p>
        {% endif %}
    </div>
</body>
</html>
''',
        'admin.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - BlackTwitter</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
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
            max-width: 800px;
            margin: 20px auto;
            padding: 0 15px;
        }
        .admin-header {
            margin-bottom: 20px;
        }
        .admin-header h2 {
            color: #14171a;
        }
        .admin-panel {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .admin-section {
            margin-bottom: 30px;
        }
        .admin-section-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #14171a;
            border-bottom: 1px solid #e1e8ed;
            padding-bottom: 10px;
        }
        .user-table {
            width: 100%;
            border-collapse: collapse;
        }
        .user-table th, .user-table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e1e8ed;
        }
        .user-table th {
            background-color: #f5f8fa;
            font-weight: bold;
        }
        .user-table tr:hover {
            background-color: #f5f8fa;
        }
        .admin-badge {
            display: inline-block;
            background-color: #1da1f2;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8rem;
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
    </style>
</head>
<body>
    <div class="navbar">
        <h1>BlackTwitter</h1>
        <div class="navbar-links">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('profile') }}">Profile</a>
            <a href="{{ url_for('admin_panel') }}">Admin</a>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>

    <div class="container">
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <div class="flash-messages">
            {% for message in messages %}
            <div class="flash-message">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        {% endwith %}

        <div class="admin-header">
            <h2>Admin Panel</h2>
            <p>Welcome, {{ session.username }}. Here you can manage users and monitor platform activity.</p>
        </div>

        <div class="admin-panel">
            <div class="admin-section">
                <div class="admin-section-title">User Management</div>

                <table class="user-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Joined Date</th>
                            <th>Role</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td>{{ user.id }}</td>
                            <td>{{ user.username }}</td>
                            <td>{{ user.joined_date }}</td>
                            <td>
                                {% if user.is_admin %}
                                <span class="admin-badge">Admin</span>
                                {% else %}
                                User
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
'''
    }

    # Create each template if it doesn't exist
    for template_name, template_content in templates.items():
        template_path = os.path.join('templates', template_name)
        if not os.path.exists(template_path):
            print(f"Creating template: {template_name}")
            with open(template_path, 'w') as f:
                f.write(template_content)
        else:
            print(f"Template already exists: {template_name}")

if __name__ == "__main__":
    create_templates()
EOF

    echo -e "${YELLOW}Creating templates...${NC}"
    $PYTHON_CMD create_templates.py
    echo -e "${GREEN}Templates created successfully.${NC}"
fi

# Create default CSS file if it doesn't exist
if [ ! -f "static/css/style.css" ]; then
    echo -e "${YELLOW}Creating default CSS...${NC}"
    mkdir -p static/css

    cat > static/css/style.css << 'EOF'
/* Global styles for BlackTwitter */
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
EOF
    echo -e "${GREEN}Default CSS created.${NC}"
fi

# Create default JS file if it doesn't exist
if [ ! -f "static/js/main.js" ]; then
    echo -e "${YELLOW}Creating default JavaScript...${NC}"
    mkdir -p static/js

    cat > static/js/main.js << 'EOF'
// BlackTwitter main JavaScript file
document.addEventListener("DOMContentLoaded", function() {
    console.log("BlackTwitter app initialized");

    // Add any JavaScript functionality here
});
EOF
    echo -e "${GREEN}Default JavaScript created.${NC}"
fi

echo -e "${CYAN}=== Setup Complete ===${NC}"
echo -e "To run the application:"
echo -e "1. ${YELLOW}chmod +x launch_blacktwitter.sh${NC}"
echo -e "2. ${YELLOW}./launch_blacktwitter.sh${NC}"
echo -e "Access the application at: ${CYAN}http://localhost:$SELECTED_PORT${NC}"
echo -e "Initial admin credentials: ${CYAN}Username: admin / Password: btadmin${NC}"

echo -e "\n${CYAN}=== Troubleshooting Tips ===${NC}"
echo -e "If you encounter login issues:"
echo -e "1. Run the application using the launch script: ${YELLOW}./launch_blacktwitter.sh${NC}"
echo -e "2. To reset the admin password: ${YELLOW}python reset_admin.py${NC}"
echo -e "3. If you get OpenSSL errors, run with: ${YELLOW}OPENSSL_CONF=/dev/null OPENSSL_LEGACY_PROVIDER=1 python run.py${NC}"
echo -e "4. For import errors, ensure PYTHONPATH includes the current directory: ${YELLOW}export PYTHONPATH=\$PYTHONPATH:\$(pwd)${NC}"

echo -e "\n${GREEN}Good luck with your BlackTwitter application!${NC}"
