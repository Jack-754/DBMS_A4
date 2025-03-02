import os
import secrets
from datetime import datetime,time
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
