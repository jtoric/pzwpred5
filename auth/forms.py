from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    """Forma za prijavu korisnika"""
    username = StringField(
        'Korisničko ime',
        validators=[
            DataRequired(message='Korisničko ime je obavezno'),
            Length(min=3, max=20, message='Korisničko ime mora imati između 3 i 20 znakova')
        ],
        render_kw={'placeholder': 'Unesite korisničko ime'}
    )
    
    password = PasswordField(
        'Lozinka',
        validators=[
            DataRequired(message='Lozinka je obavezna'),
            Length(min=6, message='Lozinka mora imati najmanje 6 znakova')
        ],
        render_kw={'placeholder': 'Unesite lozinku'}
    )
    
    submit = SubmitField('Prijavi se')

class RegisterForm(FlaskForm):
    """Forma za registraciju korisnika"""
    username = StringField(
        'Korisničko ime',
        validators=[
            DataRequired(message='Korisničko ime je obavezno'),
            Length(min=3, max=20, message='Korisničko ime mora imati između 3 i 20 znakova')
        ],
        render_kw={'placeholder': 'Unesite korisničko ime'}
    )
    
    email = StringField(
        'Email adresa',
        validators=[
            DataRequired(message='Email adresa je obavezna'),
            Email(message='Unesite ispravnu email adresu'),
            Length(max=120, message='Email adresa je predugačka')
        ],
        render_kw={'placeholder': 'Unesite email adresu'}
    )
    
    password = PasswordField(
        'Lozinka',
        validators=[
            DataRequired(message='Lozinka je obavezna'),
            Length(min=6, message='Lozinka mora imati najmanje 6 znakova')
        ],
        render_kw={'placeholder': 'Unesite lozinku'}
    )
    
    password2 = PasswordField(
        'Potvrdite lozinku',
        validators=[
            DataRequired(message='Potvrda lozinke je obavezna'),
            EqualTo('password', message='Lozinke se moraju podudarati')
        ],
        render_kw={'placeholder': 'Ponovno unesite lozinku'}
    )
    
    submit = SubmitField('Registriraj se')

