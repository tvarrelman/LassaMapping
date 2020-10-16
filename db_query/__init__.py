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
    if host=='human':
        cmd1 = "SELECT DISTINCT start_year FROM lassa_data WHERE start_year IS NOT NULL AND Genus='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL ORDER BY start_year;"
        cmd2 = "SELECT DISTINCT end_year FROM lassa_data WHERE end_year IS NOT NULL AND Genus='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL ORDER BY end_year;"
    if host=='rodent':
        cmd1 = "SELECT DISTINCT start_year FROM lassa_data WHERE (start_year IS NOT NULL AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL) OR (start_year IS NOT NULL AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAg IS NOT NULL) ORDER BY start_year;"
        cmd2 = "SELECT DISTINCT end_year FROM lassa_data WHERE (end_year IS NOT NULL AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL) OR (end_year IS NOT NULL AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAg IS NOT NULL) ORDER BY end_year;"
    #cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cursor.execute(cmd1)
    SY_list = cursor.fetchall()
    init_start_year_list = []
    for year in SY_list:
        init_start_year_list.append(year[0])
    cursor.execute(cmd2)
    EY_list = cursor.fetchall()
    init_end_year_list = []
    for e_year in EY_list:
        init_end_year_list.append(e_year[0])
    
    return init_start_year_list, init_end_year_list
def end_year_list(start_year, host):
    if host=='human':
        cmd = """SELECT DISTINCT end_year FROM lassa_data WHERE end_year>={0} AND Genus='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL ORDER BY end_year;""".format(start_year)
    if host=='rodent':
        cmd = """SELECT DISTINCT end_year FROM lassa_data WHERE (end_year>={0} AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAb IS NOT NULL) OR (end_year>={0} AND Genus!='Homo' AND Latitude IS NOT NULL AND Longitude IS NOT NULL AND PropAg IS NOT NULL) ORDER BY end_year;""".format(start_year)
    #cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cursor.execute(cmd)
    year_list = cursor.fetchall()
    json_end_year = []
    for year in year_list:
        json_end_year.append({'end_year':year[0]})
    return json_end_year
def mapper(host, start_year, end_year):
    cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
    #cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    if host == 'human':
        cmd = """SELECT Latitude, Longitude, PropAb FROM lassa_data WHERE start_year AND end_year BETWEEN {0} AND {1} AND Genus='Homo'AND PropAb IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL;""".format(start_year, end_year)
        cursor.execute(cmd)
        human_data  = cursor.fetchall()
        human_headers = [x[0] for x in cursor.description]
        json_human_data = []
        for row in human_data:
            lat = float(row[0])
            lon = float(row[1])
            AbPos = float(row[2])
            entry = (lat, lon, AbPos)
            json_human_data.append(dict(zip(human_headers, entry)))
        cursor.close()
        return json_human_data
    if host == 'rodent':
        cmd1 = """SELECT Latitude, Longitude, PropAb, PropAg FROM lassa_data WHERE (start_year AND end_year BETWEEN {0} AND {1} AND Genus!='Homo'AND PropAb IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL) OR (start_year AND end_year BETWEEN {0} AND {1} AND Genus!='Homo'AND PropAg IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL);""".format(start_year, end_year)
        cursor.execute(cmd1)
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
            entry = (lat, lon, PropAb, PropAg)
            json_rodent_data.append(dict(zip(rodent_headers, entry)))
        cursor.close()
        return json_rodent_data
def db_summary():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    #Get the number of countries represented in our dataset
    country_cmd = "SELECT COUNT(*) FROM countries;"
    #Get the number of studies that our project documents
    source_cmd = "SELECT COUNT(*) FROM data_source;"
    #Number of point samples from rodents
    rodent_sample_cmd = "SELECT COUNT(Genus) FROM lassa_data WHERE Genus!='Homo';"
    #Number of point samples from humans
    human_sample_cmd = "SELECT COUNT(Genus) FROM lassa_data WHERE Genus='Homo';"    
    cmd_list = [country_cmd, source_cmd, rodent_sample_cmd, human_sample_cmd]
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
    #cmd = "SELECT start_year, SUM(NumPosAb) FROM lassa_data WHERE Genus='Homo' GROUP BY (start_year);"
    cmd = "SELECT start_year, SUM(NumPosAb), SUM(NumTestAb) FROM lassa_data WHERE Genus='Homo' GROUP BY (start_year);"
    cursor.execute(cmd)
    human_year_data = cursor.fetchall()
    cursor.close()
    year_list = []
    totalAbPos = []
    for entry in human_year_data:
        if entry[0]!= None and entry[1]!= None and entry[2]!=None:
            if entry[1]!=0 and entry[2]!=0:
                year_list.append(entry[0])
                totalAbPos.append(int(entry[1])/int(entry[2]))            
    return year_list, totalAbPos
def rodent_year_data():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    #cmd = "SELECT start_year, SUM(NumPosAb) FROM lassa_data WHERE Genus!='Homo' GROUP BY (start_year);"
    cmd = "SELECT start_year, Sum(NumPosAb), SUM(NumTestAb) FROM lassa_data WHERE Genus!='Homo' GROUP BY (start_year);"
    cursor.execute(cmd)
    rodent_year_data = cursor.fetchall()
    cursor.close()
    year_list = []
    totalAbPos = []
    for entry in rodent_year_data:
        if entry[0]!= None and entry[1]!= None and entry[2]!=None:
            if entry[1]!=0 and entry[2]!=0:
                year_list.append(entry[0])
                totalAbPos.append(int(entry[1])/int(entry[2]))
    return year_list, totalAbPos
# This bit is only used for testing the functions before implementation 
#if __name__ == '__main__':
    #print(mapper('human', '1970','2015'))
    #print(start_year_list('rodent'))
    #print(end_year_list("2002", 'rodent'))
