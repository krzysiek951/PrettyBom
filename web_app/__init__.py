from config import config
import os
from flask import Flask
from flask_session.__init__ import Session
from .models import DefaultBomManager
from flask_mail import Mail

mail = Mail()


def create_app(env=None):
    app = Flask(__name__, instance_relative_config=True)

    if not env:
        app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
    else:
        app.config.from_object(config[env])
    app.config.from_pyfile('config.py', silent=True)

    mail.init_app(app)
    Session(app)

    from . import views
    app.register_blueprint(views.bp)

    return app
