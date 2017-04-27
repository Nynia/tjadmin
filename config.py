import os
basedir = os.path.abspath(os.path.dirname(__file__))

STATIC_URL_PREFIX = 'http://221.228.17.87/res/'
ORDER_REQUEST_URL = 'http://61.160.185.51:9250/ismp/serviceOrder'
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'skks'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:admin@127.0.0.1/ismp'
    SQLALCHEMY_BINDS = {
        'jstelecom': 'mysql://root:admin@127.0.0.1/jstelecom',
        'ora11g': 'mysql://root:admin@127.0.0.1/ora11g'
    }

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:admin@127.0.0.1/ismp'
    SQLALCHEMY_BINDS = {
        'jstelecom': 'mysql://ismpadmin:admin123@202.102.41.186/jstelecom',
        'ora11g': 'mysql://root:admin@192.168.127.53/ora11g'
    }

config = {
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default':ProductionConfig,
}
