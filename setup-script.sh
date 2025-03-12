#!/bin/bash

# BlackTwitter Application Setup Script

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
PYTHON_CMD="python3"
PIP_CMD="pip3"
VENV_DIR="venv"
PORT_OPTIONS=(5000 8000 8080 3000)
SELECTED_PORT=""

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Check system dependencies
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

# Create project structure
create_project_structure() {
    print_section "Creating Project Structure"
    
    # Create key directories
    mkdir -p models routes templates static/css static/js
    
    # Ensure __init__.py files exist
    touch models/__init__.py routes/__init__.py
    
    echo -e "${GREEN}✓ Project structure created${NC}"
}

# Find an available port
find_available_port() {
    print_section "Finding Available Port"
    
    for PORT in "${PORT_OPTIONS[@]}"; do
        if ! nc -z localhost $PORT; then
            SELECTED_PORT=$PORT
            echo -e "${GREEN}✓ Selected port: $PORT${NC}"
            return 0
        fi
    done
    
    echo -e "${RED}✗ No available ports found${NC}"
    return 1
}

# Create virtual environment
setup_virtual_environment() {
    print_section "Setting Up Virtual Environment"
    
    # Create virtual environment
    $PYTHON_CMD -m venv $VENV_DIR
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install flask werkzeug 
    
    echo -e "${GREEN}✓ Virtual environment created and dependencies installed${NC}"
}

# Update run.py with selected port
update_run_script() {
    print_section "Updating Run Script"
    
    # Create/update run.py
    cat > run.py << EOF
from flask import Flask
import os

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=$SELECTED_PORT)
EOF

    echo -e "${GREEN}✓ Updated run.py with port $SELECTED_PORT${NC}"
}

# Create requirements file
create_requirements_file() {
    print_section "Creating Requirements File"
    
    cat > requirements.txt << EOF
flask
werkzeug
EOF

    echo -e "${GREEN}✓ Created requirements.txt${NC}"
}

# Create launch script
create_launch_script() {
    print_section "Creating Launch Script"
    
    cat > launch_blacktwitter.sh << 'EOF'
#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run the application
python run.py

# Deactivate virtual environment
deactivate
EOF

    chmod +x launch_blacktwitter.sh
    echo -e "${GREEN}✓ Created launch script${NC}"
}

# Main setup function
main() {
    # Ensure script is run from project root
    if [ ! -d ".git" ] && [ ! -f "README.md" ]; then
        echo -e "${RED}✗ Please run this script from the project root directory.${NC}"
        exit 1
    fi

    # Run checks and setup
    check_dependencies
    create_project_structure
    find_available_port
    setup_virtual_environment
    update_run_script
    create_requirements_file
    create_launch_script

    # Final summary
    print_section "Setup Complete"
    echo -e "${GREEN}✓ BlackTwitter application setup finished${NC}"
    echo -e "To launch the application:"
    echo -e "1. ${YELLOW}./launch_blacktwitter.sh${NC}"
    echo -e "Application will be accessible at: ${BLUE}http://localhost:$SELECTED_PORT${NC}"
}

# Run the main function
main
