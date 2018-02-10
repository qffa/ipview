from flask import Flask
from ipview.config import configs
from flask_login import LoginManager
import datetime
from ipview.models import db


def register_blueprint(app):
    from .handlers import front, request, admin, setting
    
    app.register_blueprint(front)
    app.register_blueprint(request)
    app.register_blueprint(setting)
    app.register_blueprint(admin)





def register_extensions(app):
    db.init_app(app)



def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))

    register_blueprint(app)
    register_extensions(app)


    return app
