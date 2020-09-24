
import mysql.connector

def human_mapper():
    cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
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
    cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
    cursor = cnx.cursor()
    cursor.execute("SELECT Latitude, Longitude, NumPosAb FROM lassa_data WHERE Genus!='Homo'AND NumPosAb IS NOT NULL AND Latitude IS NOT NULL AND Longitude IS NOT NULL")
    rodent_data  = cursor.fetchall()
    rodent_headers = [x[0] for x in cursor.description]
    json_rodent_data = []
    for row in rodent_data:
        lat = float(row[0])
        lon = float(row[1])
        AbPos = int(row[2])
        entry = (lat, lon, AbPos)
        json_rodent_data.append(dict(zip(rodent_headers, entry)))
    cursor.close()
    return json_rodent_data

