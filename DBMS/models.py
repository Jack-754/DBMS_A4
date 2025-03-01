# This file is for defining classes for each of the different types of entities in the SSFDS application.

# Restaurant - Represents a restaurant user account. Used to manage restaurant profiles and post available dishes.

# User - Represents an individual user account. Used to manage donor profiles and donate to posted dishes. 

# Dish - Represents a meal or food item posted by a restaurant. Contains dish details.

# Transaction - Records donation transactions made by users to dishes. Tracks donation amounts.

# Order - Records food orders made by users for posted dishes. Tracks order status.

# Donation - Records monetary donations made by users. Tracks donation amounts.

# Time - Defines time slots for dish availability and food orders. 

from DBMS import db, login_manager,app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime, timedelta,time
from run import conn
import psycopg2

@login_manager.user_loader
def loadUser(userId):
    return User.get_user_by_id(userId)

class User(UserMixin):
    def __init__(self, user_id, username, citizen_id, type):
        self.id = user_id  # Required by Flask-Login
        self.username = username
        self.citizen_id = citizen_id
        self.type = type

    @staticmethod
    def get_user_by_id(user_id):
        """Fetch user from PostgreSQL by ID."""
        cur = conn.cursor()
        # query needs to be modified
        cur.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()

        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def authenticate(username, password):
        """Check if username and password match a record in the database."""
        conn = psycopg2.connect("dbname=your_db user=your_user password=your_password host=your_host")
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if user_data and user_data[3] == password:  # Ideally, hash passwords instead of plain-text comparison
            return User(user_data[0], user_data[1], user_data[2])
        return None
