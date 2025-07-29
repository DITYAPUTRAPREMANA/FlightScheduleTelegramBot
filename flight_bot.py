import os
import logging
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT'))
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
                SELECT id, operator, schedule, estimate, flightno, gatenumber, flightstat, fromtolocation
                FROM flights
                WHERE flightno = %s AND DATE(schedule) = %s
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
                SELECT id, operator, schedule, estimate, flightno, gatenumber, flightstat, fromtolocation
                FROM flights
                WHERE DATE(schedule) = %s
                ORDER BY schedule
                LIMIT 20
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
                SELECT id, operator, schedule, estimate, flightno, gatenumber, flightstat, fromtolocation
                FROM flights
                WHERE fromtolocation LIKE %s AND DATE(schedule) = %s
                ORDER BY schedule
                LIMIT 20
            """
            # Search for flights containing origin and destination in fromtolocation
            route_pattern = f"%{origin}%{destination}%"
            cursor.execute(query, (route_pattern, date))
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as err:
            logger.error(f"Database query failed: {err}")
            return []