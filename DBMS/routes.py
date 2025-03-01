import os
import secrets
from datetime import datetime,time
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask import Flask, session, redirect, url_for, request
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
    
    if('user' in session):
        response['status'] = 400
        response['message'] = 'User already logged in'
        return jsonify(response)
    
    data = request.json  # Get JSON payload from the request
    return jsonify({"message": "Data received!", "data": data})