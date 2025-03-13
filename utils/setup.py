def move_template_files():
    """Move template files to templates directory"""
    # Create templates directory
    templates_dir = os.path.join(os.getcwd(), 'templates')
    create_directory(templates_dir)
    
    # Template file mapping (source -> destination)
    template_files = {
        'api_docs_template.html': 'api_docs.html',
        'feed_template.html': 'feed.html',
        'hashtag_template.html': 'hashtag.html',
        'search_template.html': 'search.html',
        'setup_2fa_template.html': 'setup_2fa.html',
        'trending_template.html': 'trending.html'
    }
    
    # Copy template files
    for source, dest in template_files.items():
        if os.path.exists(source):
            copy_file(source, os.path.join(templates_dir, dest))
    
    # Look for other templates that might be in app_integration.txt
    if os.path.exists('app_integration.txt'):
        with open('app_integration.txt', 'r') as f:
            content = f.read()
            
        # Extract template names from content
        import re
        template_matches = re.findall(r'templates/([a-zA-Z_]+\.html)', content)
        for template in template_matches:
            dest_path = os.path.join(templates_dir, template)
            if not os.path.exists(dest_path):
                print_status("Template file needed: {0}".format(template), "INFO")

def setup_static_directories():
    """Set up static directories for uploads"""
    static_dir = os.path.join(os.getcwd(), 'static')
    create_directory(static_dir)
    create_directory(os.path.join(static_dir, 'profile_pics'))
    create_directory(os.path.join(static_dir, 'uploads'))
    
    # Create a default profile picture
    default_pic = os.path.join(static_dir, 'profile_pics', 'default.jpg')
    if not os.path.exists(default_pic):
        try:
            # Create a simple image or copy from existing
            # For simplicity, we'll just create an empty file
            open(default_pic, 'a').close()
            print_status("Created placeholder for default profile picture", "INFO")
        except Exception as e:
            print_status("Failed to create default profile picture: {0}".format(str(e)), "WARNING")

def verify_module_files():
    """Verify all module files are present"""
    expected_modules = [
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
    for module in expected_modules:
        if not os.path.exists(module):
            missing_modules.append(module)
    
    if missing_modules:
        print_status("Missing module files: {0}".format(", ".join(missing_modules)), "ERROR")
        return False
    
    print_status("All module files are present", "OK")
    return True

def update_app_file():
    """Update app.py with initialization code if necessary"""
    if not os.path.exists('app.py'):
        print_status("app.py not found!", "ERROR")
        return False
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check if initialization is already present
    if 'init_modules' in content:
        print_status("Module initialization already in app.py", "OK")
        return True
    
    # Get initialization code from app_integration.txt
    init_code = ""
    if os.path.exists('app_integration.txt'):
        with open('app_integration.txt', 'r') as f:
            app_integration = f.read()
            
        import re
        # Extract the init_modules function
        match = re.search(r'def init_modules\(\):(.*?)if __name__', app_integration, re.DOTALL)
        if match:
            init_code = match.group(1).strip()
            
    if not init_code:
        init_code = """
# Initialize all modules
def init_modules():
    # Import all feature modules
    from user_profiles import init_user_profiles
    from follow_system import init_follow_system
    from tweet_interactions import init_tweet_interactions
    from search_functionality import init_search_functionality
    from api_endpoints import init_api
    from media_support import init_media_support
    from notifications import init_notifications
    from security_enhancements import init_security
    
    # Initialize each module
    init_user_profiles(app, User)
    init_follow_system(app, User)
    init_tweet_interactions(app, db, User, Tweet)
    init_search_functionality(app, db, Tweet, User)
    init_api(app, db, User, Tweet)
    init_media_support(app, db, Tweet)
    init_notifications(app, db, User, Tweet)
    init_security(app, db, User, bcrypt)
"""
    
    # Add the initialization code before the if __name__ block
    if '__name__' in content:
        new_content = content.replace('if __name__ ==', '{0}\n\nif __name__ =='.format(init_code))
        
        # Also ensure db.create_all is in app context
        if 'with app.app_context():' not in new_content:
            new_content = new_content.replace('if __name__ == "__main__":', 
                                             'if __name__ == "__main__":\n    with app.app_context():\n        db.create_all()  # Ensures database tables are created\n        init_modules()   # Initialize all feature modules')
        
        # Write the updated content
        try:
            with open('app.py', 'w') as f:
                f.write(new_content)
            print_status("Updated app.py with initialization code", "OK")
        except Exception as e:
            print_status("Failed to update app.py: {0}".format(str(e)), "ERROR")
            return False
    else:
        print_status("Could not find appropriate place to insert init code in app.py", "ERROR")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_bcrypt',
        'flask_wtf',
        'itsdangerous',
        'flask_limiter',
        'flask_mail',
        'qrcode',
        'pyotp',
        'requests',
        'bs4'
    ]
    
    print_status("Installing dependencies...", "INFO")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + dependencies)
        print_status("Dependencies installed successfully", "OK")
    except subprocess.CalledProcessError as e:
        print_status("Failed to install dependencies: {0}".format(str(e)), "ERROR")
        print_status("You may need to install them manually using pip", "INFO")

def extract_templates_from_txt():
    """Extract template content from app_integration.txt"""
    if not os.path.exists('app_integration.txt'):
        print_status("app_integration.txt not found, skipping template extraction", "WARNING")
        return
    
    templates_dir = os.path.join(os.getcwd(), 'templates')
    create_directory(templates_dir)
    
    with open('app_integration.txt', 'r') as f:
        content = f.read()
    
    import re
    # Look for template code blocks like ```html ... ```
    template_blocks = re.finditer(r'```html\s*<!DOCTYPE html>.*?<title>(.*?)</title>.*?```', content, re.DOTALL)
    
    for match in template_blocks:
        # Extract title to guess filename
        title = match.group(1).strip().lower()
        filename = None
        
        # Map title to filename
        if 'login' in title:
            filename = 'login.html'
        elif 'register' in title:
            filename = 'register.html'
        elif 'profile' in title and 'edit' in title:
            filename = 'edit_profile.html'
        elif 'profile' in title:
            filename = 'profile.html'
        elif 'tweet' in title and 'view' in title:
            filename = 'view_tweet.html'
        elif 'notification' in title and 'settings' in title:
            filename = 'notification_settings.html'
        elif 'notification' in title:
            filename = 'notifications.html'
        elif 'reset' in title and 'token' in title:
            filename = 'reset_token.html'
        elif 'reset' in title:
            filename = 'reset_request.html'
        elif 'security' in title:
            filename = 'security_settings.html'
        elif 'verify' in title:
            filename = 'verify_2fa.html'
        
        if filename:
            file_path = os.path.join(templates_dir, filename)
            if not os.path.exists(file_path):
                # Extract the HTML content
                html_content = match.group(0).replace('```html', '').replace('```', '').strip()
                try:
                    with open(file_path, 'w') as f:
                        f.write(html_content)
                    print_status("Created template file: {0}".format(filename), "OK")
                except Exception as e:
                    print_status("Failed to create {0}: {1}".format(filename, str(e)), "ERROR")

def main():
    """Main function to set up the Twitter clone project"""
    print(Colors.HEADER + Colors.BOLD + "Twitter Clone Setup" + Colors.ENDC)
    print("="*50)
    
    # Verify module files
    print("\n" + Colors.BOLD + "Verifying Module Files" + Colors.ENDC)
    verify_module_files()
    
    # Set up directories
    print("\n" + Colors.BOLD + "Setting Up Directories" + Colors.ENDC)
    create_directory(os.path.join(os.getcwd(), 'instance'))
    setup_static_directories()
    
    # Move template files
    print("\n" + Colors.BOLD + "Setting Up Templates" + Colors.ENDC)
    move_template_files()
    extract_templates_from_txt()
    
    # Update app.py
    print("\n" + Colors.BOLD + "Updating app.py" + Colors.ENDC)
    update_app_file()
    
    # Install dependencies
    print("\n" + Colors.BOLD + "Installing Dependencies" + Colors.ENDC)
    install_dependencies()
    
    # Print next steps
    print("\n" + "="*50)
    print(Colors.BOLD + "Setup Complete!" + Colors.ENDC)
    print("\nNext steps:")
    print("1. Run the sanity check script to verify everything is set up correctly:")
    print("   python sanity_check.py")
    print("2. Start your Twitter clone application:")
    print("   python app.py")
    print("3. Access your application at http://localhost:5000")

if __name__ == "__main__":
    main()#!/usr/bin/env python
"""
Twitter Clone Setup Script
-------------------------
This script organizes all module files and templates into the correct
directory structure for the Twitter clone application.
"""

import os
import sys
import shutil
import subprocess
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

def create_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print_status("Created directory: {0}".format(directory), "OK")
        except Exception as e:
            print_status("Failed to create directory {0}: {1}".format(directory, str(e)), "ERROR")
            return False
    return True

def copy_file(source, destination):
    """Copy a file from source to destination"""
    try:
        shutil.copy2(source, destination)
        print_status("Copied {0} to {1}".format(os.path.basename(source), destination), "OK")
        return True
    except Exception as e:
        print_status("Failed to copy {0} to {1}: {2}".format(source, destination, str(e)), "ERROR")
        return False

def move_template_files():
    """Move template files to templates directory"""
    # Create templates directory
    templates_dir = os.path.join(os.getcwd(), 'templates')
    create_directory(templates_dir)
    
    # Template file mapping (source -> destination)
    template_files = {
        'api_docs_template.html': 'api_docs.html',
        'feed_template.html': 'feed.html',
        'hashtag_template.html': 'hashtag.html',
        'search_template.html': 'search.html',
        'setup_2fa_template.html': 'setup_2fa.html',
        'trending_template.html': 'trending.html'
    }
    
    # Copy template files
    for source, dest in template_files.items():
        if os.path.exists(source):
            copy_file(source, os.path.join(templates_dir, dest))
    
    # Look for other templates that might be in app_integration.txt
    if os.path.exists('app_integration.txt'):
        with open('app_integration.txt', 'r') as f:
            content = f.read()
            
        # Extract template names from content
        import re
        template_matches = re.findall(r'templates/([a-zA-Z_]+\.html)', content)
        for template in template_matches:
            dest_path = os.path.join(templates_dir, template)
            if not os.path.exists(dest_path):
                print_status(f"Template file needed: {template}", "INFO")

def setup_static_directories():
    """Set up static directories for uploads"""
    static_dir = os.path.join(os.getcwd(), 'static')
    create_directory(static_dir)
    create_directory(os.path.join(static_dir, 'profile_pics'))
    create_directory(os.path.join(static_dir, 'uploads'))
    
    # Create a default profile picture
    default_pic = os.path.join(static_dir, 'profile_pics', 'default.jpg')
    if not os.path.exists(default_pic):
        try:
            # Create a simple image or copy from existing
            # For simplicity, we'll just create an empty file
            open(default_pic, 'a').close()
            print_status(f"Created placeholder for default profile picture", "INFO")
        except Exception as e:
            print_status(f"Failed to create default profile picture: {str(e)}", "WARNING")

def verify_module_files():
    """Verify all module files are present"""
    expected_modules = [
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
    for module in expected_modules:
        if not os.path.exists(module):
            missing_modules.append(module)
    
    if missing_modules:
        print_status(f"Missing module files: {', '.join(missing_modules)}", "ERROR")
        return False
    
    print_status("All module files are present", "OK")
    return True

def update_app_file():
    """Update app.py with initialization code if necessary"""
    if not os.path.exists('app.py'):
        print_status("app.py not found!", "ERROR")
        return False
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check if initialization is already present
    if 'init_modules' in content:
        print_status("Module initialization already in app.py", "OK")
        return True
    
    # Get initialization code from app_integration.txt
    init_code = ""
    if os.path.exists('app_integration.txt'):
        with open('app_integration.txt', 'r') as f:
            app_integration = f.read()
            
        import re
        # Extract the init_modules function
        match = re.search(r'def init_modules\(\):(.*?)if __name__', app_integration, re.DOTALL)
        if match:
            init_code = match.group(1).strip()
            
    if not init_code:
        init_code = """
# Initialize all modules
def init_modules():
    # Import all feature modules
    from user_profiles import init_user_profiles
    from follow_system import init_follow_system
    from tweet_interactions import init_tweet_interactions
    from search_functionality import init_search_functionality
    from api_endpoints import init_api
    from media_support import init_media_support
    from notifications import init_notifications
    from security_enhancements import init_security
    
    # Initialize each module
    init_user_profiles(app, User)
    init_follow_system(app, User)
    init_tweet_interactions(app, db, User, Tweet)
    init_search_functionality(app, db, Tweet, User)
    init_api(app, db, User, Tweet)
    init_media_support(app, db, Tweet)
    init_notifications(app, db, User, Tweet)
    init_security(app, db, User, bcrypt)
"""
    
    # Add the initialization code before the if __name__ block
    if '__name__' in content:
        new_content = content.replace('if __name__ ==', f'{init_code}\n\nif __name__ ==')
        
        # Also ensure db.create_all is in app context
        if 'with app.app_context():' not in new_content:
            new_content = new_content.replace('if __name__ == "__main__":', 
                                             'if __name__ == "__main__":\n    with app.app_context():\n        db.create_all()  # Ensures database tables are created\n        init_modules()   # Initialize all feature modules')
        
        # Write the updated content
        try:
            with open('app.py', 'w') as f:
                f.write(new_content)
            print_status("Updated app.py with initialization code", "OK")
        except Exception as e:
            print_status(f"Failed to update app.py: {str(e)}", "ERROR")
            return False
    else:
        print_status("Could not find appropriate place to insert init code in app.py", "ERROR")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_bcrypt',
        'flask_wtf',
        'itsdangerous',
        'flask_limiter',
        'flask_mail',
        'qrcode',
        'pyotp',
        'requests',
        'bs4'
    ]
    
    print_status("Installing dependencies...", "INFO")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + dependencies)
        print_status("Dependencies installed successfully", "OK")
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install dependencies: {str(e)}", "ERROR")
        print_status("You may need to install them manually using pip", "INFO")

def extract_templates_from_txt():
    """Extract template content from app_integration.txt"""
    if not os.path.exists('app_integration.txt'):
        print_status("app_integration.txt not found, skipping template extraction", "WARNING")
        return
    
    templates_dir = os.path.join(os.getcwd(), 'templates')
    create_directory(templates_dir)
    
    with open('app_integration.txt', 'r') as f:
        content = f.read()
    
    import re
    # Look for template code blocks like ```html ... ```
    template_blocks = re.finditer(r'```html\s*<!DOCTYPE html>.*?<title>(.*?)</title>.*?```', content, re.DOTALL)
    
    for match in template_blocks:
        # Extract title to guess filename
        title = match.group(1).strip().lower()
        filename = None
        
        # Map title to filename
        if 'login' in title:
            filename = 'login.html'
        elif 'register' in title:
            filename = 'register.html'
        elif 'profile' in title and 'edit' in title:
            filename = 'edit_profile.html'
        elif 'profile' in title:
            filename = 'profile.html'
        elif 'tweet' in title and 'view' in title:
            filename = 'view_tweet.html'
        elif 'notification' in title and 'settings' in title:
            filename = 'notification_settings.html'
        elif 'notification' in title:
            filename = 'notifications.html'
        elif 'reset' in title and 'token' in title:
            filename = 'reset_token.html'
        elif 'reset' in title:
            filename = 'reset_request.html'
        elif 'security' in title:
            filename = 'security_settings.html'
        elif 'verify' in title:
            filename = 'verify_2fa.html'
        
        if filename:
            file_path = os.path.join(templates_dir, filename)
            if not os.path.exists(file_path):
                # Extract the HTML content
                html_content = match.group(0).replace('```html', '').replace('```', '').strip()
                try:
                    with open(file_path, 'w') as f:
                        f.write(html_content)
                    print_status(f"Created template file: {filename}", "OK")
                except Exception as e:
                    print_status(f"Failed to create {filename}: {str(e)}", "ERROR")

def main():
    """Main function to set up the Twitter clone project"""
    print(f"{Colors.HEADER}{Colors.BOLD}Twitter Clone Setup{Colors.ENDC}")
    print("="*50)
    
    # Verify module files
    print(f"\n{Colors.BOLD}Verifying Module Files{Colors.ENDC}")
    verify_module_files()
    
    # Set up directories
    print(f"\n{Colors.BOLD}Setting Up Directories{Colors.ENDC}")
    create_directory(os.path.join(os.getcwd(), 'instance'))
    setup_static_directories()
    
    # Move template files
    print(f"\n{Colors.BOLD}Setting Up Templates{Colors.ENDC}")
    move_template_files()
    extract_templates_from_txt()
    
    # Update app.py
    print(f"\n{Colors.BOLD}Updating app.py{Colors.ENDC}")
    update_app_file()
    
    # Install dependencies
    print(f"\n{Colors.BOLD}Installing Dependencies{Colors.ENDC}")
    install_dependencies()
    
    # Print next steps
    print("\n" + "="*50)
    print(f"{Colors.BOLD}Setup Complete!{Colors.ENDC}")
    print("\nNext steps:")
    print("1. Run the sanity check script to verify everything is set up correctly:")
    print("   python sanity_check.py")
    print("2. Start your Twitter clone application:")
    print("   python app.py")
    print("3. Access your application at http://localhost:5000")

if __name__ == "__main__":
    main()
