from flask import Flask, jsonify
from markupsafe import escape
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],  # Specific frontend origin
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        "supports_credentials": True,
        "expose_headers": ["Authorization"],
        "allow_credentials": True
    }
})

# # Initializes Flask configuration from keys in config.py.
# app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# SECRET_KEY = "your_se
# # Login manager for user authentication
# login_manager = LoginManager()
# login_manager.init_app(app)

jwt = JWTManager(app)


from backend import routes