from bson import ObjectId
from flask import Flask, Response, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
from datetime import datetime
from pymongo import MongoClient
import gridfs
import markdown2
import bleach

from forms import AdForm

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['pzw']
ads_collection = db['ads']
fs = gridfs.GridFS(db)

bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = "jako-jak-random-key"

# Markdown konfiguracija
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'hr'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'code': ['class']
}

def markdown_to_html(text):
    """Pretvara Markdown u sanitizirani HTML"""
    if not text:
        return ""
    # Pretvori Markdown u HTML
    html = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'break-on-newline'])
    # Sanitiziraj HTML da spriječiš XSS
    clean_html = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    return clean_html

# Registriraj Jinja2 filter
@app.template_filter('markdown')
def markdown_filter(text):
    return markdown_to_html(text)

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
            'image_id': None,
            'created_at': datetime.now().isoformat()
        }
        
        # Upload slike u GridFS
        if form.image.data:
            file = form.image.data
            image_id = fs.put(
                file.read(),
                filename=file.filename,
                content_type=file.content_type
            )
            new_ad['image_id'] = image_id
        
        # Spremi oglas u MongoDB
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
            # Obriši staru sliku iz GridFS
            if ad.get('image_id'):
                fs.delete(ad['image_id'])
            
            # Spremi novu sliku u GridFS
            file = form.image.data
            image_id = fs.put(
                file.read(),
                filename=file.filename,
                content_type=file.content_type
            )
            updated_ad['image_id'] = image_id
        else:
            # Zadrži postojeću sliku
            updated_ad['image_id'] = ad.get('image_id')
        
        # Ažuriraj oglas u MongoDB
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

@app.route('/image/<image_id>')
def get_image(image_id):
    """Serviranje slike iz GridFS"""
    try:
        image = fs.get(ObjectId(image_id))
        return Response(image.read(), mimetype=image.content_type)
    except:
        # Ako slika ne postoji, vrati placeholder
        return '', 404

@app.route('/ads/<ad_id>/delete', methods=['POST'])
def delete_ad(ad_id):
    """Brisanje oglasa"""

    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        flash('Oglas nije pronađen!', 'danger')
        return redirect(url_for('ads'))
    
    # Obriši sliku iz GridFS ako postoji
    if ad.get('image_id'):
        try:
            fs.delete(ad['image_id'])
        except:
            pass  # Ako slika ne postoji, nastavi
    
    # Obriši oglas
    ads_collection.delete_one({'_id': ObjectId(ad_id)})
    
    flash('Oglas je uspješno obrisan!', 'success')
    return redirect(url_for('ads'))


if __name__== '__main__':
    app.run(debug=True)