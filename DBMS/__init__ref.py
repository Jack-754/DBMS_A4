from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from flask_mail import Mail
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import psycopg2

app = Flask(__name__)

# Initializes Flask configuration from keys in config.py.
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config["JWT_SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
# Bcrypt instance for password hashing
bcrypt = Bcrypt(app)
# Login manager for user authentication
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

jwt = JWTManager(app)


from DBMS import routes