from DBMS import login_manager,app
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
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()

        if user_data and user_data[3] == password:  # Ideally, hash passwords instead of plain-text comparison
            return User(user_data[0], user_data[1], user_data[2])
        return None
