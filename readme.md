# Twitter Clone Feature Modules

This package contains modular features to enhance your Flask-based Twitter clone application. Each module is designed to be integrated easily, with clear documentation and minimal dependencies.

## Available Modules

1. **User Profiles** - Add user profiles with bio and profile pictures
2. **Follow System** - Implement follower/following relationships
3. **Tweet Interactions** - Add likes, replies, and retweets
4. **Search Functionality** - Implement search and hashtag features
5. **API Endpoints** - Create a RESTful API
6. **Media Support** - Allow image uploads and URL previews
7. **Notifications** - Implement a notification system
8. **Security Enhancements** - Add password reset, 2FA, and more

## Installation

1. Download the module files and place them in your project directory
2. Install the required dependencies:
   ```bash
   pip install flask-wtf flask-limiter flask-mail qrcode pyotp itsdangerous requests bs4
   ```
3. Create the necessary directories:
   ```bash
   mkdir -p static/profile_pics static/uploads templates/partials
   ```
4. Follow the integration instructions in `app_integration.py`

## Module Details

### 1. User Profiles
- **Features**: User bios, profile pictures, profile pages
- **Dependencies**: Flask-WTF (forms), Werkzeug (file uploads)
- **Files**: `user_profiles.py`, templates (`profile.html`, `edit_profile.html`)

### 2. Follow System
- **Features**: Follow/unfollow users, personalized feed
- **Dependencies**: None
- **Files**: `follow_system.py`, templates (`feed.html`)

### 3. Tweet Interactions
- **Features**: Like tweets, reply to tweets, retweet/quote tweet
- **Dependencies**: None
- **Files**: `tweet_interactions.py`, templates (`view_tweet.html`)

### 4. Search Functionality
- **Features**: Search tweets and users, hashtag support, trending topics
- **Dependencies**: None
- **Files**: `search_functionality.py`, templates (`search.html`, `hashtag.html`, `trending.html`)

### 5. API Endpoints
- **Features**: RESTful API for tweets and users, API token authentication
- **Dependencies**: None
- **Files**: `api_endpoints.py`, templates (`api_docs.html`)

### 6. Media Support
- **Features**: Image uploads, GIF support, URL previews for tweets
- **Dependencies**: requests, bs4 (BeautifulSoup)
- **Files**: `media_support.py`

### 7. Notifications
- **Features**: Notification system for likes, replies, follows, etc.
- **Dependencies**: Flask-Mail (optional for email notifications)
- **Files**: `notifications.py`, templates (`notifications.html`, `notification_settings.html`)

### 8. Security Enhancements
- **Features**: Password reset, two-factor authentication, rate limiting, CSRF protection
- **Dependencies**: Flask-WTF, Flask-Limiter, pyotp, qrcode, itsdangerous
- **Files**: `security_enhancements.py`, templates (`reset_request.html`, `reset_token.html`, `setup_2fa.html`, `verify_2fa.html`, `security_settings.html`)

## Integration

The modules are designed to work together seamlessly. Here's the recommended integration order:

1. User Profiles
2. Follow System
3. Tweet Interactions
4. Search Functionality
5. Media Support
6. Notifications
7. API Endpoints
8. Security Enhancements

Each module's `init_*` function takes care of the necessary database modifications and route registrations.

## Database Migrations

When adding new models and relationships, you may need to migrate your database:

```python
# In your app.py file, inside the app context
with app.app_context():
    # Drop all tables (WARNING: This will delete all data)
    db.drop_all()
    # Create all tables with new models
    db.create_all()
```

For production environments, use a proper migration tool like Flask-Migrate.

## Security Considerations

- Always use a strong, unique `SECRET_KEY` in your Flask application
- Store sensitive information like API keys in environment variables
- Consider implementing rate limiting for API endpoints and authentication routes
- Use HTTPS in production environments to protect user data

## Customization

Each module can be customized to fit your specific needs:

- Modify the HTML templates for different styling
- Adjust the database models to include additional fields
- Extend the route functions to add custom behavior

## Example: Adding User Profiles

Here's a quick example of how to integrate the User Profiles module:

```python
from user_profiles import init_user_profiles

# Initialize the module (typically in app.py)
init_user_profiles(app, User)
```

After integration, users can:
- View profiles at `/profile/<username>`
- Edit their profile at `/profile/edit`
- Upload profile pictures

## Contributing

Feel free to contribute to these modules by:
- Reporting bugs or suggesting features
- Submitting pull requests with improvements
- Creating new modules that integrate with the existing ones

## License

This project is licensed under the MIT License - see the LICENSE file for details.
