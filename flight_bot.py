import os
import logging
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT')) if os.getenv('DB_PORT') else None
}

logger = logging.getLogger(__name__)

class FlightScheduleBot:
    def __init__(self):
        self.db_connection = None
        self.connect_database()

    def connect_database(self):
        try:
            self.db_connection = mysql.connector.connect(**DB_CONFIG)
            logger.info("Database connected successfully")
        except mysql.connector.Error as err:
            logger.error(f"Database connection failed: {err}")

    def ensure_connection(self):
        try:
            if self.db_connection is None or not self.db_connection.is_connected():
                self.connect_database()
        except mysql.connector.Error as err:
            logger.error(f"Database reconnection failed: {err}")

    def get_flight_info(self, flight_code, date):
        try:
            self.ensure_connection()
            if self.db_connection is None:
                logger.error("Database connection is not available.")
                return None
            cursor = self.db_connection.cursor(dictionary=True)
            query = """
                SELECT f.*,
                       ap_origin.city as origin_city, ap_origin.name as origin_airport,
                       ap_dest.city as dest_city, ap_dest.name as dest_airport,
                       a.name as airline_name
                FROM flights f
                JOIN airports ap_origin ON f.origin_airport = ap_origin.code
                JOIN airports ap_dest ON f.destination_airport = ap_dest.code
                JOIN airlines a ON f.airline_id = a.id
                WHERE f.flight_code = %s AND DATE(f.departure_time) = %s
            """
            cursor.execute(query, (flight_code.upper(), date))
            result = cursor.fetchone()
            cursor.close()
            return result
        except mysql.connector.Error as err:
            logger.error(f"Database query failed: {err}")
            return None

    def get_flights_by_date(self, date):
        try:
            self.ensure_connection()
            if self.db_connection is None:
                logger.error("Database connection is not available.")
                return []
            cursor = self.db_connection.cursor(dictionary=True)
            query = """
                SELECT f.flight_code, f.departure_time, f.arrival_time, f.status,
                       ap_origin.city as origin_city, ap_dest.city as dest_city,
                       a.name as airline_name
                FROM flights f
                JOIN airports ap_origin ON f.origin_airport = ap_origin.code
                JOIN airports ap_dest ON f.destination_airport = ap_dest.code
                JOIN airlines a ON f.airline_id = a.id
                WHERE DATE(f.departure_time) = %s
                ORDER BY f.departure_time
                LIMIT 10
            """
            cursor.execute(query, (date,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as err:
            logger.error(f"Database query failed: {err}")
            return []

    def get_flights_by_route(self, origin, destination, date):
        try:
            self.ensure_connection()
            if self.db_connection is None:
                logger.error("Database connection is not available.")
                return []
            cursor = self.db_connection.cursor(dictionary=True)
            query = """
                SELECT f.flight_code, f.departure_time, f.arrival_time, f.status,
                       ap_origin.city as origin_city, ap_dest.city as dest_city,
                       a.name as airline_name
                FROM flights f
                JOIN airports ap_origin ON f.origin_airport = ap_origin.code
                JOIN airports ap_dest ON f.destination_airport = ap_dest.code
                JOIN airlines a ON f.airline_id = a.id
                WHERE f.origin_airport = %s AND f.destination_airport = %s 
                AND DATE(f.departure_time) = %s
                ORDER BY f.departure_time
            """
            cursor.execute(query, (origin.upper(), destination.upper(), date))
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as err:
            logger.error(f"Database query failed: {err}")
            return []