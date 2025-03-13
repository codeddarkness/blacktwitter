# follow_system.py
from flask import Blueprint, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db, User

follow_system = Blueprint('follow_system', __name__)

# Define the followers association table
# from follow_system import create_followers_table, add_follow_relationships
def create_followers_table(db):
    followers = db.Table('followers',
        db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
        db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
    )
    return followers

def add_follow_relationships(User, followers_table):
    User.followed = db.relationship(
        'User', secondary=followers_table,
        primaryjoin=(followers_table.c.follower_id == User.id),
        secondaryjoin=(followers_table.c.followed_id == User.id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    # Add helper methods to User model
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return True
        return False
            
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return True
        return False
            
    def is_following(self, user):
        return self.followed.filter(followers_table.c.followed_id == user.id).count() > 0
    
    def followed_tweets(self):
        # Import Tweet model here to avoid circular imports
        from app import Tweet
        return Tweet.query.join(
            followers_table, (followers_table.c.followed_id == Tweet.user_id)
        ).filter(
            followers_table.c.follower_id == self.id
        ).order_by(Tweet.timestamp.desc())
    
    # Add methods to User class
    User.follow = follow
    User.unfollow = unfollow
    User.is_following = is_following
    User.followed_tweets = followed_tweets
    
    return User

# Routes for follow actions
@follow_system.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash("You cannot follow yourself!")
        return redirect(url_for('user_profiles.profile', username=username))
    
    if current_user.follow(user):
        db.session.commit()
        flash(f'You are now following {username}!')
        
    return redirect(url_for('user_profiles.profile', username=username))

@follow_system.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash("You cannot unfollow yourself!")
        return redirect(url_for('user_profiles.profile', username=username))
    
    if current_user.unfollow(user):
        db.session.commit()
        flash(f'You have unfollowed {username}.')
        
    return redirect(url_for('user_profiles.profile', username=username))

@follow_system.route('/feed')
@login_required
def feed():
    tweets = current_user.followed_tweets().all()
    return render_template('feed.html', tweets=tweets)

# Function to initialize the blueprint
def init_follow_system(app, user_model):
    followers_table = create_followers_table(db)
    add_follow_relationships(user_model, followers_table)
    app.register_blueprint(follow_system)
