#!/bin/bash

# Create utils directory if it doesn't exist
mkdir -p utils

# List of files to move to utils
UTILS_FILES=(
    "check_login_route.py"
    "debug_login.py"
    "dep-install.sh"
    "extract_templates.py"
    "git-manager.sh"
    "run.sh"
    "sanity_check.py"
    "setup.py"
)

# List of files with special versioning to move to archive
ARCHIVE_FILES=(
    "archive/v1_app.py"
    "archive/v1_run.py"
)

# Move utility files to utils directory
for file in "${UTILS_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" utils/
        echo "Moved $file to utils/"
    fi
done

# Create archive directory if it doesn't exist
mkdir -p archive

# Move archived files to archive directory
for file in "${ARCHIVE_FILES[@]}"; do
    base_file=$(basename "$file")
    if [ -f "$base_file" ]; then
        mv "$base_file" "$file"
        echo "Moved $base_file to $file"
    fi
done

# Move cleanup and CSRF fix scripts to utils
mv utils/fix_* utils/
mv utils/update_app.py utils/

# Move CSV and other testing/utility files to utils
mv curltests utils/web.tests
mv web.tests utils/

# Create an .gitignore file if it doesn't exist
if [ ! -f .gitignore ]; then
    cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*\$py.class

# Flask
instance/
.webassets-cache

# Virtual environments
venv/
env/
.venv/

# Database
*.db

# Static uploads
static/uploads/
static/profile_pics/

# Logs
*.log

# Secrets
.env

# IDE settings
.vscode/
.idea/

# macOS system files
.DS_Store
EOL
    echo "Created .gitignore file"
fi

echo "Project cleanup complete!"
