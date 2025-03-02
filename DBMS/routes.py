import os
import secrets
from datetime import datetime,time
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask import Flask, session, redirect, url_for, request
from DBMS.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_login import login_user, current_user, logout_user, login_required
from run import conn
import psycopg2
from DBMS import app


@app.route('/login', methods=['POST'])
def post_example():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'Data' not in data or 'userId' not in data['Data'] or 'password' not in data['Data']:
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields: userId and password",
                "Data": {
                    "Query": "LOGIN",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 400
        
        # Authenticate user
        user = User.authenticate(data['Data']['userId'], data['Data']['password'])
        
        if user:
            # Login the user with Flask-Login
            login_user(user)
            
            return jsonify({
                "Status": "Success",
                "Message": "Login successful",
                "Data": {
                    "Query": "LOGIN",
                    "Result": [{
                        "userId": user.id,
                        "username": user.username,
                        "type": user.type
                    }]
                },
                "error": None
            }), 200
        else:
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid credentials",
                "Data": {
                    "Query": "LOGIN",
                    "Result": []
                },
                "error": "Authentication failed"
            }), 401
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "Server error during login",
            "Data": {
                "Query": "LOGIN",
                "Result": []
            },
            "error": str(e)
        }), 500

@app.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return jsonify({
            "Status": "Failed",
            "Message": "User already logged in",
            "Data": {
                "Query": "REGISTER",
                "Result": []
            },
            "error": "Already authenticated"
        }), 400

    try:
        data = request.get_json()
        if not data or 'Data' not in data:
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid JSON data",
                "Data": {
                    "Query": "REGISTER",
                    "Result": []
                },
                "error": "Invalid data format"
            }), 400

        required_fields = ['citizen_id', 'username', 'password']
        if not all(field in data['Data'] and data['Data'][field] for field in required_fields):
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields",
                "Data": {
                    "Query": "REGISTER",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 400

        citizen_id, username, password = data['Data']['citizen_id'], data['Data']['username'], data['Data']['password']

        if len(username) < 3 or len(password) < 6:
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid username or password length",
                "Data": {
                    "Query": "REGISTER",
                    "Result": []
                },
                "error": "Validation error"
            }), 400

        # Use psycopg2 cursor
        with conn.cursor() as cur:
            cur.execute("SELECT citizen_id, username FROM users WHERE citizen_id = %s OR username = %s",
                        (citizen_id, username))
            existing_user = cur.fetchone()

            if existing_user:
                field = 'Citizen ID' if existing_user[0] == citizen_id else 'Username'
                return jsonify({
                    "Status": "Failed",
                    "Message": f'{field} already registered',
                    "Data": {
                        "Query": "REGISTER",
                        "Result": []
                    },
                    "error": "Duplicate entry"
                }), 400

            cur.execute("INSERT INTO users (citizen_id, username, password, type) VALUES (%s, %s, %s, %s)",
                        (citizen_id, username, password, 'USER'))
            conn.commit()

        return jsonify({
            "Status": "Success",
            "Message": "User registered successfully",
            "Data": {
                "Query": "REGISTER",
                "Result": []
            },
            "error": None
        }), 201
        
    except Exception as e:
        conn.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({
            "Status": "Failed",
            "Message": "Internal server error",
            "Data": {
                "Query": "REGISTER",
                "Result": []
            },
            "error": str(e)
        }), 500

def get_citizen_profile(citizen_id):
    conn = psycopg2.connect(
        dbname="localhost",
        user="postgress",
        password="postgress",
        host="postgress",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, dob, age, gender, phone, household_id, educational_id, village_id FROM citizens WHERE id=%s", (citizen_id,))
    profile = cursor.fetchone()
    conn.close()
    if profile:
        return {
            'id': profile[0],
            'name': profile[1],
            'dob': profile[2],
            'age': profile[3],
            'gender': profile[4],
            'phone': profile[5],
            'household_id': profile[6],
            'educational_id': profile[7],
            'village_id': profile[8]
        }
    else:
        return None

@app.route('/citizen/profile', methods=['POST'])
@login_required
def citizen_profile():
    try:
        user_id = current_user.id
        profile = get_citizen_profile(user_id)
        if profile:
            return jsonify({
                "Status": "Success",
                "Message": "Profile fetched successfully",
                "Data": {
                    "Query": "SELECT",
                    "Result": [profile]
                },
                "error": None
            }), 200
        else:
            return jsonify({
                "Status": "Failed",
                "Message": "Citizen not found",
                "Data": {
                    "Query": "SELECT",
                    "Result": []
                },
                "error": "Not found"
            }), 404
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "Error fetching profile",
            "Data": {
                "Query": "SELECT",
                "Result": []
            },
            "error": str(e)
        }), 500

def get_citizen_assets(owner_id):
    cursor = conn.cursor()
    cursor.execute("SELECT , asset_id, a_type, date_of_registration FROM assets WHERE owner_id=%s", (owner_id,))
    assets = cursor.fetchall()
    cursor.close()
    
    if assets:
        return [{
            'id': asset[0],
            'citizen_id': asset[1],
            'asset_type': asset[2],
            'quantity': asset[3],
            'value': asset[4],
            'purchase_date': asset[5]
        } for asset in assets]
    return []

@app.route('/citizen/assets', methods=['POST'])
@login_required
def citizen_assets():
    try:
        user_id = current_user.id
        assets = get_citizen_assets(user_id)
        if assets:
            return jsonify({
                "Status": "Success",
                "Message": "Assets fetched successfully",
                "Data": {
                    "Query": "SELECT",
                    "Result": assets
                },
                "error": None
            }), 200
        else:
            return jsonify({
                "Status": "Failed",
                "Message": "No assets with user found",
                "Data": {
                    "Query": "SELECT",
                    "Result": []
                },
                "error": "Not found"
            }), 404
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "Error fetching assets",
            "Data": {
                "Query": "SELECT",
                "Result": []
            },
            "error": str(e)
        }), 500

def get_citizen_tax_filings(citizen_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT receipt_no, amount, filing_date, financial_year 
        FROM tax_filing 
        WHERE citizen_id=%s
        ORDER BY filing_date DESC""", (citizen_id,))
    filings = cursor.fetchall()
    cursor.close()
    
    if filings:
        return [{
            'receipt_no': filing[0],
            'amount': filing[1],
            'filing_date': filing[2].strftime('%Y-%m-%d'),
            'financial_year': filing[3]
        } for filing in filings]
    return []

@app.route('/citizen/tax', methods=['POST'])
@login_required
def citizen_tax_filings():
    user_id = current_user.id
    tax_filings = get_citizen_tax_filings(user_id)
    if tax_filings:
        return jsonify(tax_filings)
    else:
        return jsonify({'error': 'No tax filings found for user'}), 404

def get_citizen_certificates(citizen_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT certificate_no, type, issue_date
        FROM certificates 
        WHERE citizen_issued=%s
        ORDER BY issue_date DESC""", (citizen_id,))
    certificates = cursor.fetchall()
    cursor.close()
    
    if certificates:
        return [{
            'certificate_no': cert[0],
            'type': cert[1], 
            'issue_date': cert[2].strftime('%Y-%m-%d')
        } for cert in certificates]
    return []

@app.route('/citizen/certificates', methods=['POST'])
@login_required
def citizen_certificates():
    user_id = current_user.id
    certificates = get_citizen_certificates(user_id)
    if certificates:
        return jsonify(certificates)
    else:
        return jsonify({'error': 'No certificates found for user'}), 404

def get_citizen_schemes(citizen_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT scheme_id, enrollment_date, enrollment_id
        FROM scheme_enrollment 
        WHERE citizen_id=%s
        ORDER BY enrollment_date DESC""", (citizen_id,))
    enrollments = cursor.fetchall()
    cursor.close()
    
    if enrollments:
        return [{
            'scheme_id': enrollment[0],
            'enrollment_date': enrollment[1].strftime('%Y-%m-%d'),
            'enrollment_id': enrollment[2]
        } for enrollment in enrollments]
    return []

@app.route('/citizen/enrolled_schemes', methods=['POST'])
@login_required
def citizen_enrolled_schemes():
    user_id = current_user.id
    schemes = get_citizen_schemes(user_id)
    if schemes:
        return jsonify(schemes)
    else:
        return jsonify({'error': 'No scheme enrollments found for user'}), 404

@app.route('/query_table', methods=['POST'])
@login_required
def query_table():
    try:
        data = request.get_json()
        
        if not data or 'Query' not in data or 'Data' not in data:
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid request format",
                "Data": {
                    "Query": "SELECT",
                    "Result": []
                },
                "error": "Invalid request format"
            }), 400

        # Extract table name and filters from request
        table_name = data['Data'].get('table_name')
        filters = data['Data'].get('filters', {})

        # Basic SQL injection prevention for table name
        if not table_name or not table_name.isalnum():
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid table name",
                "Data": {
                    "Query": "SELECT",
                    "Result": []
                },
                "error": "Invalid table name"
            }), 400

        # Construct the SQL query
        query = f"SELECT * FROM {table_name}"
        params = []

        # Add WHERE clause if filters exist
        if filters:
            where_conditions = []
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
                        "Status": "Failed",
                        "Message": "Invalid filter field",
                        "Data": {
                            "Query": "SELECT",
                            "Result": []
                        },
                        "error": "Invalid filter field"
                    }), 400

                operator = filter_data.get('operator', 'eq')  # Default to equals
                value = filter_data.get('value')

                if operator not in valid_operators:
                    return jsonify({
                        "Status": "Failed",
                        "Message": f'Invalid operator: {operator}',
                        "Data": {
                            "Query": "SELECT",
                            "Result": []
                        },
                        "error": f"Invalid operator: {operator}"
                    }), 400

                if operator == 'between':
                    if not isinstance(value, list) or len(value) != 2:
                        return jsonify({
                            "Status": "Failed",
                            "Message": "BETWEEN operator requires a list of two values",
                            "Data": {
                                "Query": "SELECT",
                                "Result": []
                            },
                            "error": "BETWEEN operator requires a list of two values"
                        }), 400
                    where_conditions.append(f"{key} BETWEEN %s AND %s")
                    params.extend(value)
                else:
                    where_conditions.append(f"{key} {valid_operators[operator]} %s")
                    params.append(value)

            query += " WHERE " + " AND ".join(where_conditions)

        # Execute query
        with conn.cursor() as cur:
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description]
            results = cur.fetchall()
            
            # Format the results as list of dictionaries
            formatted_results = []
            for row in results:
                formatted_results.append({columns[i]: value for i, value in enumerate(row)})

        return jsonify({
            "Status": "Success",
            "Message": "Query executed successfully",
            "Data": {
                "Query": query,
                "Result": formatted_results
            },
            "error": None
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            "Status": "Failed",
            "Message": "Error executing query",
            "Data": {
                "Query": "SELECT",
                "Result": []
            },
            "error": str(e)
        }), 500
    
@app.route('/update', methods=['POST'])
def update_record():
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'Query' not in data or data['Query'] != 'UPDATE' or 'Data' not in data:
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid request format",
                "Data": {
                    "Query": "UPDATE",
                    "Result": []
                },
                "error": "Invalid request format"
            }), 400

        request_data = data['Data']
        if not all(key in request_data for key in ['table_name', 'filters', 'new_values']):
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields",
                "Data": {
                    "Query": "UPDATE",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 400

        table_name = request_data['table_name']
        filters = request_data['filters']
        new_values = request_data['new_values']

        # Construct UPDATE query
        set_clause = ', '.join([f"{key} = %s" for key in new_values.keys()])
        where_clause = ' AND '.join([f"{key} = %s" for key in filters.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

        # Prepare parameters
        params = list(new_values.values()) + list(filters.values())

        cursor = conn.cursor()
        cursor.execute(query, params)
        affected_rows = cursor.rowcount
        conn.commit()

        return jsonify({
            "Status": "Success",
            "Message": f"Updated {affected_rows} rows successfully",
            "Data": {
                "Query": "UPDATE",
                "Result": [{"affected_rows": affected_rows}]
            },
            "error": None
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            "Status": "Failed",
            "Message": "Error updating record",
            "Data": {
                "Query": "UPDATE",
                "Result": []
            },
            "error": str(e)
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()


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

        cursor = conn.cursor()
        cursor.execute(query, list(values.values()))
        conn.commit()

        return jsonify({
            'status': 'success',
            'message': 'Record inserted successfully',
            'status_code': 200
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'status_code': 500
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()


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
        conn.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'status_code': 500
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()






