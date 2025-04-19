# ------------------------------
# Database Connectivity
# ------------------------------

import sys
import traceback
import mysql.connector

class Database:
    """Handles the database connection and queries."""
    def __init__(self, host, user, password, database):
        self.connection = None
        self.cursor = None
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            sys.exit(1)

    def fetch_all(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception:
            traceback.print_exc()
            return []

    def fetch_one(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Exception:
            traceback.print_exc()
            return None

    def execute(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Exception:
            traceback.print_exc()
            return False

    def close(self):
        """Close the database connection and cursor."""
        try:
            if self.cursor:
                self.cursor.close()
        except Exception as e:
            print(f"Error closing cursor: {e}")
        try:
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")

