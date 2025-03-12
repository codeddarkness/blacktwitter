from flask import Flask, render_template, session, redirect, url_for
import os
import sqlite3
from datetime import datetime

# Set environment variables for OpenSSL 3.x compatibility
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

# Create Flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DEBUG'] = True

# Database configuration
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

# Initialize database
def init_db():
    """Initialize the database with tables and the admin user"""
    from werkzeug.security import generate_password_hash
    
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

# Import blueprints
try:
    from routes.auth import auth_bp
    from routes.post import post_bp
    from routes.comment import comment_bp
    from routes.profile import profile_bp
    from routes.admin import admin_bp
    from routes.main import main_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    
    USING_BLUEPRINTS = True
except ImportError:
    print("Could not import blueprints, using inline routes")
    USING_BLUEPRINTS = False

# Initialize the database
init_db()

# If not using blueprints, define routes directly in this file
if not USING_BLUEPRINTS:
    from flask import request, flash
    from werkzeug.security import generate_password_hash, check_password_hash
    
    @app.route('/')
    def index():
        """Main page with post timeline"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        posts = query_db('''
        SELECT p.id, p.content, p.post_date, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.post_date DESC
        ''')
        
        return render_template('blacktwitter.html', posts=posts)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login"""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
            
            if user and check_password_hash(user['password'], password):
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
            user_exists = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
            
            if user_exists:
                flash('Username already exists')
            else:
                hashed_password = generate_password_hash(password, method='sha256')
                query_db('INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)',
                        [username, hashed_password, datetime.now(), 0])
                flash('Registration successful, please login')
                return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/post', methods=['POST'])
    def create_post_route():
        """Create a new post"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        content = request.form['content']
        
        if content:
            query_db('INSERT INTO posts (user_id, content, post_date) VALUES (?, ?, ?)',
                    [session['user_id'], content, datetime.now()])
            flash('Post created successfully')
        
        return redirect(url_for('index'))

    @app.route('/post/<int:post_id>')
    def view_post(post_id):
        """View a single post with comments"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        post = query_db('''
        SELECT p.id, p.content, p.post_date, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
        ''', [post_id], one=True)
        
        comments = query_db('''
        SELECT c.id, c.content, c.comment_date, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.comment_date
        ''', [post_id])
        
        return render_template('post.html', post=post, comments=comments)

    @app.route('/comment/<int:post_id>', methods=['POST'])
    def create_comment_route(post_id):
        """Create a new comment on a post"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        content = request.form['content']
        
        if content:
            query_db('INSERT INTO comments (post_id, user_id, content, comment_date) VALUES (?, ?, ?, ?)',
                    [post_id, session['user_id'], content, datetime.now()])
            flash('Comment added successfully')
        
        return redirect(url_for('view_post', post_id=post_id))

    @app.route('/profile')
    def profile():
        """View user profile"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = query_db('SELECT * FROM users WHERE id = ?', [session['user_id']], one=True)
        
        posts = query_db('''
        SELECT p.id, p.content, p.post_date
        FROM posts p
        WHERE p.user_id = ?
        ORDER BY p.post_date DESC
        ''', [session['user_id']])
        
        return render_template('profile.html', user=user, posts=posts)

    @app.route('/admin')
    def admin_panel():
        """Admin panel for user management"""
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Unauthorized access')
            return redirect(url_for('index'))
        
        users = query_db('SELECT * FROM users ORDER BY joined_date DESC')
        
        return render_template('admin.html', users=users)

# Update run.py file to properly import the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
