import os

from datetime import datetime
import base64

from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for Properties
class Properties(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    distrito = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    area = db.Column(db.Integer, nullable=False)
    garage = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    photo = db.Column(db.String(100), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', back_populates='properties')
    def __repr__(self):
        return f'<Properties {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'distrito': self.distrito,
            'photo': self.get_photo_data() if self.photo else None,
        }

    def get_photo_data(self):
        if not os.path.exists(self.photo):
            return None

        with open(self.photo, 'rb') as f:
            photo_data = f.read()

        return base64.b64encode(photo_data).decode('utf-8')


# Model for Client
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    birthdate = db.Column(db.String(20))
    marital_status = db.Column(db.String(20))
    profession = db.Column(db.String(50))
    income = db.Column(db.Integer)
    properties = db.relationship('Properties', back_populates='client', lazy=True)
    sales = db.relationship('Sale', backref='client', lazy=True)
    interactions = db.relationship('Interaction', backref='client', lazy=True)


    def __repr__(self):
        #    return f'<Client {self.name}>'
        return f'Client({self.name}, {self.email})'


    # Model for Users
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # properties = db.relationship('Properties', backref='client')
   #  properties = db.relationship('Properties', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_username(self, username):
        self.username = username

    def set_email(self, email):
        self.email = email

# Model for Sale
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    commission = db.Column(db.Integer, nullable=False)
    closing_date = db.Column(db.DateTime)
    details = db.Column(db.String(500))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

    def __repr__(self):
        return f'<Sale {self.id}>'


# Model for Lead
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    source = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20))
    additional_info = db.Column(db.String(500))

    def __repr__(self):
        return f'<Lead {self.id}>'


# Model for Interaction
class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.String(500))
    next_action = db.Column(db.String(50))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

class ClientPropertyAssociation(db.Model):
        __tablename__ = 'client_property_association'
        id = db.Column(db.Integer, primary_key=True)
        client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
        property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
        date_acquired = db.Column(db.Date)
        client = db.relationship('Client', backref=db.backref('property_associations', cascade='all, delete-orphan'))
        property = db.relationship('Properties', backref=db.backref('client_associations', cascade='all, delete-orphan'))
