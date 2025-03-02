from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database connection configuration from environment variables
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),  # default to localhost if not specified
    'port': os.getenv('DB_PORT', '5432')  # default to 5432 if not specified
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/query_table', methods=['POST'])
def query_table():
    try:
        data = request.get_json()
        
        # Extract table name and filters from request
        table_name = data.get('table_name')
        filters = data.get('filters', {})
        
        # Basic SQL injection prevention
        if not table_name.isalnum():
            return jsonify({
                'status': 'error',
                'status_code': 400,
                'message': 'Invalid table name',
                'data': None
            }), 400
        
        # Construct the SQL query
        query = f"SELECT * FROM {table_name}"
        
        # Add WHERE clause if filters exist
        if filters:
            where_conditions = []
            params = []
            
            # Define valid operators
            valid_operators = {
                'eq': '=',
                'gt': '>',
                'lt': '<',
                'gte': '>=',
                'lte': '<=',
                'ne': '!=',
                'between': 'BETWEEN'
            }
            
            for key, filter_data in filters.items():
                if not key.isalnum():  # Basic SQL injection prevention
                    return jsonify({
                        'status': 'error',
                        'status_code': 400,
                        'message': 'Invalid filter field',
                        'data': None
                    }), 400
                
                # Extract operator and value from filter_data
                operator = filter_data.get('operator', 'eq')  # default to equals
                value = filter_data.get('value')
                
                if operator not in valid_operators:
                    return jsonify({
                        'status': 'error',
                        'status_code': 400,
                        'message': f'Invalid operator: {operator}',
                        'data': None
                    }), 400
                
                # Special handling for BETWEEN operator
                if operator == 'between':
                    if not isinstance(value, list) or len(value) != 2:
                        return jsonify({
                            'status': 'error',
                            'status_code': 400,
                            'message': 'BETWEEN operator requires a list of two values',   #### we must revieve a list from the front end 
                            'data': None
                        }), 400
                    where_conditions.append(f"{key} BETWEEN %s AND %s")
                    params.extend(value)  # Add both values to params
                else:
                    where_conditions.append(f"{key} {valid_operators[operator]} %s")
                    params.append(value)
            
            query += " WHERE " + " AND ".join(where_conditions)
        else:
            params = []
        
        # Execute query
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'status_code': 500,
                'message': 'Database connection failed',
                'data': None
            }), 500
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            
        conn.close()
        
        # Return successful response with data
        return jsonify({
            'status': 'success',
            'status_code': 200,
            'message': 'Query executed successfully',
            'data': results
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'status_code': 500,
            'message': str(e),
            'data': None
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
