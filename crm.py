import os
import sys
import base64
from base64 import b64encode
import logging.handlers
from datetime import timedelta

print(os.getcwd())

sys.path.append('/')
# import logging

from flask import (
    Blueprint,
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_migrate import Migrate
from flask_wtf.csrf import generate_csrf, CSRFProtect
from flask_wtf import form

from sqlalchemy import or_, func, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequestKeyError
from jinja2 import DebugUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify

from forms import (
    RegistrationForm,
    LoginForm,
    LeadForm,
    InteractionForm,
    ClientForm,
    SearchForm,
    PropertiesForm,
    PropertySearchForm,
)
from models import (
    db,
    Sale,
    Client,
    Properties,
    Leads,
    Interaction,
    Users,
)

# Configure logger
logger = logging.getLogger('myLogger')
logger.setLevel(logging.INFO)

handler = logging.handlers.SysLogHandler('/dev/log')
loggly_handler = logging.handlers.HTTPHandler(
    host='logs-01.loggly.com',
    url='/inputs/ae890006-bb30-4e4e-87aa-9d9a93bd8bb6/tag/python',
    method='POST',
)

formatter = logging.Formatter(
    'Python: { "loggerName":"%(name)s", "timestamp":"%(asctime)s", "pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}'
)

handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Test Log")
logger.info('This is an informational message')
logger.warning('This is a warning message')
logger.error('This is an error message')
# logging.basicConfig(filename='example.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.jinja_env.undefined = DebugUndefined
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'photos')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'e2d7dd8c522f1cf159f6b45a6d7e8c25'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # set maximum content length to 16 MB
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('SECRET_KEY') or \
                                        'abc123ced456'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1 MB

    return app


app = create_app()
print(app.config['PERMANENT_SESSION_LIFETIME'])

# Initialize Flask extensions
db.init_app(app)

migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

# csrf.init_app(app)



# Create a blueprint for this module
bp = Blueprint('views', __name__, url_prefix='/')

# Set up database connection
engine = create_engine('sqlite:///crm.db.naosei')
Session = sessionmaker(bind=engine)
session = scoped_session(Session)

toolbar = DebugToolbarExtension(app)


# Error handling
@app.errorhandler(404)
def page_not_found(error):
    app.logger.error(error)
    return 'This page does not exist', 404

@app.errorhandler(500)
def special_exception_handler(error):
    app.logger.error(error)
    return '500 error', 500

def page_not_found(error):
    return 'This page does not exist', 404


# Functions

def flash_errors(form):
    """
    Flash all errors from a form.
    """
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in the {getattr(form, field).label.text} field - {error}", "error")


@app.before_first_request
def create_tables():
    db.create_all()


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())


# Home page
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home', user=current_user)


@app.route('/static/css/style.css')
def serve_css():
    return app.send_static_file('css/style.css')


###########################################3


###### Client pages
@app.route('/clients', methods=['GET', 'POST'])
def clients():
    app.logger.debug(request.url)
    search_form = SearchForm()
    clients = Client.query.all()
    search_results = []
    form = ClientForm()

    if request.method == 'POST' and search_form.validate():
        search_query = search_form.search_query.data
        search_results = Client.query.filter(or_(
            Client.name.ilike(f'%{search_query}%'),
            Client.phone.ilike(f'%{search_query}%')
        )).all()

    if not search_results:
        flash('Nenhum resultado encontrado.')

        # Check if clients have properties
  #  has_properties = all(client.client_properties for client in clients)
    has_properties = all(hasattr(client, 'client_properties') and client.client_properties for client in clients)

    # Render template with or without client_properties depending on whether they exist
    if has_properties:
        return render_template('clients.html', clients=clients, search_form=search_form, search_results=search_results,
                               client_properties=client_properties)
    else:
        return render_template('clients.html', clients=clients, search_form=search_form, search_results=search_results,
                               client_properties=None)



@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    print("Reached add_client view function")
    search_query = request.form.get('search_query')

    form = ClientForm()
    client = []
    search_results = []

    from datetime import date
    from flask import flash

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
        age = today.year - form.birthdate.data.year - (
                (today.month, today.day) < (form.birthdate.data.month, form.birthdate.data.day))
        if age < 18:
            flash('O cliente deve ter pelo menos 18 anos de idade.', 'danger')
            return False

        # Check if income is positive
        if form.income.data < 0:
            flash('A renda não pode ser negativa.', 'danger')
            return False

        return True

    if form.validate_on_submit():
        if not validate_client_data(form):
            return render_template('add_client.html', form=form)
        # create a new client object from the form data
        new_client = Client(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            birthdate=form.birthdate.data,
            marital_status=form.marital_status.data,
            profession=form.profession.data,
            income=form.income.data
        )

        # add the new client to the database
        db.session.add(new_client)
        db.session.commit()

        # redirect to the view clients page

        flash('Cliente adicionado com sucesso!', 'success')

        # Debug
        print(f"Search Query: {search_query}")
        #  print(f"Query: {query}")
        print(f"Client: {client}")
        print(f"Search Results: {search_results}")

        return redirect(url_for('view_clients'))

    # return render_template('add_client.html', form=form)
    return render_template('add_client.html', form=form)


@app.route('/edit_client', methods=['GET', 'POST'])
def edit_client():
    global client_id
    print("Reached edit_client view function")

    search_form = SearchForm(request.form)
    client = None

    if request.method == 'POST' and search_form.validate():
        search_query = search_form.search_query.data
        search_results = Client.query.filter(or_(
            Client.name.ilike(f'%{search_query}%'),
            Client.phone.ilike(f'%{search_query}%')
        )).all()

        return render_template('edit_client.html', search_form=search_form, search_results=search_results)

    elif request.method == 'GET' and 'client_id' in request.args:
        client_id = request.args.get('client_id')
    # client = Client.query.get(client_id)
    client = db.session.get(Client, client_id)

    if client is None:
        return redirect(url_for('edit_client'))

    if request.method == 'POST':
        client.name = request.form['name']
        client.email = request.form['email']
        client.phone = request.form['phone']
        client.address = request.form['address']
        client.birthdate = request.form['birthdate']
        client.marital_status = request.form['marital_status']
        client.profession = request.form['profession']
        client.income = request.form['income']

        db.session.commit()

        flash('Client updated successfully.')
    return render_template('edit_client.html', search_form=search_form, client=client)


@app.route('/update_client/<int:client_id>', methods=['GET', 'POST'])
def update_client(client_id):
    client = db.session.query(Client).get(client_id)
    form = ClientForm(obj=client)
    if form.validate_on_submit():
        form.populate_obj(client)
        db.session.commit()
        flash('Client updated successfully!', 'success')
        return redirect(url_for('view_clients'))

    return render_template('update_client.html', form=form, client=client)


@app.route('/delete_client/<int:client_id>', methods=['GET', 'POST'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)

    if request.method == 'POST':
        db.session.delete(client)
        db.session.commit()
        flash(f'{client.name} was deleted from the database.', 'success')
        return redirect(url_for('view_clients'))

    return render_template('delete_client.html', client=client)

@app.route('/view_clients', methods=['GET', 'POST'])
def view_clients():
    search_form = SearchForm(request.form)
    clients = Client.query.all()
    search_results = []
    print(clients)

    if request.method == 'POST' and search_form.validate():
        search_query = search_form.search_query.data
        search_results = Client.query.filter(or_(
            Client.name.ilike(f'%{search_query}%'),
            Client.phone.ilike(f'%{search_query}%')
        )).all()

    if request.method == 'POST' and search_form.validate():
        search_query = search_form.search_query.data
        search_results = Client.query.filter(or_(
            Client.name.ilike(f'%{search_query}%'),
            Client.phone.ilike(f'%{search_query}%')
        )).all()

        print(search_results)

    if search_results:
        # Redirect to the client properties page for the first result
        return redirect(url_for('client_properties', client_id=search_results[0].id))

    if request.method == 'POST' and 'client_id' in request.form:
        client_id = request.form['client_id']
        return redirect(url_for('client_properties', client_id=client_id))

    return render_template('clients.html', clients=clients, search_form=search_form, search_results=search_results)


if __name__ == '__main__':
    app.run(debug=True)

from sqlalchemy import extract


@app.route('/search_clients', methods=['GET', 'POST'])
def search_clients():
    try:
        search_query = request.form['search_query']
    except BadRequestKeyError:
        search_query = ''
    search_results = []
    form = SearchForm(request.form)

    form = SearchForm(request.form)
    clients = []

    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        marital_status = form.marital_status.data
        min_age = form.min_age.data
        max_age = form.max_age.data
        min_income = form.min_income.data
        max_income = form.max_income.data

        # Query the database to find clients that match the search criteria
        clients = Client.query.filter(
            Client.name.ilike(f'%{name}%'),
            Client.email.ilike(f'%{email}%'),
            Client.marital_status.ilike(f'%{marital_status}%'),
            extract('year', func.age(Client.birthdate)) >= min_age,
            extract('year', func.age(Client.birthdate)) <= max_age,
            Client.income >= min_income,
            Client.income <= max_income
        ).all()

        # filter clients list based on search query
        for client in clients:
            if search_query.lower() in client.name.lower() or \
                    search_query.lower() in client.email.lower() or \
                    search_query.lower() in client.phone.lower():
                search_results.append(client)

    flash(f"Resultados da busca por '{search_query}': {len(search_results)} clientes encontrados.")

    return render_template('search_clients_2.html', clients=clients, search_results=search_results, form=form)


if __name__ == '__main__':
    app.run(debug=True)



################ Property pages ########################

@app.route('/properties', methods=['GET', 'POST'])
def properties():
    print("properties route requested")
    app.logger.debug(request.url)

    search_form = SearchForm()
    properties = Properties.query.all()
    search_results = []
    form = PropertiesForm()

    if request.method == 'POST' and search_form.validate():
        search_query = search_form.search_query.data
        search_results = Properties.query.filter(or_(
            Properties.address.ilike(f'%{search_query}%'),
            Properties.property_type.ilike(f'%{search_query}%')
        )).all()

    if not search_results:
        flash('Nenhum resultado encontrado.')

    print(f"search_results: {search_results}")
    return render_template('properties.html', properties=properties, search_form=search_form,
                           search_results=search_results)


if __name__ == '__main__':
    app.run(debug=True)


# Rota para página de cadastro de propriedades
@app.route('/add_property', methods=['GET', 'POST'])
@login_required
def add_property():
    form = PropertiesForm()
    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        city = form.city.data
        distrito = form.distrito.data
        value = form.value.data
        property_type = form.property_type.data
        price = form.price.data
        bedrooms = form.bedrooms.data
        bathrooms = form.bathrooms.data
        area = form.area.data
        garage = form.garage.data
        description = form.description.data
        photo = form.photo.data
        print(photo)
        print(request.form['name'])
        print(request.form['address'])
        print(request.form['city'])
        print(request.form['distrito'])
        print(request.form['value'])
        print(request.form['property_type'])
        print(request.form['price'])
        print(request.form['bedrooms'])
        print(request.form['bathrooms'])
        print(request.form['area'])
        print(request.form['garage'])
        print(request.form['description'])

        # Save uploaded photo file
        if photo:
            photo_file = request.files['photo']
            filename = secure_filename(photo_file.filename)
            upload_dir = app.config['UPLOAD_FOLDER']
            print(upload_dir)
            photo_file.save(os.path.join(upload_dir, filename))

            # Read the file contents into memory as a bytes object
            with photo_file.stream as f:
                photo_bytes = f.read()

            if not os.path.exists(upload_dir):
                flash('Upload directory does not exist', 'danger')
            elif not os.access(upload_dir, os.W_OK):
                flash('Upload directory is not writable', 'danger')
            else:
                try:
                    new_property = Properties(name=name, address=address, city=city, distrito=distrito, value=value,
                                              property_type=property_type, price=price, bedrooms=bedrooms,
                                              bathrooms=bathrooms, area=area, garage=garage, description=description,
                                              photo=photo_bytes, client_id=current_user.id)
                    db.session.add(new_property)
                    db.session.commit()
                    flash('Property added successfully!', 'success')

                    return redirect(url_for('view_properties'))

                except Exception as e:
                    db.session.rollback()
                    flash(f'Error adding property: {e}', 'danger')
                    print('Error adding property:', e)
        else:
            filename = None
            new_property = Properties(name=name, address=address, city=city, distrito=distrito, value=value,
                                      property_type=property_type, price=price, bedrooms=bedrooms,
                                      bathrooms=bathrooms, area=area, garage=garage, description=description,
                                      client_id=current_user.id)
            db.session.add(new_property)
            db.session.commit()
            flash('Property added successfully!', 'success')

            return redirect(url_for('view_properties'))

        print("The maximum content length allowed is " + str(app.config['MAX_CONTENT_LENGTH']) + " bytes.")
        print(f"Maximum content length in function {MAX_CONTENT_LENGTH} is {app.config['MAX_CONTENT_LENGTH']} bytes.")

    else:
        print(form.errors)  # Print validation errors to the console

    return render_template('add_property.html', title='Add Property', form=form)



# Rota para página de edição de propriedades
@app.route('/edit_property/<int:id>', methods=['GET', 'POST'])
def edit_property(id):
    property = Properties.query.get(id)
    if not property:
        abort(404)
    print(property)
 #  return jsonify(property.to_dict())

    form = PropertiesForm(obj=property)
    if form.validate_on_submit():
        form.populate_obj(property)
        # Process the uploaded photo, if provided
        photo_file = request.files.get('photo')
        if photo_file:
            filename = secure_filename(photo_file.filename)
            upload_dir = app.config['UPLOAD_FOLDER']
            print(upload_dir)
            photo_file.save(os.path.join(upload_dir, filename))  # save the file to disk

            # Read the file contents into memory as a memoryview object
            with open(os.path.join(upload_dir, filename), 'rb') as f:
                photo = memoryview(f.read())

            if not os.path.exists(upload_dir):
                flash('Upload directory does not exist', 'danger')
            elif not os.access(upload_dir, os.W_OK):
                flash('Upload directory is not writable', 'danger')
            else:
                try:
                    print('File saved successfully:', filename)

                except Exception as e:
                    flash(f'Error saving file: {e}', 'danger')
                    filename = None
                    print('Error saving file:', e)

            property.photo = photo

        db.session.commit()
        flash('Propriedade atualizada com sucesso!', 'success')

        return redirect(url_for('view_properties'))
    return render_template('edit_property.html', property=property, properties=properties, form=form, b64encode=b64encode)


@app.route('/search_properties', methods=['GET', 'POST'])
def search_properties():
    search_query = None  # Initialize search_query to None
    search_results = []
    form = PropertySearchForm()
    if 'search_query' in request.form:
        search_query = request.form['search_query']
        # rest of the code that uses search_query
    else:
        client_properties = None # handle the case when search_query is not present
    # search_query = f"%{form.search_query.data}%"
    print('search_properties() function executed')
    print('Template path:', os.path.join(app.template_folder, 'search_properties.html'))
    print(form)
    print(dir(form))

    properties = []

    if request.method == 'POST' and form.validate():
        address = form.address.data  # get the address value from the form
        city = form.city.data
        distrito = form.distrito.data
        property_type = form.property_type.data
        min_price = form.min_price.data
        max_price = form.max_price.data
        min_bedrooms = form.min_bedrooms.data
        max_bedrooms = form.max_bedrooms.data
        min_bathrooms = form.min_bathrooms.data
        max_bathrooms = form.max_bathrooms.data

        # Query the database to find properties that match the search criteria
        properties = Properties.query.filter(
            Properties.address.ilike(f'%{address}%'),
            Properties.city.ilike(f'%{city}%'),
            Properties.distrito.ilike(f'%{distrito}%'),
            Properties.property_type.ilike(f'%{property_type}%'),
            Properties.price >= min_price,
            Properties.price <= max_price,
            Properties.bedrooms >= min_bedrooms,
            Properties.bedrooms <= max_bedrooms,
            Properties.bathrooms >= min_bathrooms,
            Properties.bathrooms <= max_bathrooms,
            (Properties.name.ilike(search_query)) |
            (Properties.address.ilike(search_query)) |
            (Properties.city.ilike(search_query))
        )
        print(str(properties.statement.compile(compile_kwargs={"literal_binds": True})))
        properties = properties.all()

        # filter properties list based on search query
        for property in properties:
            if search_query.lower() in property.name.lower() or \
                    search_query.lower() in property.address.lower() or \
                    search_query.lower() in property.city.lower():
                search_results.append(property)

    print(f"search_query 1: {search_query}")
    print(f"search_results: {search_results}")

    flash(f"Resultados da busca por '{search_query}': {len(search_results)} imóveis encontrados.")

    return render_template('search_properties.html', properties=properties, search_results=search_results, form=form,
                           search_form=form)


# Rota para página de visualização de propriedades
@app.route('/view_properties', methods=['GET', 'POST'])
def view_properties():
    search_form = SearchForm(request.form)
    properties = Properties.query.all()
    search_results = []

    if request.method == 'POST' and search_form.validate():
        search_query = search_form.search_query.data
        search_results = Properties.query.filter(or_(
            Properties.address.ilike(f'%{search_query}%'),
            Properties.price.ilike(f'%{search_query}%')
        )).all()
        if not search_results:
            flash('No properties found.')
            return redirect(url_for('home'))

    property_id = request.args.get('id')
    if property_id:
        property = Properties.query.filter_by(id=property_id).first()
        if property:
            return render_template('view_property.html', property=property, search_form=search_form,
                                   search_results=search_results)
        else:
            flash(f'Property with id {property_id} not found.')
            return redirect(url_for('home'))

    return render_template('view_properties.html', properties=properties, search_form=search_form,
                           search_results=search_results)

@app.route('/view_property/<int:id>')
def view_property(id):
    property = Properties.query.get_or_404(id)
    photo_filename = property.photo
    print(photo_filename)

    return render_template('view_property.html', property=property, photo_filename=photo_filename)

@app.route('/property_photo/<filename>')
def property_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/delete_property/<int:id>', methods=['GET', 'POST'])
def delete_property(id):
    property = Properties.query.get_or_404(id)
    print(properties) # Add this line to print out the properties

    if request.method == 'POST':
        db.session.delete(property)
        db.session.commit()
        flash('Property deleted successfully!', 'success')
        return redirect(url_for('view_properties'))
    return render_template('confirm_delete.html', property=property)



@app.route('/update_property/<int:id>', methods=['GET', 'POST'])
@login_required
def update_property(id):
    properties = Properties.query.get_or_404(id)
    if not property:
        abort(404)

    form = PropertiesForm(obj=properties)

    if form.validate_on_submit():
        form.populate_obj(properties)
        if form.validate_on_submit():
            properties.name = form.name.data
            properties.address = form.address.data
            properties.city = form.city.data
            properties.distrito = form.distrito.data
            properties.value = form.value.data
            properties.property_type = form.property_type.data
            properties.price = form.price.data
            properties.bedrooms = form.bedrooms.data
            properties.bathrooms = form.bathrooms.data
            properties.area = form.area.data
            properties.garage = form.garage.data
            properties.description = form.description.data

            if form.photo.data:
                print("Photo data: ", form.photo.data)  # Debug statement
                photo_file = save_photo(form.photo.data)

                if photo_file:
                    #properties.photo = photo_file
                    properties.photo = os.path.join(current_app.static_folder, 'photos', photo_file)  # Concatenate folder path with file name
                    print("Full photo path: ", os.path.join(current_app.static_folder,'photos',  photo_file))
                else:
                    flash('Error saving photo.', 'error')
                    return redirect(url_for('update_property', id=id))
            db.session.commit()

            flash('Property updated successfully!', 'success')
            return redirect(url_for('view_properties', id=id))
        else:
            # Pre-fill the form fields with the existing property data
            form.name.data = properties.name
            form.address.data = properties.address
            form.city.data = properties.city
            form.state.data = properties.state
            form.value.data = properties.value
            form.property_type.data = properties.property_type
            form.price.data = properties.price
            form.bedrooms.data = properties.bedrooms
            form.bathrooms.data = properties.bathrooms
            form.area.data = properties.area
            form.garage.data = properties.garage
            form.description.data = properties.description
            form.photo.data = properties.photo

            return render_template('update_property.html', form=form)

        db.session.commit()
        flash('Property updated successfully.', 'success')
        return redirect(url_for('properties', id=properties.id))

    return render_template('update_property.html', form=form, properties=properties, property=property)


##################### SALES PAGES ##################################


# Rota para página de cadastro de vendas
@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    if request.method == 'POST':
        sale_date = request.form['sale_date']
        sale_value = request.form['sale_value']
        commission = request.form['commission']
        closing_date = request.form['closing_date']  # corrected spelling
        property_id = request.form['property_id']
        client_id = request.form['client_id']
        new_sale = Sale(sale_date=sale_date, sale_value=sale_value, commission=commission, closing_date=closing_date,
                        property_id=property_id, client_id=client_id)
        db.session.add(new_sale)
        db.session.commit()
        flash('Venda adicionada com sucesso!', 'success')
        return redirect(url_for('view_sales'))
    properties = Properties.query.all()
    clients = Client.query.all()
    return render_template('add_sale.html', properties=properties, clients=clients)


# Rota para página de edição de vendas
@app.route('/edit_sale/<int:id>', methods=['GET', 'POST'])
def edit_sale(id):
    sale = Sale.query.get_or_404(id)
    if request.method == 'POST':
        sale.sale_date = request.form['sale_date']
        sale.sale_value = request.form['sale_value']
        sale.commission = request.form['commission']
        sale.closing_date = request.form['closing_date']
        sale.property_id = request.form['property_id']
        sale.client_id = request.form['client_id']
        db.session.commit()
        flash('Venda atualizada com sucesso!', 'success')
        return redirect(url_for('view_sales'))
    properties = Properties.query.all()
    clients = Client.query.all()
    return render_template('edit_sale.html', sale=sale, properties=properties, clients=clients)


# Rota para página de visualização de vendas
@app.route('/view_sales')
def view_sales():
    sales = Sale.query.all()
    return render_template('view_sales.html', sales=sales)


########### LEADS ############


@app.route('/add_lead', methods=['GET', 'POST'])
def add_lead():
    form = LeadForm()
    print("Reached add_lead view function")
    search_query = request.form.get('search_query')
    print(f"Search Query: {search_query}")
    lead = []
    search_results = []

    from datetime import date
    from flask import flash

    if form.validate_on_submit():
        new_lead = Leads(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            lead_date=form.lead_date.data,
            lead_source=form.lead_source.data,
            status=form.status.data,
            notes=form.notes.data,
            additional_info=form.additional_info.data,
        )
        print(f"Name: {new_lead.name}")
        print(f"Email: {new_lead.email}")
        print(f"Phone: {new_lead.phone}")
        print(f"Address: {new_lead.address}")
        print(f"Lead Date: {new_lead.lead_date}")
        print(f"Lead Source: {new_lead.lead_source}")
        print(f"Status: {new_lead.status}")
        print(f"Notes: {new_lead.notes}")
        print(f"Additional Info: {new_lead.additional_info}")

        db.session.add(new_lead)
        db.session.commit()
        flash('Lead added successfully.', 'success')

        # Debug
        print(f"Search Query: {search_query}")
        print(f"Lead: {lead}")
        print(f"Search Results: {search_results}")

        return redirect(url_for('view_leads'))

    print(f"Validation errors: {form.errors}")
    return render_template('add_lead.html', title='Add Lead', form=form)



@app.route('/edit_lead/<int:lead_id>', methods=['GET', 'POST'])
def edit_lead():
    global lead_id

    lead_id = request.args.get('id')
    lead = Lead.query.filter_by(id=lead_id).first()
    lead = Lead.query.get_or_404(id)
    form = LeadForm()
    if form.validate_on_submit():
        lead.name = form.name.data
        lead.email = form.email.data
        lead.phone = form.phone.data
        lead.address = form.address.data
        lead.lead_date = form.lead_date.data
        lead.lead_source = form.lead_source.data
        lead.status = form.status.data
        lead.notes = form.notes.data
        db.session.commit()
        flash('Lead atualizado com sucesso!', 'success')
        return redirect(url_for('view_leads'))
    elif request.method == 'GET':
        form.name.data = lead.name
        form.email.data = lead.email
        form.phone.data = lead.phone
        form.address.data = lead.address
        form.lead_date.data = lead.lead_date
        form.lead_source.data = lead.lead_source
        form.status.data = lead.status
        form.notes.data = lead.notes
    return render_template('edit_lead.html', form=form)


@app.route('/view_leads', methods=['GET', 'POST'])
def view_leads():
    search_form = SearchForm(request.form)
    leads = Leads.query.all()
    search_results = []
    print(leads)

    if request.method == 'POST' and search_form.validate():
        search_query = search_form.search_query.data
        search_results = Leads.query.filter(or_(
            Leads.name.ilike(f'%{search_query}%'),
            Leads.phone.ilike(f'%{search_query}%'),
            Leads.email.ilike(f'%{search_query}%')
        )).all()

    if search_results:
        # Redirect to the lead properties page for the first result
        return redirect(url_for('lead_properties', lead_id=search_results[0].id))

    if request.method == 'POST' and 'lead_id' in request.form:
        lead_id = request.form['lead_id']
        return redirect(url_for('lead_properties', lead_id=lead_id))

    return render_template('leads.html', leads=leads, search_form=search_form, search_results=search_results)

@app.route('/lead_properties/<int:lead_id>', methods=['GET'])
def lead_properties(lead_id):
    lead = Leads.query.get_or_404(lead_id)
    return render_template('lead_properties.html', lead=lead)

@app.route('/delete_lead/<int:lead_id>', methods=['POST'])
def delete_lead(lead_id):
    lead = Leads.query.get_or_404(lead_id)
    db.session.delete(lead)
    db.session.commit()
    flash(f'Lead {lead.name} has been deleted', 'success')
    return redirect(url_for('view_leads'))




@app.route('/add_interaction', methods=['GET', 'POST'])
def add_interaction():
    form = InteractionForm()
    if form.validate_on_submit():
        interaction = Interaction(
            client_id=form.client_id.data,
            date=form.date.data,
            notes=form.notes.data,
            next_action=form.next_action.data
        )
        db.session.add(interaction)
        db.session.commit()
        flash('Interação adicionada com sucesso!', 'success')
        return redirect(url_for('view_interactions'))
    return render_template('add_interaction.html', form=form)


@app.route('/edit_interaction/<int:id>', methods=['GET', 'POST'])
def edit_interaction(id):
    interaction = Interaction.query.get_or_404(id)
    form = InteractionForm()
    if form.validate_on_submit():
        interaction.client_id = form.client_id.data
        interaction.date = form.date.data
        interaction.notes = form.notes.data
        interaction.next_action = form.next_action.data
        db.session.commit()
        flash('Interação atualizada com sucesso!', 'success')
        return redirect(url_for('view_interactions'))
    elif request.method == 'GET':
        form.client_id.data = interaction.client_id
        form.date.data = interaction.date
        form.notes.data = interaction.notes
        form.next_action.data = interaction.next_action
    return render_template('edit_interaction.html', form=form)


@app.route('/view_interactions')
def view_interactions():
    interactions = Interaction.query.all()
    return render_template('view_interactions.html', interactions=interactions)

@app.route('/view_reports')
def view_reports():
    return render_template('view_reports.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():

        current_app.logger.debug(f"Username entered: {form.username_or_email.data}")
        current_app.logger.debug(f"Password entered: {form.password.data}")
        print(f"Username entered: {form.username_or_email.data}")
        print(f"Password entered: {form.password.data}")

        username_or_email = form.username_or_email.data
        password = form.password.data

        user = Users.query.filter(or_(Users.username == username_or_email, Users.email == username_or_email)).first()

        if username_or_email is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        user = Users.query.filter((Users.username == username_or_email) | (Users.email == username_or_email)).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            app.logger.debug(f"Login successful for username: {form.username_or_email.data}")
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
            app.logger.debug(f"Login failed for username: {form.username_or_email.data}")

    # Debugging statement
    app.logger.debug(f"Errors: {form.errors}")
    print(f"Errors: {form.errors}")

    return render_template('login.html', title='Login', form=form)


@app.route('/register_user', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        print(f"Username entered: {form.username.data}")
        print(f"Password entered: {form.password.data}")
        print(f"Email entered: {form.email.data}")

        # Check if email already exists in database
        existing_user = Users.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already exists. Please choose a different email address.')
            return redirect(url_for('register'))

        # user = Users(username=form.username.data, email=form.email.data)
        user = Users()
        user.set_username(form.username.data)
        user.set_email(form.email.data)
        user.set_password(form.password.data)  # Set password hash
        # user.password_hash = user.password_hash  # Set the password_hash attribute
        #        user.password_hash = form.password.data  # Set password attribute
        user.password = generate_password_hash(form.password.data)
        #        user.password = form.password.data

        engine = db.get_engine()
        conn = engine.connect()
        Session = scoped_session(sessionmaker(bind=engine))

        db.session.add(user)

        # Print the SQL statement that will be executed
        print(str(user.__table__.insert().values(
            username=user.username,
            email=user.email,
            password=user.password_hash
            # ).compile(dialect=db.session.bind.dialect)))
        ).compile(dialect=engine.dialect)))

        db.session.commit()

        # Print the values added to the database
        print(f"Username added to database: {user.username}")
        print(f"Email added to database: {user.email}")
        print(f"Password hash added to database: {user.password}")

        #    print(str(db.session.get_bind().engine.compile(Users.__table__.insert())))
        app.logger.debug(f"Query: {db.session.query(Users).filter_by(email=form.email.data).first()}")

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register_user.html', title='Register', form=form)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

def get_client_by_id_or_name(client_id_or_name):
    try:
        # search for client by ID
        client = Client.query.filter_by(id=client_id_or_name).first()
        if not client:
            # search for client by name
            client = Client.query.filter_by(name=client_id_or_name).first()
        return client
    except:
        return None

def get_properties_for_client(client):
    properties = Properties.query.filter_by(client_id=client.id).all()
    return properties

@app.route('/client_properties/<int:client_id>', methods=['GET'])
def client_properties(client_id):
    client_id_or_name = request.form.get('client_id')
    client = Client.query.filter_by(id=client_id).first_or_404()
   # client = Client.query.filter(or_(Client.id == client_id_or_name,
   #                                  Client.name == client_id_or_name)).first_or_404()
    print('client_properties view reached with client_id:', client_id)
    properties = [association.property for association in client.property_associations]
    print('Rendering template with parameters:', {'client': client, 'properties': properties})
    return render_template('client_properties.html', client=client, properties=properties)
@app.route('/search_client_properties', methods=['GET', 'POST'])
def search_client_properties():
    clients = Client.query.all()
    print(f"clients: {clients}")
    client = None
    if request.method == 'POST':
        client_id_or_name = request.form.get('client_id_or_name')
        client = get_client_by_id_or_name(client_id_or_name)
        print(f"client: {client}")
        if client_id_or_name:
            # search for clients by ID or name
            clients = Client.query.filter(
                or_(Client.id == client_id_or_name, Client.name.like(f'%{client_id_or_name}%'))
            ).all()
            print(f"clients: {clients}")
    if client:
        properties = get_properties_for_client(client)
        print(f"properties: {properties}")
    else:
        properties = None
        if client:
            properties = get_properties_for_client(client)
            if not properties:
                properties = "Client has no properties."
    return render_template('search_client_properties.html', clients=clients, client=client, properties=properties,
                           client_id=client.id if client else None)

@app.route('/acquire_property/<int:client_id>/<int:property_id>')
def acquire_property(client_id, property_id):
    client = Client.query.get(client_id)
    property = Property.query.get(property_id)

    # Create a new association record
    association = ClientPropertyAssociation(client=client, property=property, date_acquired=date.today())

    # Add the new association record to the session and commit changes
    db.session.add(association)
    db.session.commit()

    # Set the client variable to be passed to the template
    client = client

    # Return a success message
    flash('Property successfully acquired!', 'success')
    return render_template('acquire_property.html', client=client, property=property)

@app.template_filter('decode')
def decode(s):
    return s.decode('utf-8')


@app.template_filter()
def get_attribute(obj, attribute):
    return obj[attribute]

@app.template_filter()
def to_base64(data):
    return base64.b64encode(data).decode('utf-8')

@app.context_processor
def inject_debug():
    return dict(debug=app.debug)

if __name__ == '__main__':
    app.run(debug=True)

@property
def client_properties(self):
        return self._client_properties

@client_properties.setter
def client_properties(self, value):
        self._client_properties = value

def save_photo1(photo):
    if not photo:
        return None
        print(f"Photo object: {photo}")
        print(f"Photo filename: {photo.filename}")
        # Generate a random file name to avoid collisions
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(photo.filename)
    photo_filename = random_hex + f_ext
    photo_path = os.path.join(current_app.root_path, 'static/photos', photo_filename)
    print(f"Photo path: {photo_path}")

    # Resize and save the photo
    output_size = (600, 600)
    img = Image.open(photo)
    img.thumbnail(output_size)
    img.save(photo_path)

    # Return the photo file path along with the file name
    return os.path.join('static/photos', photo_filename)

def save_photo2(photo):
    if photo:
        if isinstance(photo, str):  # Handle file paths
            filename = os.path.basename(photo)
            photo_path = os.path.join(current_app.static_folder, 'photos', filename)
            with open(photo, 'rb') as f:
                photo_data = f.read()
        else:  # Handle file storage objects
            filename = photo.filename
            photo_path = os.path.join(current_app.static_folder, 'photos', filename)
            photo_data = photo.read()
        with Image.open(BytesIO(photo_data)) as img:
            # Resize the image if necessary
            if img.width > 640 or img.height > 640:
                img.thumbnail((640, 640))
            # Save the image to a BytesIO object
            output = BytesIO()
            img.save(output, format='JPEG')
            output.seek(0)
            # Save the BytesIO object to a file
            with open(photo_path, 'wb') as f:
                f.write(output.read())
            # Return the filename
            return filename
    else:
        return None


import os
import secrets
from io import BytesIO
from PIL import Image
from flask import current_app


def save_photo(photo):
    if not photo:
        print("Photo object is not provided.")
        return None
        print(f"Photo object: {photo}")
        print(f"Photo filename: {photo.filename}")

    if isinstance(photo, str):  # Handle file paths
        filename = os.path.basename(photo)
        photo_path = os.path.join(current_app.static_folder, 'photos', filename)
        with open(photo, 'rb') as f:
            photo_data = f.read()
    else:  # Handle file storage objects
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(photo.filename)
        filename = random_hex + f_ext
        photo_path = os.path.join(current_app.static_folder, 'photos', filename)
        photo_data = photo.read()

    print(f"Photo filename: {filename}")
    print(f"Photo path: {photo_path}")

    with Image.open(BytesIO(photo_data)) as img:
        # Resize the image if necessary
        if img.width > 640 or img.height > 640:
            img.thumbnail((640, 640))
        # Save the image to a BytesIO object
        output = BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)
        # Save the BytesIO object to a file
        with open(photo_path, 'wb') as f:
            f.write(output.read())
        # Return the filename
        return filename





