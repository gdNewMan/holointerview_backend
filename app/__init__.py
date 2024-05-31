from flask import Flask
from .extensions import db, migrate, init_extensions
from .auth import auth_bp
from .main import main_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)

    init_extensions(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
