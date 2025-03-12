from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('blacktwitter.log'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
app.secret_key = os.urandom(24)
app.config['DATABASE'] = 'blacktwitter.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Custom error handler for bad requests
@app.errorhandler(400)
def bad_request(e):
    logger.warning(f"Bad request: {request.remote_addr} - {request.method} {request.url}")
    return render_template('error.html', 
                           error_code=400, 
                           error_message="Bad Request. Please check your request."), 400

# Custom error handler for SSL/TLS connection attempts
@app.before_request
def handle_ssl_connection():
    # Log and handle potential SSL connection attempts
    if request.environ.get('wsgi.url_scheme') != 'http':
        logger.info(f"SSL/TLS connection attempt from {request.remote_addr}")
        # You might want to redirect to HTTPS if you have SSL configured
        # return redirect(request.url.replace('http://', 'https://'), code=301)

# Database helper functions
def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    """Execute query and fetch results"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        conn.commit()
        return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

# Initialize database
def init_db():
    """Initialize the database with tables and the admin user"""
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
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
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        conn.close()

# Ensure the templates directory exists
def ensure_templates():
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Templates dictionary
    templates = {
        'index.html': '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>BlackTwitter</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    line-height: 1.6;
                }
                .navbar { 
                    display: flex; 
                    justify-content: space-between; 
                    margin-bottom: 20px; 
                    padding: 10px; 
                    background-color: #f4f4f4;
                }
                .flash-messages { 
                    background-color: #f0f0f0; 
                    padding: 10px; 
                    margin-bottom: 15px; 
                }
            </style>
        </head>
        <body>
            <div class="navbar">
                <h1>BlackTwitter</h1>
                {% if session.username %}
                    <div>
                        Welcome, {{ session.username }} | 
                        <a href="{{ url_for('logout') }}">Logout</a>
                    </div>
                {% else %}
                    <a href="{{ url_for('login') }}">Login</a>
                {% endif %}
            </div>

            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="flash-messages">
                        {% for message in messages %}
                            <p>{{ message }}</p>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}

            <h2>Welcome to BlackTwitter</h2>
            {% if session.username %}
                <p>You are logged in!</p>
                {% if session.is_admin %}
                    <p>You have admin privileges.</p>
                {% endif %}
            {% else %}
                <p>Please <a href="{{ url_for('login') }}">login</a> to continue.</p>
            {% endif %}
        </body>
        </html>
        ''',
        'login.html': '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Login - BlackTwitter</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 300px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    display: flex; 
                    flex-direction: column; 
                    align-items: center;
                }
                form { 
                    width: 100%; 
                    display: flex; 
                    flex-direction: column; 
                }
                input, button { 
                    margin: 10px 0; 
                    padding: 10px; 
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                button {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
                .flash-messages {
                    color: red;
                    margin-bottom: 15px;
                }
            </style>
        </head>
        <body>
            <h1>Login to BlackTwitter</h1>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="flash-messages">
                        {% for message in messages %}
                            <p>{{ message }}</p>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p><small>Default admin credentials: username: admin, password: btadmin</small></p>
        </body>
        </html>
        ''',
        'error.html': '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Error - BlackTwitter</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    text-align: center;
                }
                .error-container {
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 20px;
                    border-radius: 5px;
                    margin-top: 50px;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>Error {{ error_code }}</h1>
                <p>{{ error_message }}</p>
                <a href="{{ url_for('index') }}">Return to Home</a>
            </div>
        </body>
        </html>
        '''
    }
    
    for name, content in templates.items():
        path = os.path.join('templates', name)
        if not os.path.exists(path):
            try:
                with open(path, 'w') as f:
                    f.write(content)
                logger.info(f"Created template: {name}")
            except IOError as e:
                logger.error(f"Error creating template {name}: {e}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            # Query the user
            user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['is_admin']
                
                logger.info(f"Successful login for user: {username}")
                flash('Login successful')
                return redirect(url_for('index'))
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                flash('Invalid username or password')
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('An error occurred during login')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out')
    return redirect(url_for('login'))

# Ensure templates and database are set up
init_db()
ensure_templates()

# For development
if __name__ == '__main__':
    # Improved logging for startup
    logger.info("Starting BlackTwitter application")
    
    try:
        # Allow both localhost and all network interfaces
        app.run(
            debug=True, 
            host='0.0.0.0', 
            port=8000, 
            threaded=True
        )
    except Exception as e:
        logger.critical(f"Application startup failed: {e}")
        raise
