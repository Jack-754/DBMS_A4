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
    response = {
        'status': None,
        'message': None,
        'data': None
    }
    
    # Get JSON data from request
    data = request.form
    
    # Validate required fields
    if not data or 'userId' not in data or 'password' not in data:
        response['status'] = 400
        response['message'] = 'Missing required fields: userId and password'
        return jsonify(response)
    
    # Authenticate user
    user = User.authenticate(data['userId'], data['password'])
    
    if user:
        # Login the user with Flask-Login
        login_user(user)
        
        response['status'] = 200
        response['message'] = 'Login successful'
        response['data'] = {
            'userId': user.id,
            'username': user.username,
            'type': user.type
        }
    else:
        response['status'] = 401
        response['message'] = 'Invalid credentials'

    return jsonify(response)

@app.route('/register', methods=['POST'])
def register():
    response = {'status': None, 'message': None}

    if current_user.is_authenticated:
        response.update({'status': 400, 'message': 'User already logged in'})
        return jsonify(response)

    try:
        data = request.get_json()
        if not data:
            response.update({'status': 400, 'message': 'Invalid JSON data'})
            return jsonify(response)

        required_fields = ['citizen_id', 'username', 'password']
        if not all(field in data and data[field] for field in required_fields):
            response.update({'status': 400, 'message': 'Missing required fields'})
            return jsonify(response)

        citizen_id, username, password = data['citizen_id'], data['username'], data['password']

        if len(username) < 3 or len(password) < 6:
            response.update({'status': 400, 'message': 'Invalid username or password length'})
            return jsonify(response)

        # Use psycopg2 cursor
        with conn.cursor() as cur:
            cur.execute("SELECT citizen_id, username FROM users WHERE citizen_id = %s OR username = %s",
                        (citizen_id, username))
            existing_user = cur.fetchone()

            if existing_user:
                field = 'Citizen ID' if existing_user[0] == citizen_id else 'Username'
                response.update({'status': 400, 'message': f'{field} already registered'})
                return jsonify(response)

            cur.execute("INSERT INTO users (citizen_id, username, password, type) VALUES (%s, %s, %s, %s)",
                        (citizen_id, username, password, 'USER'))
            conn.commit()

        response.update({'status': 201, 'message': 'User registered successfully'})
        
    except Exception as e:
        conn.rollback()
        print(f"Registration error: {str(e)}")
        response.update({'status': 500, 'message': 'Internal server error'})

    return jsonify(response)

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
    user_id = current_user.id
    profile = get_citizen_profile(user_id)
    if profile:
        return jsonify(profile)
    else:
        return jsonify({'error': 'Citizen not found'}), 404

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
    user_id = current_user.id
    assets = get_citizen_assets(user_id)
    if assets:
        return jsonify(assets)
    else:
        return jsonify({'error': 'No assets with user found'}), 404

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

        # Extract table name and filters from request
        table_name = data.get('table_name')
        filters = data.get('filters', {})

        # Basic SQL injection prevention for table name
        if not table_name or not table_name.isalnum():
            return jsonify({
                'status': 'error',
                'status_code': 400,
                'message': 'Invalid table name',
                'data': None
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
                        'status': 'error',
                        'status_code': 400,
                        'message': 'Invalid filter field',
                        'data': None
                    }), 400

                operator = filter_data.get('operator', 'eq')  # Default to equals
                value = filter_data.get('value')

                if operator not in valid_operators:
                    return jsonify({
                        'status': 'error',
                        'status_code': 400,
                        'message': f'Invalid operator: {operator}',
                        'data': None
                    }), 400

                if operator == 'between':
                    if not isinstance(value, list) or len(value) != 2:
                        return jsonify({
                            'status': 'error',
                            'status_code': 400,
                            'message': 'BETWEEN operator requires a list of two values',
                            'data': None
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
            results = cur.fetchall()

        return jsonify({
            'status': 'success',
            'status_code': 200,
            'message': 'Query executed successfully',
            'data': results
        })

    except Exception as e:
        conn.rollback()
        return jsonify({
            'status': 'error',
            'status_code': 500,
            'message': str(e),
            'data': None
        }), 500
    
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
        conn.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'status_code': 500
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






