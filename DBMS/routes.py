import os
import secrets
from datetime import datetime,time
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask import Flask, session, redirect, url_for, request
from run import conn
import psycopg2
from DBMS import app


# Renders the home page. 
# If the user is authenticated and an admin, redirects to the admin page.
# If the user is authenticated but has no location set, flashes a warning to set location and redirects to account page.
# Otherwise, fetches all restaurants or only nearby restaurants based on auth status,  
# fetches all transactions, and renders the home template.
@app.route("/")
@app.route("/home")
def home():
    user=current_user
    restaurants=None
    if(user.is_authenticated and user.id==1):
        return redirect(url_for('admin'))
    if(user.is_authenticated and (user.latitude is None or user.longitude is None)):
        if(isinstance(user, User)):
            flash('Please enter your location first in Account settings for getting list of restaurants','warning')
        else:
            flash('Please enter your location first in Restaurant settings for getting list of orders','warning')
        return redirect(url_for('account'))
    elif(user.is_authenticated):
        restaurants = Restaurant.query.filter(Restaurant.latitude.isnot(None),Restaurant.longitude.isnot(None)).all()
    else:
        restaurants = Restaurant.query.all()
    transactions = Transaction.query.all()
    return render_template('home.html', restaurants=restaurants,title='Home',calculate_distance=calculate_distance,transactions=transactions)


@app.route("/admin")
@login_required
def admin():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        return render_template('admin.html', title='Admin')

# Renders a page showing all restaurants.

# If the user is not an admin, redirects to the home page.  
# Otherwise, fetches all restaurants from the database and renders the allRestaurants template.

@app.route("/allRestaurants")
@login_required
def allRestaurants():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        restaurants=Restaurant.query.all()
        return render_template('allRestaurants.html', restaurants=restaurants,title='All Restaurants')

# Renders a page showing all users except the admin.

# If the current user is not admin, redirects to the home page.
# Otherwise, fetches all users except the admin from the database and renders the allUsers template.

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

# Renders a page showing all NGO users.

# If the current user is not admin, redirects to the home page.
# Otherwise, fetches all NGO users from the database and renders the allNgos template.

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