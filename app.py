from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitter_clone.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key

# Initialize database, bcrypt, and login manager
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Tweet Model
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(280), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref=db.backref('tweets', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    tweets = Tweet.query.order_by(Tweet.timestamp.desc()).all()
    return render_template("index.html", tweets=tweets)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/tweet", methods=["POST"])
@login_required
def post_tweet():
    content = request.form["content"]
    if len(content) > 280:
        flash("Tweet exceeds 280 characters!", "danger")
        return redirect(url_for("home"))

    tweet = Tweet(user_id=current_user.id, content=content)
    db.session.add(tweet)
    db.session.commit()
    flash("Tweet posted!", "success")
    return redirect(url_for("home"))


# Initialize all modules
def init_modules():
    # Import all feature modules
    from user_profiles import init_user_profiles
    from follow_system import init_follow_system
    from tweet_interactions import init_tweet_interactions
    from search_functionality import init_search_functionality
    from api_endpoints import init_api
    from media_support import init_media_support
    from notifications import init_notifications
    from security_enhancements import init_security
    
    # Initialize each module
    init_user_profiles(app, User)
    init_follow_system(app, User)
    init_tweet_interactions(app, db, User, Tweet)
    init_search_functionality(app, db, Tweet, User)
    init_api(app, db, User, Tweet)
    init_media_support(app, db, Tweet)
    init_notifications(app, db, User, Tweet)
    init_security(app, db, User, bcrypt)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures database tables are created inside the application context
    app.run(debug=True)