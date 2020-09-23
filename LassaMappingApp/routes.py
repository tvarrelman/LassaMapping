
from flask import Flask, url_for, render_template, request, redirect
import os
from db_query import human_mapper, rodent_mapper
from LassaMappingApp.forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from LassaMappingApp.models import db, User
from flask import current_app as app
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
@app.route('/login', methods=['GET', 'POST'])
def login(): 
    form = LoginForm(csrf_enabled=False) 
    if request.method == 'POST': 
        test_user = request.form['username'] 
        passW = request.form['password'] 
        if form.validate_on_submit(): 
            user = User.query.filter_by(username=test_user).first()
            if user:
                if check_password_hash(user.password, passW):
                    login_user(user, remember=False)
                    return redirect(url_for('admin'))
            return '<h1> Invalid username or password </h1>'
    return render_template('login.html', form=form)
@app.route('/Admin', methods=['GET', 'POST'])
@login_required
def admin(): 
    return '<h1> Success! </h1>'
