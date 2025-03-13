# Twitter Clone Web Application

A feature-rich, modular Twitter clone built with Flask, showcasing modern web development practices.

## 🚀 Features

### Core Functionality
- User Authentication (Registration, Login, Logout)
- Tweet Creation and Viewing
- User Profiles
- Follow System
- Tweet Interactions (Like, Reply, Retweet)

### Advanced Features
1. **User Profiles**
   - Customizable bio
   - Profile picture upload
   - Edit profile functionality

2. **Security Enhancements**
   - Password reset
   - Two-factor authentication (2FA)
   - CSRF protection
   - Rate limiting
   - Password strength validation

3. **Social Features**
   - Follow/Unfollow users
   - Personalized feed
   - Hashtag support
   - Trending topics

4. **Media Support**
   - Image and video uploads
   - URL previews
   - Media attachments in tweets

5. **Search & Discovery**
   - Search tweets, users, and hashtags
   - Trending hashtags
   - User discovery

6. **Notifications**
   - Like, follow, reply, and mention notifications
   - Email notifications
   - Configurable notification settings

7. **API Support**
   - RESTful API endpoints
   - API token authentication
   - Comprehensive API documentation

## 🛠 Technology Stack
- **Backend**: Flask
- **Database**: SQLAlchemy (SQLite)
- **Authentication**: Flask-Login, Bcrypt
- **Frontend**: Bootstrap 5
- **Additional Libraries**: 
  - Flask-WTF
  - Flask-Limiter
  - PyOTP (Two-Factor Authentication)
  - Requests
  - BeautifulSoup

## 📦 Project Structure
```
twitter-clone/
│
├── app.py                  # Main application file
├── instance/               # SQLite database
├── static/
│   ├── uploads/            # User-uploaded media
│   └── profile_pics/       # Profile pictures
│
├── templates/              # HTML templates
│
├── utils/                  # Utility scripts
│   ├── git-manager.sh
│   ├── sanity_check.py
│   └── ...
│
└── modules/
    ├── user_profiles.py
    ├── follow_system.py
    ├── tweet_interactions.py
    └── ...
```

## 🔧 Setup and Installation

### Prerequisites
- Python 3.8+
- pip

### Installation Steps
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/twitter-clone.git
   cd twitter-clone
   ```

2. Create a virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application
   ```bash
   python app.py
   ```

### Optional: Project Cleanup
Run the cleanup script to organize project files:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

## 🔒 Security Features
- CSRF Protection
- Rate Limiting
- Two-Factor Authentication
- Secure Password Storage
- Email-based Password Reset

## 🚧 Feature Roadmap
- [ ] Direct Messaging
- [ ] Advanced Analytics
- [ ] More Robust Error Handling
- [ ] Enhanced Media Processing
- [ ] Social Share Features

## 📜 License
This project is open-source and available under the MIT License.

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support
For issues and questions, please open a GitHub issue or contact the maintainer.
