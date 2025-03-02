from DBMS import login_manager, app
from flask_login import UserMixin
from datetime import datetime
from run import conn  # Ensure 'conn' is properly initialized in 'run'
import psycopg2


@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.get_user_by_id(int(user_id)) 
        if(user is None):
            print("Error loading user")
        else:
            print("User loaded successfully: ", user.username)
        return user if user else None
    except ValueError:
        return None  

class User(UserMixin):
    def __init__(self, userId, username, citizen_id, type):
        self.id = userId  # Required by Flask-Login
        self.username = username
        self.citizen_id = citizen_id
        self.type = type

    @staticmethod
    def get_user_by_id(userId):
        try:
            """Fetch user from PostgreSQL by ID."""
            cur = conn.cursor()
            cur.execute("SELECT id, username, citizen_id, user_type FROM users WHERE id = %s", (userId,))
            user_data = cur.fetchone()
            cur.close()
            if user_data:
                return User(user_data[0], user_data[1], user_data[2], user_data[3])
            return None
        except Exception as e:
            print(f"Error loading user: {e}")
            conn.rollback()  # Add this to roll back failed transactions
            return None

    @staticmethod
    def authenticate(userId, password):
        """Check if userId and password match a record in the database."""
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT id, username, citizen_id, user_type, pswd FROM users WHERE username = %s;", (userId,))
            user_data = cur.fetchone()
            
            print("Trying to print data", user_data)
            
            cur.close()
            if user_data and user_data[4] == password:  
                return User(user_data[0], user_data[1], user_data[2], user_data[3])
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            conn.rollback()  # Add this to roll back failed transactions
            return None