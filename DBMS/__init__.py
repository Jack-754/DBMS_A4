from flask import Flask, jsonify
from flask_login import LoginManager
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Initializes Flask configuration from keys in config.py.
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

# Login manager for user authentication
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({
        "status": 100,
        "error": "Unauthorized access", 
        "message": "Please log in first"
}), 401

from DBMS import routes