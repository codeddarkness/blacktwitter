# BlackTwitter Web Application

A Flask-based web application with user authentication, posts, comments, and admin capabilities.

## Project Structure

```
blacktwitter/
│
├── config.py                # Configuration settings
├── run.py                   # Application entry point
├── create_db.py             # Database initialization
├── create_templates.py      # HTML template creation
├── blacktwitter.py          # Main application file
│
├── models/                  # Database models
│   ├── __init__.py          # Database helpers
│   ├── user.py              # User model
│   ├── post.py              # Post model
│   └── comment.py           # Comment model
│
├── routes/                  # Route handlers
│   ├── __init__.py
│   ├── auth.py              # Authentication routes
│   ├── post.py              # Post-related routes
│   ├── comment.py           # Comment-related routes
│   ├── profile.py           # User profile routes
│   ├── admin.py             # Admin routes
│   └── main.py              # Main page routes
│
├── templates/               # HTML templates
│   ├── blacktwitter.html    # Main page
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── post.html            # Single post view
│   ├── profile.html         # User profile
│   └── admin.html           # Admin panel
│
└── static/                  # Static assets
    ├── css/
    │   └── style.css        # CSS styles
    └── js/
        └── main.js          # JavaScript functionality
```

## Installation

1. Create a new directory for the project:

```bash
mkdir blacktwitter
cd blacktwitter
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install flask werkzeug
```

4. Create all the required files as shown in the project structure.

5. Initialize the database:

```bash
python create_db.py
```

## Running the Application

Run the application using:

```bash
python run.py
```

Or directly:

```bash
python blacktwitter.py
```

Access the application in your web browser at: `http://localhost:5000`

## Initial Admin Account

The application will be initialized with an admin account:

- Username: `admin`
- Password: `btadmin`

You can use these credentials to log in and access the admin panel.

## Features

- User registration and authentication
- Create and view posts
- Comment on posts
- User profiles with post history
- Admin panel for user management
- Responsive design for mobile and desktop
