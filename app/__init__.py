from flask import Flask
from .config import Config
from .models import db
from .routes.users import users_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'ewuqpdjsakcnoiwrqojaj'

    db.init_app(app)

    with app.app_context():
        db.create_all()

        app.register_blueprint(users_bp)

        return app