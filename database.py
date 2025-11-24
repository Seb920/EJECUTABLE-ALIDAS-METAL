import psycopg2
from psycopg2 import sql, Error
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            print("Conexión exitosa a PostgreSQL")
        except Error as e:
            print(f"Error al conectar a PostgreSQL: {e}")
    
    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Error en consulta: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return []
    
    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None
    
    def call_procedure(self, procedure_name, params):
        try:
            cursor = self.connection.cursor()
            cursor.callproc(procedure_name, params)
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Error en procedimiento {procedure_name}: {e}")
            return None

# Instancia global de base de datos
db = Database()