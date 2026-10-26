import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))


def create_app(config_name):
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
