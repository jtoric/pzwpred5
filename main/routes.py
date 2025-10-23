from flask import render_template, current_app
from . import bp

@bp.route('/')
def index():
    """Početna stranica"""
    ads_collection = current_app.config['ADS_COLLECTION']
    recent_ads = ads_collection.find().sort('created_at', -1).limit(6)
    total_ads = ads_collection.count_documents({})
    
    return render_template('index.html', ads=recent_ads, total_ads=total_ads)
