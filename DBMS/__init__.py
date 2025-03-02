from flask import Flask, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
# Initializes Flask configuration from keys in config.py.
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
SECRET_KEY = "your_secret_key"  # Change this to a secure key

def create_jwt(user_id):
    """Manually creates a JWT token"""
    payload = {
        "sub": user_id,  # User identity
        "iat": datetime.utcnow(),  # Issued at time
        "exp": datetime.utcnow() + timedelta(hours=1)  # Expiration time (1 hour)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
# Login manager for user authentication
login_manager = LoginManager()
login_manager.init_app(app)

jwt = JWTManager(app)

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({
        "status": 100,
        "error": "Unauthorized access", 
        "message": "Please log in first"
}), 401

from DBMS import routes