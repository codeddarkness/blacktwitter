# Create models/__init__.py if it doesn't exist
if [ ! -f "models/__init__.py" ]; then
    echo -e "${YELLOW}Creating models/__init__.py...${NC}"
    cat > models/__init__.py << 'EOF'
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
fi#!/bin/bash

# Fix for OpenSSL hash issues in BlackTwitter application

# Set text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== BlackTwitter OpenSSL Fix ===${NC}"
echo "This script will fix OpenSSL hash compatibility issues."

# Check if we're in the right directory structure
if [ ! -d "models" ]; then
    # Try to create the directory structure if it doesn't exist
    echo -e "${YELLOW}Creating models directory...${NC}"
    mkdir -p models
fi

# Check OpenSSL version
echo -e "${YELLOW}Checking OpenSSL version...${NC}"
if command -v openssl &>/dev/null; then
    OPENSSL_VERSION=$(openssl version)
    echo -e "OpenSSL version: ${CYAN}$OPENSSL_VERSION${NC}"
    
    if [[ "$OPENSSL_VERSION" != *"OpenSSL 3."* ]]; then
        echo -e "${YELLOW}You don't seem to be using OpenSSL 3.x. This fix might not be necessary.${NC}"
        read -p "Continue anyway? (y/n): " continue_anyway
        if [[ $continue_anyway != "y" && $continue_anyway != "Y" ]]; then
            echo -e "${YELLOW}Exiting without making changes.${NC}"
            exit 0
        fi
    fi
else
    echo -e "${YELLOW}OpenSSL command not found. Continuing with fix anyway.${NC}"
fi

# Backup existing user.py file
echo -e "${YELLOW}Checking for existing user model...${NC}"
if [ -f "models/user.py" ]; then
    cp "models/user.py" "models/user.py.bak"
    echo -e "${GREEN}Backup created at models/user.py.bak${NC}"
else
    echo -e "${YELLOW}No existing models/user.py found, will create a new one.${NC}"
fi

# Create the patched user model
echo -e "${YELLOW}Creating patched user model...${NC}"
cat > models/user.py << 'EOF'
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import query_db
import os

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

echo -e "${GREEN}Patched user model created.${NC}"

# Update run script
echo -e "${YELLOW}Updating run script...${NC}"
if [ -f "run_blacktwitter.sh" ]; then
    # Check if already patched
    if grep -q "OPENSSL_LEGACY_PROVIDER" run_blacktwitter.sh; then
        echo -e "${GREEN}Run script already contains OpenSSL environment variables.${NC}"
    else
        # Add OpenSSL environment variables
        sed -i.bak '/# Run the application/i\
# Set OpenSSL environment variables for older hash compatibility\
export OPENSSL_CONF=/dev/null\
export OPENSSL_LEGACY_PROVIDER=1\
' run_blacktwitter.sh
        echo -e "${GREEN}Run script updated.${NC}"
    fi
else
    # Create new run script
    cat > run_blacktwitter.sh << 'EOF'
#!/bin/bash
# Script to run the BlackTwitter application

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate || source venv/Scripts/activate
fi

# Set OpenSSL environment variables for older hash compatibility
export OPENSSL_CONF=/dev/null
export OPENSSL_LEGACY_PROVIDER=1

# Run the application
python run.py

# Deactivate virtual environment on exit
deactivate
EOF
    chmod +x run_blacktwitter.sh
    echo -e "${GREEN}New run script created.${NC}"
fi

# Check if we need to reset admin password
echo -e "${YELLOW}Do you want to reset the admin password? (y/n): ${NC}"
read reset_admin

if [[ $reset_admin == "y" || $reset_admin == "Y" ]]; then
    # Create reset_password script
    cat > reset_admin.py << 'EOF'
import sqlite3
from werkzeug.security import generate_password_hash
import os

# Set environment variables for OpenSSL 3.x compatibility
os.environ['OPENSSL_CONF'] = '/dev/null'
os.environ['OPENSSL_LEGACY_PROVIDER'] = '1'

# Connect to database
conn = sqlite3.connect('blacktwitter.db')
c = conn.cursor()

# Generate new password hash with sha256 method
new_password_hash = generate_password_hash('btadmin', method='sha256')

# Update admin password
c.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_password_hash,))
conn.commit()
conn.close()

print("Admin password has been reset to 'btadmin' with SHA-256 hashing.")
EOF

    # Run the reset script
    echo -e "${YELLOW}Resetting admin password...${NC}"
    python reset_admin.py
    echo -e "${GREEN}Admin password reset complete. Use 'admin' / 'btadmin' to login.${NC}"
fi

echo -e "${CYAN}=== Fix Complete ===${NC}"
echo -e "Run the application using: ${YELLOW}./run_blacktwitter.sh${NC}"
echo -e "If you're still having issues, try manually setting these environment variables:"
echo -e "${YELLOW}export OPENSSL_CONF=/dev/null${NC}"
echo -e "${YELLOW}export OPENSSL_LEGACY_PROVIDER=1${NC}"
