#!/usr/bin/env python3

"""
BlackTwitter Application Structure Analyzer
This script analyzes the structure of your BlackTwitter application
and provides information to help troubleshoot import issues.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path

# Set OpenSSL environment variables for compatibility with OpenSSL 3.x
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_section(text):
    print("\n" + "-" * 40)
    print(f" {text}")
    print("-" * 40)

def list_directory_contents(directory="."):
    print_section(f"Directory Contents: {directory}")
    try:
        for item in sorted(os.listdir(directory)):
            full_path = os.path.join(directory, item)
            item_type = "DIR " if os.path.isdir(full_path) else "FILE"
            print(f"{item_type}: {item}")
    except Exception as e:
        print(f"Error listing directory: {e}")

def check_python_path():
    print_section("Python Path (sys.path)")
    for i, path in enumerate(sys.path):
        print(f"{i+1}. {path}")

def check_import(module_name):
    try:
        module = importlib.import_module(module_name)
        print(f"✓ Successfully imported {module_name}")
        print(f"  Module location: {inspect.getfile(module)}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error importing {module_name}: {e}")
        return False

def check_critical_imports():
    print_section("Critical Imports Check")
    modules = [
        "flask", 
        "werkzeug",
        "sqlite3"
    ]
    
    for module in modules:
        check_import(module)

def analyze_app_structure():
    print_section("Application Structure Analysis")
    
    # Check for main application files
    main_files = ["run.py", "app.py", "blacktwitter.py"]
    found_main = False
    
    for file in main_files:
        if os.path.exists(file):
            found_main = True
            print(f"✓ Found main application file: {file}")
            with open(file, 'r') as f:
                try:
                    content = f.read(500)  # Read first 500 chars
                    print(f"\nPreview of {file}:")
                    print("-" * 20)
                    print(content + ("..." if len(content) == 500 else ""))
                    print("-" * 20)
                except Exception as e:
                    print(f"Error reading file: {e}")
    
    if not found_main:
        print("✗ No main application file found (run.py, app.py, blacktwitter.py)")
    
    # Check for key directories
    key_dirs = ["routes", "models", "templates", "static"]
    for directory in key_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            print(f"✓ Found directory: {directory}")
            # Check for __init__.py
            init_file = os.path.join(directory, "__init__.py")
            if os.path.exists(init_file):
                print(f"  ✓ __init__.py exists in {directory}")
            else:
                print(f"  ✗ Missing __init__.py in {directory} (needed for imports)")
        else:
            print(f"✗ Missing directory: {directory}")

def fix_common_issues():
    print_section("Applying Common Fixes")
    
    # Create __init__.py files in key directories
    key_dirs = ["routes", "models"]
    for directory in key_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                try:
                    with open(init_file, 'w') as f:
                        f.write("# Package initialization file\n")
                    print(f"✓ Created missing {init_file}")
                except Exception as e:
                    print(f"✗ Failed to create {init_file}: {e}")
    
    # Add current directory to Python path
    current_dir = os.path.abspath('.')
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"✓ Added current directory to Python path: {current_dir}")
    
    # Attempt to import routes/models
    try:
        import routes
        print("✓ Successfully imported routes package")
    except ImportError:
        print("✗ Still unable to import routes package")
    
    try:
        import models
        print("✓ Successfully imported models package")
    except ImportError:
        print("✗ Still unable to import models package")

def provide_recommendations():
    print_section("Recommendations")
    
    print("1. Run the application with PYTHONPATH set to include the current directory:")
    print("   PYTHONPATH=$(pwd) python run.py")
    
    print("\n2. Make sure all package directories have __init__.py files")
    
    print("\n3. Use absolute imports in your code, for example:")
    print("   from routes.auth import auth_bp  # If routes is a top-level package")
    print("   from app.routes.auth import auth_bp  # If routes is inside an app package")
    
    print("\n4. Check for circular imports")
    
    print("\n5. Run with OpenSSL legacy provider enabled:")
    print("   OPENSSL_CONF=/dev/null OPENSSL_LEGACY_PROVIDER=1 python run.py")

if __name__ == "__main__":
    print_header("BlackTwitter Application Structure Analyzer")
    
    # Current working directory
    print(f"Current directory: {os.getcwd()}")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # List directory contents
    list_directory_contents()
    
    # Check Python path
    check_python_path()
    
    # Check critical imports
    check_critical_imports()
    
    # Analyze application structure
    analyze_app_structure()
    
    # Fix common issues
    fix_common_issues()
    
    # Provide recommendations
    provide_recommendations()
    
    print_header("Analysis Complete")
