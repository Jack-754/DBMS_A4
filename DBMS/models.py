from DBMS import login_manager,app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime, timedelta,time

