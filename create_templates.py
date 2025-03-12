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
