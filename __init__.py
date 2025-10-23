from flask import Flask
from flask_bootstrap import Bootstrap5
from pymongo import MongoClient
import gridfs
from .main import bp as main_bp
from .ads import bp as ads_bp
from .ads.routes import get_image
from .utils import markdown_to_html

def create_app(config_name='development'):
    """App Factory pattern za kreiranje Flask aplikacije"""
    app = Flask(__name__, template_folder='templates')
    
    # Konfiguracija
    app.config['SECRET_KEY'] = "jako-jak-random-key"
    
    # Inicijalizacija ekstenzija
    bootstrap = Bootstrap5(app)
    
    # MongoDB konekcija
    client = MongoClient('mongodb://localhost:27017/')
    db = client['pzw']
    app.config['DB'] = db
    app.config['ADS_COLLECTION'] = db['ads']
    app.config['GRIDFS'] = gridfs.GridFS(db)
    
    # Registracija blueprint-a
    app.register_blueprint(main_bp)
    
    app.register_blueprint(ads_bp, url_prefix='/ads')
    
    # Dodaj route za slike na root level (bez /ads/ prefiksa)
    app.add_url_rule('/image/<image_id>', 'get_image', get_image)
    
    # Registracija Jinja2 filtera
    app.jinja_env.filters['markdown'] = markdown_to_html
    
    return app

