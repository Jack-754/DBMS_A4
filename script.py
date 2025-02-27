# script for initialising database, or other initialisations that may be required

from DBMS import db, app, bcrypt
from DBMS.models import User, Time
from datetime import time

with app.app_context():
    db.drop_all()
    db.create_all()
    hashedPassword=bcrypt.generate_password_hash("password").decode('utf-8')
    user = User(id= 1, username="admin", email="admin@gmail.com", password=hashedPassword, address="admin address", ngo=False)
    db.session.add(user)
    db.session.commit()
    time=Time(start=time(0, 0), end=time(23,59))
    db.session.add(time)
    db.session.commit()



