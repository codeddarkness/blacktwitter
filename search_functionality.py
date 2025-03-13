# search_functionality.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db, Tweet, User
import re

search_functionality = Blueprint('search_functionality', __name__)

# Add hashtag extraction functionality
# from search_functionality import extract_hashtags, add_hashtag_model
def extract_hashtags(content):
    # Find all hashtags in the tweet content
    hashtag_pattern = re.compile(r'#(\w+)')
    return hashtag_pattern.findall(content)

def add_hashtag_model(db):
    # Association table for hashtags and tweets
    tweet_hashtags = db.Table('tweet_hashtags',
        db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id'), primary_key=True),
        db.Column('hashtag_id', db.Integer, db.ForeignKey('hashtag.id'), primary_key=True)
    )
    
    class Hashtag(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        text = db.Column(db.String(50), unique=True, nullable=False)
        tweets = db.relationship('Tweet', secondary=tweet_hashtags, 
                                backref=db.backref('hashtags', lazy='dynamic'))
        
        @classmethod
        def get_or_create(cls, tag_text):
            tag = cls.query.filter_by(text=tag_text.lower()).first()
            if not tag:
                tag = cls(text=tag_text.lower())
                db.session.add(tag)
            return tag
    
    return Hashtag, tweet_hashtags

# Function to process hashtags in tweets
def process_hashtags(tweet_content, tweet_obj, Hashtag):
    hashtags = extract_hashtags(tweet_content)
    for tag in hashtags:
        hashtag = Hashtag.get_or_create(tag)
        tweet_obj.hashtags.append(hashtag)
    return tweet_obj

# Routes for search
@search_functionality.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', query='', tweets=[], users=[], hashtags=[])
    
    # Search for tweets
    tweets = Tweet.query.filter(Tweet.content.ilike(f'%{query}%')).order_by(Tweet.timestamp.desc()).all()
    
    # Search for users
    users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    
    # Search for hashtags
    from search_functionality import Hashtag
    if query.startswith('#'):
        query_without_hash = query[1:]
        hashtags = Hashtag.query.filter(Hashtag.text.ilike(f'%{query_without_hash}%')).all()
    else:
        hashtags = Hashtag.query.filter(Hashtag.text.ilike(f'%{query}%')).all()
    
    return render_template('search.html', query=query, tweets=tweets, users=users, hashtags=hashtags)

@search_functionality.route('/hashtag/<tag>')
def hashtag(tag):
    from search_functionality import Hashtag
    hashtag = Hashtag.query.filter_by(text=tag.lower()).first_or_404()
    tweets = hashtag.tweets.order_by(Tweet.timestamp.desc()).all()
    return render_template('hashtag.html', hashtag=hashtag, tweets=tweets)

@search_functionality.route('/trending')
def trending():
    # Get trending hashtags (most used in the last 24 hours)
    from datetime import datetime, timedelta
    from search_functionality import Hashtag, tweet_hashtags
    
    day_ago = datetime.utcnow() - timedelta(days=1)
    
    # This requires a more complex query with a subquery
    trending = db.session.query(Hashtag, db.func.count(tweet_hashtags.c.tweet_id).label('count'))\
        .join(tweet_hashtags)\
        .join(Tweet, Tweet.id == tweet_hashtags.c.tweet_id)\
        .filter(Tweet.timestamp > day_ago)\
        .group_by(Hashtag.id)\
        .order_by(db.desc('count'))\
        .limit(10)\
        .all()
    
    return render_template('trending.html', trending=trending)

# Function to initialize the blueprint
def init_search_functionality(app, db_obj, tweet_model, user_model):
    global db, Tweet, User
    db = db_obj
    Tweet = tweet_model
    User = user_model
    
    # Create models
    Hashtag, tweet_hashtags = add_hashtag_model(db)
    globals()['Hashtag'] = Hashtag
    globals()['tweet_hashtags'] = tweet_hashtags
    
    # Modify tweet post function to extract and store hashtags
    original_post_tweet = app.view_functions['post_tweet']
    
    def post_tweet_with_hashtags():
        if request.method == "POST":
            content = request.form["content"]
            if len(content) > 280:
                flash("Tweet exceeds 280 characters!", "danger")
                return redirect(url_for("home"))
    
            tweet = Tweet(user_id=current_user.id, content=content)
            tweet = process_hashtags(content, tweet, Hashtag)
            db.session.add(tweet)
            db.session.commit()
            flash("Tweet posted!", "success")
        return redirect(url_for("home"))
    
    app.view_functions['post_tweet'] = post_tweet_with_hashtags
    
    app.register_blueprint(search_functionality)
