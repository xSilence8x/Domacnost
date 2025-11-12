# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.forms import LoginForm, RegistrationForm
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Routa pro registraci nového uživatele."""
    # Pokud je uživatel již přihlášen, přesměruj ho na hlavní stránku
    if current_user.is_authenticated:
        return redirect(url_for('main.low_stock')) 
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Vytvoření nového uživatele
        user = User(username=form.username.data)
        user.set_password(form.password.data) # Použije hashování
        
        db.session.add(user)
        db.session.commit()
        
        flash('Gratulujeme, jste registrováni! Nyní se můžete přihlásit.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title='Registrace', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Routa pro přihlášení uživatele."""
    # Pokud je uživatel již přihlášen, přesměruj ho na hlavní stránku
    if current_user.is_authenticated:
        return redirect(url_for('main.low_stock')) 

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Kontrola uživatele a hesla
        if user is None or not user.check_password(form.password.data):
            flash('Neplatné uživatelské jméno nebo heslo.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Přihlášení uživatele
        login_user(user, remember=form.remember_me.data)
        
        # Zpracování parametru 'next' pro přesměrování po úspěšném přihlášení
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.low_stock') # Hlavní stránka (výpis docházejících)
            
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Přihlášení', form=form)


@auth_bp.route('/logout')
@login_required # Vyžaduje, aby uživatel byl přihlášen
def logout():
    """Routa pro odhlášení uživatele."""
    logout_user()
    flash('Byli jste odhlášeni.', 'info')
    return redirect(url_for('main.low_stock'))