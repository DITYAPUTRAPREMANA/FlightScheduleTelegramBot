import os
import requests
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://10.2.20.210/fids_new/index.php/Welcome/api_inter"
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'flight_data'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def create_table_if_not_exists(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flight_api_data (
            id INT PRIMARY KEY,
            operator VARCHAR(100),
            schedule VARCHAR(100),
            estimate VARCHAR(100),
            flightno VARCHAR(50),
            gatenumber VARCHAR(20),
            flightstat VARCHAR(50),
            fromtolocation VARCHAR(100)
        )
    ''')
    conn.commit()
    cursor.close()

def insert_or_update_data(conn, data):
    cursor = conn.cursor()
    sql = '''
        INSERT INTO flight_api_data (id, operator, schedule, estimate, flightno, gatenumber, flightstat, fromtolocation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            operator=VALUES(operator),
            schedule=VALUES(schedule),
            estimate=VALUES(estimate),
            flightno=VALUES(flightno),
            gatenumber=VALUES(gatenumber),
            flightstat=VALUES(flightstat),
            fromtolocation=VALUES(fromtolocation)
    '''
    cursor.execute(sql, (
        data['id'],
        data['operator'],
        data['schedule'],
        data['estimate'],
        data['flightno'],
        data['gatenumber'],
        data['flightstat'],
        data['fromtolocation']
    ))
    conn.commit()
    cursor.close()

def main():
    response = requests.get(API_URL)
    response.raise_for_status()
    flights = response.json()

    conn = mysql.connector.connect(**DB_CONFIG)
    create_table_if_not_exists(conn)

    for flight in flights:
        data = {
            'id': flight.get('id'),
            'operator': flight.get('operator'),
            'schedule': flight.get('schedule'),
            'estimate': flight.get('estimate'),
            'flightno': flight.get('flightno'),
            'gatenumber': flight.get('gatenumber'),
            'flightstat': flight.get('flightstat'),
            'fromtolocation': flight.get('fromtolocation')
        }
        insert_or_update_data(conn, data)
    conn.close()
    print(f"Inserted/updated {len(flights)} records.")

if __name__ == "__main__":
    main()