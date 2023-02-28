import os

from flask import (
    Blueprint,
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
)
from flask_migrate import Migrate
from flask_wtf.csrf import generate_csrf
from sqlalchemy import create_engine
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from forms import (
    RegistrationForm,
    LoginForm,
    InteractionForm,
    ClientForm,
    PropertiesForm,
    PropertySearchForm,
    CommentForm,
)
from models import (
    db,
    Client,
    Properties,
    Lead,
    Interaction,
    Users,
)

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'photos')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'e2d7dd8c522f1cf159f6b45a6d7e8c25'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # set maximum content length to 16 MB

# Initialize Flask extensions
db.init_app(app)

migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

# Create a blueprint for this module
bp = Blueprint('views', __name__, url_prefix='/')

# Set up database connection
engine = create_engine('sqlite:///crm.db')
Session = sessionmaker(bind=engine)
session = scoped_session(Session)


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


            flash(f"Error in the {getattr(form, field).label.text}: {error}", "error")
# Home page


@app.before_first_request
def create_tables():
    db.create_all()


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())


# Home page


@app.route('/')
# @login_required
def home():
     return render_template('home.html', title='Home')
  #  return render_template('index.html', title='Home', user=current_user)


@app.route('/static/css/style.css')
def serve_css():
    return app.send_static_file('css/style.css')



@app.route('/clients', methods=['GET', 'POST'])
def client_detail(client_id):
    client = Client.query.get(client_id)
    form = ClientForm(obj=client)

    if request.method == 'POST' and form.validate():
        form.populate_obj(client)
        db.session.commit()
        flash('Dados do cliente atualizados com sucesso.', 'success')

    if not client:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('clients'))

    return render_template('clients.html', client=client, form=form)


@app.route('/clients/delete/<int:client_id>', methods=['POST'])
def client_delete(client_id):
    client = Client.query.get(client_id)

    if not client:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('clients'))

    db.session.delete(client)
    db.session.commit()

    flash(f'Cliente {client.name} excluído com sucesso.', 'success')

    return redirect(url_for('clients'))


###### Properties pages

@app.route('/properties/<int:property_id>', methods=['GET', 'POST'])
def property_detail(property_id):
    property = Properties.query.get(property_id)
    form = PropertiesForm(obj=property)

    if request.method == 'POST' and form.validate():
        form.populate_obj(property)
        db.session.commit()
        flash('Dados do imóvel atualizados com sucesso.', 'success')

    if not property:
        flash('Imóvel não encontrado.', 'error')
        return redirect(url_for('properties'))

    return render_template('property_detail.html', property=property, form=form)


@app.route('/properties/delete/<int:property_id>', methods=['POST'])
def property_delete(property_id):
    property = Properties.query.get(property_id)

    if not property:
        flash('Imóvel não encontrado.', 'error')
        return redirect(url_for('properties'))

    db.session.delete(property)
    db.session.commit()

    flash(f'Imóvel {property.name} excluído com sucesso.', 'success')

    return redirect(url_for('properties'))

@app.route('/leads/<int:lead_id>', methods=['GET', 'POST'])
def view_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    interaction_form = InteractionForm()
    comment_form = CommentForm()

    if interaction_form.validate_on_submit():
        interaction = Interaction(
            date=interaction_form.date.data,
            type=interaction_form.type.data,
            notes=interaction_form.notes.data,
            lead_id=lead_id,
        )
        db.session.add(interaction)
        db.session.commit()
        flash('Nova interação adicionada com sucesso!', 'success')
        return redirect(url_for('views.view_lead', lead_id=lead_id))

    if comment_form.validate_on_submit():
        comment = Comment(
            text=comment_form.text.data,
            lead_id=lead_id,
        )
        db.session.add(comment)
        db.session.commit()
        flash('Novo comentário adicionado com sucesso!', 'success')
        return redirect(url_for('views.view_lead', lead_id=lead_id))

    return render_template(
        'view_lead.html',
        title=lead.name,
        lead=lead,
        interaction_form=interaction_form,
        comment_form=comment_form,
    )

@app.route('/properties', methods=['GET', 'POST'])
def properties():
    search_form = PropertySearchForm()
    properties = Properties.query.all()
    search_results = []

    if request.method == 'POST' and search_form.validate():
        search_query = search_form.search_query.data
        search_results = Properties.query.filter(or_(
            Properties.address.ilike(f'%{search_query}%'),
            Properties.neighborhood.ilike(f'%{search_query}%'),
            Properties.city.ilike(f'%{search_query}%'),
            Properties.state.ilike(f'%{search_query}%')
        )).all()

    if not search_results:
        flash('Nenhum resultado encontrado.')

    return render_template(
        'properties.html',
        title='Imóveis',
        properties=properties,
        search_form=search_form,
        search_results=search_results,
    )

@app.route('/properties/new', methods=['GET', 'POST'])
def new_property():
    form = PropertiesForm()

    if form.validate_on_submit():
        # Save the uploaded photo to disk
        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            form.photo.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        # Create a new property
        property = Properties(
            address=form.address.data,
            neighborhood=form.neighborhood.data,
            city=form.city.data,
            state=form.state.data,
            zip=form.zip.data,
            photo=filename,
            price=form.price.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            description=form.description.data,
        )
        db.session.add(property)
        db.session.commit()
        flash('Novo imóvel adicionado com sucesso!', 'success')
        return redirect(url_for('views.properties'))

    return render_template('new_property.html', title='Novo imóvel', form=form)

@app.route('/properties/<int:property_id>', methods=['GET', 'POST'])
def view_property(property_id):
    property = Properties.query.get_or_404(property_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            text=form.text.data,
            property_id=property_id,
        )
        db.session.add(comment)
        db.session.commit()
        flash('Novo comentário adicionado com sucesso!', 'success')
        return redirect(url_for('views.view_property', property_id=property_id))

    return render_template(
        'view_property.html',
        title=property.address,
        property=property,
        form=form,
    )
@app.route('/properties/<int:property_id>/edit', methods=['GET', 'POST'])
def edit_property(property_id):
    property = Properties.query.get_or_404(property_id)
    form = PropertiesForm(obj=property)
    if form.validate_on_submit():

        # Save the uploaded photo to disk
        if form.photo.data:
            photo_file = save_photo(form.photo.data)
            property.photo = photo_file

        property.title = form.title.data
        property.description = form.description.data
        property.price = form.price.data
        property.bedrooms = form.bedrooms.data
        property.bathrooms = form.bathrooms.data
        property.size = form.size.data
        property.property_type = form.property_type.data
        property.location = form.location.data
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('views.view_property', property_id=property_id))
    return render_template('edit_property.html', title='Edit Property', form=form, property=property)

@app.route('/properties/<int:property_id>/delete', methods=['POST'])
def delete_property(property_id):
    property = Properties.query.get_or_404(property_id)

    db.session.delete(property)
    db.session.commit()

    flash('Imóvel removido com sucesso!', 'success')

    return redirect(url_for('views.properties'))



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


