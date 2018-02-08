from flask import Flask
from ipview.config import configs
from flask_login import LoginManager
import datetime
from ipview.models import db


def register_blueprint(app):
    from .handlers import front
    
    app.register_blueprint(front)



def register_extensions(app):
    db.init_app(app)



def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))

    register_blueprint(app)
    register_extensions(app)


    return app
