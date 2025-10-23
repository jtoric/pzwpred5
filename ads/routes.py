from bson import ObjectId
from flask import render_template, request, flash, redirect, url_for, Response, current_app
from datetime import datetime

from .forms import AdForm, EditAdForm
from . import bp

@bp.route('/')
def ads():
    """Lista svih oglasa"""
    ads_collection = current_app.config['ADS_COLLECTION']
    category = request.args.get('category', '')
    if category:
        ads = ads_collection.find({'category': category}).sort('created_at', -1)
    else:
        ads = ads_collection.find().sort('created_at', -1)
    
    return render_template('ads.html', ads=ads, selected_category=category)

@bp.route('/new', methods=['GET', 'POST'])
def new_ad():
    """Kreiranje novog oglasa"""
    form = AdForm()
    ads_collection = current_app.config['ADS_COLLECTION']
    fs = current_app.config['GRIDFS']
    
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
        return redirect(url_for('ads.ads'))
    
    return render_template('new_ad.html', form=form)

@bp.route('/<ad_id>')
def ad_detail(ad_id):
    """Detalji oglasa"""
    ads_collection = current_app.config['ADS_COLLECTION']
    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        flash('Oglas nije pronađen!', 'danger')
        return redirect(url_for('ads.ads'))
    
    return render_template('ad_detail.html', ad=ad)

@bp.route('/<ad_id>/edit', methods=['GET', 'POST'])
def edit_ad(ad_id):
    """Uređivanje oglasa"""
    ads_collection = current_app.config['ADS_COLLECTION']
    fs = current_app.config['GRIDFS']
    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        flash('Oglas nije pronađen!', 'danger')
        return redirect(url_for('ads.ads'))
    
    form = EditAdForm()
    
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
        return redirect(url_for('ads.ad_detail', ad_id=ad_id))
    
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

@bp.route('/image/<image_id>')
def get_image(image_id):
    """Serviranje slike iz GridFS"""
    fs = current_app.config['GRIDFS']
    try:
        image = fs.get(ObjectId(image_id))
        return Response(image.read(), mimetype=image.content_type)
    except:
        # Ako slika ne postoji, vrati placeholder
        return '', 404

@bp.route('/<ad_id>/delete', methods=['POST'])
def delete_ad(ad_id):
    """Brisanje oglasa"""
    ads_collection = current_app.config['ADS_COLLECTION']
    fs = current_app.config['GRIDFS']
    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        flash('Oglas nije pronađen!', 'danger')
        return redirect(url_for('ads.ads'))
    
    # Obriši sliku iz GridFS ako postoji
    if ad.get('image_id'):
        try:
            fs.delete(ad['image_id'])
        except:
            pass  # Ako slika ne postoji, nastavi
    
    # Obriši oglas
    ads_collection.delete_one({'_id': ObjectId(ad_id)})
    
    flash('Oglas je uspješno obrisan!', 'success')
    return redirect(url_for('ads.ads'))
