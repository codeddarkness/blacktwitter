# tweet_interactions.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db, Tweet, User

tweet_interactions = Blueprint('tweet_interactions', __name__)

# Create models for likes, replies, and retweets
# from tweet_interactions import create_interaction_models
def create_interaction_models(db, User, Tweet):
    class Like(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)
        timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
        user = db.relationship('User', backref=db.backref('likes', lazy='dynamic'))
        tweet = db.relationship('Tweet', backref=db.backref('likes', lazy='dynamic'))
        
        __table_args__ = (db.UniqueConstraint('user_id', 'tweet_id', name='_user_tweet_like_uc'),)
    
    # Add reply functionality to Tweet model
    Tweet.parent_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=True)
    Tweet.replies = db.relationship(
        'Tweet', backref=db.backref('parent', remote_side=[Tweet.id]),
        lazy='dynamic')
    
    # Add is_retweet and original_tweet_id to Tweet model
    Tweet.is_retweet = db.Column(db.Boolean, default=False)
    Tweet.original_tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=True)
    Tweet.retweets = db.relationship(
        'Tweet', backref=db.backref('original_tweet', remote_side=[Tweet.id]),
        lazy='dynamic', foreign_keys=[original_tweet_id])
        
    # Add methods to Tweet class for interaction counts
    def get_like_count(self):
        return self.likes.count()
    
    def get_reply_count(self):
        return self.replies.count()
    
    def get_retweet_count(self):
        return self.retweets.count()
    
    def is_liked_by(self, user):
        return self.likes.filter_by(user_id=user.id).count() > 0
    
    Tweet.get_like_count = get_like_count
    Tweet.get_reply_count = get_reply_count
    Tweet.get_retweet_count = get_retweet_count
    Tweet.is_liked_by = is_liked_by
    
    return Like

# Routes for tweet interactions
@tweet_interactions.route('/tweet/<int:tweet_id>')
def view_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)
    replies = tweet.replies.order_by(Tweet.timestamp.desc()).all()
    return render_template('view_tweet.html', tweet=tweet, replies=replies)

@tweet_interactions.route('/tweet/<int:tweet_id>/like', methods=['POST'])
@login_required
def like_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)
    
    from tweet_interactions import Like
    existing_like = Like.query.filter_by(user_id=current_user.id, tweet_id=tweet_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'status': 'unliked', 'count': tweet.get_like_count()})
    else:
        like = Like(user_id=current_user.id, tweet_id=tweet_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'status': 'liked', 'count': tweet.get_like_count()})

@tweet_interactions.route('/tweet/<int:tweet_id>/reply', methods=['POST'])
@login_required
def reply_to_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)
    content = request.form.get('content')
    
    if len(content) > 280:
        flash("Reply exceeds 280 characters!", "danger")
        return redirect(url_for('tweet_interactions.view_tweet', tweet_id=tweet_id))
    
    reply = Tweet(user_id=current_user.id, content=content, parent_id=tweet_id)
    db.session.add(reply)
    db.session.commit()
    flash("Reply posted!", "success")
    return redirect(url_for('tweet_interactions.view_tweet', tweet_id=tweet_id))

@tweet_interactions.route('/tweet/<int:tweet_id>/retweet', methods=['POST'])
@login_required
def retweet(tweet_id):
    original_tweet = Tweet.query.get_or_404(tweet_id)
    quote_content = request.form.get('content', '')
    
    # Check if already retweeted
    existing_retweet = Tweet.query.filter_by(
        user_id=current_user.id, 
        is_retweet=True, 
        original_tweet_id=tweet_id
    ).first()
    
    if existing_retweet:
        flash("You've already retweeted this!", "warning")
        return redirect(url_for('home'))
    
    # Create retweet
    content = quote_content if quote_content else f"RT @{original_tweet.user.username}: {original_tweet.content}"
    
    retweet = Tweet(
        user_id=current_user.id,
        content=content,
        is_retweet=True,
        original_tweet_id=tweet_id
    )
    
    db.session.add(retweet)
    db.session.commit()
    flash("Retweeted successfully!", "success")
    return redirect(url_for('home'))

# Function to initialize the blueprint
def init_tweet_interactions(app, db_obj, user_model, tweet_model):
    global db, User, Tweet
    db = db_obj
    User = user_model
    Tweet = tweet_model
    
    # Create models
    Like = create_interaction_models(db, User, Tweet)
    globals()['Like'] = Like
    
    app.register_blueprint(tweet_interactions)
