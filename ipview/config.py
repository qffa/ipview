import os

class BaseConfig(object):
    SECRET_KEY = os.urandom(16)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@localhost:3306/ipview?charset=utf8'
    TEMPLATES_AUTO_RELOAD =True


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@localhost:3306/ipview?charset=utf8'


class TestingConfig(BaseConfig):
    pass


configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
        }

