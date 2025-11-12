from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import PolozkaZasoby, Kategorie
from app.forms import InventoryForm, KategorieForm

inventory_bp = Blueprint('inventory', __name__)

def get_kategorie_choices():
    """Pomocná funkce pro načtení kategorií pro SelectField."""
    return [(c.id, c.nazev) for c in Kategorie.query.order_by(Kategorie.nazev).all()]

@inventory_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    """Přidání nové položky do zásob."""
    form = InventoryForm()
    form.kategorie.choices = get_kategorie_choices() # Dynamické načtení kategorií

    if form.validate_on_submit():
        item = PolozkaZasoby(
            nazev=form.nazev.data,
            kategorie_id=form.kategorie.data,
            mnozstvi_v_baleni=form.mnozstvi_v_baleni.data,
            minimum_pro_upozorneni=form.minimum_pro_upozorneni.data,
            popis_baleni=form.popis_baleni.data,
            uzivatel_id=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Položka "{item.nazev}" byla přidána do zásob.', 'success')
        return redirect(url_for('main.all_inventory'))

    return render_template('inventory/add_edit.html', title='Přidat zásobu', form=form)


@inventory_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Úprava existující položky (včetně stavu balení)."""
    item = PolozkaZasoby.query.get_or_404(item_id)
    form = InventoryForm(obj=item)
    form.kategorie.choices = get_kategorie_choices()

    if form.validate_on_submit():
        # Aktualizace dat
        item.nazev = form.nazev.data
        item.kategorie_id = form.kategorie.data
        item.mnozstvi_v_baleni = form.mnozstvi_v_baleni.data
        item.minimum_pro_upozorneni = form.minimum_pro_upozorneni.data
        item.popis_baleni = form.popis_baleni.data
        
        db.session.commit()
        flash(f'Položka "{item.nazev}" byla aktualizována.', 'success')
        return redirect(url_for('main.all_inventory'))
    
    # Předvyplnění formuláře při GET požadavku
    elif request.method == 'GET':
        form.kategorie.data = item.kategorie_id

    return render_template('inventory/add_edit.html', title='Upravit zásobu', form=form, item=item)


@inventory_bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    """Smazání položky (např. po spotřebování a vyřazení)."""
    item = PolozkaZasoby.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f'Položka "{item.nazev}" byla smazána.', 'info')
    return redirect(url_for('main.low_stock'))


@inventory_bp.route('/kategorie/manage', methods=['GET', 'POST'])
@login_required
def manage_categories():
    """Správa kategorií (přidání nové)."""
    form = KategorieForm()
    
    if form.validate_on_submit():
        kategorie = Kategorie(nazev=form.nazev.data, color_hex=form.color_hex.data)
        db.session.add(kategorie)
        db.session.commit()
        flash(f'Kategorie "{kategorie.nazev}" byla přidána.', 'success')
        return redirect(url_for('inventory.manage_categories'))
        
    kategorie_list = Kategorie.query.order_by(Kategorie.nazev).all()
    return render_template('inventory/manage_categories.html', 
                           title='Správa kategorií', 
                           form=form, 
                           kategorie_list=kategorie_list)


@inventory_bp.route('/kategorie/edit/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def edit_category(cat_id):
    """Editování kategorie."""
    kategorie = Kategorie.query.get_or_404(cat_id)
    form = KategorieForm(obj=kategorie)

    if form.validate_on_submit():
        kategorie.nazev = form.nazev.data
        kategorie.color_hex = form.color_hex.data
        db.session.commit()
        flash(f'Kategorie "{kategorie.nazev}" byla aktualizována.', 'success')
        return redirect(url_for('inventory.manage_categories'))
    
    return render_template('inventory/edit_category.html',
                           title='Upravit kategorii',
                           form=form,
                           kategorie=kategorie)


@inventory_bp.route('/kategorie/delete/<int:cat_id>', methods=['POST'])
@login_required
def delete_category(cat_id):
    """Smazání kategorie. (POZOR: Neřeší co s položkami v ní!)"""
    kategorie = Kategorie.query.get_or_404(cat_id)
    
    # Kontrola, zda neobsahuje položky
    if kategorie.polozky.count() > 0:
        flash('Nelze smazat kategorii, která obsahuje položky. Nejprve je přesuňte.', 'danger')
        return redirect(url_for('inventory.manage_categories'))
        
    db.session.delete(kategorie)
    db.session.commit()
    flash(f'Kategorie "{kategorie.nazev}" byla smazána.', 'info')
    return redirect(url_for('inventory.manage_categories'))