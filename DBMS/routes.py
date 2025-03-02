import os
import secrets
from datetime import datetime,time
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask import Flask, session, redirect, url_for, request
from DBMS.models import User
from flask_login import login_user, current_user, logout_user, login_required
from run import conn
import psycopg2
from DBMS import app




@app.route("/admin")
@login_required
def admin():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        return render_template('admin.html', title='Admin')


@app.route("/allUsers")
@login_required
def allUsers():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        users=User.query.filter_by(ngo=False).all()
        if len(users) > 0:
            users = users[1:]
        return render_template('allUsers.html', users=users,title='All Users')


@app.route("/allNgos")
@login_required
def allNgo():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        ngos=User.query.filter_by(ngo=True).all()
        return render_template('allNgos.html', ngos=ngos,title='All Ngo')


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

# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if(current_user.is_authenticated):
#         return redirect(url_for('home'))
#     form = UserRegistrationForm()
#     if form.validate_on_submit():
#         hashedPassword=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user = User(id= identity(), username=form.username.data, email=form.email.data, password=hashedPassword, address=form.address.data, ngo=form.ngo.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Your account has been created! You can now login', 'success')
#         return redirect(url_for('login'))
#     return render_template('userRegister.html', title='Register', form=form)
# # Logs in a user.
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





