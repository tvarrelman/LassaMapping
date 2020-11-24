
from flask import Flask, url_for, render_template, request, redirect, flash, jsonify
import os
from os import environ
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
@app.route('/LassaSequenceRodents')
def sequence_rodent_mapping():
    visual = request.args.get('visual', 'default_if_none')
    data_summary = db_summary()
    jsonSeq = sequence_rodent_year_data()
    host = 'sequence rodent'
    StartYearList, EndYearList = initial_year_lists(host)
    jsonYears = dict(zip(('host', 'start_year', 'end_year'), (host, StartYearList, EndYearList)))
    if visual == 'chart':
        return jsonify(jsonSeq)
    if visual == 'map':
        return jsonify(jsonYears)
@app.route('/LassaSequenceHumans')
def sequence_human_mapping():
    visual = request.args.get('visual', 'default_if_none')
    data_summary = db_summary()
    jsonSeq = sequence_human_year_data()
    host = 'sequence human'
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
        if 'ViralInfection' in request.files:
            infFile = request.files['ViralInfection']
            if infFile and allowed_file(infFile.filename):
                str_data = str(infFile.read(), 'utf-8')
                data = StringIO(str_data)
                data_df = pd.read_csv(data)
                entry_columns = ["Town_Region", "Village", "Latitude", "Longitude", "Country", 
                                 "NumPosVirus", "NumTestVirus", "PropVirus", "Virus_Diagnostic_Method", "NumPosAb", 
                                 "NumTestAb", "PropAb", "Ab_Diagnostic_Method", "Antibody_Target", "Genus", "Species", 
                                 "lat_lon_source", "Source", "Citation", "DOI", "Bibtex", "Survey_Notes", "Housing_Notes",
                                 "start_year", "end_year"]
                if len(data_df.columns)==25 and sum(data_df.columns == entry_columns)==25:
                    if len(data_df) > 0:
                        dtype_errors = check_data_types(data_df)
                        if len(dtype_errors) > 0 :
                            return render_template('admin.html', error=dtype_errors)
                        else:
                            data_df2, latlonError = lat_lon_check(data_df)
                            if latlonError==None:
                                source_df = source_id_mapper(data_df2)
                                country_df, country_error = country_id_mapper(data_df2)
                                if country_error:
                                    return render_template('admin.html', error=country_error)
                                else:
                                    data_df2 = data_df2.drop(['Citation', 'Source', 'DOI', 'Bibtex', 'Country'], axis=1)
                                    final_df = pd.concat([data_df2, country_df, source_df], axis=1)
                                    db_uri = environ.get('SQLALCHEMY_DATABASE_URI')
                                    engine = create_engine(db_uri)
                                    final_df.to_sql('lassa_data_test', con=engine, if_exists='append', index=False)
                                    message = "Successfully imported data"
                                    return render_template('admin.html', message=message)
                            else:
                                return render_template('admin.html', error=latlonError)
                    else:
                        nodataerror = "No data in file"
                        return render_template('admin.html', error=nodataerror)
                else:
                    error = "Inconsistent column names"
                    return render_template('admin.html', error=error)
            else:
                error = "No file selected/incorrect file type"
                return render_template('admin.html', error=error)
        if 'ViralSequence' in request.files:
            seqFile = request.files['ViralSequence']
            if seqFile and allowed_file(seqFile.filename):
                seq_str_data = str(seqFile.read(), 'utf-8')
                seq_data = StringIO(seq_str_data)
                seq_data_df = pd.read_csv(seq_data)
                seq_columns = ["gbAccession", "gbDefinition", "gbLength", "gbHost",
                               "LocVillage", "LocState", "Country", "gbCollectDate", "CollectionMonth",
                               "gbCollectYear", "Latitude", "Longitude", "Hospital", "gbPubMedID", "gbJournal",
                               "PubYear", "GenomeCompleteness", "Tissue", "Strain", "gbProduct",
                               "gbGene", "S", "L", "GPC", "NP", "Pol", "Z", "Sequence", "Reference",
                               "Notes"]
                if len(seq_data_df.columns)==len(seq_columns):
                    if sum(seq_data_df.columns == seq_columns)==len(seq_columns):
                        seq_dtype_errors = seq_check_data_types(seq_data_df)
                        #print('Step 1')
                        if len(seq_dtype_errors) > 0 :
                            return render_template('admin.html', seq_error=seq_dtype_errors)
                        else:
                            seq_data_df2, seq_latlonError = lat_lon_check(seq_data_df)
                            #print('Step 2')
                            if seq_latlonError==None:
                                seq_ref_df = seq_ref_id_mapper(seq_data_df2)
                                seq_country_df, seq_country_error = country_id_mapper(seq_data_df2)
                                #print('Step 3')
                                if seq_country_error:
                                    return render_template('admin.html', seq_error=seq_country_error)
                                else:
                                    seq_data_df2 = seq_data_df2.drop(['Country', 'Reference'], axis=1)
                                    seq_final_df = pd.concat([seq_data_df2, seq_country_df, seq_ref_df], axis=1)
                                    for i in range(0, len(seq_final_df)):
                                        entry = seq_final_df['gbCollectDate'][i]
                                        if isinstance(entry, datetime.datetime):
                                            continue
                                        else:
                                            seq_final_df.loc[i, 'gbCollectDate'] = np.nan
                                    #print('Step 4')
                                    db_uri = environ.get('SQLALCHEMY_DATABASE_URI')
                                    engine = create_engine(db_uri)
                                    seq_final_df.to_sql('seq_data_test', con=engine, if_exists='append', index=False)
                                    seq_message = "Successfully imported data"
                                    return render_template('admin.html', seq_message=seq_message)
                            else:
                                return render_template('admin.html', seq_error=seq_latlonError)
                    else:
                        seq_col_error = "Inconsistent column names"
                        return render_template('admin.html', seq_error=seq_col_error)
                else:
                    seq_col_error = "Incorrect number of columns"
                    return render_template('admin.html', seq_error=seq_col_error)
            else:
                seq_file_error = "No file selected/incorrect file type"
                return render_template('admin.html', seq_error=seq_file_error)
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

