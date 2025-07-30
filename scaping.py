import requests
import mysql.connector
from mysql.connector import Error
import os

db_config = {
    'host': os.getenv('DB_HOST', '10.2.99.9'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'TrizzKunn182005'),
    'database': os.getenv('DB_NAME', 'flight_data'),
    'port': int(os.getenv('DB_PORT', 3306))
}

api_url = "http://10.2.20.210/fids_new/index.php/Welcome/api_inter"

def fetch_data_from_api():
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch data from API (Status code: {response.status_code})")
        return None

def create_table_if_not_exists(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INT PRIMARY KEY,
            operator VARCHAR(100),
            schedule VARCHAR(100),
            estimate VARCHAR(100),
            flightno VARCHAR(50),
            gatenumber VARCHAR(20),
            flightstat VARCHAR(50),
            fromtolocation VARCHAR(100),
            departure ENUM('ID', 'IN')
        )
    """)
    conn.commit()
    cursor.close()

def save_data_to_mysql(data):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            create_table_if_not_exists(conn)
            cursor = conn.cursor()

            flights = data.get('data', [])
            print(f"DEBUG: Jumlah flights: {len(flights)}")
            for flight in flights:
                if not isinstance(flight, dict):
                    print(f"SKIP: Bukan dict: {flight}")
                    continue
                try:
                    flight['departure'] = 'IN'

                    query = """
                        INSERT INTO flights (id, operator, schedule, estimate, flightno, gatenumber, flightstat, fromtolocation, departure)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            operator=VALUES(operator),
                            schedule=VALUES(schedule),
                            estimate=VALUES(estimate),
                            flightno=VALUES(flightno),
                            gatenumber=VALUES(gatenumber),
                            flightstat=VALUES(flightstat),
                            fromtolocation=VALUES(fromtolocation),
                            departure=VALUES(departure)
                    """
                    values = (
                        flight.get('id'),
                        flight.get('operator'),
                        flight.get('schedule'),
                        flight.get('estimate'),
                        flight.get('flightno'),
                        flight.get('gatenumber'),
                        flight.get('flightstat'),
                        flight.get('fromtolocation'),
                        flight.get('departure')
                    )
                    cursor.execute(query, values)
                except Exception as e:
                    print(f"Gagal insert/update data id={flight.get('id', 'N/A')}: {e}")
            conn.commit()
            print(f"Data successfully inserted/updated into the database.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    data = fetch_data_from_api()
    if data:
        save_data_to_mysql(data)
    else:
        print("Tidak ada data yang diambil dari API.")
