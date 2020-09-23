"""
__init__ file initializes the Application Factory.
Here, we initialize the app object, initialize plugins
that will be accessible to our app (ex. database),
import routes, and register blueprints.
"""

import mysql.connector
from flask import Flask, url_for, render_template, request
import os
from werkzeug.utils import import_string
from db_query import human_mapper, rodent_mapper
from LassaMappingApp.forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# Creates an app object

def create_app():
    # creates app object that will be used throughout this proj.
    app = Flask(__name__)
    # configures the app using a development configuration from our config file
    cfg = import_string('config.DevConfig')()
    app.config.from_object(cfg)
    #  route assigns urls to functions

    @app.route('/')
    def main_page():
        # The title of the page (will be inserted in the .html)
        message = "Lassa Virus Data Dashboard"
        #human_data = human_mapper()
        #rodent_data = rodent_mapper()
        # Returns the rendered .html for the index webpage
        return render_template('index.html', message=message)
    @app.route('/LassaHumans')
    def mapping():
        human_data = human_mapper()
        return render_template('human_mapper.html', human_data=human_data)
    @app.route('/LassaRodents')
    def rodent_mapping():
        rodent_data = rodent_mapper()
        return render_template('rodent_mapper.html', rodent_data=rodent_data)
    @app.route('/Download')
    def download_page():
        message = "Download Data!"
        # Returns the rendered .html for the data download page
        return render_template('download.html', message=message)
    # The app is returned to the wsgi.py script located in the root directory
    @app.route('/login', methods=['Get', 'POST'])
    def login():
        form = LoginForm(csrf_enabled=False)
        if request.method == 'POST':
            user = request.form['username']
            passW = request.form['password']
            if form.validate_on_submit():
            	return '<h1>' + user + ' ' + passW + '</h1>'
        return render_template('login.html', form=form)
    return app
