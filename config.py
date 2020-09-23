"""
Configuration settings for our flask application
"""

import os
from os import environ, path
from dotenv import load_dotenv

# finds the absolute path of this file
basedir = path.abspath(path.dirname(__file__))
# reads the key value from .env, and adds it to the environment variable
load_dotenv(path.join(basedir, '.env'))

# create the Config class, which will contain general configuration info.
class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    #SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
print(Config)
# create the production configuration settings, which will be added to the general config.    
class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    #DATABASE_URI = os.environ.get('PROD_DATABASE_URI')

# create the developmen configuration settings, which will be added to the general config.
class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    #DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    
    
