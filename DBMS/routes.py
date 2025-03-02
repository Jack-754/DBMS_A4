import os
import secrets
from datetime import datetime,time
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask import Flask, session, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from run import conn
import psycopg2
from DBMS import app
from models import User

@app.route('/login', methods=['POST'])
def login():
    response = {
        'status': None,
        'message': None,
        'data': None
    }
    
    # Check if user is already logged in
    if current_user.is_authenticated:
        response['status'] = 400
        response['message'] = 'User already logged in'
        return jsonify(response)
    
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