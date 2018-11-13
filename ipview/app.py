from flask import Flask
from ipview.config import configs
from flask_login import LoginManager
import datetime
from ipview.models import db, User, Host, Network, Subnet, Site



def register_blueprint(app):
    from .handlers import front, request, admin, setting, api
    
    app.register_blueprint(front)
    app.register_blueprint(request)
    app.register_blueprint(setting)
    app.register_blueprint(admin)
    app.register_blueprint(api)



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


    @app.template_filter()
    def ip_use_status(value):
        if value is True:
            return "Yes"
        if value is False:
            return "No"



def register_context_processor(app):

    @app.context_processor
    def inject_waiting_request_count():
        return dict(waiting_request_count = Host.query.filter_by(status=Host.STATUS_REQUESTING).count())

    @app.context_processor
    def inject_network_count():
        return dict(network_count = Network.query.count())

    @app.context_processor
    def inject_subnet_count():
        return dict(subnet_count = Subnet.query.count())

    @app.context_processor
    def inject_site_count():
        return dict(site_count = Site.query.count())





def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))

    register_blueprint(app)
    register_extensions(app)
    register_filters(app)
    register_context_processor(app)


    return app
