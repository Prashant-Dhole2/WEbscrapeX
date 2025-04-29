from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, User, ScrapeLog, NewsLog, init_db
from datetime import datetime, timedelta
from backend.amazon_scraper import scrape_amazon
from backend.flipkart_scraper import scrape_flipkart 
from backend.alibaba_scraper import scrape_alibaba
from backend.eBay_srap import scrape_ebay 
from backend.walmart_scraper import scrape_walmart
from backend.Nykaa_scrap import scrape_nykaa

from backend.news_scraper import scrape_bbc
from backend.google_news_scrap import scrape_google_news
 
from backend.ndtv_scraper import scrape_ndtv
from backend.India_today_scap import scrape_india_today
from backend.AajTak_scrap import scrape_aajtak_india
from functools import wraps
import secrets
import os
from urllib.parse import urlparse, urljoin

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.permanent_session_lifetime = timedelta(minutes=30)

# Initialize Database
init_db(app)

# Global variables to store scraped data
products_data = []
news_articles = []
 
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            session['next'] = request.url
            flash("Login required", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id, action):
    activity = NewsLog(
        user_id=user_id,
        source=action,
        articles_count=0,
        scraped_at=datetime.utcnow()
    )
    db.session.add(activity)
    db.session.commit()

def analyze_products(products):
    if not products:
        return {}
    total_price = sum(p['Price'] for p in products if p['Price'] > 0)
    avg_price = round(total_price / len(products), 2)
    top_rated = sorted(products, key=lambda x: x['Rating'], reverse=True)[:5]
    most_reviewed = sorted(products, key=lambda x: x['Reviews'], reverse=True)[:5]
    website_counts = {}
    for p in products:
        website_counts[p['Website']] = website_counts.get(p['Website'], 0) + 1
    return {
        'total_products': len(products),
        'average_price': avg_price,
        'top_rated': top_rated,
        'most_reviewed': most_reviewed,
        'website_distribution': website_counts
    }

# ------ ------- Routes --

@app.route('/')
def home():
    global news_articles
    if not news_articles:
        news_articles = scrape_bbc()[:6]
    sample_analysis = {
        'total_products': 42,
        'average_price': 1499,
        'top_rated': [
            {'Name': 'OnePlus Nord CE 2', 'Price': 18999, 'Rating': 4.5},
            {'Name': 'Samsung Galaxy M33', 'Price': 16499, 'Rating': 4.3},
            {'Name': 'Realme Narzo 50', 'Price': 12999, 'Rating': 4.2}
        ]
    }
    return render_template('index.html', news_articles=news_articles, analysis=sample_analysis)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']  #

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
        else:
            user_data = User(username=username, email=email, password=password)
            db.session.add(user_data)
            db.session.commit()
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please fill all fields', 'danger')
            return redirect(url_for('login'))

        user_data = User.query.filter_by(username=username).first()

        if not user_data:
            flash('Invalid username', 'danger')
            return redirect(url_for('login'))

        if user_data.password != password:
            flash('Invalid password', 'danger')
            return redirect(url_for('login'))

        session['user_id'] = user_data.id
        flash('Login successful!', 'success')

        next_page = session.get('next')
        if next_page and is_safe_url(next_page):
            session.pop('next')
            return redirect(next_page)

        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_activity(session['user_id'], 'User logged out')
        session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/scrape', methods=['GET', 'POST'])
@login_required
def scrape():
    global products_data
    if request.method == 'POST':
        product_query = request.form.get('product', 'smartphones')
        user_id = session['user_id']

        scrape_log = ScrapeLog(
            user_id=user_id,
            product_query=product_query,
            website='amazon,flipkart',
            status='pending'
        )
        db.session.add(scrape_log)
        db.session.commit()

        try:
            amazon_results = scrape_amazon(product_query)
            flipkart_results = scrape_flipkart(product_query)
            Nyakaa_result = scrape_nykaa(product_query)
            alibaba_results = scrape_alibaba(product_query)
            ebay_results = scrape_ebay(product_query)
            walmart_results = scrape_walmart(product_query)



            #products_data = Nyakaa_result             

            products_data = amazon_results + flipkart_results + Nyakaa_result + alibaba_results + ebay_results + walmart_results  
           
            scrape_log.status = 'completed'
            scrape_log.results_count = len(products_data)
            db.session.commit()

            return redirect(url_for('analyze'))

        except Exception as e:
            scrape_log.status = 'failed'
            db.session.commit()
            flash(f'Scraping failed: {str(e)}', 'danger')
            return redirect(url_for('scrape'))

    return render_template('scrape.html')

@app.route('/analyze', methods=['GET'])
@login_required
def analyze():
    global products_data
    if not products_data:
        return redirect(url_for('scrape'))
    analysis_results = analyze_products(products_data)
    return render_template('analyze.html', products=products_data, analysis=analysis_results)

@app.route('/news', methods=['GET'])
@login_required
def news():
    global news_articles
    bbc_news = scrape_bbc()
    ndtv_news = scrape_ndtv()
     
    google_news = scrape_google_news()
    news_india =scrape_india_today()
    aajTAk=scrape_aajtak_india()
   
    news_articles = bbc_news + ndtv_news + aajTAk  
    log_activity(session['user_id'], 'news_refresh')
    return render_template('news.html', news_articles=news_articles)
from sqlalchemy import extract, func
from datetime import datetime, timedelta

@app.route('/profile')
@login_required
def profile():
    user = db.session.get(User, session['user_id'])
    
    # Calculate account age in human-readable format
    account_age = (datetime.utcnow() - user.created_at).days
    if account_age < 60:
        account_age = f"{account_age} days"
    elif account_age < 365:
        account_age = f"{account_age//30} months"
    else:
        account_age = f"{account_age//365} years"
    
    # Get combined activity feed (scrapes + news)
    activities = []
    
    # Add recent scrapes (3 most recent)
    scrapes = (ScrapeLog.query
              .filter_by(user_id=user.id)
              .order_by(ScrapeLog.created_at.desc())
              .limit(3)
              .all())
    
    for scrape in scrapes:
        activities.append({
            'title': f"{scrape.website} scrape" if scrape.website else "Product scrape",
            'timestamp': scrape.created_at,
            'description': scrape.product_query or "No query details",
            'icon': 'search',
            'type': 'scrape'
        })
    
    # Add recent news activities (2 most recent)
    news_logs = (NewsLog.query
                .filter_by(user_id=user.id)
                .order_by(NewsLog.scraped_at.desc())
                .limit(2)
                .all())
    
    for news in news_logs:
        activities.append({
            'title': f"News from {news.source}" if news.source else "News update",
            'timestamp': news.scraped_at,
            'description': f"{news.articles_count} articles" if news.articles_count else "News collection",
            'icon': 'newspaper',
            'type': 'news'
        })
    
    # Sort all activities by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Get basic stats
    stats = {
        'total_scrapes': ScrapeLog.query.filter_by(user_id=user.id).count(),
        'total_news': NewsLog.query.filter_by(user_id=user.id).count(),
        'last_active': max(
            ScrapeLog.query.with_entities(ScrapeLog.created_at)
                         .filter_by(user_id=user.id)
                         .order_by(ScrapeLog.created_at.desc())
                         .first()[0] if ScrapeLog.query.filter_by(user_id=user.id).first() else None,
            NewsLog.query.with_entities(NewsLog.scraped_at)
                        .filter_by(user_id=user.id)
                        .order_by(NewsLog.scraped_at.desc())
                        .first()[0] if NewsLog.query.filter_by(user_id=user.id).first() else None
        )
    }

    return render_template(
        'profile.html',
        user=user,
        activities=activities[:5],  # Show only 5 most recent
        stats=stats,
        account_age=account_age
    )
# -------------------- Run --------------------

if __name__ == '__main__':
    app.run(debug=True)
