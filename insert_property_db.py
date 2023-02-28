from flask import (
    Flask)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/pit/PycharmProjects'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
# from app import db

from models import Properties

# create a new property object
new_property = Properties(
    name='Example Property',
    address='123 Main St',
    property_type='House',
    price=100000,
    bedrooms=3,
    bathrooms=2,
    area=1500,
    garage='2-car',
    description='This is an example property.',
    photo='https://example.com/property.jpg'
)

# add the new property to the database session and commit changes
db.session.add(new_property)
db.session.commit()

# print the ID of the newly created property
print(f"Created new property with ID {new_property.id}")
