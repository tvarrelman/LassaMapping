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
        cmd = "SELECT DISTINCT start_year, end_year FROM lassa_data WHERE start_year IS NOT NULL AND Genus='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL ORDER BY start_year;"
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
        cmd = "SELECT DISTINCT start_year, end_year FROM lassa_data WHERE (start_year IS NOT NULL AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL) OR (start_year IS NOT NULL AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAg IS NOT NULL) ORDER BY start_year;"
        cursor.execute(cmd)
        year_lists = cursor.fetchall()
        init_start_year_list = []
        init_end_year_list = []
        for i in range(0, len(year_lists)):
            init_start_year_list.append(year_lists[i][0])
            init_end_year_list.append(year_lists[i][1])
        cursor.close()
        return init_start_year_list, init_end_year_list
    if host=='sequence':
        cmd = "SELECT DISTINCT gbCollectYear FROM seq_data WHERE (gbCollectYear IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL) ORDER BY gbCollectYear;"
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
        cmd = """SELECT DISTINCT end_year FROM lassa_data WHERE (end_year>={0} AND Genus='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL) ORDER BY end_year;""".format(start_year)
    if host=='rodent':
        cmd = """SELECT DISTINCT end_year FROM lassa_data WHERE (end_year>={0} AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL) OR (end_year>={0} AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAg IS NOT NULL) ORDER BY end_year;""".format(start_year)
    if host=='sequence':
        cmd = """SELECT DISTINCT gbCollectYear FROM seq_data WHERE (gbCollectYear>={0} AND Latitude IS NOT NULL AND Longitude IS NOT NULL) ORDER BY gbCollectYear;""".format(start_year)
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
        sel_start = "SELECT DISTINCT lassa_data.start_year, lassa_data.end_year FROM lassa_data, countries WHERE"
        sel_end = "ORDER BY start_year;"
        for country in country_list:
            ext = " (start_year IS NOT NULL AND Genus='Homo' AND lassa_data.country_id=countries.country_id AND countries.country_name='{0}') ".format(country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end 
    if host == 'rodent':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data.start_year, lassa_data.end_year FROM lassa_data, countries WHERE"
        sel_end = "ORDER BY start_year;"
        for country in country_list:
            ext = " (start_year IS NOT NULL AND Genus!='Homo' AND lassa_data.country_id=countries.country_id AND countries.country_name='{0}') ".format(country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'both':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data.start_year, lassa_data.end_year FROM lassa_data, countries WHERE"
        sel_end = "ORDER BY start_year;"
        for country in country_list:
            ext = " (start_year IS NOT NULL AND lassa_data.country_id=countries.country_id AND countries.country_name='{0}') ".format(country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host=='sequence':
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
    #print(final_cmd)
    cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
    #cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
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
        sel_start = "SELECT DISTINCT lassa_data.end_year FROM lassa_data, countries WHERE"
        sel_end = "ORDER BY end_year;"
        for country in country_list:
            ext = " (end_year>={0} AND end_year IS NOT NULL AND Genus='Homo' AND lassa_data.country_id=countries.country_id AND countries.country_name='{1}') ".format(start_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'rodent':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data.end_year FROM lassa_data, countries WHERE"
        sel_end = "ORDER BY end_year;"
        for country in country_list:
            ext = " (end_year>={0} AND end_year IS NOT NULL AND Genus!='Homo' AND lassa_data.country_id=countries.country_id AND countries.country_name='{1}') ".format(start_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'both':
        ext_list = []
        sel_start = "SELECT DISTINCT lassa_data.end_year FROM lassa_data, countries WHERE"
        sel_end = "ORDER BY end_year;"
        for country in country_list:
            ext = " (end_year>={0} AND end_year IS NOT NULL AND lassa_data.country_id=countries.country_id AND countries.country_name='{1}') ".format(start_year, country)
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
    if host == 'sequence':
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
        cmd = """SELECT lassa_data.Latitude, lassa_data.Longitude, lassa_data.PropAb, data_source.Citation, data_source.DOI, lassa_data.source_id, data_source.source_id FROM lassa_data, data_source WHERE start_year AND end_year BETWEEN {0} AND {1} AND Genus='Homo'AND PropAb IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND data_source.source_id=lassa_data.source_id;""".format(start_year, end_year)
        cursor.execute(cmd)
        human_data  = cursor.fetchall()
        human_headers = [x[0] for x in cursor.description]
        json_human_data = []
        for row in human_data:
            lat = float(row[0])
            lon = float(row[1])
            AbPos = float(row[2])
            if row[3]!=None:
                Cite = row[3]
            else:
                Cite = 'NaN'
            if row[4]!=None:
                DOI = row[4]
            else:
                DOI = 'NaN'
            entry = (lat, lon, AbPos, Cite, DOI)
            json_human_data.append(dict(zip(human_headers, entry)))
        cursor.close()
        return json_human_data
    if host == 'rodent':
        cmd = """SELECT lassa_data.Latitude, lassa_data.Longitude, lassa_data.PropAb, lassa_data.PropAg, data_source.Citation, data_source.DOI FROM lassa_data, data_source WHERE (start_year AND end_year BETWEEN {0} AND {1} AND Genus!='Homo'AND PropAb IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND data_source.source_id=lassa_data.source_id) OR (start_year AND end_year BETWEEN {0} AND {1} AND Genus!='Homo'AND PropAg IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND data_source.source_id=lassa_data.source_id);""".format(start_year, end_year)
        cursor.execute(cmd)
        rodent_data = cursor.fetchall()
        rodent_headers = [x[0] for x in cursor.description]
        json_rodent_data = []
        for row in rodent_data:
            lat = float(row[0])
            lon = float(row[1])
            if row[2]!=None:
                PropAb = float(row[2])
            else:
                PropAb = 'NaN'
            if row[3]!=None:
                PropAg = float(row[3])
            else:
                PropAg = 'NaN'
            if row[4]!=None:
                Cite = row[4]
            else:
                Cite = 'NaN'
            if row[5]!=None:
                DOI = row[5]
            else:
                DOI = 'NaN'
            entry = (lat, lon, PropAb, PropAg, Cite, DOI)
            json_rodent_data.append(dict(zip(rodent_headers, entry)))
        cursor.close()
        return json_rodent_data
    if host == 'sequence':
        cmd = """SELECT seq_data.Latitude, seq_data.Longitude, seq_data.gbDefinition, seq_data.gbPubMedID, seq_reference.Reference FROM seq_data, seq_reference WHERE seq_data.gbCollectYear BETWEEN {0} AND {1} AND seq_data.Latitude IS NOT NULL AND seq_data.Longitude IS NOT NULL AND seq_data.reference_id=seq_reference.reference_id;""".format(start_year, end_year)
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
                gbDef = 'NaN'
            if row[3]!=None:
                pubMedID = row[3]
            else:
                pubMedID = 'NaN'
            if row[4]!=None:
                Ref = row[4]
            else:
                Ref = 'NaN'
            entry = (lat, lon, gbDef, pubMedID, Ref)
            json_seq_data.append(dict(zip(seq_headers, entry)))
        cursor.close()
        return json_seq_data
def country_list(host):
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    if host == "human":
        cmd = "SELECT DISTINCT lassa_data.country_id, countries.country_name FROM lassa_data, countries WHERE countries.country_id=lassa_data.country_id AND lassa_data.Genus='Homo' AND lassa_data.start_year IS NOT NULL AND lassa_data.end_year IS NOT NULL ORDER BY countries.country_name;"
    if host == "rodent":
        cmd = "SELECT DISTINCT lassa_data.country_id, countries.country_name FROM lassa_data, countries WHERE countries.country_id=lassa_data.country_id AND lassa_data.Genus!='Homo' AND lassa_data.start_year IS NOT NULL AND lassa_data.end_year IS NOT NULL ORDER BY countries.country_name;"
    if host == "sequence":
        cmd = "SELECT DISTINCT seq_data.country_id, countries.country_name FROM seq_data, countries WHERE countries.country_id=seq_data.country_id AND seq_data.gbCollectYear IS NOT NULL ORDER BY countries.country_name;"
    if host == "both":
        cmd = "SELECT DISTINCT lassa_data.country_id, countries.country_name FROM lassa_data, countries WHERE countries.country_id=lassa_data.country_id AND lassa_data.start_year IS NOT NULL AND lassa_data.end_year IS NOT NULL ORDER BY countries.country_name;"
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
    country_cmd = "SELECT COUNT(countryCount) FROM (SELECT DISTINCT country_id AS countryCount FROM lassa_data UNION SELECT DISTINCT country_id AS countryCount FROM seq_data) AS final;"
    #Get the number of studies that our project documents
    source_cmd = "SELECT COUNT(*) FROM data_source;"
    #Number of point samples from rodents
    rodent_sample_cmd = "SELECT COUNT(Genus) FROM lassa_data WHERE Genus!='Homo';"
    #Number of point samples from humans
    human_sample_cmd = "SELECT COUNT(Genus) FROM lassa_data WHERE Genus='Homo' AND PropAb IS NOT NULL;"
    #Number of sequences    
    seq_sample_cmd = "SELECT COUNT(Sequence) FROM seq_data WHERE Sequence IS NOT NULL;"
    cmd_list = [country_cmd, source_cmd, rodent_sample_cmd, human_sample_cmd, seq_sample_cmd]
    summary_list = []
    for cmd in cmd_list:
        cursor.execute(cmd)
        summary = cursor.fetchall()
        summary_list.append(str(summary[0][0]))
    cursor.close()
    return summary_list
def human_year_data():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cmd = "SELECT start_year, SUM(NumPosAb), SUM(NumTestAb) FROM lassa_data WHERE Genus='Homo' GROUP BY (start_year);"
    cursor.execute(cmd)
    human_year_data = cursor.fetchall()
    cursor.close()
    jsonAbPos = []
    for entry in human_year_data:
        if entry[0]!= None and entry[1]!= None and entry[2]!=None:
            if entry[1]!=0 and entry[2]!=0:
                AbHeader = ("Ab_year", "propAbPos")
                AbRow = (entry[0], int(entry[1])/int(entry[2]))
                jsonAbPos.append(dict(zip(AbHeader, AbRow)))                       
    return jsonAbPos
def rodent_year_data():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cmd = "SELECT start_year, Sum(NumPosAb), SUM(NumTestAb), SUM(NumPosAg), SUM(NumTestAg) FROM lassa_data WHERE Genus!='Homo' GROUP BY (start_year);"
    cursor.execute(cmd)
    rodent_year_data = cursor.fetchall()
    cursor.close()
    jsonAbPos = []
    jsonAgPos = []
    for entry in rodent_year_data:
        if entry[0]!= None and entry[1]!= None and entry[2]!=None:
            if entry[1]!=0 and entry[2]!=0:
                AbHeader = ("Ab_year", "propAbPos")
                AbRow = (entry[0], int(entry[1])/int(entry[2]))
                jsonAbPos.append(dict(zip(AbHeader, AbRow)))
        if entry[0]!= None and entry[3]!=None and entry[4]!=None:
            if entry[3]!=0 and entry[4]!=0:
                AgHeader = ("Ag_year", "propAgPos")
                AgRow = (entry[0], int(entry[3])/int(entry[4]))
                jsonAgPos.append(dict(zip(AgHeader, AgRow)))
    return jsonAbPos, jsonAgPos
def sequence_year_data():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cmd = "SELECT gbCollectYear, COUNT(Sequence) FROM seq_data GROUP BY (gbCollectYear);"
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
        sel_start = "SELECT lassa_data.Town_Region, lassa_data.Village, lassa_data.Month, lassa_data.Day, lassa_data.start_year, lassa_data.end_year, lassa_data.Latitude, lassa_data.Longitude, lassa_data.Status, lassa_data.NumPosAg, lassa_data.NumTestAg, lassa_data.PropAg, lassa_data.NumPosAb, lassa_data.NumTestAb, lassa_data.PropAb, lassa_data.Genus, lassa_data.Species, lassa_data.DiagnosticMethod, lassa_data.Target, lassa_data.lat_lon_source, lassa_data.Human_Random_Survey, countries.country_name, data_source.Citation, data_source.DOI FROM lassa_data, countries,data_source WHERE" 
        sel_end = "ORDER BY start_year;"
        for country in country_list:    
            ext = """ (lassa_data.country_id=countries.country_id AND lassa_data.source_id=data_source.source_id AND Genus='Homo' AND lassa_data.start_year AND lassa_data.end_year BETWEEN {0} AND {1} AND countries.country_name='{2}') """.format(start_year, end_year, country)   
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
        
    if host == 'rodent':
        ext_list = []
        sel_start = "SELECT lassa_data.Town_Region, lassa_data.Village, lassa_data.Month, lassa_data.Day, lassa_data.start_year, lassa_data.end_year, lassa_data.Latitude, lassa_data.Longitude, lassa_data.Status, lassa_data.NumPosAg, lassa_data.NumTestAg, lassa_data.PropAg, lassa_data.NumPosAb, lassa_data.NumTestAb, lassa_data.PropAb, lassa_data.Genus, lassa_data.Species, lassa_data.DiagnosticMethod, lassa_data.Target, lassa_data.lat_lon_source, lassa_data.Human_Random_Survey, countries.country_name, data_source.Citation, data_source.DOI FROM lassa_data, countries,data_source WHERE" 
        sel_end = "ORDER BY start_year;"
        for country in country_list:    
            ext = """ (lassa_data.country_id=countries.country_id AND lassa_data.source_id=data_source.source_id AND Genus!='Homo' AND lassa_data.start_year AND lassa_data.end_year BETWEEN {0} AND {1} AND countries.country_name='{2}') """.format(start_year, end_year, country)   
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end
        
    if host == 'both':
        ext_list = []
        sel_start = "SELECT lassa_data.Town_Region, lassa_data.Village, lassa_data.Month, lassa_data.Day, lassa_data.start_year, lassa_data.end_year, lassa_data.Latitude, lassa_data.Longitude, lassa_data.Status, lassa_data.NumPosAg, lassa_data.NumTestAg, lassa_data.PropAg, lassa_data.NumPosAb, lassa_data.NumTestAb, lassa_data.PropAb, lassa_data.Genus, lassa_data.Species, lassa_data.DiagnosticMethod, lassa_data.Target, lassa_data.lat_lon_source, lassa_data.Human_Random_Survey, countries.country_name, data_source.Citation, data_source.DOI FROM lassa_data, countries,data_source WHERE" 
        sel_end = "ORDER BY start_year;"
        for country in country_list:    
            ext = """ (lassa_data.country_id=countries.country_id AND lassa_data.source_id=data_source.source_id AND lassa_data.start_year AND lassa_data.end_year BETWEEN {0} AND {1} AND countries.country_name='{2}') """.format(start_year, end_year, country)   
            ext_list.append(ext)
        if len(country_list)>1:
            separator = 'OR'
            ext_list2 = separator.join(ext_list)
            final_cmd = sel_start + ext_list2 + sel_end
        else:
            final_cmd = sel_start + ext_list[0] + sel_end    
    if host == 'sequence':
        ext_list = []
        sel_start = "SELECT seq_data.UniqueID, seq_data.gbAccession, seq_data.gbDefinition, seq_data.gbLength, seq_data.gbHost, seq_data.LocVillage, seq_data.LocState, seq_data.gbCollectYear, seq_data.Latitude, seq_data.Longitude, seq_data.Hospital, seq_data.gbPubMedID, seq_data.gbJournal, seq_data.PubYear, seq_data.GenomeCompleteness, seq_data.Tissue, seq_data.Strain, seq_data.gbProduct, seq_data.gbGene, seq_data.S, seq_data.L, seq_data.GPC, seq_data.NP, seq_data.Pol, seq_data.Z, seq_data.Sequence, seq_data.Notes, seq_data.HostBin, seq_data.Loc_Verif, seq_data.ID_method, countries.country_name, seq_reference.Reference FROM seq_data, countries, seq_reference WHERE"
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
    cursor = cnx.cursor()
    source_cmd = "SELECT * FROM data_source;"
    source_result = pd.read_sql(source_cmd, cnx)
    source_df = pd.DataFrame(columns=['source_id'])
    for i in range(0, len(data_df)):
        cite = data_df['Citation'][i]
        source = data_df['Source'][i]
        doi = data_df['DOI'][i]
        if cite in list(source_result['Citation']):
            source_id = source_result[source_result['Citation']==cite]['source_id'].iloc[0]
            source_ind = source_result[source_result['Citation']==cite]['source_id'].index[0]
            source_df.loc[source_ind] = source_id
        else:
            insert_cmd = """INSERT INTO test_data_source (Citation, Source, DOI) VALUES ('{0}', '{1}', '{2}')""".format(cite, source, doi)
            cursor.execute(insert_cmd)
            cnx.commit()
            #return source_id_mapper()
    cursor.close()
    source_df = source_df.sort_index()
    return source_df
def country_id_mapper(data_df):
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    country_cmd = "SELECT * FROM countries;"
    country_result = pd.read_sql(country_cmd, cnx)
    country_df = pd.DataFrame(columns=['country_id'])
    for country in data_df['Country']:
        if country in list(country_result['country_name']):
            country_id = country_result[country_result['country_name']==country]['country_id'].iloc[0]
            country_ind = country_result[country_result['country_name']==country]['country_id'].index[0]
            country_df.loc[country_ind] = country_id
        else:
            insert_cmd = """INSERT INTO test_countries (country_name) VALUES ('{0}')""".format(country)
            cursor.execute(insert_cmd)
            cnx.commit()
            #return country_id_mapper()
    cursor.close()
    country_df = country_df.sort_index()
    return country_df
def lat_lon_check(data_df):
    check_list = []
    for i in range(0, len(data_df)):
        lat = data_df['Latitude'][i]
        lon = data_df['Longitude'][i]
        country = data_df['Country'][i]
        if lat or lon != None:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            africa_geo_file = os.path.join(dir_path, 'Africa.geojson')
            africa_gdf = gpd.read_file(africa_geo_file)
            africa_gdf = africa_gdf.replace({"CÃ´te d'Ivoire": "Ivory Coast"})
            result = africa_gdf['geometry'].contains(Point(lon, lat))
            res = [j for j, val in enumerate(result) if val]
            if len(res)<1:
                latlonError = 'Latitude: {0}, Longitude: {1} Not Within Africa'.format(lat, lon)
            else:
                latlonError = None
                country_gdf = africa_gdf['Country'].loc[res[0]]
                if country == country_gdf:
                    continue
                else:
                    #check_list.append([country, country_gdf])
                    data_df[['Country']] = data_df[['Country']].replace([country], [country_gdf])
    return data_df, latlonError
# This bit is only used for testing the functions before implementation 
#if __name__ == '__main__':
    #print(filtered_year_list('sequence', ['Nigeria', 'Sierra Leone']))
    #print(lat_lon_check())
    #print(filtered_download('both', '1990', '2001', ['Nigeria']))
    #print(filtered_end_year_list('both', '2003', ['Benin', 'Nigeria']))
    #print(filtered_year_list('human', ['Benin']))
    #print(country_list('human'))
