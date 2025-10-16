from bson import ObjectId
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
from datetime import datetime
import json
import os
from pymongo import MongoClient

from forms import AdForm

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['pzw']
ads_collection = db['ads']

bootstrap = Bootstrap5(app)

# JSON datoteke za pohranu podataka
ADS_FILE = 'data/ads.json'

UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "jako-jak-random-key"

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_data():
    # Inicijalizira prazne datoteke ako ne postoje
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(ADS_FILE):
        save_data([], ADS_FILE)

init_data()

@app.route('/')
def index():
    """Početna stranica"""

    recent_ads = ads_collection.find().sort('created_at', -1).limit(6)

    return render_template('index.html', ads=recent_ads)

@app.route('/ads')
def ads():
    """Lista svih oglasa"""
    category = request.args.get('category', '')
    
    if category:

        ads = ads_collection.find({'category': category}).sort('created_at', -1)
    else:
        ads = ads_collection.find().sort('created_at', -1)
    
    return render_template('ads.html', ads=ads, selected_category=category)


@app.route('/ads/new', methods=['GET', 'POST'])
def new_ad():
    """Kreiranje novog oglasa"""
    form = AdForm()
    
    if form.validate_on_submit():
        new_ad = {
            'title': form.title.data,
            'description': form.description.data,
            'seller': form.seller.data,
            'cellNo': form.cellNo.data,
            'price': float(form.price.data),
            'category': form.category.data,
            'location': form.location.data or '',
            'image': None,
            'created_at': datetime.now().isoformat()
        }
        
        # Upload slike oglasa
        if form.image.data:
            file = form.image.data
            filename = f"{str(ObjectId())}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_ad['image'] = filename
        
        ads_collection.insert_one(new_ad)

    
        flash('Oglas je uspješno kreiran!', 'success')
        return redirect(url_for('ads'))
    
    return render_template('new_ad.html', form=form)

@app.route('/ads/<ad_id>')
def ad_detail(ad_id):
    """Detalji oglasa"""
    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        flash('Oglas nije pronađen!', 'danger')
        return redirect(url_for('ads'))
    
    return render_template('ad_detail.html', ad=ad)

@app.route('/ads/<ad_id>/edit', methods=['GET', 'POST'])
def edit_ad(ad_id):
    """Uređivanje oglasa"""
    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        flash('Oglas nije pronađen!', 'danger')
        return redirect(url_for('ads'))
    
    form = AdForm()
    
    if form.validate_on_submit():
        updated_ad = {
            'title': form.title.data,
            'description': form.description.data,
            'seller': form.seller.data,
            'cellNo': form.cellNo.data,
            'price': float(form.price.data),
            'category': form.category.data,
            'location': form.location.data or '',
            'created_at': ad['created_at']  # Zadržavamo originalni datum
        }
        
        # Ako je uploadana nova slika
        if form.image.data:
            # Obriši staru sliku
            if ad.get('image'):
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], ad['image'])
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Spremi novu sliku
            file = form.image.data
            filename = f"{str(ObjectId())}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            updated_ad['image'] = filename
        else:
            # Zadrži postojeću sliku
            updated_ad['image'] = ad.get('image')
        
        ads_collection.update_one(
            {'_id': ObjectId(ad_id)},
            {'$set': updated_ad}
        )
        
        flash('Oglas je uspješno ažuriran!', 'success')
        return redirect(url_for('ad_detail', ad_id=ad_id))
    
    # Popuni formu sa postojećim podacima
    if request.method == 'GET':
        form.title.data = ad['title']
        form.description.data = ad['description']
        form.seller.data = ad['seller']
        form.cellNo.data = ad['cellNo']
        form.price.data = ad['price']
        form.category.data = ad['category']
        form.location.data = ad.get('location', '')
    
    return render_template('edit_ad.html', form=form, ad=ad)

@app.route('/ads/<ad_id>/delete', methods=['POST'])
def delete_ad(ad_id):
    """Brisanje oglasa"""

    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        flash('Oglas nije pronađen!', 'danger')
        return redirect(url_for('ads'))
    
    # Obriši sliku ako postoji
    if ad['image']:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], ad['image'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Obriši oglas
    ads_collection.delete_one({'_id': ObjectId(ad_id)})
    
    flash('Oglas je uspješno obrisan!', 'success')
    return redirect(url_for('ads'))


if __name__== '__main__':
    app.run(debug=True)