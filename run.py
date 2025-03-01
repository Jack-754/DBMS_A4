# Run the Flask application....

from DBMS import app
import psycopg2

DB_HOST = "1111.1111.1111.1111"
DB_NAME = "your_database"
DB_USER = "user"
DB_PASSWORD = "password"

conn = None

def init_db_connection():
    global conn
    if conn is None or conn.closed:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

if __name__ == '__main__':
    init_db_connection()
    app.run(debug=True)
    

