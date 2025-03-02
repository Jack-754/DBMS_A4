from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database connection configuration from environment variables
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise Exception(f"Database connection failed: {str(e)}")

@app.route('/update', methods=['POST'])
def update_record():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['table_name', 'filters', 'new_values']):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields',
                'status_code': 400
            }), 400

        table_name = data['table_name']
        filters = data['filters']
        new_values = data['new_values']

        # Construct UPDATE query
        set_clause = ', '.join([f"{key} = %s" for key in new_values.keys()])
        where_clause = ' AND '.join([f"{key} = %s" for key in filters.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

        # Prepare parameters
        params = list(new_values.values()) + list(filters.values())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        affected_rows = cursor.rowcount
        conn.commit()

        return jsonify({
            'status': 'success',
            'message': f'Updated {affected_rows} rows successfully',
            'status_code': 200
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'status_code': 500
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/insert', methods=['POST'])
def insert_record():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['table_name', 'values']):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields',
                'status_code': 400
            }), 400

        table_name = data['table_name']
        values = data['values']

        # Construct INSERT query
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, list(values.values()))
        conn.commit()

        return jsonify({
            'status': 'success',
            'message': 'Record inserted successfully',
            'status_code': 200
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'status_code': 500
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/delete', methods=['POST'])
def delete_record():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['table_name', 'filters']):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields',
                'status_code': 400
            }), 400

        table_name = data['table_name']
        filters = data['filters']

        # Construct DELETE query
        where_clause = ' AND '.join([f"{key} = %s" for key in filters.keys()])
        query = f"DELETE FROM {table_name} WHERE {where_clause}"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, list(filters.values()))
        affected_rows = cursor.rowcount
        conn.commit()

        return jsonify({
            'status': 'success',
            'message': f'Deleted {affected_rows} rows successfully',
            'status_code': 200
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'status_code': 500
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
