#!/usr/bin/env python
"""
Fix CSRF Protection Script
-------------------------
This script disables CSRF protection temporarily to help diagnose login issues.
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

def disable_csrf_protection():
    """Temporarily disable CSRF protection in app.py"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if CSRF protection is being set up
        csrf_match = re.search(r'from flask_wtf\.csrf import CSRFProtect', content)
        
        if csrf_match:
            # Comment out the CSRF protection
            new_content = content.replace('from flask_wtf.csrf import CSRFProtect', '# from flask_wtf.csrf import CSRFProtect')
            
            # Also comment out the csrf initialization
            csrf_init_match = re.search(r'csrf = CSRFProtect\(.*?\)', content)
            if csrf_init_match:
                new_content = new_content.replace(csrf_init_match.group(0), '# ' + csrf_init_match.group(0))
            
            with open('app.py', 'w') as f:
                f.write(new_content)
            
            print_status("Disabled CSRF protection in app.py", "OK")
        else:
            # Check if there's any import of flask_wtf
            import_match = re.search(r'from flask_wtf', content)
            
            if import_match:
                # Probably importing something else from flask_wtf, disable that too
                new_content = content.replace(import_match.group(0), '# ' + import_match.group(0))
                
                with open('app.py', 'w') as f:
                    f.write(new_content)
                
                print_status("Disabled Flask-WTF imports in app.py", "OK")
            else:
                print_status("Could not find CSRF protection initialization in app.py", "INFO")
                
                # Check security_enhancements.py for CSRF setup
                if os.path.exists('security_enhancements.py'):
                    disable_csrf_in_security_module()
    except Exception as e:
        print_status("Failed to disable CSRF protection: " + str(e), "ERROR")

def disable_csrf_in_security_module():
    """Disable CSRF protection in security_enhancements.py"""
    try:
        with open('security_enhancements.py', 'r') as f:
            content = f.read()
        
        # Check if CSRF protection is being set up
        csrf_match = re.search(r'from flask_wtf\.csrf import CSRFProtect', content)
        
        if csrf_match:
            # Comment out the CSRF protection
            new_content = content.replace('from flask_wtf.csrf import CSRFProtect', '# from flask_wtf.csrf import CSRFProtect')
            
            # Also comment out the csrf initialization
            csrf_init_match = re.search(r'csrf = CSRFProtect\(.*?\)', content)
            if csrf_init_match:
                new_content = new_content.replace(csrf_init_match.group(0), '# ' + csrf_init_match.group(0))
            
            with open('security_enhancements.py', 'w') as f:
                f.write(new_content)
            
            print_status("Disabled CSRF protection in security_enhancements.py", "OK")
        else:
            print_status("Could not find CSRF protection in security_enhancements.py", "INFO")
            
            # Check for setup_csrf_protection function
            setup_match = re.search(r'def setup_csrf_protection\(.*?\):(.*?)(?=\n\ndef|\Z)', content, re.DOTALL)
            
            if setup_match:
                # Modify the function to return None
                setup_func = setup_match.group(0)
                modified_func = re.sub(r'return csrf', 'print("CSRF disabled for troubleshooting")\n    return None', setup_func)
                
                new_content = content.replace(setup_func, modified_func)
                
                with open('security_enhancements.py', 'w') as f:
                    f.write(new_content)
                
                print_status("Modified CSRF setup function in security_enhancements.py", "OK")
    except Exception as e:
        print_status("Failed to disable CSRF in security module: " + str(e), "ERROR")

def update_login_template():
    """Update login.html template to make CSRF token optional"""
    template_path = os.path.join('templates', 'login.html')
    
    if not os.path.exists(template_path):
        print_status("login.html template not found", "ERROR")
        return
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Make the CSRF token conditional
        csrf_match = re.search(r'<input type="hidden" name="csrf_token" value="\{\{ csrf_token\(\) \}\}">', content)
        
        if csrf_match:
            new_content = content.replace(
                csrf_match.group(0),
                '{% if csrf_token %}<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">{% endif %}'
            )
            
            with open(template_path, 'w') as f:
                f.write(new_content)
            
            print_status("Updated login.html to make CSRF token optional", "OK")
        else:
            print_status("Could not find CSRF token in login.html", "INFO")
    except Exception as e:
        print_status("Failed to update login template: " + str(e), "ERROR")

def create_simple_login_route():
    """Create a very simple login route without CSRF protection"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if simple login route already exists
        if '@app.route("/simple_login"' in content:
            print_status("Simple login route already exists in app.py", "INFO")
            return
        
        # Find the end of the routes section
        last_route_end = 0
        for route_match in re.finditer(r'@app\.route\(.*?\)\ndef (\w+)\(.*?\):(.*?)(?=\n@|\n\n|$)', content, re.DOTALL):
            route_end = route_match.end()
            if route_end > last_route_end:
                last_route_end = route_end
        
        if last_route_end > 0:
            # Create a simple login route
            simple_route = """

@app.route("/simple_login", methods=["GET", "POST"])
def simple_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
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
        <title>Simple Login</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container">
        <h1 class="mt-4">Simple Login</h1>
        
        <form method="POST" action="/simple_login">
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
    </body>
    </html>
    '''
"""
            
            new_content = content[:last_route_end] + simple_route + content[last_route_end:]
            
            with open('app.py', 'w') as f:
                f.write(new_content)
            
            print_status("Added simple login route at /simple_login", "OK")
        else:
            print_status("Could not find a good location to add the simple login route", "ERROR")
    except Exception as e:
        print_status("Failed to add simple login route: " + str(e), "ERROR")

def main():
    """Main function to fix CSRF issues"""
    print(Colors.HEADER + Colors.BOLD + "CSRF Troubleshooting Utility" + Colors.ENDC)
    print("="*50)
    
    # Disable CSRF protection
    print("\n" + Colors.BOLD + "Disabling CSRF Protection" + Colors.ENDC)
    disable_csrf_protection()
    
    # Update login template
    print("\n" + Colors.BOLD + "Updating Login Template" + Colors.ENDC)
    update_login_template()
    
    # Create simple login route
    print("\n" + Colors.BOLD + "Creating Simple Login Route" + Colors.ENDC)
    create_simple_login_route()
    
    print("\n" + "="*50)
    print(Colors.BOLD + "CSRF Fixes Applied!" + Colors.ENDC)
    print("\nNext steps:")
    print("1. Restart your Flask application:")
    print("   python app.py")
    print("2. Try logging in at the simplified route (no CSRF protection):")
    print("   http://localhost:5000/simple_login")
    print("3. If simple login works, the issue is likely related to CSRF protection")

if __name__ == "__main__":
    main()
