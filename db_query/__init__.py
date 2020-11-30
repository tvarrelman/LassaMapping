"""script for returning db queries """
import mysql.connector
import os
import numpy as np
from os import environ, path
from dotenv import load_dotenv
import json
from decimal import Decimal
import pandas as pd
import geopandas as gpd 
from shapely.geometry import shape, Point
import datetime
from itertools import compress
import itertools 

# finds the absolute path of this file
basedir = path.abspath(path.dirname(__file__))
# reads the key value from .env, and adds it to the environment variable
load_dotenv(path.join(basedir, '.env'))
db_user = os.environ.get('user')
db_pw = os.environ.get('password')
db_host = os.environ.get('host')
db_name = os.environ.get('database')
def initial_year_lists(host):
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    if host=='human':
        cmd = "SELECT DISTINCT start_year, end_year FROM lassa_data2 WHERE start_year IS NOT NULL AND Genus='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL ORDER BY start_year;"
        cursor.execute(cmd)
        year_lists = cursor.fetchall()
        init_start_year_list = []
        init_end_year_list = []
        for i in range(0, len(year_lists)):
            init_start_year_list.append(year_lists[i][0])
            init_end_year_list.append(year_lists[i][1])
        cursor.close()
        return init_start_year_list, init_end_year_list
    if host=='rodent':
        cmd = "SELECT DISTINCT start_year, end_year FROM lassa_data2 WHERE (start_year IS NOT NULL AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL) OR (start_year IS NOT NULL AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropVirus IS NOT NULL) ORDER BY start_year;"
        cursor.execute(cmd)
        year_lists = cursor.fetchall()
        init_start_year_list = []
        init_end_year_list = []
        for i in range(0, len(year_lists)):
            init_start_year_list.append(year_lists[i][0])
            init_end_year_list.append(year_lists[i][1])
        cursor.close()
        return init_start_year_list, init_end_year_list
    if host=='sequence rodent':
        cmd = "SELECT DISTINCT gbCollectYear FROM seq_data WHERE (gbCollectYear IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND gbHost!='Human' AND gbHost!='Homo sapiens') ORDER BY gbCollectYear;"
        cursor.execute(cmd)
        year_lists = cursor.fetchall()
        init_start_year_list = []
        init_end_year_list = []
        for i in range(0, len(year_lists)):
            init_start_year_list.append(year_lists[i][0])
            init_end_year_list.append(year_lists[i][0])
        cursor.close()
        return init_start_year_list, init_end_year_list
    if host=='sequence human':
        cmd = "SELECT DISTINCT gbCollectYear FROM seq_data WHERE (gbCollectYear IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND gbHost='Human') OR (gbCollectYear IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND gbHost='Homo sapiens') ORDER BY gbCollectYear;"
        cursor.execute(cmd)
        year_lists = cursor.fetchall()
        init_start_year_list = []
        init_end_year_list = []
        for i in range(0, len(year_lists)):
            init_start_year_list.append(year_lists[i][0])
            init_end_year_list.append(year_lists[i][0])
        cursor.close()
        return init_start_year_list, init_end_year_list
def end_year_list(start_year, host):
    if host=='human':
        cmd = """SELECT DISTINCT end_year FROM lassa_data2 WHERE (end_year>={0} AND Genus='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL) ORDER BY end_year;""".format(start_year)
    if host=='rodent':
        cmd = """SELECT DISTINCT end_year FROM lassa_data2 WHERE (end_year>={0} AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL) OR (end_year>={0} AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropVirus IS NOT NULL) ORDER BY end_year;""".format(start_year)
    if host=='sequence rodent':
        cmd = """SELECT DISTINCT gbCollectYear FROM seq_data WHERE (gbCollectYear>={0} AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND gbHost!='Human' AND gbHost!='Homo sapiens') ORDER BY gbCollectYear;""".format(start_year)
    if host=='sequence human':
        cmd = """SELECT DISTINCT gbCollectYear FROM seq_data WHERE (gbCollectYear>={0} AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND gbHost='Human') OR (gbCollectYear>={0} AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND gbHost='Homo sapiens') ORDER BY gbCollectYear;""".format(start_year)
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cursor.execute(cmd)
    year_list = cursor.fetchall()
    json_end_year = []
    for year in year_list:
        json_end_year.append({'end_year':year[0]})
    return json_end_year
def filtered_year_list(host, country_list):
    if host == 'human':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data2.start_year, lassa_data2.end_year FROM lassa_data2, countries WHERE"
        sel_end = "ORDER BY start_year;"
        for country in country_list:
            ext = " (start_year IS NOT NULL AND Genus='Homo' AND lassa_data2.country_id=countries.country_id AND countries.country_name='{0}') ".format(country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end 
    if host == 'rodent':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data2.start_year, lassa_data2.end_year FROM lassa_data2, countries WHERE"
        sel_end = "ORDER BY start_year;"
        for country in country_list:
            ext = " (start_year IS NOT NULL AND Genus!='Homo' AND lassa_data2.country_id=countries.country_id AND countries.country_name='{0}') ".format(country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'both':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data2.start_year, lassa_data2.end_year FROM lassa_data2, countries WHERE"
        sel_end = "ORDER BY start_year;"
        for country in country_list:
            ext = " (start_year IS NOT NULL AND lassa_data2.country_id=countries.country_id AND countries.country_name='{0}') ".format(country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host=='sequence rodent':
        ext_list = []
        sel_start = "SELECT DISTINCT seq_data.gbCollectYear FROM seq_data, countries WHERE"
        sel_end = "ORDER BY gbCollectYear;"
        for country in country_list:
            ext = " (gbCollectYear IS NOT NULL AND seq_data.country_id=countries.country_id AND countries.country_name='{0}' AND gbHost!='Human' AND gbHost!='Homo sapiens') ".format(country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host=='sequence human':
        ext_list = []
        sel_start = "SELECT DISTINCT seq_data.gbCollectYear FROM seq_data, countries WHERE"
        sel_end = "ORDER BY gbCollectYear;"
        for country in country_list:
            ext = " (gbCollectYear IS NOT NULL AND seq_data.country_id=countries.country_id AND countries.country_name='{0}' AND gbHost='Human') OR (gbCollectYear IS NOT NULL AND seq_data.country_id=countries.country_id AND countries.country_name='{0}' AND gbHost='Homo sapiens') ".format(country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host=='sequence both':
        ext_list = []
        sel_start = "SELECT DISTINCT seq_data.gbCollectYear FROM seq_data, countries WHERE"
        sel_end = "ORDER BY gbCollectYear;"
        for country in country_list:
            ext = " (gbCollectYear IS NOT NULL AND seq_data.country_id=countries.country_id AND countries.country_name='{0}') ".format(country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cursor.execute(final_cmd)
    year_list = cursor.fetchall()
    init_start_year_list = []
    init_end_year_list = []
    if host=='rodent' or host=='human' or host=='both':
        for i in range(0, len(year_list)):
            init_start_year_list.append(year_list[i][0])
            init_end_year_list.append(year_list[i][1])
    else:
        for i in range(0, len(year_list)):
            init_start_year_list.append(year_list[i][0])
            init_end_year_list.append(year_list[i][0])
    cursor.close()
    return init_start_year_list, init_end_year_list
def filtered_end_year_list(host, start_year, country_list):
    if host == 'human':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data2.end_year FROM lassa_data2, countries WHERE"
        sel_end = "ORDER BY end_year;"
        for country in country_list:
            ext = " (end_year>={0} AND end_year IS NOT NULL AND Genus='Homo' AND lassa_data2.country_id=countries.country_id AND countries.country_name='{1}') ".format(start_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'rodent':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data2.end_year FROM lassa_data2, countries WHERE"
        sel_end = "ORDER BY end_year;"
        for country in country_list:
            ext = " (end_year>={0} AND end_year IS NOT NULL AND Genus!='Homo' AND lassa_data2.country_id=countries.country_id AND countries.country_name='{1}') ".format(start_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'both':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data2.end_year FROM lassa_data2, countries WHERE"
        sel_end = "ORDER BY end_year;"
        for country in country_list:
            ext = " (end_year>={0} AND end_year IS NOT NULL AND lassa_data2.country_id=countries.country_id AND countries.country_name='{1}') ".format(start_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'sequence rodent':
        ext_list = []
        sel_start = "SELECT DISTINCT seq_data.gbCollectYear FROM seq_data, countries WHERE"
        sel_end = "ORDER BY gbCollectYear;"
        for country in country_list:
            ext = " (gbCollectYear>={0} AND gbCollectYear IS NOT NULL AND seq_data.country_id=countries.country_id AND countries.country_name='{1}' AND gbHost!='Human' AND gbHost!='Homo sapiens') ".format(start_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'sequence human':
        ext_list = []
        sel_start = "SELECT DISTINCT seq_data.gbCollectYear FROM seq_data, countries WHERE"
        sel_end = "ORDER BY gbCollectYear;"
        for country in country_list:
            ext = " (gbCollectYear>={0} AND gbCollectYear IS NOT NULL AND seq_data.country_id=countries.country_id AND countries.country_name='{1}' AND gbHost='Human') OR (gbCollectYear>={0} AND gbCollectYear IS NOT NULL AND seq_data.country_id=countries.country_id AND countries.country_name='{1}' AND gbHost='Homo sapiens') ".format(start_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'sequence both':
        ext_list = []
        sel_start = "SELECT DISTINCT seq_data.gbCollectYear FROM seq_data, countries WHERE"
        sel_end = "ORDER BY gbCollectYear;"
        for country in country_list:
            ext = " (gbCollectYear>={0} AND gbCollectYear IS NOT NULL AND seq_data.country_id=countries.country_id AND countries.country_name='{1}') ".format(start_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cursor.execute(final_cmd)
    end_year_list = cursor.fetchall()
    json_end_year = []
    for end_year in end_year_list:
        json_end_year.append(end_year[0])
    cursor.close()
    return json_end_year
def mapper(host, start_year, end_year):
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    if host == 'human':
        cmd = """SELECT lassa_data2.Latitude, lassa_data2.Longitude, lassa_data2.PropAb, lassa_data2.NumTestAb, data_source2.Citation, data_source2.DOI, lassa_data2.source_id, data_source2.source_id FROM lassa_data2, data_source2 WHERE start_year AND end_year BETWEEN {0} AND {1} AND Genus='Homo'AND PropAb IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND data_source2.source_id=lassa_data2.source_id;""".format(start_year, end_year)
        cursor.execute(cmd)
        human_data  = cursor.fetchall()
        json_human_data = []
        for row in human_data:
            lat = float(row[0])
            lon = float(row[1])
            AbPos = float(row[2])
            NumTestAb = float(row[3])
            if row[4]!=None:
                Cite = row[4]
            else:
                Cite = 'unspecified'
            if row[5]!=None:
                DOI = row[5]
            else:
                DOI = 'unspecified'
            entry = (lat, lon, AbPos, NumTestAb, Cite, DOI)
            human_headers = ("Latitude", "Longitude", "PropAb", "NumTestAb", "Citation", "DOI")
            json_human_data.append(dict(zip(human_headers, entry)))
        cursor.close()
        return json_human_data
    if host == 'rodent':
        cmd = """SELECT lassa_data2.Latitude, lassa_data2.Longitude, lassa_data2.PropAb, lassa_data2.NumTestAb, lassa_data2.PropVirus, lassa_data2.NumTestVirus, data_source2.Citation, data_source2.DOI FROM lassa_data2, data_source2 WHERE (start_year AND end_year BETWEEN {0} AND {1} AND Genus!='Homo'AND PropAb IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND data_source2.source_id=lassa_data2.source_id) OR (start_year AND end_year BETWEEN {0} AND {1} AND Genus!='Homo'AND PropVirus IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND data_source2.source_id=lassa_data2.source_id);""".format(start_year, end_year)
        cursor.execute(cmd)
        rodent_data = cursor.fetchall()
        json_rodent_data = []
        for row in rodent_data:
            lat = float(row[0])
            lon = float(row[1])
            if row[2]!=None:
                PropAb = float(row[2])
            else:
                PropAb = 'NaN'
            if row[3]!=None:
                NumTestAb = float(row[3])
            else:
                NumTestAb = 'NaN'
            if row[4]!=None:
                PropAg = float(row[4])
            else:
                PropAg = 'NaN'
            if row[5]!=None:
                NumTestVirus = float(row[5])
            else:
                NumTestVirus = 'NaN'
            if row[6]!=None:
                Cite = row[6]
            else:
                Cite = 'unspecified'
            if row[7]!=None:
                DOI = row[7]
            else:
                DOI = 'unspecified'
            entry = (lat, lon, PropAb, NumTestAb, PropAg, NumTestVirus, Cite, DOI)
            rodent_headers = ("Latitude", "Longitude", "PropAb", "NumTestAb", "PropVirus", "NumTestVirus", "Citation", "DOI")
            json_rodent_data.append(dict(zip(rodent_headers, entry)))
        cursor.close()
        return json_rodent_data
    if host == 'sequence rodent':
        cmd = """SELECT seq_data.Latitude, seq_data.Longitude, seq_data.gbDefinition, seq_data.gbPubMedID, seq_reference.Reference FROM seq_data, seq_reference WHERE (seq_data.gbCollectYear BETWEEN {0} AND {1} AND seq_data.Latitude IS NOT NULL AND seq_data.Longitude IS NOT NULL AND seq_data.reference_id IS NOT NULL AND seq_data.reference_id=seq_reference.reference_id AND gbHost!='Human' AND gbHost!='Homo sapiens') UNION SELECT seq_data.Latitude, seq_data.Longitude, seq_data.gbDefinition, seq_data.gbPubMedID, seq_data.reference_id FROM seq_data WHERE (seq_data.gbCollectYear BETWEEN {0} AND {1} AND seq_data.Latitude IS NOT NULL AND seq_data.Longitude IS NOT NULL AND seq_data.reference_id IS NULL AND gbHost!='Human' AND gbHost!='Homo sapiens');""".format(start_year, end_year)
        cursor.execute(cmd)
        seq_data = cursor.fetchall()
        seq_headers = [x[0] for x in cursor.description]
        json_seq_data = []
        for row in seq_data:
            lat = float(row[0])
            lon = float(row[1])
            if row[2]!=None:
                gbDef = row[2]
            else:
                gbDef = 'unspecified'
            if row[3]!=None:
                pubMedID = row[3]
            else:
                pubMedID = 'unspecified'
            if row[4]!=None:
                Ref = row[4]
            else:
                Ref = 'unspecified'
            entry = (lat, lon, gbDef, pubMedID, Ref)
            json_seq_data.append(dict(zip(seq_headers, entry)))
        cursor.close()
        return json_seq_data
    if host == 'sequence human':
        cmd = """SELECT seq_data.Latitude, seq_data.Longitude, seq_data.gbDefinition, seq_data.gbPubMedID, seq_reference.Reference FROM seq_data, seq_reference WHERE (seq_data.gbCollectYear BETWEEN {0} AND {1} AND seq_data.Latitude IS NOT NULL AND seq_data.Longitude IS NOT NULL AND seq_data.reference_id IS NOT NULL AND seq_data.reference_id=seq_reference.reference_id AND gbHost='Human') OR (seq_data.gbCollectYear BETWEEN {0} AND {1} AND seq_data.Latitude IS NOT NULL AND seq_data.Longitude IS NOT NULL AND seq_data.reference_id IS NOT NULL AND seq_data.reference_id=seq_reference.reference_id AND gbHost='Homo sapiens') UNION SELECT seq_data.Latitude, seq_data.Longitude, seq_data.gbDefinition, seq_data.gbPubMedID, seq_data.reference_id FROM seq_data WHERE (seq_data.gbCollectYear BETWEEN {0} AND {1} AND seq_data.Latitude IS NOT NULL AND seq_data.Longitude IS NOT NULL AND seq_data.reference_id IS NULL AND gbHost='Human') OR (seq_data.gbCollectYear BETWEEN {0} AND {1} AND seq_data.Latitude IS NOT NULL AND seq_data.Longitude IS NOT NULL AND seq_data.reference_id IS NULL AND gbHost='Homo sapiens');""".format(start_year, end_year)
        cursor.execute(cmd)
        seq_data = cursor.fetchall()
        seq_headers = [x[0] for x in cursor.description]
        json_seq_data = []
        for row in seq_data:
            lat = float(row[0])
            lon = float(row[1])
            if row[2]!=None:
                gbDef = row[2]
            else:
                gbDef = 'unspecified'
            if row[3]!=None:
                pubMedID = row[3]
            else:
                pubMedID = 'unspecified'
            if row[4]!=None:
                Ref = row[4]
            else:
                Ref = 'unspecified'
            entry = (lat, lon, gbDef, pubMedID, Ref)
            json_seq_data.append(dict(zip(seq_headers, entry)))
        cursor.close()
        return json_seq_data
def country_list(host):
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    if host == "human":
        cmd = "SELECT DISTINCT lassa_data2.country_id, countries.country_name FROM lassa_data2, countries WHERE countries.country_id=lassa_data2.country_id AND lassa_data2.Genus='Homo' AND lassa_data2.start_year IS NOT NULL AND lassa_data2.end_year IS NOT NULL ORDER BY countries.country_name;"
    if host == "rodent":
        cmd = "SELECT DISTINCT lassa_data2.country_id, countries.country_name FROM lassa_data2, countries WHERE countries.country_id=lassa_data2.country_id AND lassa_data2.Genus!='Homo' AND lassa_data2.start_year IS NOT NULL AND lassa_data2.end_year IS NOT NULL ORDER BY countries.country_name;"
    if host == "sequence rodent":
        cmd = "SELECT DISTINCT seq_data.country_id, countries.country_name FROM seq_data, countries WHERE countries.country_id=seq_data.country_id AND seq_data.gbCollectYear IS NOT NULL AND gbHost!='Human' AND gbHost!='Homo sapiens' ORDER BY countries.country_name;"
    if host == "sequence human":
        cmd = "SELECT DISTINCT seq_data.country_id, countries.country_name FROM seq_data, countries WHERE (countries.country_id=seq_data.country_id AND seq_data.gbCollectYear IS NOT NULL AND gbHost='Human') OR (countries.country_id=seq_data.country_id AND seq_data.gbCollectYear IS NOT NULL AND gbHost='Homo sapiens') ORDER BY countries.country_name;"
    if host == "both":
        cmd = "SELECT DISTINCT lassa_data2.country_id, countries.country_name FROM lassa_data2, countries WHERE countries.country_id=lassa_data2.country_id AND lassa_data2.start_year IS NOT NULL AND lassa_data2.end_year IS NOT NULL ORDER BY countries.country_name;"
    if host == "sequence both":
        cmd = "SELECT DISTINCT seq_data.country_id, countries.country_name FROM seq_data, countries WHERE (countries.country_id=seq_data.country_id AND seq_data.gbCollectYear IS NOT NULL) ORDER BY countries.country_name;"
    cursor.execute(cmd)
    country_headers = [x[0] for x in cursor.description]
    country_list = cursor.fetchall()
    countryJson = []
    for countryEntry in country_list:
        countryJson.append(dict(zip(country_headers, countryEntry)))
    return countryJson
def db_summary():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    #Get the number of countries represented in our dataset
    country_cmd = "SELECT COUNT(countryCount) FROM (SELECT DISTINCT country_id AS countryCount FROM lassa_data2 UNION SELECT DISTINCT country_id AS countryCount FROM seq_data) AS final;"
    #Get the number of studies that our project documents
    source_cmd = "SELECT * FROM data_source2;"
    ref_cmd = "SELECT * FROM seq_reference;"
    #Number of point samples from rodents
    rodent_sample_cmd = "SELECT COUNT(Genus) FROM lassa_data2 WHERE Genus!='Homo';"
    #Number of point samples from humans
    human_sample_cmd = "SELECT COUNT(Genus) FROM lassa_data2 WHERE Genus='Homo' AND PropAb IS NOT NULL;"
    #Number of sequences    
    seq_sample_cmd = "SELECT COUNT(Sequence) FROM seq_data WHERE Sequence IS NOT NULL;"
    cmd_list = [country_cmd, rodent_sample_cmd, human_sample_cmd, seq_sample_cmd]
    source_df = pd.read_sql(source_cmd, cnx)
    ref_df = pd.read_sql(ref_cmd, cnx)
    ref_list = ref_df['Reference'].unique()
    source_list = source_df['Citation'].unique()
    res_list = []
    for ref in ref_list:
        if pd.notnull(ref):
            ref_title = ref.split('.')
            if len(ref_title)>2:
                bin_list = source_df.Citation.str.lower().str.contains(ref_title[2].lower())
                res = list(compress(range(len(bin_list)), bin_list))
                if len(res) > 0:
                    res_list.append(res)
    common_index = list(itertools.chain.from_iterable(res_list))
    common_cite = []
    for ind in common_index:
        cite = source_df['Citation'][ind]
        common_cite.append(cite)
    shared_citation = len(np.unique(common_cite)) 
    # Find the length of both source tables, subtract common refs, and remove 2 from the count as each table has a null row 
    source_count = len(ref_list) + len(source_list) - shared_citation - 2
    summary_list = []
    for cmd in cmd_list:
        cursor.execute(cmd)
        summary = cursor.fetchall()
        summary_list.append(str(summary[0][0]))
    cursor.close()
    summary_list.append(source_count)
    return summary_list
def human_year_data():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cmd = "SELECT start_year, SUM(NumPosAb), SUM(NumTestAb), Ab_Diagnostic_Method FROM lassa_data2 WHERE Genus='Homo' GROUP BY (start_year);"
    cursor.execute(cmd)
    human_year_data = cursor.fetchall()
    cursor.close()
    jsonAbPos = []
    for entry in human_year_data:
        if entry[0]!= None and entry[1]!= None and entry[2]!=None:
            if entry[1]!=0 and entry[2]!=0:
                AbHeader = ("Ab_year", "propAbPos", "DiagnosticMethod")
                if entry[3] != None:
                    diagMethod = entry[3]
                else:
                    diagMethod = 'unspecified'
                AbRow = (entry[0], int(entry[1])/int(entry[2]), diagMethod)
                jsonAbPos.append(dict(zip(AbHeader, AbRow)))                       
    return jsonAbPos
def rodent_year_data():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cmd = "SELECT start_year, Sum(NumPosAb), SUM(NumTestAb), SUM(NumPosVirus), SUM(NumTestVirus), Ab_Diagnostic_Method, Virus_Diagnostic_Method FROM lassa_data2 WHERE Genus!='Homo' GROUP BY (start_year);"
    cursor.execute(cmd)
    rodent_year_data = cursor.fetchall()
    cursor.close()
    jsonAbPos = []
    jsonAgPos = []
    for entry in rodent_year_data:
        if entry[5] != None:
            seroDiagMethod = entry[5]
        else:
            seroDiagMethod = 'unspecified'
        if entry[6] != None:
            virDiagMethod = entry[6]
        else:
            virDiagMethod = 'unspecified'
        if entry[0]!= None and entry[1]!= None and entry[2]!=None:
            if entry[1]!=0 and entry[2]!=0:
                AbHeader = ("Ab_year", "propAbPos", "AbDiagnosticMethod", "VirusDiagnosticMethod")
                AbRow = (entry[0], int(entry[1])/int(entry[2]), seroDiagMethod, virDiagMethod)
                jsonAbPos.append(dict(zip(AbHeader, AbRow)))
        if entry[0]!= None and entry[3]!=None and entry[4]!=None:
            if entry[3]!=0 and entry[4]!=0:
                AgHeader = ("Ag_year", "propAgPos", "AbDiagnosticMethod", "VirusDiagnosticMethod")
                AgRow = (entry[0], int(entry[3])/int(entry[4]), seroDiagMethod, virDiagMethod)
                jsonAgPos.append(dict(zip(AgHeader, AgRow)))
    return jsonAbPos, jsonAgPos
def sequence_rodent_year_data():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cmd = "SELECT gbCollectYear, COUNT(Sequence) FROM seq_data WHERE gbHost!='Human' AND gbHost!='Homo sapiens' GROUP BY (gbCollectYear);"
    cursor.execute(cmd)
    sequence_year_data = cursor.fetchall()
    cursor.close()
    jsonSeq = []
    for entry in sequence_year_data:
        seqRow = (entry[0], entry[1])
        seqHeader = ("seq_year", "seq_count")
        jsonSeq.append(dict(zip(seqHeader, seqRow)))
    return jsonSeq
def sequence_human_year_data():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cmd = "SELECT gbCollectYear, COUNT(Sequence) FROM seq_data WHERE gbHost='Human' OR gbHost='Homo sapiens' GROUP BY (gbCollectYear);"
    cursor.execute(cmd)
    sequence_year_data = cursor.fetchall()
    cursor.close()
    jsonSeq = []
    for entry in sequence_year_data:
        seqRow = (entry[0], entry[1])
        seqHeader = ("seq_year", "seq_count")
        jsonSeq.append(dict(zip(seqHeader, seqRow)))
    return jsonSeq
def filtered_download(host, start_year, end_year, country_list):
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    if host == 'human':
        ext_list = []
        sel_start = """SELECT lassa_data2.lassa_id, lassa_data2.Town_Region, lassa_data2.Village,  
                       lassa_data2.Latitude, lassa_data2.Longitude, countries.country_name, 
                       lassa_data2.NumPosVirus, lassa_data2.NumTestVirus, lassa_data2.PropVirus,
                       lassa_data2.Virus_Diagnostic_Method, lassa_data2.NumPosAb, lassa_data2.NumTestAb, 
                       lassa_data2.PropAb, lassa_data2.Ab_Diagnostic_Method, lassa_data2.Antibody_Target, 
                       lassa_data2.Genus, lassa_data2.Species, lassa_data2.lat_lon_source, data_source2.Source, 
                       data_source2.Citation, data_source2.DOI FROM lassa_data2, countries,data_source2 WHERE"""
        sel_end = "ORDER BY start_year;"
        for country in country_list:    
            ext = """ (lassa_data2.country_id=countries.country_id AND lassa_data2.source_id=data_source2.source_id AND Genus='Homo' AND lassa_data2.start_year AND lassa_data2.end_year BETWEEN {0} AND {1} AND countries.country_name='{2}') """.format(start_year, end_year, country)   
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'rodent':
        ext_list = []
        sel_start = """SELECT lassa_data2.lassa_id, lassa_data2.Town_Region, lassa_data2.Village,  
                       lassa_data2.Latitude, lassa_data2.Longitude, countries.country_name, 
                       lassa_data2.NumPosVirus, lassa_data2.NumTestVirus, lassa_data2.PropVirus,
                       lassa_data2.Virus_Diagnostic_Method, lassa_data2.NumPosAb, lassa_data2.NumTestAb, 
                       lassa_data2.PropAb, lassa_data2.Ab_Diagnostic_Method, lassa_data2.Antibody_Target, 
                       lassa_data2.Genus, lassa_data2.Species, lassa_data2.lat_lon_source, data_source2.Source, 
                       data_source2.Citation, data_source2.DOI FROM lassa_data2, countries,data_source2 WHERE"""
        sel_end = "ORDER BY start_year;"
        for country in country_list:    
            ext = """ (lassa_data2.country_id=countries.country_id AND lassa_data2.source_id=data_source2.source_id AND Genus!='Homo' AND lassa_data2.start_year AND lassa_data2.end_year BETWEEN {0} AND {1} AND countries.country_name='{2}') """.format(start_year, end_year, country)   
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'both':
        ext_list = []
        sel_start = """SELECT lassa_data2.lassa_id, lassa_data2.Town_Region, lassa_data2.Village,  
                       lassa_data2.Latitude, lassa_data2.Longitude, countries.country_name, 
                       lassa_data2.NumPosVirus, lassa_data2.NumTestVirus, lassa_data2.PropVirus,
                       lassa_data2.Virus_Diagnostic_Method, lassa_data2.NumPosAb, lassa_data2.NumTestAb, 
                       lassa_data2.PropAb, lassa_data2.Ab_Diagnostic_Method, lassa_data2.Antibody_Target, 
                       lassa_data2.Genus, lassa_data2.Species, lassa_data2.lat_lon_source, data_source2.Source, 
                       data_source2.Citation, data_source2.DOI FROM lassa_data2, countries,data_source2 WHERE""" 
        sel_end = "ORDER BY start_year;"
        for country in country_list:    
            ext = """ (lassa_data2.country_id=countries.country_id AND lassa_data2.source_id=data_source2.source_id AND lassa_data2.start_year AND lassa_data2.end_year BETWEEN {0} AND {1} AND countries.country_name='{2}') """.format(start_year, end_year, country)   
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end    
    if host == 'sequence rodent':
        ext_list = []
        sel_start = """SELECT seq_data.seq_id, seq_data.gbAccession, seq_data.gbDefinition, seq_data.gbLength, seq_data.gbHost, 
                       seq_data.LocVillage, seq_data.LocState, countries.country_name, seq_data.gbCollectYear, seq_data.Latitude, 
                       seq_data.Longitude, seq_data.Hospital, seq_data.gbPubMedID, seq_data.gbJournal, 
                       seq_data.PubYear, seq_data.GenomeCompleteness, seq_data.Tissue, seq_data.Strain, 
                       seq_data.gbProduct, seq_data.gbGene, seq_data.S, seq_data.L, seq_data.GPC, seq_data.NP, 
                       seq_data.Pol, seq_data.Z, seq_data.Sequence, seq_reference.Reference, seq_data.Notes FROM seq_data, countries, seq_reference WHERE"""
        sel_end = "ORDER BY gbCollectYear"
        for country in country_list:
            ext = """ (seq_data.country_id=countries.country_id AND seq_data.reference_id=seq_reference.reference_id AND seq_data.gbCollectYear BETWEEN {0} AND {1} AND countries.country_name='{2}' AND gbHost!='Human' AND gbHost!='Homo sapiens') """.format(start_year, end_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'sequence human':
        ext_list = []
        sel_start = """SELECT seq_data.seq_id, seq_data.gbAccession, seq_data.gbDefinition, seq_data.gbLength, seq_data.gbHost, 
                       seq_data.LocVillage, seq_data.LocState, countries.country_name, seq_data.gbCollectYear, seq_data.Latitude, 
                       seq_data.Longitude, seq_data.Hospital, seq_data.gbPubMedID, seq_data.gbJournal, 
                       seq_data.PubYear, seq_data.GenomeCompleteness, seq_data.Tissue, seq_data.Strain, 
                       seq_data.gbProduct, seq_data.gbGene, seq_data.S, seq_data.L, seq_data.GPC, seq_data.NP, 
                       seq_data.Pol, seq_data.Z, seq_data.Sequence, seq_reference.Reference, seq_data.Notes FROM seq_data, countries, seq_reference WHERE"""
        sel_end = "ORDER BY gbCollectYear"
        for country in country_list:
            ext = """ (seq_data.country_id=countries.country_id AND seq_data.reference_id=seq_reference.reference_id AND seq_data.gbCollectYear BETWEEN {0} AND {1} AND countries.country_name='{2}' AND gbHost='Human') OR (seq_data.country_id=countries.country_id AND seq_data.reference_id=seq_reference.reference_id AND seq_data.gbCollectYear BETWEEN {0} AND {1} AND countries.country_name='{2}' AND gbHost='Homo sapiens') """.format(start_year, end_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'sequence both':
        ext_list = []
        sel_start = """SELECT seq_data.seq_id, seq_data.gbAccession, seq_data.gbDefinition, seq_data.gbLength, seq_data.gbHost, 
                       seq_data.LocVillage, seq_data.LocState, countries.country_name, seq_data.gbCollectYear, seq_data.Latitude, 
                       seq_data.Longitude, seq_data.Hospital, seq_data.gbPubMedID, seq_data.gbJournal, 
                       seq_data.PubYear, seq_data.GenomeCompleteness, seq_data.Tissue, seq_data.Strain, 
                       seq_data.gbProduct, seq_data.gbGene, seq_data.S, seq_data.L, seq_data.GPC, seq_data.NP, 
                       seq_data.Pol, seq_data.Z, seq_data.Sequence, seq_reference.Reference, seq_data.Notes FROM seq_data, countries, seq_reference WHERE"""
        sel_end = "ORDER BY gbCollectYear"
        for country in country_list:
            ext = """ (seq_data.country_id=countries.country_id AND seq_data.reference_id=seq_reference.reference_id AND seq_data.gbCollectYear BETWEEN {0} AND {1} AND countries.country_name='{2}') """.format(start_year, end_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    cursor.execute(final_cmd)
    dataDump = cursor.fetchall()
    headers = [x[0] for x in cursor.description]
    jsonDump = []
    for result in dataDump:
        col_vals = []
        for data in result:
            if type(data) is Decimal:
                col_vals.append(float(data))
            else:
                col_vals.append(str(data))
        jsonDump.append(dict(zip(headers, col_vals)))
    return jsonDump
def source_id_mapper(data_df):
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    source_cmd = "SELECT * FROM data_source2;"
    source_result = pd.read_sql(source_cmd, cnx)
    cnx.close()
    source_df = pd.DataFrame(columns=['source_id'])
    for i in range(0, len(data_df)):
        cite = data_df['Citation'][i]
        source = data_df['Source'][i]
        doi = data_df['DOI'][i]
        bibtex = data_df['Bibtex'][i]
        if cite in list(source_result['Citation']):
            source_id = source_result[source_result['Citation']==cite]['source_id'].iloc[0]
            source_df.loc[i] = source_id
        else:
            cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
            cursor = cnx.cursor()
            insert_cmd = """INSERT INTO data_source2 (Citation, Source, DOI, Bibtex) VALUES ('{0}', '{1}', '{2}', '{3}')""".format(cite, source, doi, bibtex)
            cursor.execute(insert_cmd)
            cnx.commit()
            cursor.close()
            cnx.close()
            return source_id_mapper()
    source_df = source_df.sort_index()
    return source_df
def seq_ref_id_mapper(data_df):
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    ref_cmd = "SELECT * FROM seq_reference;"
    ref_result = pd.read_sql(ref_cmd, cnx)
    ref_result = ref_result.fillna('No Data')
    cnx.close()
    null_ref_id = ref_result[ref_result['Reference']=='No Data']['reference_id'].iloc[0]
    reference_df = pd.DataFrame(columns=['reference_id'])
    rows_with_nan = np.where(data_df.Reference.isnull())
    for ind2 in rows_with_nan[0]:
        reference_df.loc[ind2] = null_ref_id
    for i in range(0, len(data_df)):
        ref = data_df['Reference'][i]
        if pd.notnull(ref):
            if ref in list(ref_result['Reference']):
                ref_id = ref_result[ref_result['Reference']==ref]['reference_id'].iloc[0]
                reference_df.loc[i] = ref_id
            else:
                cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
                cursor = cnx.cursor()
                insert_cmd = """INSERT INTO seq_reference (Reference) VALUES ('{0}')""".format(ref)
                cursor.execute(insert_cmd)
                cnx.commit()
                cursor.close()
                cnx.close()
                return seq_ref_id_mapper(data_df)
    reference_df = reference_df.sort_index()
    return reference_df
def country_id_mapper(data_df):
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    country_cmd = "SELECT * FROM countries;"
    country_result = pd.read_sql(country_cmd, cnx)
    country_df = pd.DataFrame(columns=['country_id'])
    for country in data_df['Country']:
        if pd.notnull(country):
            if country in list(country_result['country_name']):
                country_id = country_result[country_result['country_name']==country]['country_id'].iloc[0]
                country_ind = country_result[country_result['country_name']==country]['country_id'].index[0]
                country_df.loc[country_ind] = country_id
                country_error = None
            else:
                country_error = "Country: {0}, not recognized. See help for a full list of accepted countries".format(country)
        else:
            country_error = 'Missing country name'
    cursor.close()
    country_df = country_df.sort_index()
    return country_df, country_error
def lat_lon_check(data_df):
    check_list = []
    latlonError = None
    dir_path = os.path.dirname(os.path.realpath(__file__))
    africa_geo_file = os.path.join(dir_path, 'Africa.geojson')
    africa_gdf = gpd.read_file(africa_geo_file)
    africa_gdf = africa_gdf.replace({"CÃ´te d'Ivoire": "Ivory Coast"})
    for i in range(0, len(data_df)):
        lat = data_df['Latitude'][i]
        lon = data_df['Longitude'][i]
        country = data_df['Country'][i]
        if pd.notnull([lat, lon]).all():
            result = africa_gdf['geometry'].contains(Point(lon, lat))
            res = [j for j, val in enumerate(result) if val]
            if len(res)<1:
                latlonError = 'Latitude: {0}, Longitude: {1}, Not Within Africa. Line: {2}'.format(lat, lon, i)
            else:
                latlonError = None
                country_gdf = africa_gdf['Country'].loc[res[0]]
                if country == country_gdf:
                    continue
                else:
                    #check_list.append([country, country_gdf])
                    data_df[['Country']] = data_df[['Country']].replace([country], [country_gdf])
    return data_df, latlonError
def check_data_types(data_df):
    error_list = []
    for index, row in data_df.iterrows():
        col_list = ["lassa_id", "Town_Region", "Village", "Latitude", "Longitude", "Country", 
                    "NumPosVirus", "NumTestVirus", "PropVirus", "Virus_Diagnostic_Method", "NumPosAb", 
                    "NumTestAb", "PropAb", "Ab_Diagnostic_Method", "Antibody_Target", "Genus", "Species", 
                    "lat_lon_source", "Source", "Citation", "DOI", "Bibtex", "Survey_Notes", "Housing_Notes",
                    "start_year", "end_year"]
        type_list = [int, str, str, float, float, str, int, int, float, str, int, int , float, 
                     str, str, str, str, str, str, str, str, str, str, str, int, int]
        for i in range(0, len(col_list)):
            col = col_list[i]
            dtype = type_list[i]
            if col == 'start_year' or col == 'end_year' or col == 'NumPosAb' or \
                col == 'NumPosVirus' or col == 'NumTestAb' or col == 'NumTestVirus' or \
                col == 'PropAb' or col == 'PropVirus':
                if pd.notnull(row[col]):
                    # print(row[col])
                    if isinstance(row[col], int) or isinstance(row[col], float):
                        continue
                    else:
                        error_data_t = type(row[col])
                        error = "{0} is incorrect datatype at line: {1}. Should be: {2}, instead of: {3}".format(col, index, dtype, error_data_t)
                        error_list.append(error)
            else:
                if pd.notnull(row[col]):
                    if isinstance(row[col], dtype):
                        continue
                    else:
                        error_data_t = type(row[col])
                        error = "{0} is incorrect datatype at line: {1}. Should be: {2}, instead of: {3}".format(col, index, dtype, error_data_t)
                        error_list.append(error)
    return error_list
def seq_check_data_types(data_df):
    error_list = []
    for index, row in data_df.iterrows():
        col_list = ["seq_id", "gbAccession", "gbDefinition", "gbLength", "gbHost", 
                    "LocVillage", "LocState", "Country", "gbCollectDate", "CollectionMonth", 
                    "gbCollectYear", "Latitude", "Longitude", "Hospital", "gbPubMedID", "gbJournal", 
                    "PubYear", "GenomeCompleteness", "Tissue", "Strain", "gbProduct", 
                    "gbGene", "S", "L", "GPC", "NP", "Pol", "Z", "Sequence", "Reference", 
                    "Notes"]
        type_list = [int, str, str, int, str, str, str, str, datetime.datetime, str, int, float, float,
                     str, float, str, int, str, str, str, str, str, int, int, int, int, int,
                     int, str, str, str]
        for i in range(0, len(col_list)):
            col = col_list[i]
            dtype = type_list[i]
            if col == 'PubYear' or col == 'gbCollectYear' or col == 'S' or col == 'L' or col == 'GPC' or col == 'NP'\
            or col == 'Pol' or col == 'Z':
                if pd.notnull(row[col]):
                    # print(row[col])
                    if isinstance(row[col], int) or isinstance(row[col], float):
                        continue
                    else:
                        error_data_t = type(row[col])
                        error = "{0} is incorrect datatype at line: {1}. Should be: {2}, instead of: {3}".format(col, index, dtype, error_data_t)
                        error_list.append(error)
            if col == 'gbCollectDate':
                if pd.notnull(row[col]):
                    if isinstance(row[col], datetime.datetime) or isinstance(row[col], int) or isinstance(row[col], str):
                        continue
                    else:
                        error_data_t = type(row[col])
                        error = "{0} is incorrect datatype at line: {1}. Should be: {2}, instead of: {3}".format(col, index, dtype, error_data_t)
                        error_list.append(error)
            if col == 'Strain':
                if pd.notnull(row[col]):
                    if isinstance(row[col], str) or isinstance(row[col], int):
                        continue
                    else:
                        error_data_t = type(row[col])
                        error = "{0} is incorrect datatype at line: {1}. Should be: {2}, instead of: {3}".format(col, index, dtype, error_data_t)
                        error_list.append(error)                        
            if pd.notnull(row[col]):
                if isinstance(row[col], dtype):
                    continue
                else:
                    error_data_t = type(row[col])
                    error = "{0} is incorrect datatype at line: {1}. Should be: {2}, instead of: {3}".format(col, index, dtype, error_data_t)
                    error_list.append(error)
    return error_list  
# This bit is only used for testing the functions before implementation 
#if __name__ == '__main__':
#    print(mapper('rodent', '1970', '2016'))
