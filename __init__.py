from flask import Flask, render_template, abort
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
    
    # Test route za 500 grešku (samo u development modu)
    if config_name == 'development':
        @app.route('/test-500')
        def test_500():
            raise Exception("Test 500 greška")

     # Test route za 403 grešku (samo u development modu)
    if config_name == 'development':
        @app.route('/test-403')
        def test_403():
            abort(403)
    
    # Error handleri
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    return app

