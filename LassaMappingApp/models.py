"""models.py contains the database model for our users"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
# Initialize database
db = SQLAlchemy()
# Defie that user class found in the database
class App_User(UserMixin,db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80), unique=False)
