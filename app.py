from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
import uuid
from datetime import datetime
import json
import os

from forms import AdForm

app = Flask(__name__)

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
    ads = load_data(ADS_FILE)
    # Prikaži samo najnovijih 6 oglasa
    recent_ads = sorted(ads, key=lambda x: x['created_at'], reverse=True)[:6]   

    return render_template('index.html', ads=recent_ads)

@app.route('/ads')
def ads():
    """Lista svih oglasa"""
    ads = load_data(ADS_FILE)
    category = request.args.get('category', '')
    
    if category:
        # Ovo je generator
        # filtered_ads = []
        # for ad in ads:
        #   if ad['category']==category:
        #       filtered_ads.append(ad)
        # ads = filtered_ads
        ads = [ad for ad in ads if ad['category'] == category]
    
    # Sortiranje po datumu kreiranja (najnoviji prvi)
    ads = sorted(ads, key=lambda x: x['created_at'], reverse=True)
    
    return render_template('ads.html', ads=ads, selected_category=category)


@app.route('/ads/new', methods=['GET', 'POST'])
def new_ad():
    """Kreiranje novog oglasa"""
    form = AdForm()
    
    if form.validate_on_submit():
        new_ad = {
            'id': str(uuid.uuid4()),
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
            filename = f"{new_ad['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_ad['image'] = filename
        
        ads = load_data(ADS_FILE)
        ads.append(new_ad)
        save_data(ads, ADS_FILE)
        
        flash('Oglas je uspješno kreiran!', 'success')
        return redirect(url_for('ads'))
    
    return render_template('new_ad.html', form=form)

@app.route('/ads/<ad_id>')
def ad_detail(ad_id):
    """Detalji oglasa"""
    ads = load_data(ADS_FILE)

    # Next vraća samo prvu vrijednost generatora
    # Generator možemo napisati i sa for petljom
    # ad = None
    #   for item in ads:
    #       if item['id'] == ad_id:
    #           ad = item
    #           break
    ad = next((ad for ad in ads if ad['id'] == ad_id), None)
    
    if not ad:
        flash('Oglas nije pronađen!', 'danger')
        return redirect(url_for('ads'))
    
    return render_template('ad_detail.html', ad=ad)

@app.route('/ads/<ad_id>/delete', methods=['POST'])
def delete_ad(ad_id):
    """Brisanje oglasa"""

    ads = load_data(ADS_FILE)
    ad = next((ad for ad in ads if ad['id'] == ad_id), None)
    
    if not ad:
        flash('Oglas nije pronađen!', 'danger')
        return redirect(url_for('ads'))
    
    # Obriši sliku ako postoji
    if ad['image']:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], ad['image'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Obriši oglas
    ads = [ad for ad in ads if ad['id'] != ad_id]
    save_data(ads, ADS_FILE)
    
    flash('Oglas je uspješno obrisan!', 'success')
    return redirect(url_for('ads'))


if __name__== '__main__':
    app.run(debug=True)