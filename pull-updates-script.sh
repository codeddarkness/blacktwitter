#!/usr/bin/env bash

# BlackTwitter Update Script - Pull updates from source server
# This script pulls the latest files from the source server to the local installation

# Set text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default settings
SOURCE_SERVER="platformzero2"
SOURCE_USER="pi"
SOURCE_PATH="~/blacktwitter/"
LOCAL_PATH="$(pwd)"
USERNAME="raymond"
EXCLUDE_OPTS="--exclude 'venv/' --exclude '*.pyc' --exclude '.DS_Store' --exclude '__pycache__/' --exclude 'blacktwitter.db'"

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s|--server) SOURCE_SERVER="$2"; shift ;;
        -u|--user) SOURCE_USER="$2"; shift ;;
        -p|--path) SOURCE_PATH="$2"; shift ;;
        -l|--local) LOCAL_PATH="$2"; shift ;;
        --username) USERNAME="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo -e "${CYAN}=== BlackTwitter Update - Pull Latest Files ===${NC}"
echo -e "This script will pull the latest files from the source server to your local installation."
echo -e "Source: ${YELLOW}$SOURCE_USER@$SOURCE_SERVER:$SOURCE_PATH${NC}"
echo -e "Destination: ${YELLOW}$LOCAL_PATH${NC}"
echo -e "Username for paths: ${YELLOW}$USERNAME${NC}"

# Confirm before proceeding
read -p "Continue with these settings? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo -e "${YELLOW}Operation cancelled.${NC}"
    exit 0
fi

# Resolve ~ in paths if needed
if [[ "$SOURCE_PATH" == "~"* ]]; then
    SOURCE_PATH="${SOURCE_PATH/#\~/$HOME}"
fi

if [[ "$LOCAL_PATH" == "~"* ]]; then
    LOCAL_PATH="${LOCAL_PATH/#\~/$HOME}"
fi

# Replace username variable if present in SOURCE_PATH
SOURCE_PATH="${SOURCE_PATH//\$USER/$USERNAME}"

# Execute rsync to pull files
echo -e "${YELLOW}Pulling files from $SOURCE_USER@$SOURCE_SERVER:$SOURCE_PATH to $LOCAL_PATH${NC}"
echo -e "${YELLOW}Using exclude options: $EXCLUDE_OPTS${NC}"

# If path has special characters, make sure it's escaped properly
SOURCE_PATH_ESCAPED=$(printf "%q" "$SOURCE_PATH")

rsync -avz $EXCLUDE_OPTS "$SOURCE_USER@$SOURCE_SERVER:$SOURCE_PATH" "$LOCAL_PATH"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Files successfully pulled from the source server!${NC}"
else
    echo -e "${RED}Error occurred during file transfer. Please check your settings and try again.${NC}"
    exit 1
fi

echo -e "${CYAN}=== Update Complete ===${NC}"
echo -e "The BlackTwitter application files have been updated from the source server."
echo -e "You may need to restart the application for changes to take effect."

# Check if we need to update the database schema
echo -e "${YELLOW}Do you want to run database updates if any? (y/n): ${NC}"
read run_db_updates

if [[ $run_db_updates == "y" || $run_db_updates == "Y" ]]; then
    echo -e "${YELLOW}Running database updates...${NC}"
    
    if [ -f "$LOCAL_PATH/update_db.py" ]; then
        python "$LOCAL_PATH/update_db.py"
        echo -e "${GREEN}Database updates completed.${NC}"
    else
        echo -e "${YELLOW}No database update script found at $LOCAL_PATH/update_db.py${NC}"
    fi
fi

# Offer to restart the application
echo -e "${YELLOW}Do you want to restart the BlackTwitter application? (y/n): ${NC}"
read restart_app

if [[ $restart_app == "y" || $restart_app == "Y" ]]; then
    # Look for common run scripts
    if [ -f "$LOCAL_PATH/run_blacktwitter.sh" ]; then
        echo -e "${YELLOW}Restarting the application...${NC}"
        bash "$LOCAL_PATH/run_blacktwitter.sh"
    elif [ -f "$LOCAL_PATH/run.sh" ]; then
        echo -e "${YELLOW}Restarting the application...${NC}"
        bash "$LOCAL_PATH/run.sh"
    else
        echo -e "${YELLOW}No run script found. Please restart the application manually.${NC}"
    fi
fi
