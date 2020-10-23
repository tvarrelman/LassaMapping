"""script for returning db queries """
import mysql.connector
import os
import numpy as np
from os import environ, path
from dotenv import load_dotenv
import json
#from shapely.geometry import shape, Point

# finds the absolute path of this file
basedir = path.abspath(path.dirname(__file__))
# reads the key value from .env, and adds it to the environment variable
load_dotenv(path.join(basedir, '.env'))
db_user = os.environ.get('user')
db_pw = os.environ.get('password')
db_host = os.environ.get('host')
db_name = os.environ.get('database')
def initial_year_lists(host):
    cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
    #cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
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
def db_summary():
    cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
    #cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
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
    cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
    #cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
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
# This bit is only used for testing the functions before implementation 
#if __name__ == '__main__':
    #print(sequence_year_data())
    #print(db_summary())
    #print(initial_year_lists('sequence'))
    #print(rodent_year_data())
    #print(mapper('sequence', '2015','2015'))
    #print(start_year_list('rodent'))
    #print(end_year_list("2002", 'sequence'))
