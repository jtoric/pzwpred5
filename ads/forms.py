from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp

class AdForm(FlaskForm):
    """Forma za kreiranje/uređivanje oglasa"""
    title = StringField(
        'Naziv oglasa',
        validators=[
            DataRequired(message='Naziv oglasa je obavezan'),
            Length(min=1, max=100, message='Naziv mora imati manje od 100 znakova')
        ],
        render_kw={'placeholder': 'Unesite naziv vašeg proizvoda'}
    )
    
    description = TextAreaField(
        'Opis',
        validators=[
            DataRequired(message='Opis je obavezan'),
            Length(min=10, max=2000, message='Opis mora imati između 10 i 2000 znakova')
        ],
        render_kw={'placeholder': 'Detaljno opišite vaš proizvod...', 'rows': 4}
    )

    seller = StringField(
        'Prodavač',
        validators=[
            DataRequired(message='Ime prodavača je obavezno')
        ]
    )

    cellNo = StringField(
        'Broj mobitela',
        validators=[
            DataRequired(message="Unesite broj mobitela"),
            Length(min=8, max=15, message="Broj mora imati između 8 i 15 znamenki"),
            Regexp(r'^\+?\d{8,15}$', message="Unesite ispravan broj (npr. +385912345678)")
        ]
    )
    
    price = DecimalField(
        'Cijena (€)',
        validators=[
            DataRequired(message='Cijena je obavezna'),
            NumberRange(min=0, message='Cijena mora biti pozitivan broj')
        ],
        places=2,
        render_kw={'placeholder': '0.00', 'step': '0.01'}
    )
    
    category = SelectField(
        'Kategorija',
        validators=[DataRequired(message='Odaberite kategoriju')],
        choices=[
            ('', 'Odaberite kategoriju'),
            ('Elektronika', 'Elektronika'),
            ('Dom i vrt', 'Dom i vrt'),
            ('Automobili', 'Automobili'),
            ('Odjeća', 'Odjeća'),
            ('Sport', 'Sport'),
            ('Knjige', 'Knjige'),
            ('Ostalo', 'Ostalo')
        ]
    )
    
    location = StringField(
        'Lokacija',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Grad ili regija'}
    )
    
    image = FileField(
        'Slika proizvoda',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Samo slike (JPG, PNG, GIF)')
        ]
    )
    
    submit = SubmitField('Objavi oglas')

class EditAdForm(AdForm):
    """Forma za uređivanje oglasa (naslijeđuje AdForm)"""
    submit = SubmitField('Spremi promjene')

