from flask import Flask
from ipview.config import configs
from flask_login import LoginManager
import datetime
from ipview.models import db, User, Host


def register_blueprint(app):
    from .handlers import front, request, admin, setting
    
    app.register_blueprint(front)
    app.register_blueprint(request)
    app.register_blueprint(setting)
    app.register_blueprint(admin)



def register_extensions(app):
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(id):
        return User.query.get(id)

    login_manager.login_view = 'front.login'



def register_filters(app):

    @app.template_filter()
    def request_status(value):
        if value == Host.STATUS_REQUESTING:
            return "requesting"
        if value == Host.STATUS_REJECTED:
            return "rejected"
        if value == Host.STATUS_ASSIGNED:
            return "assigned"
        if value == Host.STATUS_RELEASED:
            return "released"





def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))

    register_blueprint(app)
    register_extensions(app)
    register_filters(app)


    return app
