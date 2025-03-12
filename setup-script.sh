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
