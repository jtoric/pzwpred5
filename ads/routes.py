from bson import ObjectId
from flask import render_template, request, flash, redirect, url_for, Response, current_app, abort
from datetime import datetime

from flask_login import current_user, login_required

from .forms import AdForm, EditAdForm
from . import bp
from ..utils import get_pagination_info, get_pagination_range

@bp.route('/')
def ads():
    """Lista svih oglasa s paginacijom i pretragom"""
    ads_collection = current_app.config['ADS_COLLECTION']
    category = request.args.get('category', '')
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 12  # 3x4 grid
    
    # Izgradi query
    query = {}
    
    # Dodaj kategoriju filter
    if category:
        query['category'] = category
    
    # Dodaj search filter
    if search:
        query['title'] = {'$regex': search, '$options': 'i'}  # Case-insensitive search
    
    # Izračunaj ukupan broj oglasa
    total = ads_collection.count_documents(query)
    
    # Dohvati oglase s paginacijom
    skip = (page - 1) * per_page
    ads = ads_collection.find(query).sort('created_at', -1).skip(skip).limit(per_page)
    
    # Generiraj paginacijske podatke
    pagination = get_pagination_info(page, per_page, total)
    pagination['pages'] = get_pagination_range(page, pagination['total_pages'])

    print(pagination)
    
    return render_template('ads.html', 
                         ads=ads, 
                         selected_category=category,
                         pagination=pagination)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_ad():
    """Kreiranje novog oglasa"""
    form = AdForm()
    ads_collection = current_app.config['ADS_COLLECTION']
    fs = current_app.config['GRIDFS']
    
    if form.validate_on_submit():
        new_ad = {
            'title': form.title.data,
            'description': form.description.data,
            'seller': (f"{current_user.first_name} {current_user.last_name}".strip() or current_user.username),
            'cellNo': current_user.phone,
            'price': float(form.price.data),
            'category': form.category.data,
            'location': form.location.data or '',
            'image_id': None,
            'created_at': datetime.now(),
            'user_id': ObjectId(current_user.id)
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

@bp.route('/my')
@login_required
def my_ads():
    """Moji oglasi (oglasi prijavljenog korisnika)"""
    ads_collection = current_app.config['ADS_COLLECTION']
    page = int(request.args.get('page', 1))
    per_page = 12
    query = {'user_id': ObjectId(current_user.id)}
    total = ads_collection.count_documents(query)
    skip = (page - 1) * per_page
    ads = ads_collection.find(query).sort('created_at', -1).skip(skip).limit(per_page)
    pagination = get_pagination_info(page, per_page, total)
    pagination['pages'] = get_pagination_range(page, pagination['total_pages'])
    return render_template('ads.html', ads=ads, selected_category=request.args.get('category',''), pagination=pagination, my_view=True)

@bp.route('/<ad_id>')
def ad_detail(ad_id):
    """Detalji oglasa"""
    ads_collection = current_app.config['ADS_COLLECTION']
    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        abort(404)
    
    return render_template('ad_detail.html', ad=ad)

@bp.route('/<ad_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ad(ad_id):
    """Uređivanje oglasa"""
    ads_collection = current_app.config['ADS_COLLECTION']
    fs = current_app.config['GRIDFS']
    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        abort(404)
    
    form = EditAdForm()
    # Dozvoli uređivanje samo vlasniku
    if ad.get('user_id') and str(ad.get('user_id')) != str(current_user.id):
        abort(403)
    
    if form.validate_on_submit():
        updated_ad = {
            'title': form.title.data,
            'description': form.description.data,
            'seller': (f"{current_user.first_name} {current_user.last_name}".strip() or current_user.username),
            'cellNo': current_user.phone,
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
        # Ako slika ne postoji, vrati 404
        abort(404)

@bp.route('/<ad_id>/delete', methods=['POST'])
@login_required
def delete_ad(ad_id):
    """Brisanje oglasa"""
    ads_collection = current_app.config['ADS_COLLECTION']
    fs = current_app.config['GRIDFS']
    ad = ads_collection.find_one({'_id': ObjectId(ad_id)})
    
    if not ad:
        abort(404)
    
    # Dozvoli brisanje samo vlasniku
    if ad.get('user_id') and str(ad.get('user_id')) != str(current_user.id):
        abort(403)

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
