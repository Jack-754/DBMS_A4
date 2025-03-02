from DBMS import db, login_manager,app
from flask_login import UserMixin

class user(UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    typ = db.Column(db.integer, nullable=False)

    def __repr__(self):
        return f"hello user('{self.user_id}','{self.username}', '{self.typ}')"

    

    