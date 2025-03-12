#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== Starting BlackTwitter Application ===${NC}"

# Check the directory structure
echo -e "${YELLOW}Checking directory structure...${NC}"

# Detect if we're using modular app or single-file app
if [ -d "routes" ] && [ -d "models" ]; then
    APP_STRUCTURE="modular"
    echo -e "${GREEN}Detected modular application structure.${NC}"
elif [ -f "blacktwitter.py" ] && ! [ -d "routes" ]; then
    APP_STRUCTURE="single-file"
    echo -e "${GREEN}Detected single-file application structure.${NC}"
else
    echo -e "${YELLOW}Uncertain application structure. Will attempt to run anyway.${NC}"
    APP_STRUCTURE="unknown"
fi

# Create empty __init__.py files if needed (to make Python recognize directories as packages)
for dir in routes models templates; do
    if [ -d "$dir" ] && [ ! -f "$dir/__init__.py" ]; then
        echo -e "${YELLOW}Creating $dir/__init__.py${NC}"
        touch "$dir/__init__.py"
    fi
done

# Set OpenSSL environment variables for compatibility with OpenSSL 3.x
export OPENSSL_CONF=/dev/null
export OPENSSL_LEGACY_PROVIDER=1

# Determine Python executable
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python not found. Please install Python 3.${NC}"
    exit 1
fi

# Check for virtual environment and activate if present
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate || source venv/Scripts/activate
elif [ -d "env" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source env/bin/activate || source env/Scripts/activate
fi

# Ensure PYTHONPATH includes current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start the application
echo -e "${YELLOW}Starting application...${NC}"

# Determine the correct entry point
if [ -f "run.py" ]; then
    $PYTHON_CMD run.py
elif [ -f "app.py" ]; then
    $PYTHON_CMD app.py
elif [ -f "blacktwitter.py" ]; then
    $PYTHON_CMD blacktwitter.py
else
    echo -e "${RED}Error: Cannot find application entry point (run.py, app.py, or blacktwitter.py)${NC}"
    echo -e "${YELLOW}Please specify the correct Python file to run:${NC}"
    read -p "Enter the main Python file name: " main_file
    
    if [ -f "$main_file" ]; then
        $PYTHON_CMD "$main_file"
    else
        echo -e "${RED}Error: File $main_file not found.${NC}"
        exit 1
    fi
fi

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
