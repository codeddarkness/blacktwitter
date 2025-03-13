# media_support.py
from flask import Blueprint, request, current_app, url_for, redirect, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import re
from app import db, Tweet

media_support = Blueprint('media_support', __name__)

# Add media relationship to Tweet model
# from media_support import add_media_model
def add_media_model(db, Tweet):
    class Media(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)
        filename = db.Column(db.String(100), nullable=False)
        media_type = db.Column(db.String(10), nullable=False)  # 'image', 'gif', 'video'
        timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
        
        tweet = db.relationship('Tweet', backref=db.backref('media', lazy=True))
    
    # Create directory for media uploads
    os.makedirs(os.path.join(current_app.root_path, 'static/uploads'), exist_ok=True)
    
    return Media

# URL Preview functionality
# from media_support import add_url_preview_model
def add_url_preview_model(db, Tweet):
    class URLPreview(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)
        url = db.Column(db.String(2048), nullable=False)
        title = db.Column(db.String(200), nullable=True)
        description = db.Column(db.String(500), nullable=True)
        image_url = db.Column(db.String(2048), nullable=True)
        
        tweet = db.relationship('Tweet', backref=db.backref('url_previews', lazy=True))
    
    return URLPreview

# Helper function to extract URLs from tweet content
def extract_urls(content):
    url_pattern = re.compile(r'https?://\S+')
    return url_pattern.findall(content)

# Helper for fetching URL preview metadata
def fetch_url_metadata(url):
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        metadata = {
            'url': url,
            'title': None,
            'description': None,
            'image_url': None
        }
        
        # Get title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.string[:200] if title_tag.string else None
            
        # Get description
        description_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if description_tag and description_tag.get('content'):
            metadata['description'] = description_tag['content'][:500]
            
        # Get image
        image_tag = soup.find('meta', attrs={'property': 'og:image'}) or soup.find('meta', attrs={'name': 'twitter:image'})
        if image_tag and image_tag.get('content'):
            metadata['image_url'] = image_tag['content']
            
        return metadata
    except Exception as e:
        current_app.logger.error(f"Error fetching URL metadata: {str(e)}")
        return None

# Allowed file extensions and validation
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes for media upload
@media_support.route('/upload', methods=['POST'])
@login_required
def upload_media():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.referrer or url_for('home'))
        
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.referrer or url_for('home'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{current_user.id}_{file.filename}")
        file_path = os.path.join(current_app.root_path, 'static/uploads', filename)
        file.save(file_path)
        
        tweet_id = request.form.get('tweet_id')
        
        # Determine media type
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension in ['jpg', 'jpeg', 'png']:
            media_type = 'image'
        elif extension == 'gif':
            media_type = 'gif'
        elif extension == 'mp4':
            media_type = 'video'
        
        # Save to database
        from media_support import Media
        media = Media(tweet_id=tweet_id, filename=filename, media_type=media_type)
        db.session.add(media)
        db.session.commit()
        
        return redirect(url_for('tweet_interactions.view_tweet', tweet_id=tweet_id))
    
    flash('Invalid file type', 'danger')
    return redirect(request.referrer or url_for('home'))

# Process URL previews
def process_url_previews(tweet):
    urls = extract_urls(tweet.content)
    if not urls:
        return
    
    from media_support import URLPreview
    for url in urls[:1]:  # Process only the first URL for simplicity
        metadata = fetch_url_metadata(url)
        if metadata:
            preview = URLPreview(
                tweet_id=tweet.id,
                url=url,
                title=metadata.get('title'),
                description=metadata.get('description'),
                image_url=metadata.get('image_url')
            )
            db.session.add(preview)
    
    db.session.commit()

# Function to initialize the blueprint
def init_media_support(app, db_obj, tweet_model):
    global db, Tweet
    db = db_obj
    Tweet = tweet_model
    
    # Create models
    Media = add_media_model(db, Tweet)
    URLPreview = add_url_preview_model(db, Tweet)
    globals()['Media'] = Media
    globals()['URLPreview'] = URLPreview
    
    # Modify tweet post function to process URL previews
    original_post_tweet = app.view_functions.get('post_tweet')
    
    def post_tweet_with_media():
        if request.method == "POST":
            content = request.form["content"]
            if len(content) > 280:
                flash("Tweet exceeds 280 characters!", "danger")
                return redirect(url_for("home"))
    
            tweet = Tweet(user_id=current_user.id, content=content)
            db.session.add(tweet)
            db.session.commit()
            
            # Process URL previews
            process_url_previews(tweet)
            
            # Handle file upload if present
            if 'file' in request.files and request.files['file'].filename != '':
                file = request.files['file']
                if allowed_file(file.filename):
                    filename = secure_filename(f"{current_user.id}_{file.filename}")
                    file_path = os.path.join(current_app.root_path, 'static/uploads', filename)
                    file.save(file_path)
                    
                    # Determine media type
                    extension = file.filename.rsplit('.', 1)[1].lower()
                    if extension in ['jpg', 'jpeg', 'png']:
                        media_type = 'image'
                    elif extension == 'gif':
                        media_type = 'gif'
                    elif extension == 'mp4':
                        media_type = 'video'
                    
                    media = Media(tweet_id=tweet.id, filename=filename, media_type=media_type)
                    db.session.add(media)
                    db.session.commit()
            
            flash("Tweet posted!", "success")
            return redirect(url_for("home"))
        
        return original_post_tweet()
    
    # Replace the original function if it exists
    if original_post_tweet:
        app.view_functions['post_tweet'] = post_tweet_with_media
    
    app.register_blueprint(media_support)