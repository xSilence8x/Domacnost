# app/routes/views.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from app.models import PolozkaZasoby, Kategorie

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/low_stock')
@login_required 
def low_stock():
    """Hlavní stránka: Seznam docházejících položek."""
    
    # Dotaz: Načte položky, kde je množství menší nebo rovno minimu
    dochazejici_polozky = PolozkaZasoby.query.join(Kategorie).filter(
        PolozkaZasoby.mnozstvi_v_baleni <= PolozkaZasoby.minimum_pro_upozorneni
    ).order_by(Kategorie.nazev, PolozkaZasoby.nazev).all()

    return render_template('inventory/low_stock.html', 
                           title='Docházející zásoby', 
                           items=dochazejici_polozky)

@main_bp.route('/all_inventory')
@login_required
def all_inventory():
    """Výpis všech položek v domácnosti."""
    
    vsechny_polozky = PolozkaZasoby.query.join(Kategorie).order_by(Kategorie.nazev, PolozkaZasoby.nazev).all()
    
    return render_template('inventory/list.html', 
                           title='Všechny zásoby', 
                           items=vsechny_polozky)

@main_bp.route('/kategorie/<int:cat_id>')
@login_required
def kategorie_detail(cat_id):
    """Zobrazení položek dle kategorie."""
    kategorie = Kategorie.query.get_or_404(cat_id)
    # Zde .join() není potřeba, protože neřadíme podle Kategorie.nazev
    polozky = PolozkaZasoby.query.filter_by(kategorie_id=cat_id).all()
    
    return render_template('inventory/list.html', 
                           title=f'Kategorie: {kategorie.nazev}', 
                           items=polozky)