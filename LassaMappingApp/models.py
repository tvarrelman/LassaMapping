"""models.py contains the database model for our users"""

from . import db
from flask_login import UserMixin

# Define the user class found in the database
class User(UserMixin,db.Model):
    __tablename__ = 'App_User'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80), unique=False)
