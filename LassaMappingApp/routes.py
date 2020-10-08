
from flask import Flask, url_for, render_template, request, redirect, flash
import os
from db_query import human_mapper, rodent_mapper, db_summary, human_year_data, rodent_year_data, total_year_data
from LassaMappingApp.forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from LassaMappingApp.models import db, User
from flask import current_app as app
from . import login_manager
from werkzeug.utils import secure_filename
import pandas as pd
from io import StringIO

# This is a callback function that relaods the user object from the User ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def main_page():
    # The title of the page (will be inserted in the .html)
    message = "Lassa Virus Data Dashboard"
    # Function returns summary of the data in the db
    data_summary = db_summary()
    bar_title = "(Human+Rodents)"
    total_year_list, AllspeciesTotalPosAb = total_year_data()
    # Returns the rendered .html for the index webpage
    return render_template('index.html', message=message, data_summary=data_summary, year_list=total_year_list, totalAbPos=AllspeciesTotalPosAb, bar_title=bar_title)
@app.route('/LassaHumans')
def human_mapping():
    data_summary = db_summary()
    human_data = human_mapper()
    year_list, totalAbPos = human_year_data()
    bar_title = "(Human)"
    return render_template('human_mapper.html', human_data=human_data, data_summary=data_summary, year_list=year_list, totalAbPos=totalAbPos, bar_title=bar_title)    
@app.route('/LassaRodents')
def rodent_mapping():
    data_summary = db_summary()
    rodent_data = rodent_mapper()
    rodent_year_list, rodentTotalAbPos = rodent_year_data()
    bar_title = "(Rodent)"
    return render_template('rodent_mapper.html', rodent_data=rodent_data, data_summary=data_summary, year_list=rodent_year_list, totalAbPos=rodentTotalAbPos, bar_title=bar_title)
@app.route('/Download')
def download_page():
    message = "Download Data!"
    # Returns the rendered .html for the data download page
    return render_template('download.html', message=message)
@app.route('/login', methods=['GET', 'POST'])
def login(): 
    form = LoginForm() 
    if request.method == 'POST':
        # Get the username and pass from the form 
        test_user = request.form['username'] 
        passW = request.form['password'] 
        # If this is an active request continue on
        if form.validate_on_submit(): 
            # Retrieve the user from the database
            user = User.query.filter_by(username=test_user).first()
            if user:
                # Check the user password
                if check_password_hash(user.password, passW):
                    login_user(user, remember=False)
                    return redirect(url_for('admin'))
            error = "Invalid username or password"
            return render_template('login.html', form=form, error=error)
    return render_template('login.html', form=form)
ALLOWED_EXTENSIONS = {'csv'}
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/Admin', methods=['GET', 'POST'])
@login_required
def admin(): 
    if request.method == 'POST':
        myfile = request.files['fileupload']
        if myfile and allowed_file(myfile.filename):
            str_data = str(myfile.read(), 'utf-8')
            data = StringIO(str_data)
            data_df = pd.read_csv(data, sep='\t')
            message = 'Successfully imported data'
            return render_template('admin.html', message=message)
        else:
            error = "No file selected/incorrect file type"
            return render_template('admin.html', error=error)
    return render_template('admin.html')
