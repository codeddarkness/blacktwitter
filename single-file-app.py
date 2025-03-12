#!/usr/bin/env python3

"""
BlackTwitter - Single File Version

This is a simplified, single-file version of the BlackTwitter application.
It combines all the functionality into one file to avoid import issues.
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# Set OpenSSL environment variables for compatibility with OpenSSL 3.x
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

# Application setup
app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'blacktwitter.db'

# Database helper functions
def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
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

def init_db():
    """Initialize the database with tables and the admin user"""
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

# User model functions
def get_user_by_id(user_id):
    """Get user by ID"""
    return query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)

def get_user_by_username(username):
    """Get user by username"""
    return query_db('SELECT * FROM users WHERE username = ?', [username], one=True)

def create_user(username, password, is_admin=0):
    """Create a new user"""
    try:
        # Use SHA-256 hashing method (compatible with OpenSSL 3.x)
        hashed_password = generate_password_hash(password, method='sha256')
        query_db(
            'INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)',
            [username, hashed_password, datetime.now(), is_admin]
        )
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def verify_password(username, password):
    """Verify user password"""
    try:
        user = get_user_by_username(username)
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

def get_all_users():
    """Get all users"""
    return query_db('SELECT * FROM users ORDER BY joined_date DESC')

# Post model functions
def get_all_posts():
    """Get all posts with user info"""
    return query_db('''
    SELECT p.id, p.content, p.post_date, u.username
    FROM posts p
    JOIN users u ON p.user_id = u.id
    ORDER BY p.post_date DESC
    ''')

def get_post_by_id(post_id):
    """Get post by ID with user info"""
    return query_db('''
    SELECT p.id, p.content, p.post_date, u.username
    FROM posts p
    JOIN users u ON p.user_id = u.id
    WHERE p.id = ?
    ''', [post_id], one=True)

def get_posts_by_user(user_id):
    """Get posts by user ID"""
    return query_db('''
    SELECT p.id, p.content, p.post_date
    FROM posts p
    WHERE p.user_id = ?
    ORDER BY p.post_date DESC
    ''', [user_id])

def create_post(user_id, content):
    """Create a new post"""
    query_db(
        'INSERT INTO posts (user_id, content, post_date) VALUES (?, ?, ?)',
        [user_id, content, datetime.now()]
    )

# Comment model functions
def get_comments_by_post(post_id):
    """Get comments for a post with user info"""
    return query_db('''
    SELECT c.id, c.content, c.comment_date, u.username
    FROM comments c
    JOIN users u ON c.user_id = u.id
    WHERE c.post_id = ?
    ORDER BY c.comment_date
    ''', [post_id])

def create_comment(post_id, user_id, content):
    """Create a new comment"""
    query_db(
        'INSERT INTO comments (post_id, user_id, content, comment_date) VALUES (?, ?, ?, ?)',
        [post_id, user_id, content, datetime.now()]
    )

# Initialize the database
init_db()

# Routes
@app.route('/')
def index():
    """Main page with post timeline"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    posts = get_all_posts()
    
    return render_template('blacktwitter.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = verify_password(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash('Login successful')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username exists
        user_exists = get_user_by_username(username)
        
        if user_exists:
            flash('Username already exists')
        else:
            if create_user(username, password):
                flash('Registration successful, please login')
                return redirect(url_for('login'))
            else:
                flash('Error creating user')
    
    return render_template('register.html')

@app.route('/post', methods=['POST'])
def create_post_route():
    """Create a new post"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    content = request.form['content']
    
    if content:
        create_post(session['user_id'], content)
        flash('Post created successfully')
    
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """View a single post with comments"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    post = get_post_by_id(post_id)
    if not post:
        flash('Post not found')
        return redirect(url_for('index'))
    
    comments = get_comments_by_post(post_id)
    
    return render_template('post.html', post=post, comments=comments)

@app.route('/comment/<int:post_id>', methods=['POST'])
def create_comment_route(post_id):
    """Create a new comment on a post"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    content = request.form['content']
    
    if content:
        create_comment(post_id, session['user_id'], content)
        flash('Comment added successfully')
    
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/profile')
def profile():
    """View user profile"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    posts = get_posts_by_user(session['user_id'])
    
    return render_template('profile.html', user=user, posts=posts)

@app.route('/admin')
def admin_panel():
    """Admin panel for user management"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    users = get_all_users()
    
    return render_template('admin.html', users=users)

# Check if templates exist
def ensure_templates_exist():
    """Make sure template files exist"""
    template_dir = 'templates'
    
    # Create template directory if it doesn't exist
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # Check for each template file
    templates = [
        'blacktwitter.html',
        'login.html',
        'register.html',
        'post.html',
        'profile.html',
        'admin.html'
    ]
    
    for template in templates:
        template_path = os.path.join(template_dir, template)
        if not os.path.exists(template_path):
            print(f"Warning: Template {template} not found.")

# Entry point
if __name__ == '__main__':
    ensure_templates_exist()
    app.run(debug=True, host='0.0.0.0', port=5000)
