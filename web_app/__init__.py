import os

from flask import Flask
from flask_session.__init__ import Session

from config import config
from .models import DefaultBomManager


def create_app(env=None):
    app = Flask(__name__, instance_relative_config=True)

    if not env:
        app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
    else:
        app.config.from_object(config[env])
    app.config.from_pyfile('config.py', silent=True)

    Session(app)

    from . import views
    app.register_blueprint(views.bp)

    return app
