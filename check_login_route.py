#!/usr/bin/env python
"""
Check Login Route Script
-----------------------
This script inspects the login route in app.py and creates a simple backup login route.
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

def check_app_logs():
    """Look for any error logs in the directory"""
    log_files = [f for f in os.listdir('.') if f.endswith('.log')]
    
    if log_files:
        print_status("Found log files: " + ", ".join(log_files), "INFO")
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                
                # Look for error messages
                if 'Error' in content or 'ERROR' in content or 'Exception' in content:
                    print_status("Found errors in " + log_file + ":", "WARNING")
                    
                    # Extract error messages
                    error_pattern = r'(Error|ERROR|Exception).*?(?=\n\d|\n[A-Z]|\Z)'
                    errors = re.findall(error_pattern, content, re.DOTALL)
                    
                    for i, error in enumerate(errors[-5:]):  # Show only the last 5 errors
                        print_status("Error {0}: {1}".format(i+1, error.strip()), "ERROR")
            except Exception as e:
                print_status("Failed to read log file " + log_file + ": " + str(e), "ERROR")
    else:
        print_status("No log files found in the current directory", "INFO")

def enable_debug_mode():
    """Enable debug mode in app.py if not already enabled"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if debug mode is enabled
        if 'debug=True' not in content:
            # Find the app.run() call
            run_match = re.search(r'app\.run\((.*?)\)', content)
            
            if run_match:
                run_args = run_match.group(1)
                
                if 'debug=' in run_args:
                    # Replace debug=False with debug=True
                    new_args = re.sub(r'debug\s*=\s*False', 'debug=True', run_args)
                else:
                    # Add debug=True to arguments
                    new_args = run_args + (', ' if run_args else '') + 'debug=True'
                
                new_content = content.replace('app.run(' + run_args + ')', 'app.run(' + new_args + ')')
                
                with open('app.py', 'w') as f:
                    f.write(new_content)
                
                print_status("Enabled debug mode in app.py", "OK")
            else:
                print_status("Could not find app.run() call in app.py", "ERROR")
        else:
            print_status("Debug mode is already enabled in app.py", "INFO")
    except Exception as e:
        print_status("Failed to enable debug mode: " + str(e), "ERROR")

def create_backup_login_route():
    """Create a backup login route in app.py"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if a backup login route already exists
        if '@app.route("/login_backup"' in content:
            print_status("Backup login route already exists in app.py", "INFO")
            return
        
        # Find the end of the routes section
        last_route_end = 0
        for route_match in re.finditer(r'@app\.route\(.*?\)\ndef (\w+)\(.*?\):(.*?)(?=\n@|\n\n|$)', content, re.DOTALL):
            route_end = route_match.end()
            if route_end > last_route_end:
                last_route_end = route_end
        
        if last_route_end > 0:
            # Create a backup login route
            backup_route = """

@app.route("/login_backup", methods=["GET", "POST"])
def login_backup():
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
    return render_template("login.html")
"""
            
            new_content = content[:last_route_end] + backup_route + content[last_route_end:]
            
            with open('app.py', 'w') as f:
                f.write(new_content)
            
            print_status("Added backup login route at /login_backup", "OK")
        else:
            print_status("Could not find a good location to add the backup login route", "ERROR")
    except Exception as e:
        print_status("Failed to add backup login route: " + str(e), "ERROR")

def show_login_route():
    """Display the current login route code"""
    if not os.path.exists('app.py'):
        print_status("app.py not found", "ERROR")
        return
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Find the login route
        login_route = re.search(r'@app\.route\([\'"]\/login[\'"].*?\)\ndef login\(\):(.*?)(?=\n@|\n\ndef|\n\nif|\Z)', content, re.DOTALL)
        
        if login_route:
            print_status("Current login route code:", "INFO")
            print("\n" + login_route.group(0))
        else:
            print_status("Could not find login route in app.py", "ERROR")
    except Exception as e:
        print_status("Failed to display login route: " + str(e), "ERROR")

def main():
    """Main function to check login route"""
    print(Colors.HEADER + Colors.BOLD + "Login Route Diagnostic Tool" + Colors.ENDC)
    print("="*50)
    
    # Check for app logs
    print("\n" + Colors.BOLD + "Checking Application Logs" + Colors.ENDC)
    check_app_logs()
    
    # Enable debug mode
    print("\n" + Colors.BOLD + "Enabling Debug Mode" + Colors.ENDC)
    enable_debug_mode()
    
    # Show current login route
    print("\n" + Colors.BOLD + "Current Login Route" + Colors.ENDC)
    show_login_route()
    
    # Create backup login route
    print("\n" + Colors.BOLD + "Creating Backup Login Route" + Colors.ENDC)
    create_backup_login_route()
    
    print("\n" + "="*50)
    print(Colors.BOLD + "Diagnostic Complete!" + Colors.ENDC)
    print("\nNext steps:")
    print("1. Restart your Flask application with debug enabled:")
    print("   python app.py")
    print("2. Try logging in at the backup route:")
    print("   http://localhost:5000/login_backup")
    print("3. Look for detailed error messages in the console output")

if __name__ == "__main__":
    main()
