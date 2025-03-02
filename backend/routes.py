import os
import secrets
from datetime import datetime, time, timedelta

import psycopg2
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from flask_cors import CORS
from flask_jwt_extended import (JWTManager, create_access_token,
                                get_jwt_identity, jwt_required)
from flask_login import current_user, login_required, login_user, logout_user

from backend import app
from backend.models import User
from run import conn

# Add these configurations after creating the app
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"]
    }
})

app.config['JWT_SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)



@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        

    try:
        data = request.get_json()
        if not data or "Data" not in data or 'username' not in data['Data'] or 'password' not in data['Data']:
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields: username and password",
                "Data": {
                    "Query": "LOGIN",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 400

        # Modify the User.authenticate method according to your needs
        user = User.authenticate(data['Data']['username'], data['Data']['password'])
        if user:
            access_token = create_access_token(identity=user.id)
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
                "error": None,
                "access_token": access_token
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
    response = {}
    if current_user.is_authenticated:
        response.update({
            "status": "Failed",
            "message": "User already logged in",
            "Data": {
                "Query" : "REGISTER",
                "Data" : []
            },
            "error": "User already logged in"
            })
        return jsonify(response)
    try:
        data = request.get_json()
        if not data:
            response.update({"status": "Failed",
            "message": "Invalid JSON data",
            "Data": {
                "Query" : "REGISTER",
                "Data" : []
            },
            "error": "Invalid JSON data"
            })
            return jsonify(response)
        required_fields = ['citizen_id', 'username', 'password']
        if not all(field in data['Data'] and data['Data'][field] for field in required_fields):
            response.update({
                "status": "Failure",
                "message": "Missing required fields",
                "Data": {
                    "Query" : "REGISTER",
                    "Data" : []
                },
                "error": "Missing required fields"
            })
            return jsonify(response)


        citizen_id, username, password = data['Data']['citizen_id'], data['Data']['username'], data['Data']['password']

        if len(username) < 3 or len(password) < 6:
            response.update({
                "status": "Failure",
                "message": "Invalid username or password length",
                "Data": {
                    "Query" : "REGISTER",
                    "Data" : []
                },
                "error": "Invalid username or password length"
            })
            return jsonify(response)

        # Use psycopg2 cursor
        with conn.cursor() as cur:
            cur.execute("SELECT citizen_id, username FROM users WHERE citizen_id = %s OR username = %s",
                        (citizen_id, username))
            existing_user = cur.fetchone()
            if existing_user:
                field = 'Citizen ID' if existing_user[0] == citizen_id else 'Username'
                response.update({
                    "status": "Failure",
                    "message": f'{field} already registered',
                    "Data": {
                        "Query" : "REGISTER",
                        "Data" : []
                    },
                    "error": f'{field} already registered'
                })
                return jsonify(response)
            
            cur.execute("SELECT id FROM citizens WHERE id = %s ",(citizen_id,))
            valid = cur.fetchone()
            if not valid:
                response.update({
                    "status": "Failure",
                    "message": f'No such citizen found',
                    "Data": {
                        "Query" : "REGISTER",
                        "Data" : []
                    },
                    "error": f'No such citizen found'
                })
                return jsonify(response)
            cur.execute("INSERT INTO users (citizen_id, username, pswd, user_type) VALUES (%s, %s, %s, %s)",
                        (citizen_id, username, password, 'CITIZEN'))
            conn.commit()

        response.update({
            "status": "Success",
            "message": "User registered successfully",
            "Data": {
                "Query" : "REGISTER",
                "Data" : []
            },
            "error": None
        })
        return jsonify(response), 200
    except Exception as e:
        conn.rollback()
        print(f"Registration error: {str(e)}")
        response.update({
            "status": "Failure",
            "message": "Internal server error",
            "Data": {
                "Query" : "REGISTER",
                "Data" : []
            },
            "error": str(e)
        })
        return jsonify(response), 500

def get_citizen_profile(citizen_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name, dob, gender, phone, household_id, educational_qualification, village_id FROM citizens WHERE id={citizen_id};")
    profile = cursor.fetchone()
    if profile:
        return {
            'id': profile[0],
            'name': profile[1],
            'dob': profile[2],
            'gender': profile[3],
            'phone': profile[4],
            'household_id': profile[5],
            'educational_id': profile[6],
            'village_id': profile[7]
        }
    else:
        return None

@app.route('/profile', methods=['GET'])
@jwt_required()
def citizen_profile():
    try:
        print(request.headers)
        user_id = get_jwt_identity()
        print(user_id)
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
    cursor.execute("SELECT asset_id, asset_type, date_of_registration FROM assets WHERE owner_id=%s", (owner_id,))
    assets = cursor.fetchall()
    cursor.close()
    
    if assets:
        return [{
            'id': asset[0],
            'citizen_id': owner_id,
            'asset_type': asset[1],
            'date_of_registration': asset[2]
        } for asset in assets]
    return []

@app.route('/citizen/assets', methods=['GET'])
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
        SELECT receipt_no, amount, filing_date
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
        } for filing in filings]
    return []

@app.route('/citizen/tax', methods=['GET'])
@login_required
def citizen_tax_filings():
    user_id = current_user.id
    tax_filings = get_citizen_tax_filings(user_id)
    if tax_filings:
        return jsonify({
            "status": "Success",
            "Message": "Tax filings retrieved successfully",
            "Data": {
                "Query": "SELECT",
                "Result": [tax_filings]
            },
            "error": None
        }), 200

def get_citizen_certificates(citizen_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT certificate_no, cert_type, issue_date
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

@app.route('/citizen/certificates', methods=['GET'])
@login_required
def citizen_certificates():
    user_id = current_user.id
    certificates = get_citizen_certificates(user_id)
    if certificates:
        return jsonify({
            "status": "Success",
            "Message": "Certificates retrieved successfully",
            "Data": {
                "Query": "SELECT",
                "Result": [certificates]
            },
            "error": None
        }), 200

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

@app.route('/citizen/enrolled_schemes', methods=['GET'])
@login_required
def citizen_enrolled_schemes():
    user_id = current_user.id
    schemes = get_citizen_schemes(user_id)
    if schemes:
        return jsonify({
            "status": "Success",
            "Message": "Scheme enrollments retrieved successfully",
            "Data": {
                "Query": "SELECT",
                "Result": [schemes]
            },
            "error": None
        }), 200

@app.route('/query_table', methods=['GET'])
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
            }), 200

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
            }), 200

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
                operator = filter_data['operator']  
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
                    }), 200

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
                        }), 200

                    where_conditions.append(f"{key} BETWEEN %s AND %s")
                    params.extend(value)
                else:
                    where_conditions.append(f"{key} {valid_operators[operator]} %s")
                    params.append(value)

            query += " WHERE " + " AND ".join(where_conditions)

        # Execute query
        with conn.cursor() as cur:
            query += ";"
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
                "Query": "SELECT",
                "Result": formatted_results
            },
            "error": None,
            
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
            }), 200

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
            }), 200

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

        if not all(key in data["Data"] for key in ['table_name', 'values']):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields',
                'status_code': 200
            }), 200

        table_name = data["Data"]['table_name']
        values = data["Data"]['values']

        # Construct INSERT query
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        print(query)
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

# @app.route('/delete', methods=['DELETE'])
# def delete_record():
#     # try:
#         data = request.get_json()

#         # Validate required fields
#         if not all(key in data["Data"] for key in ['table_name', 'filters']):
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Missing required fields',
#                 'status_code': 200
#             }), 200

#         table_name = data['Data']['table_name']
#         filters = data['Data']['filters']

#         # Construct DELETE query
#         where_clause = ' AND '.join([f"{key} = %s" for key in filters.keys()])
#         query = f"DELETE FROM {table_name} WHERE {where_clause}"

#         cursor = conn.cursor()
#         cursor.execute(query)
#         affected_rows = cursor.rowcount
#         conn.commit()

#         return jsonify({
#             'status': 'success',
#             'message': f'Deleted {affected_rows} rows successfully',
#             'status_code': 200
#         }), 200

    # except Exception as e:
    #     conn.rollback()
    #     return jsonify({
    #         'status': 'error',
    #         'message': str(e),
    #         'status_code': 500
    #     }), 500
    # finally:
    #     if 'cursor' in locals():
    #         cursor.close()

@app.route('/delete', methods=['DELETE'])
@login_required
def delete():
    try:
        data = request.get_json()
        if not data or 'Query' not in data or 'Data' not in data:
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid request format",
                "Data": {
                    "Query": "DELETE",
                    "Result": []
                },
                "error": "Invalid request format"
            }), 200

        # Extract table name and filters from request
        table_name = data['Data'].get('table_name')
        filters = data['Data'].get('filters', {})

        # Basic SQL injection prevention for table name
        if not table_name or not table_name.isalnum():
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid table name",
                "Data": {
                    "Query": "DELETE",
                    "Result": []
                },
                "error": "Invalid table name"
            }), 200

        # Construct the SQL query
        query = f"DELETE FROM {table_name}"
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
                operator = filter_data['operator']  
                value = filter_data.get('value')

                if operator not in valid_operators:
                    return jsonify({
                        "Status": "Failed",
                        "Message": f'Invalid operator: {operator}',
                        "Data": {
                            "Query": "DELETE",
                            "Result": []
                        },
                        "error": f"Invalid operator: {operator}"
                    }), 200

                if operator == 'between':
                    if not isinstance(value, list) or len(value) != 2:
                        return jsonify({
                            "Status": "Failed",
                            "Message": "BETWEEN operator requires a list of two values",
                            "Data": {
                                "Query": "DELETE",
                                "Result": []
                            },
                            "error": "BETWEEN operator requires a list of two values"
                        }), 200

                    where_conditions.append(f"{key} BETWEEN %s AND %s")
                    params.extend(value)
                else:
                    where_conditions.append(f"{key} {valid_operators[operator]} %s")
                    params.append(value)

            query += " WHERE " + " AND ".join(where_conditions)

        # Execute query
        with conn.cursor() as cur:
            query += ";"
            cur.execute(query, params)

            conn.commit()
        return jsonify({
            "Status": "Success",
            "Message": "DELETE executed successfully",
            "Data": {
                "Query": "DELETE",
                "Result": []
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





