#!/usr/bin/env python
"""
Fix Module Initialization Script
------------------------------
This script modifies app.py to ensure init_modules() is called properly.
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

def fix_app_py():
    """Fix app.py to ensure init_modules() is called before routes are defined"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            
        # Find the init_modules() function definition
        init_modules_def = re.search(r'def init_modules\(\):(.*?)(?=\n\n|\n\w)', content, re.DOTALL)
        
        if not init_modules_def:
            print_status("Could not find init_modules() definition in app.py", "ERROR")
            return
            
        # Find where the initialization happens in the main block
        main_init = re.search(r'if __name__ == "__main__":(.*?)init_modules\(\)', content, re.DOTALL)
        
        if not main_init:
            print_status("Could not find init_modules() call in the main block", "ERROR")
            return
            
        # Make sure the init_modules function is called explicitly before the routes
        if '@app.route' in content and content.find('@app.route') < content.find('init_modules()'):
            # We need to add an extra call to init_modules() before the routes
            # Find a good spot to insert it
            
            # First choice: after the login manager setup
            login_mgr_setup = re.search(r'login_manager\.init_app\(app\)(.*?)(?=\n\n|\n\w)', content, re.DOTALL)
            
            if login_mgr_setup:
                # Insert the call after login manager setup
                insert_pos = login_mgr_setup.end()
                new_content = content[:insert_pos] + "\n\n# Initialize all modules\ninit_modules()" + content[insert_pos:]
                
                # Now remove or comment out the call in the main block
                main_init_start = main_init.start() + content[main_init.start():].find('init_modules()')
                main_init_end = main_init_start + len('init_modules()')
                new_content = new_content[:main_init_start] + "# init_modules() # Already called earlier" + new_content[main_init_end:]
                
                with open('app.py', 'w') as f:
                    f.write(new_content)
                    
                print_status("Fixed init_modules() call in app.py", "OK")
            else:
                # Second choice: after the models before routes
                models_end = max(
                    content.find('class User('), 
                    content.find('class Tweet(')
                )
                
                if models_end > 0:
                    # Find the end of the class definition
                    class_end = content.find('\n\n', models_end)
                    if class_end > 0:
                        insert_pos = class_end
                        new_content = content[:insert_pos] + "\n\n# Initialize all modules\ninit_modules()" + content[insert_pos:]
                        
                        # Now remove or comment out the call in the main block
                        main_init_start = main_init.start() + content[main_init.start():].find('init_modules()')
                        main_init_end = main_init_start + len('init_modules()')
                        new_content = new_content[:main_init_start] + "# init_modules() # Already called earlier" + new_content[main_init_end:]
                        
                        with open('app.py', 'w') as f:
                            f.write(new_content)
                            
                        print_status("Fixed init_modules() call in app.py", "OK")
        else:
            print_status("init_modules() seems to be called in the right place", "INFO")

    except Exception as e:
        print_status("Failed to fix app.py: " + str(e), "ERROR")

def fix_security_module():
    """Fix the security_enhancements.py module to properly replace the login function"""
    if not os.path.exists('security_enhancements.py'):
        print_status("security_enhancements.py not found", "ERROR")
        return
    
    try:
        with open('security_enhancements.py', 'r') as f:
            content = f.read()
            
        # Check if the module tries to replace the login function
        if 'app.view_functions[\'login\']' in content:
            # Fix the error handling around the login function replacement
            original_pattern = r'app\.view_functions\[\'login\'\] = login_with_2fa'
            fixed_code = """try:
                app.view_functions['login'] = login_with_2fa
                print("Successfully replaced login function with 2FA-enabled version")
            except Exception as e:
                print("Error replacing login function: " + str(e))
                # As a fallback, define a new route
                @app.route('/login2fa', methods=['GET', 'POST'])
                def login2fa():
                    return login_with_2fa()"""
                
            new_content = re.sub(original_pattern, fixed_code, content)
            
            with open('security_enhancements.py', 'w') as f:
                f.write(new_content)
                
            print_status("Fixed login function replacement in security_enhancements.py", "OK")
            
    except Exception as e:
        print_status("Failed to fix security_enhancements.py: " + str(e), "ERROR")

def main():
    """Main function to fix initialization issues"""
    print(Colors.HEADER + Colors.BOLD + "Fix Module Initialization" + Colors.ENDC)
    print("="*50)
    
    # Fix app.py
    print("\n" + Colors.BOLD + "Fixing app.py" + Colors.ENDC)
    fix_app_py()
    
    # Fix security module
    print("\n" + Colors.BOLD + "Fixing security_enhancements.py" + Colors.ENDC)
    fix_security_module()
    
    print("\n" + "="*50)
    print(Colors.BOLD + "Fixes Applied!" + Colors.ENDC)
    print("\nNext steps:")
    print("1. Restart your Flask application:")
    print("   python app.py")
    print("2. Try logging in again")
    print("3. If you still encounter issues, run the debug_login.py script for more detailed diagnostics")

if __name__ == "__main__":
    main()
