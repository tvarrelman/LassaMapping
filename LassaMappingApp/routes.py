
from flask import Flask, url_for, render_template, request, redirect, flash, jsonify
import os
from db_query import *
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
from sqlalchemy import create_engine
# This is a callback function that relaods the user object from the User ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def main_page():
    data_summary = db_summary()
    return render_template('index.html', data_summary = data_summary)
@app.route('/LassaHumans')
def human_mapping():
    visual = request.args.get('visual', 'default_if_none')
    jsonPropAb = human_year_data()
    host = 'human'
    StartYearList, EndYearList = initial_year_lists(host)
    jsonYears = dict(zip(('host', 'start_year', 'end_year'), (host, StartYearList, EndYearList)))
    if visual == 'chart':
        return jsonify(jsonPropAb)
    if visual == 'map':
        return jsonify(jsonYears)
@app.route('/LassaRodents')
def rodent_mapping():
    visual = request.args.get('visual', 'default_if_none')
    jsonPropAb, jsonPropAg = rodent_year_data()
    host = 'rodent'
    StartYearList, EndYearList = initial_year_lists(host)
    jsonYears = dict(zip(('host', 'start_year', 'end_year'), (host, StartYearList, EndYearList)))
    if visual == 'chart':
        return jsonify([jsonPropAb, jsonPropAg])
    if visual == 'map':
        return jsonify(jsonYears)
@app.route('/LassaSequence')
def sequence_mapping():
    visual = request.args.get('visual', 'default_if_none')
    data_summary = db_summary()
    jsonSeq = sequence_year_data()
    host = 'sequence'
    StartYearList, EndYearList = initial_year_lists(host)
    jsonYears = dict(zip(('host', 'start_year', 'end_year'), (host, StartYearList, EndYearList)))
    if visual == 'chart':
        return jsonify(jsonSeq)
    if visual == 'map':
        return jsonify(jsonYears)
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
            data_df = pd.read_csv(data)
            entry_columns = ['Town_Region', 'Village', 'Month', 'Day', 'Year', 'Latitude',
               'Longitude', 'Country', 'Confidence', 'Status', 'NumPosAg', 'NumTestAg',
               'PropAg', 'NumPosAb', 'NumTestAb', 'PropAb', 'Genus', 'Species',
               'DiagnosticMethod', 'Target', 'lat-lon-source', 'Source', 'Citation',
               'DOI', 'Human_Random_Survey', 'Notes']
            if len(data_df.columns)==26 and sum(data_df.columns == entry_columns)==26:
                dtype_errors = check_data_types(data_df)
                if len(dtype_errors) > 0 :
                    return render_template('admin.html', error=dtype_errors)
                else:
                    data_df2, latlonError = lat_lon_check(data_df)
                    if latlonError==None:
                        source_df = source_id_mapper(data_df2)
                        country_df = country_id_mapper(data_df2)
                        data_df2 = data_df2.drop(['Citation', 'Source', 'DOI', 'Country','Year'], axis=1)
                        final_df = pd.concat([data_df2, country_df, source_df], axis=1)
                        engine = create_engine('mysql+mysqlconnector://tanner:atgh-klpM-cred5@localhost/lassa_tanner')
                        final_df.to_sql('test_lassa_data', con=engine, if_exists='append', index=False)
                        message = "Successfully imported data"
                        return render_template('admin.html', message=message)
                    else:
                        return render_template('admin.html', error=latlonError)
            else:
                error = "Inconsistent column names"
                return render_template('admin.html', error=error)
        else:
            error = "No file selected/incorrect file type"
            return render_template('admin.html', error=error)
    return render_template('admin.html')
@app.route('/_get_end_year', methods=['GET'])
def get_end_year():
    start_year = request.args.get('start_year', 'default_if_none')
    host_mapped = request.args.get('host', 'default_if_none')
    end_year_json = end_year_list(start_year, host_mapped)
    return jsonify(end_year_json)
@app.route('/_filter_points', methods=['GET']) 
def filter_points():
    start_year = request.args.get('start_year', 'default_if_none')
    end_year = request.args.get('end_year', 'default_if_none')
    host_species = request.args.get('host', 'default_if_none')
    mapping_json = mapper(host_species, start_year, end_year) 
    return jsonify(mapping_json)
@app.route('/_get_init_year_lists', methods=['GET'])  
def get_init_year_lists():
    host = request.args.get('host', 'default_if_none')
    StartYearList, EndYearList = initial_year_lists(host)
    return jsonify(StartYearList, EndYearList)
@app.route('/_download_data', methods=['GET'])
def download_data():
    host = request.args.get('host', 'default_if_none')
    start_year = request.args.get('start_year', 'default_if_none')
    end_year = request.args.get('end_year', 'default_if_none')
    country_list = request.args.getlist('country')
    jsonDump = filtered_download(host, start_year, end_year, country_list)
    return jsonify(jsonDump)
@app.route('/_get_countries', methods=['GET'])
def get_country_list():
    host = request.args.get('host', 'default_if_none') 
    countryJson = country_list(host)
    return jsonify(countryJson)
@app.route('/_test', methods=['GET'])
def test():
    #print(request)
    country_list = request.args.getlist('country')
    host = request.args.get('host')
    #print(host, country_list)
    StartYearList, EndYearList = filtered_year_list(host, country_list)
    return jsonify(StartYearList, EndYearList)
@app.route('/_get_filtered_end_year', methods=['GET'])
def filtered_end_year():
    host = request.args.get('host', 'default_if_none')
    start_year = request.args.get('start_year', 'default_if_none')
    country_list = request.args.getlist('country')
    json_end_year = filtered_end_year_list(host, start_year, country_list)
    return jsonify(json_end_year)

