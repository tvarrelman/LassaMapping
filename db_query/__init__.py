
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

def db_summary():
    cnx = mysql.connector.connect(user='tanner', password='atgh-klpM-cred5', host='localhost', database='lassa_tanner')
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

# This bit is only used for testing the functions before implementation 
#if __name__ == '__main__':
#    db_summary()
