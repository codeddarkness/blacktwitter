# notifications.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db, User, Tweet
import datetime

notifications = Blueprint('notifications', __name__)

# Add notification model
# from notifications import create_notification_model
def create_notification_model(db):
    class Notification(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        type = db.Column(db.String(20), nullable=False)  # 'like', 'follow', 'reply', 'retweet', 'mention'
        tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=True)
        timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
        read = db.Column(db.Boolean, default=False)
        
        recipient = db.relationship('User', foreign_keys=[recipient_id],
                               backref=db.backref('notifications_received', lazy='dynamic'))
        sender = db.relationship('User', foreign_keys=[sender_id],
                               backref=db.backref('notifications_sent', lazy='dynamic'))
        tweet = db.relationship('Tweet', backref=db.backref('notifications', lazy='dynamic'))
    
    # Add methods to User model for notification counts
    def add_notification_methods(User):
        def get_unread_notification_count(self):
            return Notification.query.filter_by(recipient_id=self.id, read=False).count()
            
        User.get_unread_notification_count = get_unread_notification_count
        return User
    
    return Notification, add_notification_methods

# Add email configuration
# from notifications import configure_email
def configure_email(app):
    # Configure Flask-Mail if installed
    try:
        from flask_mail import Mail, Message
        
        app.config['MAIL_SERVER'] = 'smtp.example.com'  # Update with your mail server
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Update with your email
        app.config['MAIL_PASSWORD'] = 'your-password'  # Update with your password
        app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@example.com'  # Update with your sender email
        
        mail = Mail(app)
        return mail
    except ImportError:
        app.logger.warning("Flask-Mail not installed. Email notifications disabled.")
        return None

# Helper function to create notifications
def create_notification(recipient_id, sender_id, type, tweet_id=None):
    from notifications import Notification
    
    # Don't notify yourself
    if recipient_id == sender_id:
        return None
    
    notification = Notification(
        recipient_id=recipient_id,
        sender_id=sender_id,
        type=type,
        tweet_id=tweet_id
    )
    db.session.add(notification)
    db.session.commit()
    
    # Send email notification if enabled
    if hasattr(current_app, 'mail'):
        try:
            recipient = User.query.get(recipient_id)
            sender = User.query.get(sender_id)
            
            if recipient and sender and hasattr(recipient, 'email') and recipient.email:
                from flask_mail import Message
                
                subject_map = {
                    'like': f"{sender.username} liked your tweet",
                    'follow': f"{sender.username} followed you",
                    'reply': f"{sender.username} replied to your tweet",
                    'retweet': f"{sender.username} retweeted your tweet",
                    'mention': f"{sender.username} mentioned you in a tweet"
                }
                
                msg = Message(
                    subject=subject_map.get(type, "New notification"),
                    recipients=[recipient.email]
                )
                
                # Create appropriate message body
                if tweet_id:
                    tweet = Tweet.query.get(tweet_id)
                    tweet_url = url_for('tweet_interactions.view_tweet', tweet_id=tweet_id, _external=True)
                    msg.body = f"{subject_map.get(type, 'New notification')}\n\n"
                    if tweet:
                        msg.body += f"Tweet: {tweet.content[:50]}...\n\n"
                    msg.body += f"Click here to view: {tweet_url}"
                else:
                    profile_url = url_for('user_profiles.profile', username=sender.username, _external=True)
                    msg.body = f"{subject_map.get(type, 'New notification')}\n\nClick here to view: {profile_url}"
                
                current_app.mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email notification: {str(e)}")
    
    return notification

# Function to extract mentions from tweet content
def extract_mentions(content):
    mention_pattern = r'@(\w+)'
    import re
    return re.findall(mention_pattern, content)

# Function to process mentions in tweets
def process_mentions(tweet):
    mentions = extract_mentions(tweet.content)
    for username in mentions:
        user = User.query.filter_by(username=username).first()
        if user:
            create_notification(user.id, tweet.user_id, 'mention', tweet.id)

# Routes for notifications
@notifications.route('/notifications')
@login_required
def view_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    from notifications import Notification
    notifications = Notification.query.filter_by(recipient_id=current_user.id)\
        .order_by(Notification.timestamp.desc())\
        .paginate(page=page, per_page=per_page)
    
    # Mark all as read
    unread = Notification.query.filter_by(recipient_id=current_user.id, read=False).all()
    for notification in unread:
        notification.read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifications)

@notifications.route('/notifications/count')
@login_required
def notification_count():
    count = current_user.get_unread_notification_count()
    return jsonify({'count': count})

@notifications.route('/notifications/settings', methods=['GET', 'POST'])
@login_required
def notification_settings():
    if request.method == 'POST':
        # Update notification settings
        if hasattr(current_user, 'notification_settings'):
            current_user.notification_settings = {
                'email_likes': request.form.get('email_likes') == 'on',
                'email_follows': request.form.get('email_follows') == 'on',
                'email_replies': request.form.get('email_replies') == 'on',
                'email_retweets': request.form.get('email_retweets') == 'on',
                'email_mentions': request.form.get('email_mentions') == 'on'
            }
            db.session.commit()
            flash('Notification settings updated!', 'success')
        
        return redirect(url_for('notifications.notification_settings'))
    
    return render_template('notification_settings.html')

# Function to initialize the blueprint
def init_notifications(app, db_obj, user_model, tweet_model):
    global db, User, Tweet
    db = db_obj
    User = user_model
    Tweet = tweet_model
    
    # Create notification model
    Notification, add_notification_methods = create_notification_model(db)
    add_notification_methods(User)
    globals()['Notification'] = Notification
    
    # Configure email if flask-mail is installed
    mail = configure_email(app)
    if mail:
        app.mail = mail
        
        # Add email field to User model if not present
        if not hasattr(User, 'email'):
            User.email = db.Column(db.String(120), unique=True, nullable=True)
        
        # Add notification settings to User model
        if not hasattr(User, 'notification_settings'):
            import json
            User.notification_settings = db.Column(db.Text, default=json.dumps({
                'email_likes': True,
                'email_follows': True,
                'email_replies': True,
                'email_retweets': True,
                'email_mentions': True
            }))
    
    # Hook into existing modules
    
    # Hook into tweet creation to process mentions
    original_post_tweet = app.view_functions.get('post_tweet')
    if original_post_tweet:
        def post_tweet_with_notifications():
            if request.method == "POST":
                content = request.form["content"]
                if len(content) > 280:
                    flash("Tweet exceeds 280 characters!", "danger")
                    return redirect(url_for("home"))
        
                tweet = Tweet(user_id=current_user.id, content=content)
                db.session.add(tweet)
                db.session.commit()
                
                # Process mentions
                process_mentions(tweet)
                
                flash("Tweet posted!", "success")
                return redirect(url_for("home"))
            
            return original_post_tweet()
        
        app.view_functions['post_tweet'] = post_tweet_with_notifications
    
    # Hook into like functionality if it exists
    try:
        from tweet_interactions import like_tweet as original_like_tweet
        
        def like_tweet_with_notification(tweet_id):
            result = original_like_tweet(tweet_id)
            
            # Check if this was a like (not unlike)
            if isinstance(result, tuple) and len(result) > 0:
                data = result[0].get_json()
                if data.get('status') == 'liked':
                    tweet = Tweet.query.get(tweet_id)
                    if tweet:
                        create_notification(tweet.user_id, current_user.id, 'like', tweet_id)
            
            return result
        
        if hasattr(app.view_functions, 'tweet_interactions.like_tweet'):
            app.view_functions['tweet_interactions.like_tweet'] = like_tweet_with_notification
    except ImportError:
        pass
    
    # Hook into reply functionality if it exists
    try:
        from tweet_interactions import reply_to_tweet as original_reply_to_tweet
        
        def reply_to_tweet_with_notification(tweet_id):
            result = original_reply_to_tweet(tweet_id)
            
            tweet = Tweet.query.get(tweet_id)
            if tweet:
                # Notify the original tweet author
                create_notification(tweet.user_id, current_user.id, 'reply', tweet_id)
                
                # Process mentions in the reply
                replies = tweet.replies.order_by(Tweet.timestamp.desc()).first()
                if replies:
                    process_mentions(replies)
            
            return result
        
        if hasattr(app.view_functions, 'tweet_interactions.reply_to_tweet'):
            app.view_functions['tweet_interactions.reply_to_tweet'] = reply_to_tweet_with_notification
    except ImportError:
        pass
    
    # Hook into follow functionality if it exists
    try:
        from follow_system import follow as original_follow
        
        def follow_with_notification(username):
            result = original_follow(username)
            
            user = User.query.filter_by(username=username).first()
            if user:
                create_notification(user.id, current_user.id, 'follow')
            
            return result
        
        if hasattr(app.view_functions, 'follow_system.follow'):
            app.view_functions['follow_system.follow'] = follow_with_notification
    except ImportError:
        pass
    
    app.register_blueprint(notifications)
