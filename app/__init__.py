from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate, init_extensions
from app.auth.routes import auth_bp
from app.main.routes import main_bp


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
