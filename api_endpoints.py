# api_endpoints.py
from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from app import db, Tweet, User
from werkzeug.security import generate_password_hash
import datetime
from functools import wraps

api = Blueprint('api', __name__)

# API Authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # This is a simple token implementation
            # In production, use a proper token like JWT
            user = User.query.filter_by(api_token=token).first()
            if not user:
                return jsonify({'message': 'Invalid token!'}), 401
        except:
            return jsonify({'message': 'Invalid token!'}), 401
            
        return f(user, *args, **kwargs)
    
    return decorated

# Add API token to User model
# from api_endpoints import add_api_token
def add_api_token(User):
    import secrets
    User.api_token = db.Column(db.String(100), unique=True, nullable=True)
    
    # Method to generate a token
    def generate_token(self):
        self.api_token = secrets.token_urlsafe(32)
        db.session.commit()
        return self.api_token
        
    User.generate_token = generate_token
    return User

# API Routes
@api.route('/api/tweets', methods=['GET'])
def get_tweets():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    tweets = Tweet.query.order_by(Tweet.timestamp.desc()).limit(limit).offset(offset).all()
    
    result = []
    for tweet in tweets:
        tweet_data = {
            'id': tweet.id,
            'content': tweet.content,
            'timestamp': tweet.timestamp.isoformat(),
            'user': {
                'id': tweet.user.id,
                'username': tweet.user.username
            }
        }
        result.append(tweet_data)
    
    return jsonify(result)

@api.route('/api/tweets/<int:tweet_id>', methods=['GET'])
def get_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)
    
    tweet_data = {
        'id': tweet.id,
        'content': tweet.content,
        'timestamp': tweet.timestamp.isoformat(),
        'user': {
            'id': tweet.user.id,
            'username': tweet.user.username
        }
    }
    
    # Add interaction counts if available
    if hasattr(tweet, 'get_like_count'):
        tweet_data['like_count'] = tweet.get_like_count()
    
    if hasattr(tweet, 'get_reply_count'):
        tweet_data['reply_count'] = tweet.get_reply_count()
        
    if hasattr(tweet, 'get_retweet_count'):
        tweet_data['retweet_count'] = tweet.get_retweet_count()
    
    return jsonify(tweet_data)

@api.route('/api/tweets', methods=['POST'])
@token_required
def create_tweet(current_user):
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'message': 'No content provided!'}), 400
        
    content = data.get('content')
    
    if len(content) > 280:
        return jsonify({'message': 'Tweet exceeds 280 characters!'}), 400
        
    tweet = Tweet(user_id=current_user.id, content=content)
    
    # Process hashtags if search module is installed
    try:
        from search_functionality import process_hashtags, Hashtag
        tweet = process_hashtags(content, tweet, Hashtag)
    except ImportError:
        pass
    
    db.session.add(tweet)
    db.session.commit()
    
    return jsonify({'message': 'Tweet created!', 'id': tweet.id}), 201

@api.route('/api/users/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    user_data = {
        'id': user.id,
        'username': user.username
    }
    
    # Add profile fields if available
    if hasattr(user, 'bio'):
        user_data['bio'] = user.bio
        
    if hasattr(user, 'profile_picture'):
        user_data['profile_picture'] = user.profile_picture
    
    return jsonify(user_data)

@api.route('/api/users/<username>/tweets', methods=['GET'])
def get_user_tweets(username):
    user = User.query.filter_by(username=username).first_or_404()
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    tweets = Tweet.query.filter_by(user_id=user.id).order_by(Tweet.timestamp.desc()).limit(limit).offset(offset).all()
    
    result = []
    for tweet in tweets:
        tweet_data = {
            'id': tweet.id,
            'content': tweet.content,
            'timestamp': tweet.timestamp.isoformat()
        }
        result.append(tweet_data)
    
    return jsonify(result)

@api.route('/api/token', methods=['POST'])
@login_required
def get_token():
    token = current_user.generate_token()
    return jsonify({'token': token})

# Documentation route
@api.route('/api/docs')
def api_docs():
    return render_template('api_docs.html')

# Function to initialize the blueprint
def init_api(app, db_obj, user_model, tweet_model):
    global db, User, Tweet
    db = db_obj 
    User = user_model
    Tweet = tweet_model
    
    add_api_token(User)
    app.register_blueprint(api)
