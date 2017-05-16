from flask import Flask
from flask_bootstrap import Bootstrap
from config import config,BaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from celery import Celery

bootstrap = Bootstrap()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

celery = Celery(__name__,broker=BaseConfig.CELERY_BROKER_URL)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    with app.test_request_context():
        db.create_all(bind=['ora11g'])

    celery.conf.update(app.config)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
