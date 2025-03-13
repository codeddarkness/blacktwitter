#!/usr/bin/env python
"""
Template Extractor Script
-------------------------
This script extracts template content from app_integration.txt and 
creates the necessary template files for the Twitter clone application.
"""

import os
import re
import shutil

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_status(message, status=None):
    """Print status messages with color-coding"""
    if status == "OK":
        print(Colors.GREEN + "[OK]" + Colors.ENDC + " " + message)
    elif status == "WARNING":
        print(Colors.YELLOW + "[WARNING]" + Colors.ENDC + " " + message)
    elif status == "ERROR":
        print(Colors.RED + "[ERROR]" + Colors.ENDC + " " + message)
    elif status == "INFO":
        print(Colors.BLUE + "[INFO]" + Colors.ENDC + " " + message)
    else:
        print(message)

def create_template(html_content, filename):
    """Create a template file with the given content"""
    templates_dir = os.path.join(os.getcwd(), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    file_path = os.path.join(templates_dir, filename)
    
    try:
        with open(file_path, 'w') as f:
            f.write(html_content)
        print_status("Created template file: {0}".format(filename), "OK")
        return True
    except Exception as e:
        print_status("Failed to create {0}: {1}".format(filename, str(e)), "ERROR")
        return False

def copy_template(src, dest):
    """Copy a template file from src to dest"""
    try:
        shutil.copy2(src, dest)
        print_status("Copied template from {0} to {1}".format(src, dest), "OK")
        return True
    except Exception as e:
        print_status("Failed to copy from {0} to {1}: {2}".format(src, dest, str(e)), "ERROR")
        return False

def main():
    """Main function to extract template files"""
    print(Colors.HEADER + Colors.BOLD + "Template Extractor" + Colors.ENDC)
    print("="*50)
    
    # List of required templates
    required_templates = [
        'profile.html',
        'edit_profile.html',
        'view_tweet.html',
        'notifications.html',
        'reset_request.html',
        'reset_token.html',
        'verify_2fa.html',
        'security_settings.html'
    ]
    
    # Templates that can be created from existing template files
    template_mappings = {
        'feed_template.html': 'feed.html',
        'api_docs_template.html': 'api_docs.html',
        'hashtag_template.html': 'hashtag.html',
        'search_template.html': 'search.html',
        'setup_2fa_template.html': 'setup_2fa.html',
        'trending_template.html': 'trending.html'
    }
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.getcwd(), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Copy existing template files
    for src, dest in template_mappings.items():
        if os.path.exists(src):
            dest_path = os.path.join(templates_dir, dest)
            if not os.path.exists(dest_path):
                copy_template(src, dest_path)
    
    # Create missing templates manually
    profile_html = """<!DOCTYPE html>
<html>
<head>
    <title>User Profile</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('home') }}">Twitter Clone</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('home') }}">Home</a>
                    </li>
                </ul>
                <div class="navbar-nav">
                    {% if current_user.is_authenticated %}
                        <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                    {% else %}
                        <a class="nav-link" href="{{ url_for('login') }}">Login</a>
                        <a class="nav-link" href="{{ url_for('register') }}">Register</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <div class="card-body text-center">
                    <img src="{{ url_for('static', filename='profile_pics/' + user.profile_picture) }}" class="rounded-circle img-fluid mb-3" style="max-width: 150px;">
                    <h3>{{ user.username }}</h3>
                    {% if user.bio %}
                        <p>{{ user.bio }}</p>
                    {% endif %}
                    
                    {% if current_user.is_authenticated and current_user.id != user.id %}
                        {% if current_user.is_following(user) %}
                            <form action="{{ url_for('follow_system.unfollow', username=user.username) }}" method="POST" class="d-inline">
                                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                                <button type="submit" class="btn btn-outline-danger">Unfollow</button>
                            </form>
                        {% else %}
                            <form action="{{ url_for('follow_system.follow', username=user.username) }}" method="POST" class="d-inline">
                                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                                <button type="submit" class="btn btn-primary">Follow</button>
                            </form>
                        {% endif %}
                    {% elif current_user.is_authenticated and current_user.id == user.id %}
                        <a href="{{ url_for('user_profiles.edit_profile') }}" class="btn btn-outline-primary">Edit Profile</a>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="col-md-8">
            <h3>{{ user.username }}'s Tweets</h3>
            {% for tweet in tweets %}
                <div class="card mt-3">
                    <div class="card-body">
                        <p class="card-text">{{ tweet.content }}</p>
                        <small class="text-muted">{{ tweet.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</small>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>"""

    edit_profile_html = """<!DOCTYPE html>
<html>
<head>
    <title>Edit Profile</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('home') }}">Twitter Clone</a>
        </div>
    </nav>

    <h1 class="mt-4">Edit Profile</h1>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="card">
        <div class="card-body">
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                
                <div class="mb-3">
                    <label for="bio" class="form-label">Bio</label>
                    <textarea class="form-control" id="bio" name="bio" rows="3">{{ current_user.bio }}</textarea>
                </div>
                
                <div class="mb-3">
                    <label for="profile_picture" class="form-label">Profile Picture</label>
                    <input class="form-control" type="file" id="profile_picture" name="profile_picture" accept="image/*">
                </div>
                
                <button type="submit" class="btn btn-primary">Save Changes</button>
                <a href="{{ url_for('user_profiles.profile', username=current_user.username) }}" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
    </div>
</body>
</html>"""

    view_tweet_html = """<!DOCTYPE html>
<html>
<head>
    <title>View Tweet</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('home') }}">Twitter Clone</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('home') }}">Home</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <!-- Original Tweet -->
    <div class="card mb-4">
        <div class="card-body">
            <div class="d-flex justify-content-between">
                <h5 class="card-title">
                    <a href="{{ url_for('user_profiles.profile', username=tweet.user.username) }}">
                        {{ tweet.user.username }}
                    </a>
                </h5>
                <small class="text-muted">{{ tweet.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</small>
            </div>
            <p class="card-text">{{ tweet.content }}</p>
        </div>
    </div>

    <!-- Reply Form -->
    {% if current_user.is_authenticated %}
        <div class="card mb-4">
            <div class="card-body">
                <h5 class="card-title">Reply to this tweet</h5>
                <form action="{{ url_for('tweet_interactions.reply_to_tweet', tweet_id=tweet.id) }}" method="POST">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                    <textarea name="content" class="form-control" rows="3" placeholder="Write your reply..." required></textarea>
                    <button type="submit" class="btn btn-primary mt-2">Reply</button>
                </form>
            </div>
        </div>
    {% else %}
        <div class="alert alert-info">
            <a href="{{ url_for('login') }}">Login</a> to reply to this tweet.
        </div>
    {% endif %}

    <!-- Replies -->
    <h3>Replies</h3>
    {% if replies %}
        {% for reply in replies %}
            <div class="card mt-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h5 class="card-title">
                            <a href="{{ url_for('user_profiles.profile', username=reply.user.username) }}">
                                {{ reply.user.username }}
                            </a>
                        </h5>
                        <small class="text-muted">{{ reply.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</small>
                    </div>
                    <p class="card-text">{{ reply.content }}</p>
                </div>
            </div>
        {% endfor %}
    {% else %}
        <p>No replies yet.</p>
    {% endif %}
</body>
</html>"""

    notifications_html = """<!DOCTYPE html>
<html>
<head>
    <title>Notifications</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('home') }}">Twitter Clone</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('home') }}">Home</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <h1 class="mt-4">Notifications</h1>
    
    <div class="list-group">
        {% for notification in notifications.items %}
            <div class="list-group-item">
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">
                        <a href="{{ url_for('user_profiles.profile', username=notification.sender.username) }}">{{ notification.sender.username }}</a>
                        {% if notification.type == 'like' %}
                            liked your tweet
                        {% elif notification.type == 'follow' %}
                            followed you
                        {% elif notification.type == 'reply' %}
                            replied to your tweet
                        {% elif notification.type == 'retweet' %}
                            retweeted your tweet
                        {% elif notification.type == 'mention' %}
                            mentioned you in a tweet
                        {% endif %}
                    </h5>
                    <small>{{ notification.timestamp.strftime('%Y-%m-%d %H:%M') }}</small>
                </div>
                {% if notification.tweet %}
                    <p class="mb-1">
                        <a href="{{ url_for('tweet_interactions.view_tweet', tweet_id=notification.tweet.id) }}">
                            {{ notification.tweet.content[:100] }}{% if notification.tweet.content|length > 100 %}...{% endif %}
                        </a>
                    </p>
                {% endif %}
            </div>
        {% endfor %}
    </div>
</body>
</html>"""

    reset_request_html = """<!DOCTYPE html>
<html>
<head>
    <title>Reset Password</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container">
    <h1 class="mt-4">Reset Password</h1>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="card">
        <div class="card-body">
            <p>Enter your email address to receive a password reset link.</p>
            <form method="POST">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <button type="submit" class="btn btn-primary">Request Password Reset</button>
            </form>
            <p class="mt-3"><a href="{{ url_for('login') }}">Return to login</a></p>
        </div>
    </div>
</body>
</html>"""

    reset_token_html = """<!DOCTYPE html>
<html>
<head>
    <title>Reset Password - New Password</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container">
    <h1 class="mt-4">Reset Your Password</h1>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="card">
        <div class="card-body">
            <form method="POST">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <div class="mb-3">
                    <label for="password" class="form-label">New Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <div class="mb-3">
                    <label for="confirm_password" class="form-label">Confirm New Password</label>
                    <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                </div>
                <button type="submit" class="btn btn-primary">Reset Password</button>
            </form>
        </div>
    </div>
</body>
</html>"""

    verify_2fa_html = """<!DOCTYPE html>
<html>
<head>
    <title>Verify Two-Factor Authentication</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container">
    <div class="row justify-content-center">
        <div class="col-md-6 mt-5">
            <div class="card">
                <div class="card-header">
                    <h5>Two-Factor Authentication</h5>
                </div>
                <div class="card-body">
                    <h3 class="mb-4 text-center">Verification Required</h3>
                    
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <p>Please enter the verification code from your authenticator app.</p>
                    
                    <form method="POST">
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                        <div class="mb-3">
                            <label for="token" class="form-label">Verification Code</label>
                            <input type="text" class="form-control" id="token" name="token" placeholder="Enter 6-digit code" required autocomplete="off">
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Verify</button>
                        </div>
                    </form>
                    
                    <div class="mt-3 text-center">
                        <a href="{{ url_for('logout') }}" class="btn btn-link">Cancel and return to login</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

    security_settings_html = """<!DOCTYPE html>
<html>
<head>
    <title>Security Settings</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('home') }}">Twitter Clone</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('home') }}">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('user_profiles.profile', username=current_user.username) }}">My Profile</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <h1 class="mt-4">Security Settings</h1>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="row">
        <div class="col-md-6">
            <div class="card mb-4">
                <div class="card-header">
                    <h5>Change Password</h5>
                </div>
                <div class="card-body">
                    <form action="{{ url_for('security.change_password') }}" method="POST">
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                        <div class="mb-3">
                            <label for="current_password" class="form-label">Current Password</label>
                            <input type="password" class="form-control" id="current_password" name="current_password" required>
                        </div>
                        <div class="mb-3">
                            <label for="new_password" class="form-label">New Password</label>
                            <input type="password" class="form-control" id="new_password" name="new_password" required>
                        </div>
                        <div class="mb-3">
                            <label for="confirm_password" class="form-label">Confirm New Password</label>
                            <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Change Password</button>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            {% if hasattr(current_user, 'two_factor_enabled') %}
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Two-Factor Authentication</h5>
                    </div>
                    <div class="card-body">
                        {% if current_user.two_factor_enabled %}
                            <p class="alert alert-success">Two-factor authentication is enabled.</p>
                            <form action="{{ url_for('security.disable_2fa') }}" method="POST">
                                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                                <div class="mb-3">
                                    <label for="password" class="form-label">Enter Password to Disable</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-danger">Disable Two-Factor Authentication</button>
                            </form>
                        {% else %}
                            <p>Two-factor authentication adds an extra layer of security to your account.</p>
                            <a href="{{ url_for('security.setup_2fa') }}" class="btn btn-primary">Set Up Two-Factor Authentication</a>
                        {% endif %}
                    </div>
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>"""

    # Create all the missing templates
    templates = {
        'profile.html': profile_html,
        'edit_profile.html': edit_profile_html,
        'view_tweet.html': view_tweet_html,
        'notifications.html': notifications_html,
        'reset_request.html': reset_request_html,
        'reset_token.html': reset_token_html,
        'verify_2fa.html': verify_2fa_html,
        'security_settings.html': security_settings_html
    }
    
    for filename, content in templates.items():
        if filename in required_templates:
            create_template(content, filename)
    
    # Extract templates from app_integration.txt if it exists
    if os.path.exists('app_integration.txt'):
        try:
            with open('app_integration.txt', 'r') as f:
                content = f.read()
            
            # Find login.html and register.html templates
            login_match = re.search(r'```html\s*<!DOCTYPE html>.*?<title>Login</title>.*?```', content, re.DOTALL)
            register_match = re.search(r'```html\s*<!DOCTYPE html>.*?<title>Register</title>.*?```', content, re.DOTALL)
            
            if login_match:
                login_html = login_match.group(0).replace('```html', '').replace('```', '').strip()
                create_template(login_html, 'login.html')
            
            if register_match:
                register_html = register_match.group(0).replace('```html', '').replace('```', '').strip()
                create_template(register_html, 'register.html')
            
        except Exception as e:
            print_status("Error extracting templates from app_integration.txt: {0}".format(str(e)), "ERROR")
    
    # Print summary
    print("\n" + "="*50)
    print(Colors.BOLD + "Template Creation Complete!" + Colors.ENDC)
    print("\nNext steps:")
    print("1. Run the sanity check script again to verify templates:")
    print("   python sanity_check.py")
    print("2. Start your Twitter clone application:")
    print("   python app.py")

if __name__ == "__main__":
    main()
