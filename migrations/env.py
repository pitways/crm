import sys
sys.path.append('/')
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from flask_migrate import Migrate
from models import db
from flask import (
    Flask
)

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = '/home/pit/PycharmProjects'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # ... rest of the code ...
    return app

# Create the Flask app instance
app = create_app()

# Initialize the database connection
db.init_app(app)

# Set up Flask-Migrate
migrate = Migrate(app, db)

# Set up Alembic configuration
config = context.config
config.set_main_option('sqlalchemy.url', str(app.config['SQLALCHEMY_DATABASE_URI']))
config.set_main_option('script_location', 'migrations')
fileConfig(config.config_file_name)

# Bind the database engine to the metadata of the Flask app instance
with app.app_context():
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )
    context.configure(
        connection=engine.connect(),
        target_metadata=db.metadata,
        include_schemas=True
    )
    migrate = Migrate(app, db)

# Run the migration
    with context.begin_transaction():
        context.run_migrations()
