#!/usr/bin/env python
"""
Debug Login Issues Script
------------------------
This script helps identify and fix login-related issues in the Twitter clone.
"""

import os
import sys
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

def check_login_route():
    """Check the login route in app.py"""
    if not os.path.exists('app.py'):
        print_status("app.py not found!", "ERROR")
        return False
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check for login route
    login_route = re.search(r'@app\.route\([\'"]\/login[\'"].*?\)\ndef login\(\):(.*?)return render_template', 
                           content, re.DOTALL)
    
    if not login_route:
        print_status("Could not find login route in app.py", "ERROR")
        return False
    
    # Check for common issues in login route
    login_code = login_route.group(1)
    
    issues = []
    fixes = []
    
    # Check for potential missing CSRF token
    if 'csrf_token' not in login_code and 'csrf_token' in content:
        issues.append("Login route might be missing CSRF token handling")
        fixes.append("Add CSRF token handling to login form")
        
    # Check if the login route calls security module's 2FA verification
    if 'security' in content and 'verify_2fa' in content and 'verify_2fa' not in login_code:
        issues.append("Login route might not handle 2FA correctly")
        fixes.append("Update login route to redirect to 2FA verification when needed")
    
    # Check if modules initialized correctly before being used
    if 'init_modules()' in content:
        init_position = content.find('init_modules()')
        login_position = content.find('@app.route("/login"')
        
        app_context_pattern = r'with app\.app_context\(\):\s*db\.create_all\(\)\s*init_modules\(\)'
        if re.search(app_context_pattern, content) and login_position < init_position:
            issues.append("Login route might be called before modules are initialized")
            fixes.append("Move 'init_modules()' call before the route definitions")
    
    # Check security_enhancements module integration
    security_module_issues = check_security_module_integration()
    issues.extend(security_module_issues[0])
    fixes.extend(security_module_issues[1])
    
    if issues:
        print_status("Found potential issues in login route:", "WARNING")
        for i, issue in enumerate(issues):
            print_status("Issue {0}: {1}".format(i+1, issue), "WARNING")
            print_status("  Fix: {0}".format(fixes[i]), "INFO")
        
        if confirm("Would you like to attempt to fix these issues? (y/n): "):
            fix_login_issues(issues, fixes)
    else:
        print_status("Login route looks good!", "OK")
    
    return True

def check_security_module_integration():
    """Check security_enhancements module integration"""
    issues = []
    fixes = []
    
    if not os.path.exists('security_enhancements.py'):
        issues.append("security_enhancements.py not found")
        fixes.append("Ensure security_enhancements.py is in the project directory")
        return issues, fixes
    
    # Check if security module has login_with_2fa function
    with open('security_enhancements.py', 'r') as f:
        security_content = f.read()
    
    if 'login_with_2fa' in security_content and 'app.view_functions[\'login\'] = login_with_2fa' in security_content:
        # This is likely causing the issue - security module is trying to replace login function
        # but it's done incorrectly
        issues.append("Security module tries to replace login function but might be doing it incorrectly")
        fixes.append("Update security_enhancements.py to properly replace the login function")
        
        # Check if verify_2fa route is present
        if 'verify_2fa' in security_content and '@security.route(\'/verify_2fa\'' in security_content:
            # The route exists but might not be registered
            if 'app.register_blueprint(security)' not in security_content:
                issues.append("Security blueprint may not be registered correctly")
                fixes.append("Ensure 'app.register_blueprint(security)' is called in init_security")
    
    # Check templates for login.html
    if not os.path.exists(os.path.join('templates', 'login.html')):
        issues.append("login.html template is missing")
        fixes.append("Create login.html template in the templates directory")
    else:
        with open(os.path.join('templates', 'login.html'), 'r') as f:
            login_template = f.read()
        
        if 'csrf_token' in login_template and '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">' not in login_template:
            issues.append("CSRF token usage in login.html might be incorrect")
            fixes.append("Add proper CSRF token input field to login.html")
    
    return issues, fixes

def fix_login_issues(issues, fixes):
    """Fix identified login issues"""
    # Fix missing CSRF token in login.html
    if "login.html template is missing" in issues:
        create_login_template()
    elif "CSRF token usage in login.html might be incorrect" in issues:
        fix_csrf_in_login_template()
    
    # Fix security module issues
    if "Security module tries to replace login function but might be doing it incorrectly" in issues:
        fix_security_module()
    
    # Fix module initialization
    if "Login route might be called before modules are initialized" in issues:
        fix_module_initialization()
    
    print_status("Applied fixes. Please restart your Flask application and try logging in again.", "INFO")
    
def create_login_template():
    """Create a basic login.html template"""
    template_dir = os.path.join(os.getcwd(), 'templates')
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    login_html = """<!DOCTYPE html>
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
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        <input type="text" name="username" class="form-control" placeholder="Username" required>
        <input type="password" name="password" class="form-control mt-2" placeholder="Password" required>
        <button type="submit" class="btn btn-primary mt-2">Login</button>
    </form>
    <p class="mt-3"><a href="{{ url_for('register') }}">Don't have an account? Register</a></p>
    <p><a href="{{ url_for('security.reset_request') }}">Forgot password?</a></p>
</body>
</html>"""
    
    try:
        with open(os.path.join(template_dir, 'login.html'), 'w') as f:
            f.write(login_html)
        print_status("Created login.html template", "OK")
    except Exception as e:
        print_status("Failed to create login.html: {0}".format(str(e)), "ERROR")

def fix_csrf_in_login_template():
    """Fix CSRF token in login.html template"""
    template_path = os.path.join(os.getcwd(), 'templates', 'login.html')
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check if form tag exists
        form_start = content.find('<form')
        form_end = content.find('</form>', form_start)
        
        if form_start >= 0 and form_end >= 0:
            form_content = content[form_start:form_end]
            
            # Check if CSRF token exists but is incorrectly formatted
            if 'csrf_token' in form_content and '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">' not in form_content:
                # Add correct CSRF token input
                new_form_content = form_content.replace('<form', '<form\n        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">', 1)
                new_content = content[:form_start] + new_form_content + content[form_end:]
                
                with open(template_path, 'w') as f:
                    f.write(new_content)
                print_status("Fixed CSRF token in login.html", "OK")
            else:
                # Add CSRF token if missing
                new_form_content = form_content.replace('<form', '<form method="POST">\n        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">', 1)
                new_content = content[:form_start] + new_form_content + content[form_end:]
                
                with open(template_path, 'w') as f:
                    f.write(new_content)
                print_status("Added CSRF token to login.html", "OK")
    except Exception as e:
        print_status("Failed to fix CSRF token in login.html: {0}".format(str(e)), "ERROR")

def fix_security_module():
    """Fix security module issues"""
    if not os.path.exists('security_enhancements.py'):
        print_status("security_enhancements.py not found", "ERROR")
        return
    
    try:
        with open('security_enhancements.py', 'r') as f:
            content = f.read()
        
        # Check if the module tries to replace the login function
        if 'app.view_functions[\'login\'] = login_with_2fa' in content:
            # Fix the way login function is replaced
            fixed_content = content.replace(
                'app.view_functions[\'login\'] = login_with_2fa',
                'try:\n                app.view_functions[\'login\'] = login_with_2fa\n            except Exception as e:\n                app.logger.error(f"Failed to replace login function: {str(e)}")'
            )
            
            with open('security_enhancements.py', 'w') as f:
                f.write(fixed_content)
            print_status("Fixed security module's login function replacement", "OK")
    except Exception as e:
        print_status("Failed to fix security module: {0}".format(str(e)), "ERROR")

def fix_module_initialization():
    """Fix module initialization order in app.py"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if init_modules is defined
        init_modules_def = re.search(r'def init_modules\(\):(.*?)if __name__', content, re.DOTALL)
        
        if init_modules_def:
            # Extract the init_modules definition
            init_def = init_modules_def.group(0)
            remaining = content.replace(init_def, '')
            
            # Find where routes begin
            route_start = remaining.find('@app.route')
            
            if route_start >= 0:
                # Reorganize by placing init_modules call before routes
                init_call = "# Initialize modules\ninit_modules()\n\n"
                new_content = remaining[:route_start] + init_call + remaining[route_start:]
                
                # Re-add the init_modules definition
                new_content = init_def + new_content
                
                # Remove duplicated init_modules call from main block
                new_content = new_content.replace('init_modules()   # Initialize all feature modules', '# Modules already initialized')
                
                with open('app.py', 'w') as f:
                    f.write(new_content)
                print_status("Fixed module initialization order in app.py", "OK")
    except Exception as e:
        print_status("Failed to fix module initialization: {0}".format(str(e)), "ERROR")

def confirm(message):
    """Ask for confirmation"""
    response = input(message).lower()
    return response == 'y' or response == 'yes'

def check_app_for_errors():
    """Check app.py for any obvious errors"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for missing import statements
        missing_imports = []
        
        # Common imports needed for Flask app with new modules
        required_imports = [
            'flask',
            'flask_sqlalchemy',
            'flask_login',
            'flask_bcrypt',
            'render_template', 
            'request', 
            'redirect', 
            'url_for', 
            'flash',
            'datetime'
        ]
        
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print_status("Missing imports in app.py: {0}".format(", ".join(missing_imports)), "WARNING")
            
            # Add missing imports
            import_statements = ""
            for imp in missing_imports:
                if imp in ['render_template', 'request', 'redirect', 'url_for', 'flash']:
                    import_statements += "from flask import {0}\n".format(imp)
                elif imp == 'flask':
                    import_statements += "from flask import Flask\n"
                elif imp == 'flask_sqlalchemy':
                    import_statements += "from flask_sqlalchemy import SQLAlchemy\n"
                elif imp == 'flask_login':
                    import_statements += "from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user\n"
                elif imp == 'flask_bcrypt':
                    import_statements += "from flask_bcrypt import Bcrypt\n"
                elif imp == 'datetime':
                    import_statements += "import datetime\n"
            
            # Add imports to the top of the file
            new_content = import_statements + content
            
            with open('app.py', 'w') as f:
                f.write(new_content)
            print_status("Added missing imports to app.py", "OK")
    except Exception as e:
        print_status("Failed to check app.py for errors: {0}".format(str(e)), "ERROR")

def main():
    """Main function to debug login issues"""
    print(Colors.HEADER + Colors.BOLD + "Login Debug Utility" + Colors.ENDC)
    print("="*50)
    
    # Check for basic app errors
    print("\n" + Colors.BOLD + "Checking App for Errors" + Colors.ENDC)
    check_app_for_errors()
    
    # Check login route
    print("\n" + Colors.BOLD + "Checking Login Route" + Colors.ENDC)
    check_login_route()
    
    print("\n" + "="*50)
    print(Colors.BOLD + "Debug Complete!" + Colors.ENDC)
    print("\nNext steps:")
    print("1. Restart your Flask application:")
    print("   python app.py")
    print("2. Try logging in again")
    print("3. If you still encounter issues, check server logs for specific error messages")

if __name__ == "__main__":
    main()
