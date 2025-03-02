# Run the Flask application.

from DBMS import app
from DBMS.functionals.connectdb import connect_to_database,execute_sql_file
import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

conn = connect_to_database(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT)

def init_db_connection():
    global conn
    if conn is None or conn.closed:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

if __name__ == '__main__':
    init_db_connection()
    execute_sql_file(conn, "./DBMS/initialzations.sql")
    app.run(debug=True)
    

