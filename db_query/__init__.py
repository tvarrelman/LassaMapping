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
def start_year_list():
    #cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
    cursor = cnx.cursor()
    cursor.execute("SELECT DISTINCT start_year FROM lassa_data WHERE start_year IS NOT NULL ORDER BY start_year;")
    year_list = cursor.fetchall()
    start_year_list = []
    for year in year_list:
        start_year_list.append(year[0])
    return start_year_list
def human_mapper():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cursor.execute("SELECT Latitude, Longitude, NumPosAb FROM lassa_data WHERE Genus='Homo'AND NumPosAb IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL")
    human_data  = cursor.fetchall()
    human_headers = [x[0] for x in cursor.description]
    json_human_data = []
    for row in human_data:
        lat = float(row[0])
        lon = float(row[1])
        AbPos = int(row[2])
        entry = (lat, lon, AbPos)
        json_human_data.append(dict(zip(human_headers, entry)))
    cursor.close()
    return json_human_data

def rodent_mapper():
    cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_name)
    cursor = cnx.cursor()
    cursor.execute("SELECT lassa_data.Latitude, lassa_data.Longitude, lassa_data.NumPosAb, countries.country_name FROM lassa_data, countries WHERE lassa_data.country_id=countries.country_id AND Genus!='Homo'AND NumPosAb IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL")
    rodent_data  = cursor.fetchall()
    rodent_headers = [x[0] for x in cursor.description]
    json_rodent_data = []
    with open("LassaMappingApp/static/Africa.geojson") as JsonFile:
        strJson = json.load(JsonFile)
    for row in rodent_data:
        lat = float(row[0])
        lon = float(row[1])
 #       point = Point(lon, lat)
        # check each polygon to see if it contains the point
#        for feature in strJson['features']:
#            polygon = shape(feature['geometry'])
#            if polygon.contains(point):
#                center_point = polygon.centroid
#                center_lon = center_point.coords.xy[0][0]
#                center_lat = center_point.coords.xy[1][0]
        AbPos = int(row[2])
        country = str(row[3])
        entry = (lat, lon, AbPos, country)
 #       json_headers.append(['centerLat', 'centerLon'])
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
if __name__ == '__main__':
    start_year_list()
