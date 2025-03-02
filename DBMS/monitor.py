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
            return jsonify({'error': 'Invalid table name'}), 400
        
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
                'ne': '!='
            }
            
            for key, filter_data in filters.items():
                if not key.isalnum():  # Basic SQL injection prevention
                    return jsonify({'error': 'Invalid filter field'}), 400
                
                # Extract operator and value from filter_data
                operator = filter_data.get('operator', 'eq')  # default to equals
                value = filter_data.get('value')
                
                if operator not in valid_operators:
                    return jsonify({'error': f'Invalid operator: {operator}'}), 400
                
                where_conditions.append(f"{key} {valid_operators[operator]} %s")
                params.append(value)
            
            query += " WHERE " + " AND ".join(where_conditions)
        else:
            params = []
        
        # Execute query
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            
        conn.close()
        
        # Convert results to JSON
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
