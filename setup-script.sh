#!/bin/bash

# BlackTwitter Application Setup and Sanity Check Script

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to check system dependencies
check_dependencies() {
    print_section "Checking System Dependencies"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓ Python found:${NC} $(python3 --version)"
    else
        echo -e "${RED}✗ Python3 not found. Please install Python.${NC}"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}✓ pip found:${NC} $(pip3 --version)"
    else
        echo -e "${RED}✗ pip3 not found. Please install pip.${NC}"
        exit 1
    fi
    
    # Check sqlite3
    if command -v sqlite3 &> /dev/null; then
        echo -e "${GREEN}✓ SQLite found:${NC} $(sqlite3 --version)"
    else
        echo -e "${RED}✗ SQLite not found. Please install SQLite.${NC}"
        exit 1
    fi
}

# Function to create application structure
create_app_structure() {
    print_section "Creating Application Structure"
    
    # Create key directories
    mkdir -p models routes templates static/css static/js
    
    # Ensure __init__.py files exist
    touch models/__init__.py routes/__init__.py templates/__init__.py
    
    # Create initial files if they don't exist
    [ ! -f "models/user.py" ] && cat > models/user.py << 'EOF'
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import query_db

class User:
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        return query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        return query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    
    @staticmethod
    def create(username, password, is_admin=0):
        """Create a new user"""
        hashed_password = generate_password_hash(password)
        query_db(
            'INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)',
            [username, hashed_password, datetime.now(), is_admin]
        )
    
    @staticmethod
    def verify_password(username, password):
        """Verify user password"""
        user = User.get_by_username(username)
        if user and check_password_hash(user['password'], password):
            return user
        return None
    
    @staticmethod
    def get_all():
        """Get all users"""
        return query_db('SELECT * FROM users ORDER BY joined_date DESC')
EOF

    [ ! -f "routes/auth.py" ] && cat > routes/auth.py << 'EOF'
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.verify_password(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash('Login successful')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username exists
        user_exists = User.get_by_username(username)
        
        if user_exists:
            flash('Username already exists')
        else:
            User.create(username, password)
            flash('Registration successful, please login')
            return redirect(url_for('auth.login'))
    
    return render_template('register.html')
EOF

    echo -e "${GREEN}✓ Application structure created${NC}"
}

# Function to check network ports
check_network_ports() {
    print_section "Checking Available Ports"
    
    # Ports to check
    PORTS=(5000 8000 8080 3000)
    
    for PORT in "${PORTS[@]}"; do
        if nc -z localhost $PORT; then
            echo -e "${YELLOW}✗ Port $PORT is already in use${NC}"
        else
            echo -e "${GREEN}✓ Port $PORT is available${NC}"
        fi
    done
}

# Function to create launch script
create_launch_script() {
    print_section "Creating Launch Script"
    
    cat > launch_blacktwitter.sh << 'EOF'
#!/bin/bash

# BlackTwitter Launch Script

# Set environment variables for OpenSSL compatibility
export OPENSSL_CONF=/dev/null
export OPENSSL_LEGACY_PROVIDER=1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
fi

# Run the application
python run.py
EOF

    chmod +x launch_blacktwitter.sh
    echo -e "${GREEN}✓ Launch script created${NC}"
}

# Function to create requirements file
create_requirements_file() {
    print_section "Creating Requirements File"
    
    cat > requirements.txt << 'EOF'
flask
werkzeug
sqlite3
EOF

    echo -e "${GREEN}✓ Requirements file created${NC}"
}

# Main script execution
main() {
    # Ensure script is run from project root
    if [ ! -d "models" ] && [ ! -d "routes" ]; then
        echo -e "${RED}✗ Please run this script from the project root directory.${NC}"
        exit 1
    fi

    # Run checks and setup
    check_dependencies
    create_app_structure
    check_network_ports
    create_launch_script
    create_requirements_file

    # Final summary
    print_section "Setup Complete"
    echo -e "${GREEN}✓ BlackTwitter application setup finished${NC}"
    echo -e "To launch the application:"
    echo -e "1. ${YELLOW}Activate virtual environment (if using)${NC}"
    echo -e "2. ${YELLOW}Install requirements: pip install -r requirements.txt${NC}"
    echo -e "3. ${YELLOW}./launch_blacktwitter.sh${NC}"
}

# Run the main function
main
#!/bin/bash

# BlackTwitter Application Setup and Fix Script
# This script validates and fixes the BlackTwitter application structure

# Set text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Port configuration - ports to try in order of preference
PORT_OPTIONS=(5000 8000 8080 8888 8899)

# Default options
SELECTED_PORT=""
FIX_OPENSSL=1
RESET_ADMIN=0
BACKUP_FILES=1

# Print header
echo -e "${CYAN}=== BlackTwitter Application Setup and Fix ===${NC}"
echo "This script will set up and fix the BlackTwitter application."

# Check current directory structure
echo -e "${YELLOW}Analyzing current directory structure...${NC}"

# Determine application structure (app directory or flat)
if [ -d "app" ]; then
    APP_DIR="app"
    echo -e "${GREEN}Found app directory structure.${NC}"
else
    APP_DIR="."
    echo -e "${YELLOW}Using flat directory structure.${NC}"
fi

# Check for OpenSSL version
echo -e "${YELLOW}Checking OpenSSL version...${NC}"
if command -v openssl &>/dev/null; then
    OPENSSL_VERSION=$(openssl version)
    echo -e "OpenSSL version: ${CYAN}$OPENSSL_VERSION${NC}"
    
    # Detect if it's OpenSSL 3.x
    if [[ "$OPENSSL_VERSION" == *"OpenSSL 3."* ]]; then
        echo -e "${YELLOW}OpenSSL 3.x detected. Will apply hash compatibility fixes.${NC}"
        FIX_OPENSSL=1
    fi
else
    echo -e "${YELLOW}OpenSSL command not found. Skipping version check.${NC}"
fi

# Check Python version
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}Python 3 found: $PYTHON_VERSION${NC}"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}Python not found. Please install Python 3.${NC}"
    exit 1
fi

# Check for pip
echo -e "${YELLOW}Checking pip installation...${NC}"
if command -v pip3 &>/dev/null; then
    PIP_CMD="pip3"
    echo -e "${GREEN}pip3 found.${NC}"
elif command -v pip &>/dev/null; then
    PIP_CMD="pip"
    echo -e "${GREEN}pip found.${NC}"
else
    echo -e "${RED}pip not found. Please install pip.${NC}"
    exit 1
fi

# Install required packages
echo -e "${YELLOW}Ensuring required packages are installed...${NC}"
$PIP_CMD install flask werkzeug cryptography

# Find Models directory
if [ -d "$APP_DIR/models" ]; then
    MODELS_DIR="$APP_DIR/models"
    echo -e "${GREEN}Found models directory at $MODELS_DIR${NC}"
elif [ -f "user-model.py" ] || [ -f "post-model.py" ]; then
    # Files are in flat structure, need to create models directory
    echo -e "${YELLOW}Model files found in flat structure. Creating models directory...${NC}"
    mkdir -p "$APP_DIR/models"
    MODELS_DIR="$APP_DIR/models"
    
    # Check and copy model files
    for model_file in user-model.py post-model.py comment-model.py; do
        if [ -f "$model_file" ]; then
            BASE_NAME=$(basename "$model_file" -model.py)
            echo -e "${YELLOW}Moving $model_file to $MODELS_DIR/${BASE_NAME}.py${NC}"
            cp "$model_file" "$MODELS_DIR/${BASE_NAME}.py"
        fi
    done
else
    # No models found, create directory
    echo -e "${YELLOW}No models directory found. Creating one...${NC}"
    mkdir -p "$APP_DIR/models"
    MODELS_DIR="$APP_DIR/models"
fi

# Create __init__.py in models if it doesn't exist
if [ ! -f "$MODELS_DIR/__init__.py" ]; then
    echo -e "${YELLOW}Creating $MODELS_DIR/__init__.py...${NC}"
    cat > "$MODELS_DIR/__init__.py" << 'EOF'
import sqlite3

def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect('blacktwitter.db')
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    """Execute query and fetch results"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv
EOF
    echo -e "${GREEN}Created models/__init__.py${NC}"
fi

# Find Routes directory
if [ -d "$APP_DIR/routes" ]; then
    ROUTES_DIR="$APP_DIR/routes"
    echo -e "${GREEN}Found routes directory at $ROUTES_DIR${NC}"
elif [ -f "auth-routes.py" ] || [ -f "post-routes.py" ]; then
    # Files are in flat structure, need to create routes directory
    echo -e "${YELLOW}Route files found in flat structure. Creating routes directory...${NC}"
    mkdir -p "$APP_DIR/routes"
    ROUTES_DIR="$APP_DIR/routes"
    
    # Check and copy route files
    for route_file in auth-routes.py post-routes.py comment-routes.py profile-routes.py admin-routes.py main-routes.py; do
        if [ -f "$route_file" ]; then
            BASE_NAME=$(basename "$route_file" -routes.py)
            echo -e "${YELLOW}Moving $route_file to $ROUTES_DIR/${BASE_NAME}.py${NC}"
            cp "$route_file" "$ROUTES_DIR/${BASE_NAME}.py"
        fi
    done
else
    # No routes found, create directory
    echo -e "${YELLOW}No routes directory found. Creating one...${NC}"
    mkdir -p "$APP_DIR/routes"
    ROUTES_DIR="$APP_DIR/routes"
fi

# Create __init__.py in routes if it doesn't exist
if [ ! -f "$ROUTES_DIR/__init__.py" ]; then
    echo -e "${YELLOW}Creating $ROUTES_DIR/__init__.py...${NC}"
    cat > "$ROUTES_DIR/__init__.py" << 'EOF'
# Routes package initialization
EOF
    echo -e "${GREEN}Created routes/__init__.py${NC}"
fi

# Find templates directory
if [ ! -d "$APP_DIR/templates" ]; then
    echo -e "${YELLOW}Creating templates directory...${NC}"
    mkdir -p "$APP_DIR/templates"
fi

# Find static directory
if [ ! -d "$APP_DIR/static" ]; then
    echo -e "${YELLOW}Creating static directories...${NC}"
    mkdir -p "$APP_DIR/static/css"
    mkdir -p "$APP_DIR/static/js"
fi

# Fix user model for OpenSSL 3.x compatibility
if [ "$FIX_OPENSSL" = "1" ]; then
    echo -e "${YELLOW}Applying OpenSSL 3.x compatibility fix to user model...${NC}"
    
    # Backup existing model if it exists
    if [ -f "$MODELS_DIR/user.py" ] && [ "$BACKUP_FILES" = "1" ]; then
        echo -e "${YELLOW}Backing up existing user model...${NC}"
        cp "$MODELS_DIR/user.py" "$MODELS_DIR/user.py.bak"
        echo -e "${GREEN}Backup created at $MODELS_DIR/user.py.bak${NC}"
    fi
    
    # Create fixed user model
    cat > "$MODELS_DIR/user.py" << 'EOF'
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys

# Add parent directory to path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try different import patterns depending on the directory structure
try:
    from models import query_db
except ImportError:
    try:
        from app.models import query_db
    except ImportError:
        # Fallback to a local implementation
        import sqlite3
        
        def get_db():
            conn = sqlite3.connect('blacktwitter.db')
            conn.row_factory = sqlite3.Row
            return conn
        
        def query_db(query, args=(), one=False):
            conn = get_db()
            cur = conn.cursor()
            cur.execute(query, args)
            rv = cur.fetchall()
            conn.commit()
            conn.close()
            return (rv[0] if rv else None) if one else rv

# Set legacy provider for OpenSSL 3.x
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

class User:
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        return query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        return query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    
    @staticmethod
    def create(username, password, is_admin=0):
        """Create a new user"""
        try:
            # Use simpler hashing method compatible with OpenSSL 3.x
            hashed_password = generate_password_hash(password, method='sha256')
            query_db(
                'INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)',
                [username, hashed_password, datetime.now(), is_admin]
            )
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    @staticmethod
    def verify_password(username, password):
        """Verify user password"""
        try:
            user = User.get_by_username(username)
            if user and check_password_hash(user['password'], password):
                return user
            return None
        except ValueError as e:
            # Handle OpenSSL 3.x issues
            print(f"OpenSSL error: {e}")
            return None
        except Exception as e:
            print(f"Error verifying password: {e}")
            return None
    
    @staticmethod
    def get_all():
        """Get all users"""
        return query_db('SELECT * FROM users ORDER BY joined_date DESC')
EOF
    echo -e "${GREEN}Fixed user model created at $MODELS_DIR/user.py${NC}"
fi

# Find an available port
echo -e "${YELLOW}Checking for available ports...${NC}"
check_port() {
    local port=$1
    if command -v nc &>/dev/null; then
        nc -z localhost $port &>/dev/null
        if [ $? -eq 0 ]; then
            return 0  # Port is in use
        else
            return 1  # Port is available
        fi
    elif command -v lsof &>/dev/null; then
        lsof -i:$port &>/dev/null
        if [ $? -eq 0 ]; then
            return 0  # Port is in use
        else
            return 1  # Port is available
        fi
    else
        # Fallback method
        (echo > /dev/tcp/localhost/$port) 2>/dev/null
        if [ $? -eq 0 ]; then
            return 0  # Port is in use
        else
            return 1  # Port is available
        fi
    fi
}

for port in "${PORT_OPTIONS[@]}"; do
    if ! check_port $port; then
        echo -e "${GREEN}Port $port is available.${NC}"
        SELECTED_PORT=$port
        break
    else
        echo -e "${YELLOW}Port $port is already in use.${NC}"
    fi
done

if [ -z "$SELECTED_PORT" ]; then
    echo -e "${RED}No available ports found. Using default port 5000.${NC}"
    SELECTED_PORT=5000
fi

# Check if run.py exists and update it
if [ -f "run.py" ]; then
    echo -e "${YELLOW}Updating run.py with port $SELECTED_PORT...${NC}"
    if [ "$BACKUP_FILES" = "1" ]; then
        cp run.py run.py.bak
    fi
    cat > run.py << EOF
from blacktwitter import app
import os

# Set environment variables for OpenSSL 3.x compatibility
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=$SELECTED_PORT)
EOF
    echo -e "${GREEN}Updated run.py to use port $SELECTED_PORT${NC}"
else
    echo -e "${YELLOW}Creating run.py with port $SELECTED_PORT...${NC}"
    cat > run.py << EOF
from blacktwitter import app
import os

# Set environment variables for OpenSSL 3.x compatibility
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=$SELECTED_PORT)
EOF
    echo -e "${GREEN}Created run.py configured to use port $SELECTED_PORT${NC}"
fi

# Create convenient launch script
echo -e "${YELLOW}Creating launch script...${NC}"
cat > launch_blacktwitter.sh << 'EOF'
#!/bin/bash
# Script to run the BlackTwitter application

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Set OpenSSL environment variables for older hash compatibility
export OPENSSL_CONF=/dev/null
export OPENSSL_LEGACY_PROVIDER=1

echo -e "${CYAN}=== Starting BlackTwitter Application ===${NC}"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d "env" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source env/bin/activate
fi

# Run the application
echo -e "${GREEN}Starting application...${NC}"
python run.py

# Deactivate virtual environment on exit
if command -v deactivate &>/dev/null; then
    deactivate
fi
EOF
chmod +x launch_blacktwitter.sh
echo -e "${GREEN}Created launch_blacktwitter.sh${NC}"

# Ask user if they want to reset admin password
echo -e "${YELLOW}Do you want to reset the admin password? (y/n): ${NC}"
read -p "" reset_admin

if [[ $reset_admin == "y" || $reset_admin == "Y" ]]; then
    # Create reset_password script
    echo -e "${YELLOW}Creating admin password reset script...${NC}"
    cat > reset_admin.py << 'EOF'
import sqlite3
from werkzeug.security import generate_password_hash
import os

# Set environment variables for OpenSSL 3.x compatibility
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

# Connect to database - try different possible locations
db_paths = ['blacktwitter.db', 'app/blacktwitter.db', 'instance/blacktwitter.db']
conn = None

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Found database at {db_path}")
        conn = sqlite3.connect(db_path)
        break

if conn is None:
    print("Could not find database. Enter database path:")
    db_path = input().strip()
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
    else:
        print("Database not found. Creating new one at blacktwitter.db")
        conn = sqlite3.connect('blacktwitter.db')

c = conn.cursor()

# Check if users table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if not c.fetchone():
    print("Creating users table...")
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        joined_date TIMESTAMP NOT NULL,
        is_admin BOOLEAN NOT NULL DEFAULT 0
    )
    ''')

# Generate new password hash with sha256 method
new_password_hash = generate_password_hash('btadmin', method='sha256')

# Check if admin user exists
c.execute("SELECT * FROM users WHERE username = 'admin'")
if c.fetchone():
    # Update admin password
    c.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_password_hash,))
    print("Admin password has been reset to 'btadmin' with SHA-256 hashing.")
else:
    # Create admin user
    from datetime import datetime
    c.execute("INSERT INTO users (username, password, joined_date, is_admin) VALUES (?, ?, ?, ?)",
             ('admin', new_password_hash, datetime.now(), 1))
    print("Admin user created with password 'btadmin' using SHA-256 hashing.")

conn.commit()
conn.close()
EOF

    # Run the reset script
    echo -e "${YELLOW}Resetting admin password...${NC}"
    python reset_admin.py
    echo -e "${GREEN}Admin password reset complete. Use 'admin' / 'btadmin' to login.${NC}"
fi

echo -e "${CYAN}=== Setup Complete ===${NC}"
echo -e "To run the application:"
echo -e "1. ${YELLOW}chmod +x launch_blacktwitter.sh${NC}"
echo -e "2. ${YELLOW}./launch_blacktwitter.sh${NC}"
echo -e "Access the application at: ${CYAN}http://localhost:$SELECTED_PORT${NC}"
echo -e "Initial admin credentials: ${CYAN}Username: admin / Password: btadmin${NC}"

echo -e "\n${CYAN}=== Troubleshooting ===${NC}"
echo -e "If you encounter login issues:"
echo -e "1. Make sure to use the script to launch: ${YELLOW}./launch_blacktwitter.sh${NC}"
echo -e "2. If you need to reset the admin password, run: ${YELLOW}python reset_admin.py${NC}"

echo -e "\nGood luck! Happy tweeting!"
