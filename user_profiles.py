# user_profiles.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db, User

user_profiles = Blueprint('user_profiles', __name__)

# Add profile fields to User model in your main app
# from user_profiles import add_profile_fields
def add_profile_fields(User):
    User.bio = db.Column(db.String(200), nullable=True)
    User.profile_picture = db.Column(db.String(100), nullable=True, default='default.jpg')
    return User

# Create profile pictures directory
def create_profile_picture_dir():
    os.makedirs(os.path.join(current_app.root_path, 'static/profile_pics'), exist_ok=True)

@user_profiles.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    tweets = user.tweets.order_by(db.desc('timestamp')).all()
    return render_template("profile.html", user=user, tweets=tweets)

@user_profiles.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.bio = request.form.get("bio", "")
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            picture = request.files['profile_picture']
            if picture.filename != '':
                filename = secure_filename(f"{current_user.id}_{picture.filename}")
                picture_path = os.path.join(current_app.root_path, 'static/profile_pics', filename)
                picture.save(picture_path)
                current_user.profile_picture = filename
        
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('user_profiles.profile', username=current_user.username))
    
    return render_template("edit_profile.html")

# Function to initialize the blueprint
def init_user_profiles(app, user_model):
    add_profile_fields(user_model)
    with app.app_context():
        create_profile_picture_dir()
    app.register_blueprint(user_profiles)
