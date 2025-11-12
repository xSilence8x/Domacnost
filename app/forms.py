from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, ColorField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length, NumberRange
from app.models import User, Kategorie

# --- AUTENTIZACE FORMULÁŘE ---
class LoginForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[DataRequired()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    remember_me = BooleanField('Zapamatovat si mě')
    submit = SubmitField('Přihlásit se')

class RegistrationForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Heslo', validators=[DataRequired()])
    password2 = PasswordField(
        'Opakujte heslo', 
        validators=[DataRequired(), EqualTo('password', message='Hesla se musí shodovat')]
    )
    submit = SubmitField('Zaregistrovat')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Toto uživatelské jméno je již obsazené.')

# --- ZÁSOBY FORMULÁŘE ---
class InventoryForm(FlaskForm):
    nazev = StringField('Název produktu', validators=[DataRequired(), Length(max=150)])
    
    kategorie = SelectField('Kategorie', coerce=int, validators=[DataRequired()])
    
    # --- ZMĚNA ZDE ---
    mnozstvi_v_baleni = FloatField(
        'Celkové množství (např. 3.0 = 3 balení, 0.5 = půl balení)', 
        validators=[DataRequired(), NumberRange(min=0.0, message="Hodnota musí být nezáporná")], 
        default=1.0
    )
    
    # --- A ZMĚNA ZDE ---
    minimum_pro_upozorneni = FloatField(
        'Limit docházení (např. 1.0)', 
        validators=[DataRequired(), NumberRange(min=0.0, message="Hodnota musí být nezáporná")],
        default=0.25
    )
    
    popis_baleni = StringField('Popis (např. značka, typ)', validators=[Length(max=200)])
    
    submit = SubmitField('Uložit položku')

class KategorieForm(FlaskForm):
    nazev = StringField('Název nové kategorie', validators=[DataRequired(), Length(max=100)])
    color_hex = ColorField('Barva kategorie', default='#94a3b8')
    
    submit = SubmitField('Přidat kategorii')