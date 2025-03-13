#!/usr/bin/env python3
"""
Twitter Clone Sanity Check Script
--------------------------------
This script verifies that all required modules, dependencies, and 
directory structures are in place for the Twitter clone application.
"""

import os
import sys
import importlib
import subprocess
import pkgutil
import shutil
from pathlib import Path

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

# Track issues for summary
issues = []

def print_status(message, status, details=None):
    """Print status messages with color-coding"""
    status_str = ""
    if status == "OK":
        status_str = f"{Colors.GREEN}[OK]{Colors.ENDC}"
    elif status == "WARNING":
        status_str = f"{Colors.YELLOW}[WARNING]{Colors.ENDC}"
    elif status == "ERROR":
        status_str = f"{Colors.RED}[ERROR]{Colors.ENDC}"
        issues.append((message, details))
    elif status == "INFO":
        status_str = f"{Colors.BLUE}[INFO]{Colors.ENDC}"
    
    print(f"{status_str} {message}")
    if details:
        print(f"     {details}")

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    if os.path.isfile(filepath):
        return True
    else:
        if required:
            print_status(f"File not found: {filepath}", "ERROR")
        else:
            print_status(f"Optional file not found: {filepath}", "WARNING")
        return False

def check_directory_exists(directory, create=False):
    """Check if a directory exists, optionally create it"""
    if os.path.isdir(directory):
        return True
    else:
        if create:
            try:
                os.makedirs(directory, exist_ok=True)
                print_status(f"Created directory: {directory}", "INFO")
                return True
            except Exception as e:
                print_status(f"Failed to create directory: {directory}", "ERROR", str(e))
                return False
        else:
            print_status(f"Directory not found: {directory}", "ERROR")
            return False

def check_python_module_import(module_name):
    """Check if a Python module can be imported"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        print_status(f"Failed to import module: {module_name}", "ERROR")
        return False

def check_pip_package(package_name):
    """Check if a pip package is installed"""
    try:
        subprocess.check_output([sys.executable, '-m', 'pip', 'show', package_name], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        print_status(f"Pip package not installed: {package_name}", "ERROR", 
                    f"Run 'pip install {package_name}' to install it")
        return False

def check_html_templates(base_dir):
    """Check for HTML templates for various features"""
    template_dir = os.path.join(base_dir, 'templates')
    template_files = [
        'index.html',       # Main page
        'login.html',       # Authentication
        'register.html',    # Authentication
        'profile.html',     # User profiles
        'edit_profile.html', # User profiles
        'feed.html',        # Follow system
        'view_tweet.html',  # Tweet interactions
        'search.html',      # Search
        'hashtag.html',     # Search/hashtags
        'trending.html',    # Search/trending
        'api_docs.html',    # API documentation
        'notifications.html', # Notifications
        'reset_request.html', # Security
        'reset_token.html',  # Security
        'setup_2fa.html',    # Security
        'verify_2fa.html',   # Security
        'security_settings.html' # Security
    ]
    
    missing_templates = []
    for template in template_files:
        path = os.path.join(template_dir, template)
        if not os.path.isfile(path):
            # Try to find template files in current directory
            source_file = None
            potential_sources = [
                f"{template}",
                f"{template.replace('.html', '')}_template.html",
                f"{template.replace('.html', '_template.html')}"
            ]
            
            for src in potential_sources:
                if os.path.isfile(src):
                    source_file = src
                    break
            
            if source_file:
                # Copy template file to correct location
                try:
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    shutil.copy2(source_file, path)
                    print_status(f"Copied template {source_file} to {path}", "INFO")
                except Exception as e:
                    print_status(f"Failed to copy template {source_file} to {path}", "ERROR", str(e))
                    missing_templates.append(template)
            else:
                missing_templates.append(template)
    
    if missing_templates:
        print_status("Missing template files", "ERROR", ", ".join(missing_templates))
        return False
    return True

def check_module_files(base_dir):
    """Check for module files for features"""
    module_files = [
        'user_profiles.py',
        'follow_system.py',
        'tweet_interactions.py',
        'search_functionality.py',
        'api_endpoints.py',
        'media_support.py',
        'notifications.py',
        'security_enhancements.py'
    ]
    
    missing_modules = []
    for module in module_files:
        path = os.path.join(base_dir, module)
        if not os.path.isfile(path):
            missing_modules.append(module)
    
    if missing_modules:
        print_status("Missing module files", "ERROR", ", ".join(missing_modules))
        return False
    return True

def check_static_dirs(base_dir):
    """Check for static directories required for uploads"""
    static_dirs = [
        os.path.join(base_dir, 'static'),
        os.path.join(base_dir, 'static', 'profile_pics'),
        os.path.join(base_dir, 'static', 'uploads')
    ]
    
    for directory in static_dirs:
        check_directory_exists(directory, create=True)
    
    return True

def check_required_dependencies():
    """Check for required pip packages"""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_bcrypt',
        'flask_wtf',
        'itsdangerous'
    ]
    
    optional_packages = [
        'flask_limiter',
        'flask_mail',
        'qrcode',
        'pyotp',
        'requests',
        'bs4'
    ]
    
    all_required_installed = True
    for package in required_packages:
        if not check_pip_package(package):
            all_required_installed = False
    
    optional_count = 0
    for package in optional_packages:
        try:
            subprocess.check_output([sys.executable, '-m', 'pip', 'show', package], stderr=subprocess.STDOUT)
            optional_count += 1
        except subprocess.CalledProcessError:
            pass
    
    print_status(f"Installed {optional_count}/{len(optional_packages)} optional packages", 
                "INFO" if optional_count > 0 else "WARNING")
    
    return all_required_installed

def check_app_initialization(base_dir):
    """Check if app.py initializes the modules correctly"""
    app_path = os.path.join(base_dir, 'app.py')
    if not os.path.isfile(app_path):
        print_status("app.py not found", "ERROR")
        return False
    
    # Look for module initialization
    with open(app_path, 'r') as f:
        content = f.read()
        
    init_functions = [
        'init_user_profiles',
        'init_follow_system',
        'init_tweet_interactions',
        'init_search_functionality',
        'init_api',
        'init_media_support',
        'init_notifications',
        'init_security'
    ]
    
    missing_inits = []
    for init_func in init_functions:
        if init_func not in content:
            missing_inits.append(init_func)
    
    if missing_inits:
        print_status("Missing module initialization in app.py", "ERROR", 
                    "Add init_modules() function from app_integration.txt")
        return False
    
    # Check for db.create_all() inside app context
    if 'with app.app_context():' not in content or 'db.create_all()' not in content:
        print_status("Missing db.create_all() inside app context", "WARNING",
                    "Add 'with app.app_context():\\n    db.create_all()' to app.py")
    
    return True

def check_instance_dir(base_dir):
    """Check if the instance directory exists (for SQLite database)"""
    instance_dir = os.path.join(base_dir, 'instance')
    return check_directory_exists(instance_dir, create=True)

def move_template_files(base_dir):
    """Move template files from current directory to templates directory"""
    template_dir = os.path.join(base_dir, 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    template_files = [f for f in os.listdir('.') if f.endswith('_template.html') or f.endswith('.html')]
    
    for file in template_files:
        target_name = file.replace('_template', '')
        if 'api_docs' in file:
            target_name = 'api_docs.html'
        elif 'setup_2fa' in file:
            target_name = 'setup_2fa.html'
        
        target_path = os.path.join(template_dir, target_name)
        
        if not os.path.exists(target_path):
            try:
                shutil.copy2(file, target_path)
                print_status(f"Copied {file} to {target_path}", "INFO")
            except Exception as e:
                print_status(f"Failed to copy {file} to {target_path}", "ERROR", str(e))

def main():
    """Main function to run all checks"""
    base_dir = os.getcwd()
    
    print(f"{Colors.HEADER}{Colors.BOLD}Twitter Clone Sanity Check{Colors.ENDC}")
    print("="*50)
    
    print(f"\n{Colors.BOLD}Checking Base Structure{Colors.ENDC}")
    check_instance_dir(base_dir)
    check_static_dirs(base_dir)
    move_template_files(base_dir)
    
    print(f"\n{Colors.BOLD}Checking Module Files{Colors.ENDC}")
    check_module_files(base_dir)
    
    print(f"\n{Colors.BOLD}Checking Templates{Colors.ENDC}")
    check_html_templates(base_dir)
    
    print(f"\n{Colors.BOLD}Checking Dependencies{Colors.ENDC}")
    check_required_dependencies()
    
    print(f"\n{Colors.BOLD}Checking App Initialization{Colors.ENDC}")
    check_app_initialization(base_dir)
    
    # Print summary
    print("\n" + "="*50)
    print(f"{Colors.BOLD}Summary{Colors.ENDC}")
    if issues:
        print(f"{Colors.RED}Found {len(issues)} issues that need to be fixed:{Colors.ENDC}")
        for idx, (message, details) in enumerate(issues, 1):
            print(f"{idx}. {message}")
            if details:
                print(f"   {details}")
    else:
        print(f"{Colors.GREEN}All checks passed! Your Twitter clone is ready to run.{Colors.ENDC}")
        print("Run the application with: python app.py")
    
    # Instructions for next steps
    print("\n" + "="*50)
    print(f"{Colors.BOLD}Next Steps{Colors.ENDC}")
    print("1. Fix any issues reported above")
    print("2. Run the app with 'python app.py' or 'flask run'")
    print("3. Access the app at http://localhost:5000")
    print("4. Create an account and start tweeting!")

if __name__ == "__main__":
    main()
