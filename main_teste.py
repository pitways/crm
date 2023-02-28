import os
import sqlite3
from datetime import datetime

from flask import Blueprint
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_

from forms import LeadForm, InteractionForm, ClientForm, SearchForm
from helpers import validate_client_data
from models import db, Sale, Client, Property, Lead, Interaction
from search_form import SearchForm


# from email_validator import validate_email, EmailNotValidError

def flash_errors(form):
    """
    Flash all errors from a form.
    """
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in the {getattr(form, field).label.text} field - {error}", "error")


app = Flask(__name__)
# db.init_app(app)

dir_path = os.path.dirname(os.path.realpath(__file__))
root_path = dir_path
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates_imocrm')

# app = Flask(__name__, root_path=dir_path)
# app = Flask(__name__, template_folder='static', static_folder="./static")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

# db = SQLAlchemy(app)
db.init_app(app)
# Conexão com o banco de dados
conn = sqlite3.connect('crm.db.bckup')
cursor = conn.cursor()


@app.before_first_request
def create_tables():
    db.create_all()


views = Blueprint('views', __name__, template_folder='tamplates')


@views.route('/')
# Home page
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/static/css/style.css')
def serve_css():
    return app.send_static_file('/css/style.css')


# Client pages


@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        # get form data
        client_data = {
            'name': request.form['nome'],
            'email': request.form['email'],
            'phone': request.form['telefone'],
            'address': request.form['address'],
            'birthdate': request.form['birthdate'],
            'marital_status': request.form['marital_status'],
            'profession': request.form['profession'],
            'income': request.form['income']
        }

        # validate form data
        errors = validate_client_data(client_data)

        if errors:
            flash(errors)
            return render_template('add_client.html', client=client_data)

        # add client to database
        new_client = Client(name=client_data['name'],
                            email=client_data['email'],
                            phone=client_data['phone'],
                            address=client_data['address'],
                            birthdate=datetime.strptime(client_data['birthdate'], '%Y-%m-%d').date(),
                            # birthdate=datetime.datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date(),
                            # birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date(),
                            # birthdate = datetime.strptime(form.birthdate.data, '%Y-%m-%d').date(),
                            marital_status=client_data['marital_status'],
                            profession=client_data['profession'],
                            income=client_data['income'])

        db.session.add(new_client)
        db.session.commit()

        flash('Client added successfully!')
        return redirect(url_for('view_clients'))

    return render_template('add_client.html')


@app.route('/edit_client', methods=['GET', 'POST'])
def edit_client():
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
        client = Client.query.get(client_id)

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


@app.route('/update-client/<int:client_id>', methods=['GET', 'POST'])
def update_client(client_id):
    client = Client.query.get(client_id)
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


@app.route('/view_clients')
# def view_client(client_id):
def view_clients():
    clients = Client.query.all()
    return render_template('view_clients.html', clients=clients)


if __name__ == '__main__':
    app.run(debug=True)


# Rota para página de cadastro de propriedades
@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        address = request.form['address']
        property_type = request.form['property_type']
        price = request.form['price']
        description = request.form['description']
        photo = request.form['photo']
        new_property = Property(address=address, property_type=property_type, price=price, description=description,
                                photo=photo)
        db.session.add(new_property)
        db.session.commit()
        flash('Propriedade adicionada com sucesso!', 'success')
        return redirect(url_for('view_properties'))
    return render_template('add_property.html')


# Rota para página de edição de propriedades
@app.route('/edit_property/<int:id>', methods=['GET', 'POST'])
def edit_property(id):
    property = Property.query.get_or_404(id)
    if request.method == 'POST':
        property.address = request.form['address']
        property.property_type = request.form['property_type']
        property.price = request.form['price']
        property.description = request.form['description']
        property.photo = request.form['photo']
        db.session.commit()
        flash('Propriedade atualizada com sucesso!', 'success')
        return redirect(url_for('view_properties'))
    return render_template('edit_property.html', property=property)


# Rota para página de visualização de propriedades
@app.route('/view_properties')
def view_properties():
    properties = Property.query.all()
    return render_template('view_properties.html', properties=properties)


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
    properties = Property.query.all()
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
    properties = Property.query.all()
    clients = Client.query.all()
    return render_template('edit_sale.html', sale=sale, properties=properties, clients=clients)


# Rota para página de visualização de vendas
@app.route('/view_sales')
def view_sales():
    sales = Sale.query.all()
    return render_template('view_sales.html', sales=sales)


@app.route('/add_lead', methods=['GET', 'POST'])
def add_lead():
    form = LeadForm()
    if form.validate_on_submit():
        lead = Lead(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            lead_date=form.lead_date.data,
            lead_source=form.lead_source.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(lead)
        db.session.commit()
        flash('Lead adicionado com sucesso!', 'success')
        return redirect(url_for('view_leads'))
    return render_template('add_lead.html', form=form)


@app.route('/edit_lead/<int:id>', methods=['GET', 'POST'])
def edit_lead(id):
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


@app.route('/view_leads')
def view_leads():
    leads = Lead.query.all()
    return render_template('view_leads.html', leads=leads)


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


@app.route('/add_interaction', methods=['GET', 'POST'])
def add_interaction():
    form = InteractionForm()
    if form.validate_on_submit():
        interaction = Interaction(
            date=form.date.data,
            client=form.client.data,
            property=form.property.data,
            notes=form.notes.data
        )
        db.session.add(interaction)
        db.session.commit()
        flash('Interação adicionada com sucesso.', 'success')
        return redirect(url_for('view_interactions'))
    return render_template('add_interaction.html', form=form)


@app.route('/edit_interaction/<int:id>', methods=['GET', 'POST'])
def edit_interaction(id):
    interaction = Interaction.query.get_or_404(id)
    form = InteractionForm(obj=interaction)
    if form.validate_on_submit():
        interaction.date = form.date.data
        interaction.client = form.client.data
        interaction.property = form.property.data
        interaction.notes = form.notes.data
        db.session.commit()
        flash('Interação atualizada com sucesso.', 'success')
        return redirect(url_for('view_interactions'))
    return render_template('edit_interaction.html', form=form)


@app.route('/delete_interaction/<int:id>', methods=['POST'])
def delete_interaction(id):
    interaction = Interaction.query.get_or_404(id)
    db.session.delete(interaction)
    db.session.commit()
    flash('Interação deletada com sucesso.', 'success')
    return redirect(url_for('view_interactions'))


@app.route('/view_reports')
def view_reports():
    return render_template('view_reports.html')
