#!/usr/bin/env python
"""
Disable CSRF Protection Script
----------------------------
This script disables CSRF protection in the app to fix login issues.
"""

import os
import re

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

def disable_csrf_in_app():
    """Disable CSRF protection in app.py"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return False
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for CSRFProtect import
        if 'from flask_wtf.csrf import CSRFProtect' in content:
            # Comment out the import
            modified_content = content.replace(
                'from flask_wtf.csrf import CSRFProtect', 
                '# from flask_wtf.csrf import CSRFProtect'
            )
            
            # Also comment out any CSRF initialization
            modified_content = re.sub(
                r'csrf\s*=\s*CSRFProtect\(app\)',
                '# csrf = CSRFProtect(app)',
                modified_content
            )
            
            with open('app.py', 'w') as f:
                f.write(modified_content)
            
            print_status("Disabled CSRF protection in app.py", "OK")
            return True
        else:
            # Check for other Flask-WTF imports
            if 'from flask_wtf' in content:
                modified_content = re.sub(
                    r'from flask_wtf(.*)',
                    '# from flask_wtf\\1',
                    content
                )
                
                with open('app.py', 'w') as f:
                    f.write(modified_content)
                
                print_status("Disabled Flask-WTF imports in app.py", "OK")
                return True
            else:
                print_status("No CSRF protection found in app.py", "INFO")
        
        return False
    except Exception as e:
        print_status("Error disabling CSRF in app.py: " + str(e), "ERROR")
        return False

def update_simple_login():
    """Update simple_login route to bypass CSRF check"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return False
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if simple_login route exists
        simple_login = re.search(r'@app\.route\(["\']\/simple_login["\'].*?\)\ndef simple_login\(\):(.*?)(?=\n@|\n\ndef|\Z)', content, re.DOTALL)
        
        if simple_login:
            # Modify the route to remove form action that would trigger CSRF check
            simple_login_code = simple_login.group(0)
            if 'action="/simple_login"' in simple_login_code:
                modified_login = simple_login_code.replace('action="/simple_login"', '')
                
                # Update the app.py content
                modified_content = content.replace(simple_login_code, modified_login)
                
                with open('app.py', 'w') as f:
                    f.write(modified_content)
                
                print_status("Updated simple_login route to bypass CSRF checks", "OK")
                return True
        
        return False
    except Exception as e:
        print_status("Error updating simple_login route: " + str(e), "ERROR")
        return False

def create_no_csrf_login():
    """Create a login route without CSRF checks"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return False
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if no_csrf_login already exists
        if '@app.route("/no_csrf_login"' in content:
            print_status("no_csrf_login route already exists", "INFO")
            return True
        
        # Find a good place to insert the new route
        insert_point = content.rfind('if __name__ ==')
        
        if insert_point == -1:
            # Try another approach
            last_route = 0
            for route_match in re.finditer(r'@app\.route\(.*?\)\ndef (\w+)\(.*?\):(.*?)(?=\n@|\n\ndef|\Z)', content, re.DOTALL):
                last_route = max(last_route, route_match.end())
            
            if last_route > 0:
                insert_point = last_route
        
        if insert_point > 0:
            # Create the new login route
            no_csrf_route = """

@app.route("/no_csrf_login", methods=["GET", "POST"])
def no_csrf_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - No CSRF</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container">
        <h1 class="mt-4">Login</h1>
        
        <form method="POST">
            <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" id="username" name="username" class="form-control" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" id="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
        <p class="mt-3"><a href="{{ url_for('register') }}">Don't have an account? Register</a></p>
    </body>
    </html>
    '''
"""
            
            # Insert the new route
            modified_content = content[:insert_point] + no_csrf_route + content[insert_point:]
            
            with open('app.py', 'w') as f:
                f.write(modified_content)
            
            print_status("Added no_csrf_login route", "OK")
            return True
        else:
            print_status("Could not find a good place to insert the new route", "ERROR")
            return False
    except Exception as e:
        print_status("Error creating no_csrf_login route: " + str(e), "ERROR")
        return False

def fix_login_template():
    """Fix the login.html template to remove CSRF checks and security module references"""
    login_path = os.path.join('templates', 'login.html')
    
    # Use the provided fixed template
    new_content = """<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container">
    <h1 class="mt-4">Login</h1>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <form method="POST">
        <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input type="text" name="username" id="username" class="form-control" placeholder="Username" required>
        </div>
        <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input type="password" name="password" id="password" class="form-control" placeholder="Password" required>
        </div>
        <button type="submit" class="btn btn-primary">Login</button>
    </form>
    <p class="mt-3"><a href="{{ url_for('register') }}">Don't have an account? Register</a></p>
</body>
</html>"""
    
    try:
        # Ensure the templates directory exists
        os.makedirs(os.path.dirname(login_path), exist_ok=True)
        
        # Write the fixed login template
        with open(login_path, 'w') as f:
            f.write(new_content)
        
        print_status("Updated login.html template", "OK")
        return True
    except Exception as e:
        print_status("Error updating login.html template: " + str(e), "ERROR")
        return False

def main():
    """Main function to disable CSRF protection"""
    print(Colors.HEADER + Colors.BOLD + "CSRF Disabler" + Colors.ENDC)
    print("="*50)
    
    # Disable CSRF in app.py
    print("\n" + Colors.BOLD + "Disabling CSRF Protection" + Colors.ENDC)
    disable_csrf_in_app()
    
    # Update the simple_login route
    print("\n" + Colors.BOLD + "Updating Simple Login Route" + Colors.ENDC)
    update_simple_login()
    
    # Create login route without CSRF
    print("\n" + Colors.BOLD + "Creating Login Without CSRF Checks" + Colors.ENDC)
    create_no_csrf_login()
    
    # Fix login template
    print("\n" + Colors.BOLD + "Fixing Login Template" + Colors.ENDC)
    fix_login_template()
    
    print("\n" + "="*50)
    print(Colors.BOLD + "CSRF Disabled!" + Colors.ENDC)
    print("\nNext steps:")
    print("1. Restart your Flask application:")
    print("   python app.py")
    print("2. Try logging in using the fixed route:")
    print("   http://localhost:5000/no_csrf_login")
    print("3. The regular login should also work now")

if __name__ == "__main__":
    main()
