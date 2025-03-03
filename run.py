# Run the Flask application....

from backend import app
from backend.functionals.connectdb import connect_to_database,execute_sql_file
import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

conn = connect_to_database(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT)

if(conn is None):   
    print("Connection to database failed")  
    exit(1)

if __name__ == '__main__':
    # execute_sql_file(conn, "./DBMS/kill_script.sql")
    app.run(debug=True, host = "0.0.0.0",port=5001)
    

