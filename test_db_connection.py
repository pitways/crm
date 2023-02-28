from flask import Flask


def create_app():
    app = Flask(__name__)
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
    register_extensions(app)
    return app

    db.init_app(app)

    query = "SELECT * FROM users LIMIT 50;"
    result = db.engine.execute(query)
    print(list(result))
