from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import bp
from .forms import LoginForm, RegisterForm
from .models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Stranica za prijavu korisnika"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash(f'Dobrodošli, {user.username}!', 'success')
            
            # Preusmjeravanje na stranicu gdje je korisnik želio ići
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Neispravno korisničko ime ili lozinka', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Stranica za registraciju korisnika"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            user = User.create(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            login_user(user, remember=True)
            flash(f'Registracija uspješna! Dobrodošli, {user.username}!', 'success')
            return redirect(url_for('main.index'))
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template('register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Odjava korisnika"""
    username = current_user.username
    logout_user()
    flash(f'Odjavljeni ste, {username}.', 'info')
    return redirect(url_for('main.index'))

