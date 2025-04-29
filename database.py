# database.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime 
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

 

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)  # Plaintext (insecure)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    membership = db.Column(db.String(20), default='free')
    
class ScrapeLog(db.Model):
    """Logs all scraping activities"""
    __tablename__ = 'scrape_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_query = db.Column(db.String(200))
    website = db.Column(db.String(50))
    status = db.Column(db.String(20))  # 'pending', 'completed', 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results_count = db.Column(db.Integer)

class NewsLog(db.Model):
    """Logs user activities and news scraping"""
    __tablename__ = 'news_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    source = db.Column(db.String(50))   # e.g., 'amazon', 'flipkart', 'news'
    articles_count = db.Column(db.Integer)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
 
    
def init_db(app):
    """Initialize database with Flask app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/webscrapx'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }


    db.init_app(app)
    
  
        

def create_default_admin():
    """Create admin user if not exists"""
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@webscrapx.com',
            membership='premium'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()