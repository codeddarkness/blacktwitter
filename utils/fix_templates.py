#!/usr/bin/env python
"""
Fix Templates Script
------------------
This script updates all templates to make CSRF tokens conditional.
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

def update_login_template():
    """Update login.html to make CSRF token optional"""
    template_path = os.path.join('templates', 'login.html')
    
    if not os.path.exists(template_path):
        print_status("login.html not found", "ERROR")
        return False
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Replace the CSRF token line with a conditional version
        old_line = '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">'
        new_line = '{% if csrf_token is defined %}<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">{% endif %}'
        
        if old_line in content:
            new_content = content.replace(old_line, new_line)
            
            with open(template_path, 'w') as f:
                f.write(new_content)
            
            print_status("Updated CSRF token in login.html", "OK")
            return True
        else:
            print_status("CSRF token line not found in login.html", "WARNING")
            # See if there's any mention of csrf_token
            if 'csrf_token' in content:
                # Try a more general replacement
                pattern = r'<input[^>]*name=["\']csrf_token["\'][^>]*>'
                if re.search(pattern, content):
                    new_content = re.sub(
                        pattern, 
                        '{% if csrf_token is defined %}<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">{% endif %}',
                        content
                    )
                    
                    with open(template_path, 'w') as f:
                        f.write(new_content)
                    
                    print_status("Updated CSRF token pattern in login.html", "OK")
                    return True
            
            # If we couldn't find a way to update, rewrite the template
            create_new_login_template(template_path)
            return True
            
    except Exception as e:
        print_status("Error updating login.html: " + str(e), "ERROR")
        return False

def create_new_login_template(path):
    """Create a new login.html template without CSRF"""
    try:
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
        {% if csrf_token is defined %}
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        {% endif %}
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
        
        with open(path, 'w') as f:
            f.write(new_content)
        
        print_status("Created new login.html template", "OK")
        return True
    except Exception as e:
        print_status("Error creating login.html: " + str(e), "ERROR")
        return False

def update_register_template():
    """Update register.html to make CSRF token optional"""
    template_path = os.path.join('templates', 'register.html')
    
    if not os.path.exists(template_path):
        print_status("register.html not found", "WARNING")
        return False
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Replace the CSRF token line with a conditional version
        old_line = '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">'
        new_line = '{% if csrf_token is defined %}<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">{% endif %}'
        
        if old_line in content:
            new_content = content.replace(old_line, new_line)
            
            with open(template_path, 'w') as f:
                f.write(new_content)
            
            print_status("Updated CSRF token in register.html", "OK")
            return True
        else:
            print_status("CSRF token line not found in register.html", "WARNING")
            
            # See if there's any mention of csrf_token
            if 'csrf_token' in content:
                # Try a more general replacement
                pattern = r'<input[^>]*name=["\']csrf_token["\'][^>]*>'
                if re.search(pattern, content):
                    new_content = re.sub(
                        pattern, 
                        '{% if csrf_token is defined %}<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">{% endif %}',
                        content
                    )
                    
                    with open(template_path, 'w') as f:
                        f.write(new_content)
                    
                    print_status("Updated CSRF token pattern in register.html", "OK")
                    return True
            
            # If we couldn't find a match, just leave it
            return False
            
    except Exception as e:
        print_status("Error updating register.html: " + str(e), "ERROR")
        return False

def update_all_templates():
    """Update all templates with CSRF tokens to make them conditional"""
    templates_dir = os.path.join(os.getcwd(), 'templates')
    
    if not os.path.exists(templates_dir):
        print_status("Templates directory not found", "ERROR")
        return
    
    # Get all HTML files
    templates = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
    
    for template in templates:
        if template in ['login.html', 'register.html']:
            # These are handled separately
            continue
        
        template_path = os.path.join(templates_dir, template)
        
        try:
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Check if the template uses csrf_token
            if 'csrf_token' in content:
                # Replace the CSRF token with a conditional version
                pattern = r'<input[^>]*name=["\']csrf_token["\'][^>]*>'
                if re.search(pattern, content):
                    new_content = re.sub(
                        pattern, 
                        '{% if csrf_token is defined %}<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">{% endif %}',
                        content
                    )
                    
                    with open(template_path, 'w') as f:
                        f.write(new_content)
                    
                    print_status("Updated CSRF token in " + template, "OK")
        except Exception as e:
            print_status("Error updating " + template + ": " + str(e), "ERROR")

def ensure_csrf_initialized():
    """Ensure CSRF is properly initialized in app.py"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if Flask-WTF is imported
        if 'from flask_wtf' not in content:
            # Add the import
            import_section_end = content.find('\n\n# Initialize')
            if import_section_end > 0:
                # Add import after other imports
                modified_content = content[:import_section_end] + '\nfrom flask_wtf.csrf import CSRFProtect\n' + content[import_section_end:]
                
                # Add initialization after app is created
                app_init_end = modified_content.find('app = Flask(__name__)') + len('app = Flask(__name__)')
                next_line = modified_content.find('\n', app_init_end)
                
                if next_line > 0:
                    modified_content = modified_content[:next_line+1] + 'csrf = CSRFProtect(app)\n' + modified_content[next_line+1:]
                    
                    with open('app.py', 'w') as f:
                        f.write(modified_content)
                    
                    print_status("Added CSRF protection to app.py", "OK")
                    return True
            
            # If we couldn't find the right spots, just print a warning
            print_status("Could not add CSRF protection to app.py - structure not recognized", "WARNING")
            return False
        else:
            # Check if CSRFProtect is initialized
            if 'CSRFProtect(app)' not in content and 'csrf = CSRFProtect' not in content:
                # Add initialization
                app_init_end = content.find('app = Flask(__name__)') + len('app = Flask(__name__)')
                next_line = content.find('\n', app_init_end)
                
                if next_line > 0:
                    modified_content = content[:next_line+1] + 'csrf = CSRFProtect(app)\n' + content[next_line+1:]
                    
                    with open('app.py', 'w') as f:
                        f.write(modified_content)
                    
                    print_status("Initialized CSRFProtect in app.py", "OK")
                    return True
                else:
                    print_status("Could not initialize CSRFProtect in app.py", "WARNING")
                    return False
            else:
                print_status("CSRFProtect already initialized in app.py", "INFO")
                return True
    except Exception as e:
        print_status("Error ensuring CSRF is initialized: " + str(e), "ERROR")
        return False

def main():
    """Main function to fix template issues"""
    print(Colors.HEADER + Colors.BOLD + "Template Fixer" + Colors.ENDC)
    print("="*50)
    
    # Update login template
    print("\n" + Colors.BOLD + "Updating Login Template" + Colors.ENDC)
    update_login_template()
    
    # Update register template
    print("\n" + Colors.BOLD + "Updating Register Template" + Colors.ENDC)
    update_register_template()
    
    # Update all other templates
    print("\n" + Colors.BOLD + "Updating All Other Templates" + Colors.ENDC)
    update_all_templates()
    
    # Ensure CSRF is initialized
    print("\n" + Colors.BOLD + "Ensuring CSRF is Initialized" + Colors.ENDC)
    ensure_csrf_initialized()
    
    print("\n" + "="*50)
    print(Colors.BOLD + "Template Updates Complete!" + Colors.ENDC)
    print("\nNext steps:")
    print("1. Restart your Flask application:")
    print("   python app.py")
    print("2. Try logging in again at the regular login page:")
    print("   http://localhost:5000/login")
    print("3. If login still fails, the simple login page should work:")
    print("   http://localhost:5000/simple_login")

if __name__ == "__main__":
    main()
