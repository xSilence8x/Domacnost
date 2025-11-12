from app import db 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# --- UŽIVATELSKÝ MODEL ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    polozky = db.relationship('PolozkaZasoby', backref='pridal_uzivatel', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# --- KATEGORIE ---
class Kategorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazev = db.Column(db.String(100), unique=True, nullable=False)
    color_hex = db.Column(db.String(7), nullable=False, default='#94a3b8')
    
    polozky = db.relationship('PolozkaZasoby', backref='kategorie', lazy='dynamic')

    def __repr__(self):
        return f'<Kategorie {self.nazev}>'

# --- POLOŽKA ZÁSOBY ---
class PolozkaZasoby(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazev = db.Column(db.String(150), nullable=False) 
    
    # 1.0 = celé balení, 0.0 = prázdné
    mnozstvi_v_baleni = db.Column(db.Float, default=1.0) 
    
    # Hranice pro upozornění "Dochází"
    minimum_pro_upozorneni = db.Column(db.Float, default=0.25)
    
    popis_baleni = db.Column(db.String(200), nullable=True)

    # Vztahy
    kategorie_id = db.Column(db.Integer, db.ForeignKey('kategorie.id'), nullable=False)
    uzivatel_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def dochazi(self):
        return self.mnozstvi_v_baleni <= self.minimum_pro_upozorneni

    def get_stav(self):
        """Vrátí textový popis celkového stavu."""
        plne_kusy = int(self.mnozstvi_v_baleni)
        zbytek = self.mnozstvi_v_baleni - plne_kusy

        text_plne = ""
        if plne_kusy == 1:
            text_plne = "1 celé"
        elif plne_kusy > 1:
            text_plne = f"{plne_kusy} celé"

        text_zbytek = ""
        if zbytek == 0.0:
            if plne_kusy == 0:
                return "Prázdné/Spotřebováno"
            return text_plne # Např. "3 celé"
        
        elif zbytek > 0.75:
            text_zbytek = "1 téměř plné"
        elif zbytek > 0.5:
            text_zbytek = "1 více než polovina"
        elif zbytek == 0.5:
            text_zbytek = "1 polovina"
        elif zbytek > 0.25:
            text_zbytek = "1 méně než polovina"
        elif zbytek > 0.0:
            text_zbytek = "1 dochází (méně než 1/4)"
        
        if plne_kusy > 0:
            return f"{text_plne}, {text_zbytek}" # Např. "2 celé, 1 polovina"
        else:
            return text_zbytek # Např. "1 polovina"
    
    def __repr__(self):
        return f'<Polozka {self.nazev} ({self.mnozstvi_v_baleni})>'