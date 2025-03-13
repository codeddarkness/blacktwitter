# security_enhancements.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db, User, bcrypt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import datetime
from functools import wraps
import re

security = Blueprint('security', __name__)

# Rate limiting helper
# from security_enhancements import setup_rate_limiting
def setup_rate_limiting(app):
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        
        # Apply specific limits to login route
        limiter.limit("10 per minute")(app.view_functions['login'])
        
        return limiter
    except ImportError:
        app.logger.warning("Flask-Limiter not installed. Rate limiting disabled.")
        return None

# Add CSRF protection
# from security_enhancements import setup_csrf_protection
def setup_csrf_protection(app):
    try:
        # from flask_wtf.csrf import CSRFProtect
        
        # csrf = CSRFProtect(app)
        return csrf
    except ImportError:
        app.logger.warning("Flask-WTF not installed. CSRF protection disabled.")
        return None

# Password reset functionality
# from security_enhancements import add_password_reset
def add_password_reset(app, user_model):
    # Generate a secure token
    def get_reset_token(user, expires_sec=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': user.id})
    
    # Verify the token
    def verify_reset_token(token, expires_sec=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except (SignatureExpired, BadSignature):
            return None
        return User.query.get(user_id)
    
    # Add methods to User class
    User.get_reset_token = get_reset_token
    User.verify_reset_token = staticmethod(verify_reset_token)
    
    return User

# Two-factor authentication
# from security_enhancements import add_two_factor_auth
def add_two_factor_auth(db, User):
    # Add necessary fields to User model
    User.two_factor_enabled = db.Column(db.Boolean, nullable=False, default=False)
    User.two_factor_secret = db.Column(db.String(32), nullable=True)
    
    try:
        import pyotp
        
        # Add methods to User class
        def generate_totp_secret(self):
            self.two_factor_secret = pyotp.random_base32()
            db.session.commit()
            return self.two_factor_secret
            
        def verify_totp(self, token):
            if not self.two_factor_secret:
                return False
            totp = pyotp.TOTP(self.two_factor_secret)
            return totp.verify(token)
            
        def get_totp_uri(self):
            if not self.two_factor_secret:
                return None
            totp = pyotp.TOTP(self.two_factor_secret)
            return totp.provisioning_uri(name=self.username, issuer_name="Twitter Clone")
        
        User.generate_totp_secret = generate_totp_secret
        User.verify_totp = verify_totp
        User.get_totp_uri = get_totp_uri
        
        return True
    except ImportError:
        return False

# Password strength validator
def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    
    return True, "Password meets strength requirements."

# Routes for security features
@security.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Send reset email
            token = user.get_reset_token()
            reset_url = url_for('security.reset_token', token=token, _external=True)
            
            # Send email if flask-mail is configured
            if hasattr(current_app, 'mail'):
                from flask_mail import Message
                msg = Message('Password Reset Request',
                              recipients=[user.email])
                msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, please ignore this email.
'''
                current_app.mail.send(msg)
            
            flash('An email has been sent with instructions to reset your password.', 'info')
        else:
            flash('No account found with that email.', 'warning')
            
        return redirect(url_for('login'))
    
    return render_template('reset_request.html')

@security.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    user = User.verify_reset_token(token)
    
    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('security.reset_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_token.html')
        
        # Validate password strength
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            flash(message, 'danger')
            return render_template('reset_token.html')
        
        # Hash and set new password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_token.html')

@security.route('/2fa/setup', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if not hasattr(User, 'two_factor_enabled'):
        flash('Two-factor authentication is not available.', 'warning')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        token = request.form.get('token')
        
        if current_user.verify_totp(token):
            current_user.two_factor_enabled = True
            db.session.commit()
            flash('Two-factor authentication has been enabled.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid token. Please try again.', 'danger')
    
    # Generate secret if not already set
    if not current_user.two_factor_secret:
        current_user.generate_totp_secret()
    
    # Generate QR code
    try:
        import qrcode
        import io
        import base64
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(current_user.get_totp_uri())
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered)
        qr_code = base64.b64encode(buffered.getvalue()).decode('utf-8')
    except ImportError:
        qr_code = None
    
    return render_template('setup_2fa.html', 
                           secret=current_user.two_factor_secret, 
                           qr_code=qr_code)

@security.route('/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    if not hasattr(User, 'two_factor_enabled'):
        flash('Two-factor authentication is not available.', 'warning')
        return redirect(url_for('home'))
    
    password = request.form.get('password')
    
    if bcrypt.check_password_hash(current_user.password, password):
        current_user.two_factor_enabled = False
        current_user.two_factor_secret = None
        db.session.commit()
        flash('Two-factor authentication has been disabled.', 'success')
    else:
        flash('Incorrect password.', 'danger')
    
    return redirect(url_for('security.settings'))

@security.route('/settings')
@login_required
def settings():
    return render_template('security_settings.html')

@security.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not bcrypt.check_password_hash(current_user.password, current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('security.settings'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('security.settings'))
    
    # Validate password strength
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        flash(message, 'danger')
        return redirect(url_for('security.settings'))
    
    # Update password
    current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    
    flash('Your password has been updated.', 'success')
    return redirect(url_for('security.settings'))

# Function to initialize the blueprint
def init_security(app, db_obj, user_model, bcrypt_obj):
    global db, User, bcrypt
    db = db_obj
    User = user_model
    bcrypt = bcrypt_obj
    
    # Set up rate limiting
    setup_rate_limiting(app)
    
    # Set up CSRF protection
    setup_csrf_protection(app)
    
    # Add password reset functionality
    add_password_reset(app, User)
    
    # Add two-factor authentication if possible
    has_2fa = add_two_factor_auth(db, User)
    
    # Register the blueprint
    app.register_blueprint(security)
    
    # Replace the original register route
    original_register = app.view_functions.get('register')
    
    if original_register:
        def register_with_validation():
            if request.method == "POST":
                username = request.form["username"]
                password = request.form["password"]
                email = request.form.get("email")
                
                # Check if username exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    flash("Username already exists. Please choose another one.", "danger")
                    return render_template("register.html")
                
                # Validate password strength
                is_valid, message = validate_password_strength(password)
                if not is_valid:
                    flash(message, "danger")
                    return render_template("register.html")
                
                # Create new user
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
                user = User(username=username, password=hashed_password)
                
                # Add email if field exists
                if hasattr(User, 'email') and email:
                    user.email = email
                
                db.session.add(user)
                db.session.commit()
                
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for("login"))
                
            return original_register()
        
        app.view_functions['register'] = register_with_validation
    
    # Modify login route to support 2FA if enabled
    if has_2fa:
        original_login = app.view_functions.get('login')
        
        if original_login:
            def login_with_2fa():
                if request.method == "POST":
                    username = request.form["username"]
                    password = request.form["password"]
                    
                    user = User.query.filter_by(username=username).first()
                    if user and bcrypt.check_password_hash(user.password, password):
                        # Check if 2FA is enabled for this user
                        if user.two_factor_enabled:
                            # Store user ID in session for 2FA verification
                            from flask import session
                            session['_2fa_user_id'] = user.id
                            return redirect(url_for('security.verify_2fa'))
                        
                        # Regular login if 2FA not enabled
                        from flask_login import login_user
                        login_user(user)
                        flash("Login successful!", "success")
                        return redirect(url_for("home"))
                    else:
                        flash("Invalid username or password", "danger")
                
                return original_login()
            
            try:
                try:
                app.view_functions['login'] = login_with_2fa
            except Exception as e:
                app.logger.error(f"Failed to replace login function: {str(e)}")
                print("Successfully replaced login function with 2FA-enabled version")
            except Exception as e:
                print("Error replacing login function: " + str(e))
                # As a fallback, define a new route
                @app.route('/login2fa', methods=['GET', 'POST'])
                def login2fa():
                    return login_with_2fa()
            
            # Add 2FA verification route
            @security.route('/verify_2fa', methods=['GET', 'POST'])
            def verify_2fa():
                from flask import session
                
                # Check if user is in 2FA flow
                if '_2fa_user_id' not in session:
                    return redirect(url_for('login'))
                
                user_id = session['_2fa_user_id']
                user = User.query.get(user_id)
                
                if not user:
                    session.pop('_2fa_user_id', None)
                    return redirect(url_for('login'))
                
                if request.method == 'POST':
                    token = request.form.get('token')
                    
                    if user.verify_totp(token):
                        # 2FA verification successful
                        from flask_login import login_user
                        login_user(user)
                        
                        # Clear 2FA session
                        session.pop('_2fa_user_id', None)
                        
                        flash("Login successful!", "success")
                        return redirect(url_for("home"))
                    else:
                        flash("Invalid verification code.", "danger")
                
                return render_template('verify_2fa.html')
    
    return app