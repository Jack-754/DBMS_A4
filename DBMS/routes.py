import os
import secrets
from datetime import datetime,time
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask import Flask, session, redirect, url_for, request
from functools import wraps
from DBMS.models import User
from flask_login import login_user, current_user, logout_user, login_required
from run import conn
import psycopg2
from DBMS import app


@app.route("/logout")
def logout():
    logout_user()
    return jsonify({
                "Status": "Success",
                "Message": "Logout successful",
                "Data": {
                    "Query": "LOGOUT",
                    "Result": []
                },
                "error": None
            })

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"Received data is: \n {data}")
        if not data or "Data" not in data or 'userId' not in data['Data'] or 'password' not in data['Data']:
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields: userId and password",
                "Data": {
                    "Query": "LOGIN",
                    "Result": []
                },
                "error": "Missing required fields"
            })
        user = User.authenticate(data['Data']['userId'], data['Data']['password'])
        if user:
            login_user(user)
            return jsonify({
                "Status": "Success",
                "Message": "Login successful",
                "Data": {
                    "Query": "LOGIN",
                    "Result": [{
                        "userId": user.id,
                        "username": user.username,
                        "type": user.user_type
                    }]
                },
                "error": None
            })
        else:
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid credentials",
                "Data": {
                    "Query": "LOGIN",
                    "Result": []
                },
                "error": "Authentication failed"
            })
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "Server error during login",
            "Data": {
                "Query": "LOGIN",
                "Result": []
            },
            "error": str(e)
        })

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
    cursor.execute("SELECT id, name, dob, gender, phone, household_id, educational_qualification, village_id FROM citizens WHERE id=%s", (citizen_id,))
    profile = cursor.fetchone()
    cursor.close()
    if profile:
        return {
            'id': profile[0],
            'name': profile[1],
            'dob': profile[2].strftime('%Y-%m-%d') if profile[2] else None,
            'gender': profile[3],
            'phone': profile[4],
            'household_id': profile[5],
            'educational_qualification': profile[6],
            'village_id': profile[7]
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

@app.route('/citizen/certificates', methods=['POST'])
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

@app.route('/citizen/enrolled_schemes', methods=['POST'])
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
                if not key.isalnum():  # Basic SQL injection prevention
                    return jsonify({

                        "Status": "Failed",
                        "Message": "Invalid filter field",
                        "Data": {
                            "Query": "SELECT",
                            "Result": []
                        },
                        "error": "Invalid filter field"
                    }), 200

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

        # Validate required fields
        if not all(key in data for key in ['table_name', 'values']):
            return jsonify({
                'Status': 'error',
                'Message': 'Missing required fields',
                "Data": {
                    "Query": "INSERT",
                    "Result": []
                },
                "error": "Missing required fields"  
            }), 200

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
            'Status': 'success',
            'Message': 'Record inserted successfully',
            "Data": {
                "Query": "INSERT",
                "Result": []
            },
            "error": None
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            'Status': 'error',
            'Message': 'Error inserting record',
            "Data": {
                "Query": "INSERT",
                "Result": []
            },
            "error": str(e)
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
                'Status': 'error',
                'Message': 'Missing required fields',
                "Data": {
                    "Query": "DELETE",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 200

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
            'Status': 'success',
            'Message': f'Deleted {affected_rows} rows successfully',
            "Data": {
                "Query": "DELETE",
                "Result": []
            },
            "error": None
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            'Status': 'error',
            'Message': str(e),
            "Data": {
                "Query": "DELETE",
                "Result": []
            },
            "error": str(e)
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'SYSTEM_ADMINISTRATOR':
            return jsonify({
                "Status": "Failed",
                "Message": "Admin access required",
                "Data": {
                    "Query": "ADMIN",
                    "Result": []
                },
                "error": "Unauthorized access"
            }), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, username, user_type, citizen_id 
                FROM users 
                ORDER BY id
            """)
            columns = [desc[0] for desc in cur.description]
            users = cur.fetchall()
            
            formatted_users = []
            for user in users:
                formatted_users.append({columns[i]: value for i, value in enumerate(user)})
                
        return jsonify({
            "Status": "Success",
            "Message": "Users retrieved successfully",
            "Data": {
                "Query": "SELECT",
                "Result": formatted_users
            },
            "error": None
        }), 200
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "Error retrieving users",
            "Data": {
                "Query": "SELECT",
                "Result": []
            },
            "error": str(e)
        }), 500

@app.route('/admin/villages', methods=['GET'])
@admin_required
def admin_get_villages():
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM village ORDER BY id")
            columns = [desc[0] for desc in cur.description]
            villages = cur.fetchall()
            
            formatted_villages = []
            for village in villages:
                formatted_villages.append({columns[i]: value for i, value in enumerate(village)})
                
        return jsonify({
            "Status": "Success",
            "Message": "Villages retrieved successfully",
            "Data": {
                "Query": "SELECT",
                "Result": formatted_villages
            },
            "error": None
        }), 200
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "Error retrieving villages",
            "Data": {
                "Query": "SELECT",
                "Result": []
            },
            "error": str(e)
        }), 500

@app.route('/admin/panchayat_employees', methods=['GET'])
@admin_required
def admin_get_panchayat_employees():
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.citizen_id, c.name, p.position, p.salary, v.name as village_name, p.village_id
                FROM panchayat_employees p
                JOIN citizens c ON p.citizen_id = c.id
                JOIN village v ON p.village_id = v.id
                ORDER BY p.village_id, p.position
            """)
            columns = [desc[0] for desc in cur.description]
            employees = cur.fetchall()
            
            formatted_employees = []
            for employee in employees:
                formatted_employees.append({columns[i]: value for i, value in enumerate(employee)})
                
        return jsonify({
            "Status": "Success",
            "Message": "Panchayat employees retrieved successfully",
            "Data": {
                "Query": "SELECT",
                "Result": formatted_employees
            },
            "error": None
        }), 200
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "Error retrieving panchayat employees",
            "Data": {
                "Query": "SELECT",
                "Result": []
            },
            "error": str(e)
        }), 500

@app.route('/admin/update_user_type', methods=['POST'])
@admin_required
def admin_update_user_type():
    try:
        data = request.get_json()
        
        if not data or 'userId' not in data or 'newType' not in data:
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields: userId and newType",
                "Data": {
                    "Query": "UPDATE",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 400
        
        user_id = data['userId']
        new_type_input = data['newType']
        
        # Map input types to database types and positions
        valid_inputs = ['USER', 'GOVERNMENT_MONITOR', 'PRADHAN', 'MEMBER']
        if new_type_input not in valid_inputs:
            return jsonify({
                "Status": "Failed",
                "Message": f"Invalid user type. Must be one of: {', '.join(valid_inputs)}",
                "Data": {
                    "Query": "UPDATE",
                    "Result": []
                },
                "error": "Invalid user type"
            }), 400
            
        # Map input type to database type and position
        if new_type_input in ['PRADHAN', 'MEMBER']:
            new_type = 'PANCHAYAT_EMPLOYEES'
            position = new_type_input
        else:
            new_type = new_type_input
            position = None
        
        with conn.cursor() as cur:
            # Check if user exists and get citizen_id
            cur.execute("""
                SELECT u.id, u.citizen_id, u.user_type, c.village_id 
                FROM users u
                LEFT JOIN citizens c ON u.citizen_id = c.id
                WHERE u.id = %s
            """, (user_id,))
            user = cur.fetchone()
            
            if not user:
                return jsonify({
                    "Status": "Failed",
                    "Message": f"User with ID {user_id} not found",
                    "Data": {
                        "Query": "UPDATE",
                        "Result": []
                    },
                    "error": "User not found"
                }), 404
                
            # Extract user info
            citizen_id = user[1]
            old_type = user[2]
            village_id = user[3]
            
            # Check if user has required citizen data for certain roles
            if not citizen_id and new_type in ['USER', 'PANCHAYAT_EMPLOYEES', 'GOVERNMENT_MONITOR']:
                return jsonify({
                    "Status": "Failed",
                    "Message": f"User must have an associated citizen record to be a {new_type}",
                    "Data": {
                        "Query": "UPDATE",
                        "Result": []
                    },
                    "error": "Missing citizen record"
                }), 400
                
            # If the old type and new type are the same and not handling position change for PANCHAYAT_EMPLOYEES
            if old_type == new_type and (old_type != 'PANCHAYAT_EMPLOYEES' or not position):
                return jsonify({
                    "Status": "Success",
                    "Message": f"User is already of type {new_type}",
                    "Data": {
                        "Query": "UPDATE",
                        "Result": [{
                            "userId": user_id,
                            "type": new_type
                        }]
                    },
                    "error": None
                }), 200
            
            # Handle special case for GOVERNMENT_MONITOR
            if new_type == 'GOVERNMENT_MONITOR':
                if not citizen_id:
                    return jsonify({
                        "Status": "Failed",
                        "Message": "User must have an associated citizen record to be a Government Monitor",
                        "Data": {
                            "Query": "UPDATE",
                            "Result": []
                        },
                        "error": "Missing citizen record"
                    }), 400
            
            # Handle conversion to PANCHAYAT_EMPLOYEES
            if new_type == 'PANCHAYAT_EMPLOYEES':
                if not village_id:
                    return jsonify({
                        "Status": "Failed",
                        "Message": "Citizen does not have an associated village",
                        "Data": {
                            "Query": "UPDATE",
                            "Result": []
                        },
                        "error": "Missing village"
                    }), 400
                    
                # Check for existing pradhan if trying to make this user a pradhan
                if position == 'PRADHAN':
                    cur.execute("""
                        SELECT c.name
                        FROM panchayat_employees p
                        JOIN citizens c ON p.citizen_id = c.id
                        WHERE p.village_id = %s AND p.position = 'PRADHAN' AND p.citizen_id != %s
                    """, (village_id, citizen_id))
                    existing_pradhan = cur.fetchone()
                    
                    if existing_pradhan:
                        return jsonify({
                            "Status": "Failed",
                            "Message": f"Village already has a PRADHAN: {existing_pradhan[0]}",
                            "Data": {
                                "Query": "UPDATE",
                                "Result": []
                            },
                            "error": "PRADHAN already exists"
                        }), 400
                
                # Check if already in panchayat_employees
                cur.execute("SELECT position FROM panchayat_employees WHERE citizen_id = %s", (citizen_id,))
                existing_record = cur.fetchone()
                
                if existing_record:
                    # Update existing record
                    cur.execute("""
                        UPDATE panchayat_employees 
                        SET position = %s, village_id = %s 
                        WHERE citizen_id = %s
                    """, (position, village_id, citizen_id))
                else:
                    # Insert new record
                    cur.execute("""
                        INSERT INTO panchayat_employees (citizen_id, position, salary, village_id)
                        VALUES (%s, %s, %s, %s)
                    """, (citizen_id, position, 0, village_id))
                    
            # If changing from panchayat employee to something else, remove from panchayat_employees
            elif old_type == 'PANCHAYAT_EMPLOYEES' and new_type != 'PANCHAYAT_EMPLOYEES':
                cur.execute("DELETE FROM panchayat_employees WHERE citizen_id = %s", (citizen_id,))
            
            # Update user type
            cur.execute("UPDATE users SET user_type = %s WHERE id = %s", (new_type, user_id))
            conn.commit()
                
        return jsonify({
            "Status": "Success",
            "Message": f"User type updated successfully to {new_type}",
            "Data": {
                "Query": "UPDATE",
                "Result": [{
                    "userId": user_id,
                    "newType": new_type,
                    "position": position if new_type == 'PANCHAYAT_EMPLOYEES' else None
                }]
            },
            "error": None
        }), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({
            "Status": "Failed",
            "Message": "Error updating user type",
            "Data": {
                "Query": "UPDATE",
                "Result": []
            },
            "error": str(e)
        }), 500

@app.route('/admin/add_village', methods=['POST'])
@admin_required
def admin_add_village():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required field: name",
                "Data": {
                    "Query": "INSERT",
                    "Result": []
                },
                "error": "Missing required field"
            }), 400
        
        village_name = data['name']
        
        with conn.cursor() as cur:
            # Check if village already exists
            cur.execute("SELECT id FROM village WHERE name = %s", (village_name,))
            if cur.fetchone():
                return jsonify({
                    "Status": "Failed",
                    "Message": f"Village with name '{village_name}' already exists",
                    "Data": {
                        "Query": "INSERT",
                        "Result": []
                    },
                    "error": "Village already exists"
                }), 400
            
            # Insert new village
            cur.execute("INSERT INTO village (name) VALUES (%s) RETURNING id", (village_name,))
            new_id = cur.fetchone()[0]
            conn.commit()
                
        return jsonify({
            "Status": "Success",
            "Message": "Village added successfully",
            "Data": {
                "Query": "INSERT",
                "Result": [{
                    "id": new_id,
                    "name": village_name
                }]
            },
            "error": None
        }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({
            "Status": "Failed",
            "Message": "Error adding village",
            "Data": {
                "Query": "INSERT",
                "Result": []
            },
            "error": str(e)
        }), 500


@app.route('/admin/schemes', methods=['GET'])
@admin_required
def admin_get_schemes():
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, description FROM schemes ORDER BY id")
            columns = [desc[0] for desc in cur.description]
            schemes = cur.fetchall()
            
            formatted_schemes = []
            for scheme in schemes:
                formatted_schemes.append({columns[i]: value for i, value in enumerate(scheme)})
                
        return jsonify({
            "Status": "Success",
            "Message": "Schemes retrieved successfully",
            "Data": {
                "Query": "SELECT",
                "Result": formatted_schemes
            },
            "error": None
        }), 200
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "Error retrieving schemes",
            "Data": {
                "Query": "SELECT",
                "Result": []
            },
            "error": str(e)
        }), 500

@app.route('/admin/add_scheme', methods=['POST'])
@admin_required
def admin_add_scheme():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'description' not in data:
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields: name, description",
                "Data": {
                    "Query": "INSERT",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 400
        
        scheme_name = data['name']
        description = data['description']
        
        with conn.cursor() as cur:
            # Check if scheme already exists
            cur.execute("SELECT id FROM schemes WHERE name = %s", (scheme_name,))
            if cur.fetchone():
                return jsonify({
                    "Status": "Failed",
                    "Message": f"Scheme with name '{scheme_name}' already exists",
                    "Data": {
                        "Query": "INSERT",
                        "Result": []
                    },
                    "error": "Scheme already exists"
                }), 400
            
            # Insert new scheme
            cur.execute("""
                INSERT INTO schemes (name, description) 
                VALUES (%s, %s) RETURNING id
            """, (scheme_name, description))
            
            new_id = cur.fetchone()[0]
            conn.commit()
                
        return jsonify({
            "Status": "Success",
            "Message": "Scheme added successfully",
            "Data": {
                "Query": "INSERT",
                "Result": [{
                    "id": new_id,
                    "name": scheme_name,
                    "description": description
                }]
            },
            "error": None
        }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({
            "Status": "Failed",
            "Message": "Error adding scheme",
            "Data": {
                "Query": "INSERT",
                "Result": []
            },
            "error": str(e)
        }), 500


@app.route('/panchayat_employee/census_data', methods=['GET'])
@login_required
def get_census_data():
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT c.citizen_id, ci.name, c.event_type, c.event_date 
            FROM census_data c
            JOIN citizens ci ON c.citizen_id = ci.id
            ORDER BY c.event_date DESC
        """)
        
        census_records = cur.fetchall()
        
        # Convert to list of dictionaries for JSON response
        census_data = []
        for record in census_records:
            census_data.append({
                'citizen_id': record[0],
                'citizen_name': record[1],
                'event_type': record[2],
                'event_date': record[3].strftime('%Y-%m-%d')
            })
        
        cur.close()
        
        return jsonify({
            "Status": "Success",
            "Message": "Census data retrieved successfully",
            "Data": {
                "Query": "SELECT",
                "Result": [census_data]
            },
            "error": None
        }), 200
        
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "An unexpected error occurred",
            "Data": {
                "Query": "SELECT",
                "Result": []
            },
            "error": str(e)
        }), 500

@app.route('/panchayat_employee/census_data/add', methods=['POST'])
@login_required
def add_census_record():
    try:
        data = request.get_json()
        
        # Validate request format
        if not data or 'Query' not in data or data['Query'] != 'INSERT' or 'Data' not in data:
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid request format",
                "Data": {
                    "Query": "INSERT",
                    "Result": []
                },
                "error": "Invalid request format"
            }), 400

        request_data = data['Data']
        # Validate required fields
        required_fields = ['citizen_id', 'event_type', 'event_date']
        if not all(field in request_data for field in required_fields):
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields",
                "Data": {
                    "Query": "INSERT",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 400
        
        # Validate event_type
        valid_event_types = ['Birth', 'Death', 'Marriage', 'Divorce']
        if request_data['event_type'] not in valid_event_types:
            return jsonify({
                "Status": "Failed",
                "Message": f"Invalid event type. Must be one of: {', '.join(valid_event_types)}",
                "Data": {
                    "Query": "INSERT",
                    "Result": []
                },
                "error": "Invalid event type"
            }), 400
        
        # Check if citizen exists
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM citizens WHERE id = %s", (request_data['citizen_id'],))
            if not cur.fetchone():
                return jsonify({
                    "Status": "Failed",
                    "Message": "Citizen ID does not exist",
                    "Data": {
                        "Query": "INSERT",
                        "Result": []
                    },
                    "error": "Citizen not found"
                }), 404
            
            # Insert new census record
            cur.execute("""
                INSERT INTO census_data (citizen_id, event_type, event_date)
                VALUES (%s, %s, %s)
                RETURNING citizen_id, event_type, event_date
            """, (request_data['citizen_id'], request_data['event_type'], request_data['event_date']))
            
            new_record = cur.fetchone()
            conn.commit()
            
            return jsonify({
                "Status": "Success",
                "Message": "Census record added successfully",
                "Data": {
                    "Query": "INSERT",
                    "Result": [{
                        "citizen_id": new_record[0],
                        "event_type": new_record[1],
                        "event_date": new_record[2].strftime('%Y-%m-%d')
                    }]
                },
                "error": None
            }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            "Status": "Failed",
            "Message": "Error adding census record",
            "Data": {
                "Query": "INSERT",
                "Result": []
            },
            "error": str(e)
        }), 500

@app.route('/panchayat_employee/census_data/delete', methods=['POST'])
@login_required
def delete_census_record():
    try:
        data = request.get_json()
        
        # Validate request format
        if not data or 'Query' not in data or data['Query'] != 'DELETE' or 'Data' not in data:
            return jsonify({
                "Status": "Failed",
                "Message": "Invalid request format",
                "Data": {
                    "Query": "DELETE",
                    "Result": []
                },
                "error": "Invalid request format"
            }), 400

        request_data = data['Data']
        # Validate required fields
        if not request_data or "citizen_id" not in request_data or "event_date" not in request_data or "event_type" not in request_data: 
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields: citizen_id and event_date and event_type",
                "Data": {
                    "Query": "DELETE",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 400
        
        with conn.cursor() as cur:
            # First check if the record exists and get its details
            cur.execute("""
                SELECT c.citizen_id, ci.name, c.event_type, c.event_date 
                FROM census_data c
                JOIN citizens ci ON c.citizen_id = ci.id
                WHERE c.citizen_id = %s AND c.event_date::text = %s AND c.event_type = %s
            """, (request_data['citizen_id'], request_data['event_date'], request_data['event_type']))
            
            record = cur.fetchone()
            if not record:
                return jsonify({
                    "Status": "Failed",
                    "Message": "Census record not found",
                    "Data": {
                        "Query": "DELETE",
                        "Result": []
                    },
                    "error": "Record not found"
                }), 404
            
            # Store record details for response
            deleted_record = {
                "citizen_id": record[0],
                "citizen_name": record[1],
                "event_type": record[2],
                "event_date": record[3].strftime('%Y-%m-%d')
            }
            
            # Delete the record
            cur.execute("""
                DELETE FROM census_data 
                WHERE citizen_id = %s AND event_date::text = %s AND event_type = %s
            """, (request_data['citizen_id'], request_data['event_date'], request_data['event_type']))
            
            conn.commit()
            
            return jsonify({
                "Status": "Success",
                "Message": "Census record deleted successfully",
                "Data": {
                    "Query": "DELETE",
                    "Result": [deleted_record]
                },
                "error": None
            }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            "Status": "Failed",
            "Message": "Error deleting census record",
            "Data": {
                "Query": "DELETE",
                "Result": []
            },
            "error": str(e)
        }), 500
    

def get_citizen_land_records(citizen_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT lr.land_id, lr.citizen_id, lr.area_acres,lr.crop_type, v.name as village_name
        FROM land_records lr
        JOIN village v ON lr.village_id = v.id
        WHERE lr.citizen_id = %s
        ORDER BY lr.registration_date DESC""", (citizen_id,))
    records = cursor.fetchall()
    cursor.close()
    
    if records:
        return [{
            'land_id': record[0],
            'citizen_id': record[1],
            'area_acres': float(record[2]),
            'crop_type': record[3],
            'village_name': record[4]
        } for record in records]
    return []

@app.route('/citizen/land_records', methods=['POST'])
@login_required
def citizen_land_records():
    try:
        user_id = current_user.id
        
        # First get the citizen_id from users table
        with conn.cursor() as cur:
            cur.execute("SELECT citizen_id FROM users WHERE id = %s", (user_id,))
            result = cur.fetchone()
            if not result or not result[0]:
                return jsonify({
                    "Status": "Failed",
                    "Message": "No citizen ID associated with user",
                    "Data": {
                        "Query": "SELECT",
                        "Result": []
                    },
                    "error": "Citizen ID not found"
                }), 404
            
            citizen_id = result[0]
            land_records = get_citizen_land_records(citizen_id)
            
            if land_records:
                return jsonify({
                    "Status": "Success",
                    "Message": "Land records retrieved successfully",
                    "Data": {
                        "Query": "SELECT",
                        "Result": land_records
                    },
                    "error": None
                }), 200
            else:
                return jsonify({
                    "Status": "Success",
                    "Message": "No land records found",
                    "Data": {
                        "Query": "SELECT",
                        "Result": []
                    },
                    "error": None
                }), 200
            
    except Exception as e:
        return jsonify({
            "Status": "Failed",
            "Message": "Error retrieving land records",
            "Data": {
                "Query": "SELECT",
                "Result": []
            },
            "error": str(e)
        }), 500
    
@app.route('/panchayat_employee/land_records/update', methods=['POST'])
@login_required
def update_land_record():
    try:
        data = request.get_json()
        
        # Validate request format
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
        # Validate required fields
        required_fields = ['land_id', 'updates']
        if not all(field in request_data for field in required_fields):
            return jsonify({
                "Status": "Failed",
                "Message": "Missing required fields: land_id and updates",
                "Data": {
                    "Query": "UPDATE",
                    "Result": []
                },
                "error": "Missing required fields"
            }), 400

        # Validate that user is a panchayat employee
        if not current_user.user_type == 'PANCHAYAT_EMPLOYEES':
            return jsonify({
                "Status": "Failed",
                "Message": "Unauthorized access. Only panchayat employees can update land records",
                "Data": {
                    "Query": "UPDATE",
                    "Result": []
                },
                "error": "Unauthorized access"
            }), 403

        land_id = request_data['land_id']
        updates = request_data['updates']

        # Validate updatable fields
        allowed_fields = {'area_acres', 'crop_type'}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            return jsonify({
                "Status": "Failed",
                "Message": f"Invalid fields for update: {', '.join(invalid_fields)}",
                "Data": {
                    "Query": "UPDATE",
                    "Result": []
                },
                "error": "Invalid fields"
            }), 400

        with conn.cursor() as cur:
            # First check if record exists
            cur.execute("""
                SELECT lr.*, v.name as village_name
                FROM land_records lr
                JOIN village v ON lr.village_id = v.id
                WHERE lr.land_id = %s
            """, (land_id,))
            
            existing_record = cur.fetchone()
            if not existing_record:
                return jsonify({
                    "Status": "Failed",
                    "Message": f"Land record with ID {land_id} not found",
                    "Data": {
                        "Query": "UPDATE",
                        "Result": []
                    },
                    "error": "Record not found"
                }), 404

            # Construct UPDATE query
            update_fields = []
            update_values = []
            for field, value in updates.items():
                update_fields.append(f"{field} = %s")
                update_values.append(value)
            
            # Add land_id to values
            update_values.append(land_id)
            
            update_query = f"""
                UPDATE land_records 
                SET {', '.join(update_fields)}
                WHERE land_id = %s
                RETURNING land_id, citizen_id, area_acres, crop_type, village_id
            """
            
            cur.execute(update_query, update_values)
            updated_record = cur.fetchone()
            
            # Get village name for the updated record
            cur.execute("SELECT name FROM village WHERE id = %s", (updated_record[4],))
            village_name = cur.fetchone()[0]
            
            conn.commit()
            
            # Format the response
            formatted_record = {
                "land_id": updated_record[0],
                "citizen_id": updated_record[1],
                "area_acres": float(updated_record[2]),
                "crop_type": updated_record[3],
                "village_name": village_name
            }
            
            return jsonify({
                "Status": "Success",
                "Message": "Land record updated successfully",
                "Data": {
                    "Query": "UPDATE",
                    "Result": [formatted_record]
                },
                "error": None
            }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            "Status": "Failed",
            "Message": "Error updating land record",
            "Data": {
                "Query": "UPDATE",
                "Result": []
            },
            "error": str(e)
        }), 500