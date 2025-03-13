#!/usr/bin/env python
"""
App Update Script
----------------
This script updates app.py to include the module initialization code.
"""

import os
import sys

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

def update_app_file():
    """Update app.py with initialization code"""
    if not os.path.exists('app.py'):
        print_status("app.py not found!", "ERROR")
        return False
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check if initialization is already present
    if 'init_modules' in content:
        print_status("Module initialization already in app.py - checking if properly called", "INFO")
        
        # Check if init_modules() is called
        if 'init_modules()' not in content:
            # Add the call to init_modules()
            if 'if __name__ == "__main__":' in content:
                modified_content = content.replace(
                    'if __name__ == "__main__":', 
                    'if __name__ == "__main__":\n    with app.app_context():\n        db.create_all()  # Ensures database tables are created\n        init_modules()   # Initialize all feature modules'
                )
                
                # Write the updated content
                try:
                    with open('app.py', 'w') as f:
                        f.write(modified_content)
                    print_status("Updated app.py to call init_modules()", "OK")
                    return True
                except Exception as e:
                    print_status("Failed to update app.py: " + str(e), "ERROR")
                    return False
        else:
            print_status("init_modules() is already called in app.py", "OK")
            return True
    
    # Create initialization code
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
    if 'if __name__ ==' in content:
        new_content = content.replace('if __name__ ==', init_code + '\n\nif __name__ ==')
        
        # Also ensure db.create_all is in app context
        if 'with app.app_context():' not in new_content:
            new_content = new_content.replace('if __name__ == "__main__":', 
                                            'if __name__ == "__main__":\n    with app.app_context():\n        db.create_all()  # Ensures database tables are created\n        init_modules()   # Initialize all feature modules')
        
        # Write the updated content
        try:
            with open('app.py', 'w') as f:
                f.write(new_content)
            print_status("Updated app.py with initialization code", "OK")
            return True
        except Exception as e:
            print_status("Failed to update app.py: " + str(e), "ERROR")
            return False
    else:
        # If we can't find the if __name__ block, append to the end
        try:
            with open('app.py', 'a') as f:
                f.write("\n" + init_code + "\n\nif __name__ == \"__main__\":\n    with app.app_context():\n        db.create_all()  # Ensures database tables are created\n        init_modules()   # Initialize all feature modules\n    app.run(debug=True)")
            print_status("Added initialization code to app.py", "OK")
            return True
        except Exception as e:
            print_status("Failed to update app.py: " + str(e), "ERROR")
            return False

def main():
    """Main function to update the app.py file"""
    print(Colors.HEADER + Colors.BOLD + "App.py Update" + Colors.ENDC)
    print("="*50)
    
    update_app_file()
    
    print("\n" + "="*50)
    print(Colors.BOLD + "Update Complete!" + Colors.ENDC)
    print("\nNext steps:")
    print("1. Run the sanity check script again to verify app initialization:")
    print("   python sanity_check.py")
    print("2. Start your Twitter clone application:")
    print("   python app.py")

if __name__ == "__main__":
    main()
