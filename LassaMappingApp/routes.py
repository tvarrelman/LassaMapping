
from flask import Flask, url_for, render_template, request, redirect, flash, jsonify
import os
from db_query import mapper, db_summary, human_year_data, rodent_year_data, initial_year_lists, end_year_list
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
    return redirect(url_for('human_mapping'))
@app.route('/LassaHumans')
def human_mapping():
    data_summary = db_summary()
    year_list, totalAbPos = human_year_data()
    host = 'human'
    StartYearList, EndYearList = initial_year_lists(host)
    bar_title = "(Human)"
    return render_template('human_mapper.html', data_summary=data_summary, year_list=year_list, totalAbPos=totalAbPos, bar_title=bar_title, StartYearList=StartYearList, EndYearList=EndYearList, host=host)    
@app.route('/LassaRodents')
def rodent_mapping():
    data_summary = db_summary()
    rodent_year_list, rodentTotalAbPos = rodent_year_data()
    host = 'rodent'
    StartYearList, EndYearList = initial_year_lists(host)
    bar_title = "(Rodent)"
    return render_template('rodent_mapper.html', data_summary=data_summary, year_list=rodent_year_list, totalAbPos=rodentTotalAbPos, bar_title=bar_title, StartYearList=StartYearList, EndYearList=EndYearList, host=host)
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
@app.route('/_get_end_year', methods=['GET','POST'])
def get_end_year():
    start_year = request.args.get('start_year', 'default_if_none')
    host_mapped = request.args.get('host', 'default_if_none')
    end_year_json = end_year_list(start_year, host_mapped)
    return jsonify(end_year_json)
@app.route('/_filter_points', methods=['GET', 'POST']) 
def filter_points():
    start_year = request.args.get('start_year', 'default_if_none')
    end_year = request.args.get('end_year', 'default_if_none')
    host_species = request.args.get('host', 'default_if_none')
    mapping_json = mapper(host_species, start_year, end_year) 
    return jsonify(mapping_json)  
