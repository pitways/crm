from datetime import date

from flask import Flask
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import PasswordField, BooleanField, StringField, DateField, IntegerField, SelectField, TextAreaField, \
    SubmitField, DecimalField
from wtforms.validators import DataRequired, Email, Optional, EqualTo, Length, NumberRange

from models import Client, Properties

app = Flask(__name__)
app.secret_key = "e2d7dd8c522f1cf159f6b45a6d7e8c25"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

###### FORMS #######

class ClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    address = StringField('Address')
    birthdate = DateField('Birthdate', validators=[DataRequired()])
    marital_status = SelectField('Marital Status',
                                 choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'),
                                          ('Widowed', 'Widowed')])
    profession = StringField('Profession')
    income = IntegerField('Income')

class PropertiesForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    distrito = SelectField('Distrito',
                        choices=[('', 'Selecione um distrito'), ('Aveiro', 'Aveiro'), ('Beja', 'Beja'),
                                 ('Braga', 'Braga'),
                                 ('Bragança', 'Bragança'), ('Castelo Branco', 'Castelo Branco'), ('Coimbra', 'Coimbra'),
                                 ('Évora', 'Évora'), ('Faro', 'Faro'), ('Guarda', 'Guarda'), ('Leiria', 'Leiria'),
                                 ('Lisboa', 'Lisboa'), ('Portalegre', 'Portalegre'), ('Porto', 'Porto'),
                                 ('Santarém', 'Santarém'), ('Setúbal', 'Setúbal'),
                                 ('Viana do Castelo', 'Viana do Castelo'),
                                 ('Vila Real', 'Vila Real'), ('Viseu', 'Viseu'), ('Azores', 'Açores'),
                                 ('Madeira', 'Madeira')])
    property_type = StringField('Property Type', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    value = IntegerField('Value', validators=[DataRequired()])
    bedrooms = IntegerField('Bedrooms', validators=[DataRequired()])
    bathrooms = IntegerField('Bathrooms', validators=[DataRequired()])
    area = IntegerField('Area', validators=[DataRequired()])
    garage = StringField('Garage', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'), Optional()])
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

    def __str__(self):
        return f"Property(id={self.id}, name='{self.name}', address='{self.address}', city='{self.city}', distrito='{self.distrito}', property_type='{self.property_type}', price={self.price}, value={self.value}, bedrooms={self.bedrooms}, bathrooms={self.bathrooms}, area={self.area}, garage={self.garage}, description='{self.description}', photo='{self.photo}')"

class PropertySearchForm(FlaskForm):
    search_query = StringField('Search Query')
    submit = SubmitField('Search')
    name = StringField('Nome')
    address = StringField('Endereço')
    city = StringField('Cidade')
    distrito = SelectField('Distrito',
                        choices=[('', 'Selecione um distrito'), ('Aveiro', 'Aveiro'), ('Beja', 'Beja'),
                                 ('Braga', 'Braga'),
                                 ('Bragança', 'Bragança'), ('Castelo Branco', 'Castelo Branco'), ('Coimbra', 'Coimbra'),
                                 ('Évora', 'Évora'), ('Faro', 'Faro'), ('Guarda', 'Guarda'), ('Leiria', 'Leiria'),
                                 ('Lisboa', 'Lisboa'), ('Portalegre', 'Portalegre'), ('Porto', 'Porto'),
                                 ('Santarém', 'Santarém'), ('Setúbal', 'Setúbal'),
                                 ('Viana do Castelo', 'Viana do Castelo'),
                                 ('Vila Real', 'Vila Real'), ('Viseu', 'Viseu'), ('Azores', 'Açores'),
                                 ('Madeira', 'Madeira')])
    property_type = SelectField('Tipo de Propriedade',
                                choices=[('', 'Selecione um tipo'), ('house', 'Casa'), ('apartment', 'Apartamento'),
                                         ('land', 'Terreno'), ('commercial', 'Comercial'),
                                         ('industrial', 'Industrial')])
    min_price = DecimalField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = DecimalField('Max Price', validators=[Optional(), NumberRange(min=0)])
    min_bedrooms = IntegerField('Min Bedrooms', validators=[Optional(), NumberRange(min=0)])
    max_bedrooms = IntegerField('Max Bedrooms', validators=[Optional(), NumberRange(min=0)])
    min_bathrooms = IntegerField('Min Bathrooms', validators=[Optional(), NumberRange(min=0)])
    max_bathrooms = IntegerField('Max Bathrooms', validators=[Optional(), NumberRange(min=0)])

class SearchForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    marital_status = SelectField('Marital Status', choices=[('single', 'Single'), ('married', 'Married')],
                                 validators=[Optional()])
    min_age = IntegerField('Minimum Age', validators=[Optional()])
    max_age = IntegerField('Maximum Age', validators=[Optional()])
    min_income = DecimalField('Minimum Income', validators=[Optional()])
    max_income = DecimalField('Maximum Income', validators=[Optional()])
    search_query = StringField('Search by Name or Phone', validators=[DataRequired()])
    submit = SubmitField('Search')

    def search_input(self):
        return self.search_query(class_='form-control', placeholder='Enter a name or phone number', name='search_query')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

def validate_client_data(form):
    # Check if email already exists
    existing_client = Client.query.filter_by(email=form.email.data).first()
    if existing_client:
        flash('Email já cadastrado. Por favor, utilize outro email.', 'danger')
        return False
    # Check if phone number already exists
    existing_client = Client.query.filter_by(phone=form.phone.data).first()
    if existing_client:
        flash('Número de telefone já cadastrado. Por favor, utilize outro número de telefone.', 'danger')
        return False
    # Check if birthdate is valid
    today = date.today()
    age = today.year - form.birthdate.data.year - ((today.month, today.day) < (form.birthdate.data.month, form.birthdate.data.day))
    if age < 18:
        flash('O cliente deve ter pelo menos 18 anos de idade.', 'danger')
        return False
    # Check if income is positive
    if form.income.data < 0:
        flash('A renda não pode ser negativa.', 'danger')
        return False

    return True

class LeadForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[Email(), DataRequired()])
    phone = StringField('Telefone', validators=[DataRequired()])
    address = StringField('Endereço', validators=[Optional()])
    lead_date = DateField('Data do Lead', format='%d/%m/%Y', validators=[DataRequired()])
    lead_source = SelectField('Origem do Lead', choices=[
        ('Anúncio', 'Anúncio'),
        ('Indicação', 'Indicação'),
        ('Evento', 'Evento'),
        ('Outros', 'Outros')
    ], validators=[DataRequired()])
    status = SelectField('Status do Lead', choices=[
        ('Novo', 'Novo'),
        ('Em andamento', 'Em andamento'),
        ('Convertido', 'Convertido'),
        ('Descartado', 'Descartado')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notas', validators=[Optional()])
    additional_info = TextAreaField('Info Adicional', validators=[Optional()])
    date= DateField('Data de insercao', format='%d/%m/%Y', validators=[DataRequired()])


class InteractionForm(FlaskForm):
    client_id = IntegerField('Client ID', validators=[DataRequired()])
    property = SelectField('Imóvel', query_factory=lambda: Properties.query.all(), get_label='title',
                           validators=[Optional()])
    client = SelectField('Client', query_factory=lambda: Client.query.all(), validators=[DataRequired()])
    date = DateField('Data da interação', format='%d/%m/%Y', validators=[DataRequired()])
    type = SelectField('Tipo de interação', choices=[
        ('Email', 'Email'),
        ('Telefone', 'Telefone'),
        ('Reunião', 'Reunião'),
        ('Outros', 'Outros')
    ], validators=[DataRequired()])
    notes = TextAreaField('Observações', validators=[Optional()])
    next_action = StringField('Próxima ação', validators=[Optional()])


class SaleForm(FlaskForm):
    date = DateField('Data da venda', format='%d/%m/%Y', validators=[DataRequired()])
    value = IntegerField('Valor', validators=[DataRequired()])
    notes = TextAreaField('Observações', validators=[Optional()])


class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class CommentForm(FlaskForm):
    author = StringField('Your Name', validators=[DataRequired()])
    text = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Client:
    def __init__(self, name, email, phone, client_properties=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.client_properties = client_properties
