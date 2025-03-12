from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'blacktwitter.db'

# Initialize database
def init_db():
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
        hashed_password = generate_password_hash('btadmin')
        c.execute("INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)",
                 ('admin', hashed_password, datetime.now(), 1))
    
    conn.commit()
    conn.close()

# Database helper functions
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# Initialize the database
init_db()

# Routes
@app.route('/')
def index():
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
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username exists
        user_exists = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        
        if user_exists:
            flash('Username already exists')
        else:
            hashed_password = generate_password_hash(password)
            query_db('INSERT INTO users (username, password, joined_date) VALUES (?, ?, ?)',
                    [username, hashed_password, datetime.now()])
            flash('Registration successful, please login')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    content = request.form['content']
    
    if content:
        query_db('INSERT INTO posts (user_id, content, post_date) VALUES (?, ?, ?)',
                [session['user_id'], content, datetime.now()])
        flash('Post created successfully')
    
    return redirect(url_for('index'))

@app.route('/comment/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    content = request.form['content']
    
    if content:
        query_db('INSERT INTO comments (post_id, user_id, content, comment_date) VALUES (?, ?, ?, ?)',
                [post_id, session['user_id'], content, datetime.now()])
        flash('Comment added successfully')
    
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def view_post(post_id):
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

@app.route('/profile')
def profile():
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
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    users = query_db('SELECT * FROM users ORDER BY joined_date DESC')
    
    return render_template('admin.html', users=users)

# Create HTML templates
create_templates()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# Create the HTML templates
def create_templates():
    # Create template directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    # blacktwitter.html (main page)
    with open('templates/blacktwitter.html', 'w') as f:
        f.write('''
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
            <a href="{{ url_for('logout') }}">Logout</a></a>
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
            <form action="{{ url_for('create_post') }}" method="post">
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
''')

    # login.html
    with open('templates/login.html', 'w') as f:
        f.write('''
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
''')

    # register.html
    with open('templates/register.html', 'w') as f:
        f.write('''
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
''')

    # post.html
    with open('templates/post.html', 'w') as f:
        f.write('''
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
            <form action="{{ url_for('create_comment', post_id=post.id) }}" method="post">
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
''')

    # admin.html
    with open('templates/admin.html', 'w') as f:
        f.write('''
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
''')
    with open('templates/profile.html', 'w') as f:
        f.write('''
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
            <a href="{{ url_for('logout') }}">Logout