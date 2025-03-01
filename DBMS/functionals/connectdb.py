import psycopg2
from psycopg2 import sql, OperationalError

def connect_to_database(host, dbname, user, password, port):
    """
    Establishes a connection to the PostgreSQL database.
    """
    try:
        connection = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port
        )
        print("Connection to PostgreSQL DB successful")
        return connection
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None

def execute_query(connection, query):
    """
    Executes the provided SQL query and returns results as a list of dictionaries.
    Each dictionary represents a row with column names as keys.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            return [dict(zip(column_names, row)) for row in results]
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

if __name__ == "__main__":
    # Database connection details
    HOST = "10.5.18.73"
    DBNAME = "22CS30066"
    USER = "22CS30066"
    PASSWORD = "pwd2202"
    PORT = 5432  
    connection = connect_to_database(HOST, DBNAME, USER, PASSWORD, PORT)
    Query = "SELECT c.name AS People_with_more_than_1_acre FROM citizens c JOIN land_records lr ON c.citizen_id = lr.citizen_id WHERE lr.area_acres > 1;"
    print(execute_query(connection=connection, query=Query))