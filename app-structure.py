blacktwitter/
│
├── config.py                # Configuration settings
├── run.py                   # Application entry point
├── create_db.py             # Database initialization
├── blacktwitter.py          # Main application file
│
├── models/                  # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── post.py
│   └── comment.py
│
├── routes/                  # Route handlers
│   ├── __init__.py
│   ├── auth.py              # Authentication routes
│   ├── post.py              # Post-related routes
│   ├── comment.py           # Comment-related routes
│   ├── profile.py           # User profile routes
│   └── admin.py             # Admin routes
│
├── templates/               # HTML templates
│   ├── blacktwitter.html    # Main page
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── post.html            # Single post view
│   ├── profile.html         # User profile
│   └── admin.html           # Admin panel
│
└── static/                 # Static assets
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
