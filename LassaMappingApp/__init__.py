"""
__init__ file initializes the Application Factory.
Here, we initialize the app object, initialize plugins
that will be accessible to our app (ex. database),
import routes, and register blueprints.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
# Creates an app object
def create_app():
    # creates app object that will be used throughout this proj.
    app = Flask(__name__)
    # configures the app using a development configuration from our config file
    cfg = import_string('config.DevConfig')()
    app.config.from_object(cfg)
    # initialize the database w/ the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    csrf.init_app(app)
    with app.app_context():
        from . import routes   
        return app
